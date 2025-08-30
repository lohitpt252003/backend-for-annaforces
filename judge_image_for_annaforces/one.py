# robust_subprocess_runner.py
import subprocess
import tempfile
import os
import re
import uuid
import shutil
import traceback

# configuration
IMAGE_NAME = "sandbox-image:latest"
WORKDIR = "/sandbox/temp"

def ensure_image_exists(image_name):
    """Return (True, None) if exists or built; (False, error_message) on failure."""
    try:
        # check image
        proc = subprocess.run(["docker", "image", "inspect", image_name],
                              capture_output=True, text=True)
        if proc.returncode == 0:
            return True, None
        # try to build a minimal image if missing
        dockerfile = r'''
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ python3 coreutils time && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /sandbox/temp
'''
        build = subprocess.run(["docker", "build", "-t", image_name, "-"],
                               input=dockerfile, text=True, capture_output=True)
        if build.returncode != 0:
            return False, f"docker build failed: {build.stderr or build.stdout}"
        return True, None
    except FileNotFoundError as e:
        return False, "docker CLI not found"
    except Exception as e:
        return False, f"ensure_image_exists error: {e}"

def safe_remove_container(container_name):
    try:
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, text=True)
    except Exception:
        pass

def execute_code(language='python',
                 code='print("this is test code\\nsubmit ur own code, this is the default code")',
                 stdin='',
                 time_limit_s=2,
                 memory_limit_mb=1024,
                 image_name=IMAGE_NAME):
    """
    Run user code inside a docker container using subprocess (docker CLI).
    This function always attempts to remove the container and delete temp files, no matter what.
    Returns a dict with keys:
      - success (bool)
      - timed_out (bool)
      - exit_code (int or None)
      - stdout (str)
      - stderr (str)
      - compile_error (str or "")
      - err_message (str or "")
    """
    # Normalize stdin
    try:
        if stdin is None:
            stdin = ""
        stdin = stdin.replace("\r\n", "\n")
        if stdin and not stdin.endswith("\n"):
            stdin += "\n"
    except Exception:
        stdin = str(stdin)

    lang = language.lower()
    if lang not in ("python", "c", "c++"):
        return {"success": False, "timed_out": False, "exit_code": None,
                "stdout": "", "stderr": "", "compile_error": "", "err_message": f"Unsupported language: {language}"}

    ext = {"python": ".py", "c": ".c", "c++": ".cpp"}[lang]
    exec_name = "main"  # output binary for c/c++, ignored for python

    tmp_dir = None
    container_name = f"judge_{uuid.uuid4().hex[:8]}"
    container_started = False

    result = {
        "success": False,
        "timed_out": False,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "compile_error": "",
        "err_message": ""
    }

    try:
        # make temp dir and files on host
        tmp_dir = tempfile.mkdtemp(prefix="judge_")
        code_filename = f"main{ext}"
        code_path = os.path.join(tmp_dir, code_filename)
        input_path = os.path.join(tmp_dir, "input.txt")

        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        with open(input_path, "w", encoding="utf-8") as f:
            f.write(stdin)

        # ensure docker is available & image exists (or build)
        ok, err = ensure_image_exists(image_name)
        if not ok:
            result["err_message"] = err or "docker image not available"
            return result

        # start detached container (root inside)
        run_cmd = [
            "docker", "run", "--name", container_name,
            "--memory", f"{memory_limit_mb}m",
            "--memory-swap", f"{memory_limit_mb}m",
            "-d", image_name, "sleep", "300"
        ]
        p = subprocess.run(run_cmd, capture_output=True, text=True)
        if p.returncode != 0:
            result["err_message"] = f"Failed to start container: {p.stderr.strip() or p.stdout.strip()}"
            return result

        container_started = True
        container_id = p.stdout.strip()

        # create target dir just in case
        subprocess.run(["docker", "exec", container_id, "mkdir", "-p", WORKDIR], capture_output=True, text=True)

        # copy code and input into container
        cp1 = subprocess.run(["docker", "cp", code_path, f"{container_id}:{WORKDIR}/{code_filename}"],
                             capture_output=True, text=True)
        if cp1.returncode != 0:
            result["err_message"] = f"docker cp code failed: {cp1.stderr.strip() or cp1.stdout.strip()}"
            return result

        cp2 = subprocess.run(["docker", "cp", input_path, f"{container_id}:{WORKDIR}/input.txt"],
                             capture_output=True, text=True)
        if cp2.returncode != 0:
            result["err_message"] = f"docker cp input failed: {cp2.stderr.strip() or cp2.stdout.strip()}"
            return result

        # compile if needed
        if lang in ("c", "c++"):
            compiler = "gcc" if lang == "c" else "g++"
            # cd to WORKDIR so compiled binary is there
            compile_cmd = f"cd {WORKDIR} && {compiler} {code_filename} -o {exec_name} 2>&1"
            cp = subprocess.run(["docker", "exec", container_id, "sh", "-c", compile_cmd],
                                capture_output=True, text=True)
            if cp.returncode != 0:
                # compilation failed: capture both stdout/stderr
                compile_out = (cp.stdout or "") + (cp.stderr or "")
                result["compile_error"] = compile_out
                result["err_message"] = "Compilation failed"
                return result

        # prepare run command inside container
        if lang == "python":
            run_main = f"python3 {code_filename}"
        else:
            run_main = f"./{exec_name}"

        inner_cmd = f"cd {WORKDIR} && /usr/bin/timeout {int(time_limit_s)}s /usr/bin/time -v {run_main} < input.txt"

        # execute inside container, interactive not needed because input redirected from file
        try:
            exec_proc = subprocess.run(["docker", "exec", "-i", container_id, "sh", "-c", inner_cmd],
                                       capture_output=True, text=True, timeout=time_limit_s + 4)
        except subprocess.TimeoutExpired as te:
            # Host side timeout — best effort cleanup and report TLE
            result["timed_out"] = True
            result["err_message"] = f"Host-side timeout expired: {te}"
            return result

        # collect outputs
        result["exit_code"] = exec_proc.returncode
        stdout_output = exec_proc.stdout or ""
        stderr_output = exec_proc.stderr or ""

        # parse time output (if present in stderr)
        time_taken = 0.0
        mem_mb = 0.0
        tm = re.search(r"User time \(seconds\): ([\d\.]+)", stderr_output)
        mm = re.search(r"Maximum resident set size \(kbytes\): (\d+)", stderr_output)
        if tm:
            try:
                time_taken = float(tm.group(1))
            except Exception:
                pass
        if mm:
            try:
                mem_mb = int(mm.group(1)) / 1024.0
            except Exception:
                pass

        # clean program stderr by removing time output
        cleaned_stderr = stderr_output
        split_marker = None
        if "Command being timed:" in stderr_output:
            split_marker = "Command being timed:"
        elif "User time (seconds):" in stderr_output:
            split_marker = "User time (seconds):"
        if split_marker:
            cleaned_stderr = stderr_output.split(split_marker)[0].rstrip()

        result["stdout"] = stdout_output
        result["stderr"] = cleaned_stderr

        # determine statuses
        if exec_proc.returncode == 124:
            result["timed_out"] = True
            result["err_message"] = f"Time Limit Exceeded (> {time_limit_s}s)"
            result["success"] = False
            return result
        if exec_proc.returncode == 137:
            result["err_message"] = f"Memory Limit Exceeded (> {memory_limit_mb} MB)"
            result["success"] = False
            return result
        if exec_proc.returncode != 0:
            result["err_message"] = f"Runtime Error (Exit Code: {exec_proc.returncode})"
            result["success"] = False
            return result

        # success
        result["success"] = True
        return result

    except Exception as e:
        # Capture traceback for debugging but don't crash
        tb = traceback.format_exc()
        result["err_message"] = f"Runner exception: {e}\n{tb}"
        return result

    finally:
        # cleanup container if it was started
        try:
            if container_started:
                safe_remove_container(container_name)
        except Exception:
            pass
        # cleanup temp dir
        try:
            if tmp_dir and os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


if __name__ == '__main__':
    import json
    # --- Example Usage ---

    # Example 0: Using all default values
    print("--- Example 0: Python Defaults ---")
    result = execute_code()
    print(json.dumps(result, indent=2))
    print("-" * 20)

    # Example 1: Successful Python execution
    print("--- Example 1: Python Success ---")
    python_code = """
import sys
name = sys.stdin.readline()
print(f"Hello, {name.strip()}!")
"""
    result = execute_code(language='python', code=python_code, stdin='World', time_limit_s=5, memory_limit_mb=128)
    print(json.dumps(result, indent=2))
    print("-" * 20)

    # Example 2: C++ code with a runtime error
    print("--- Example 2: C++ Runtime Error ---")
    cpp_code = """
#include <iostream>
#include <vector>
int main() {
    std::vector<int> v;
    std::cout << v.at(10); // This will throw an exception
    return 0;
}
"""
    result = execute_code(language='c++', code=cpp_code, stdin='', time_limit_s=5, memory_limit_mb=128)
    print(json.dumps(result, indent=2))
    print("-" * 20)
    
    # Example 3: C code with Time Limit Exceeded
    print("--- Example 3: C Time Limit Exceeded ---")
    c_code_tle = """
#include <stdio.h>
int main() {
    while(1); // Infinite loop
    return 0;
}
"""
    result = execute_code(language='c', code=c_code_tle, stdin='', time_limit_s=2, memory_limit_mb=128)
    print(json.dumps(result, indent=2))
    print("-" * 20)

    # Example 4: C++ code with Memory Limit Exceeded
    print("--- Example 4: C++ Memory Limit Exceeded ---")
    cpp_code_mle = """
#include <iostream>
#include <vector>
int main() {
    // Allocate a large amount of memory
    std::vector<int> large_vector(50 * 1024 * 1024); 
    std::cout << "Allocated memory" << std::endl;
    return 0;
}
"""
    result = execute_code(language='c++', code=cpp_code_mle, stdin='', time_limit_s=5, memory_limit_mb=128)
    print(json.dumps(result, indent=2))
    print("-" * 20)

import subprocess
import tempfile
import os
import re
import uuid
from io import BytesIO

def execute_code(language='python', 
                 code='print("this is test code\\nsubmit ur own code, this is the default code")', 
                 stdin='', 
                 time_limit_s=2, 
                 memory_limit_mb=1024):
    """
    Executes user-provided code in a secure Docker sandbox using subprocess.

    Args:
        language (str): The programming language ('c', 'c++', 'python').
        code (str): The source code to execute.
        stdin (str): The standard input for the code.
        time_limit_s (int): The time limit in seconds.
        memory_limit_mb (int): The memory limit in megabytes.

    Returns:
        dict: A dictionary containing execution results.
    """
    # 1. Validate the language input
    language = language.lower()
    file_info = {
        'c': {'ext': 'c', 'compiler': 'gcc', 'executable': 'a.out'},
        'c++': {'ext': 'cpp', 'compiler': 'g++', 'executable': 'a.out'},
        'python': {'ext': 'py', 'compiler': None, 'executable': 'solution.py'}
    }
    if language not in file_info:
        return {
            "stdout": "", "stderr": "", "err": f"Language '{language}' is not supported.",
            "timetaken": 0, "memorytaken": 0, "success": False
        }

    # 2. Check for Docker and prepare the image
    image_name = "code-runner-image:latest"
    try:
        # Check if Docker is running
        subprocess.run(["docker", "info"], check=True, capture_output=True)
        # Check if image exists
        image_check = subprocess.run(["docker", "image", "inspect", image_name], check=False, capture_output=True)
        
        if image_check.returncode != 0:
            print(f"Image '{image_name}' not found. Building...")
            dockerfile = """
            FROM ubuntu:22.04
            ENV DEBIAN_FRONTEND=noninteractive
            RUN apt-get update && \
                apt-get install -y --no-install-recommends gcc g++ python3 python3-pip time coreutils && \
                apt-get clean && \
                rm -rf /var/lib/apt/lists/*
            WORKDIR /sandbox/temp
            """
            build_process = subprocess.run(
                ["docker", "build", "-t", image_name, "-"],
                input=dockerfile.encode('utf-8'),
                check=True,
                capture_output=True
            )
            print("Image built successfully.")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        error_message = e.stderr.decode('utf-8') if hasattr(e, 'stderr') and e.stderr else str(e)
        return {
            "stdout": "", "stderr": "", "err": f"Docker error: {error_message}",
            "timetaken": 0, "memorytaken": 0, "success": False
        }

    info = file_info[language]
    code_filename = f"solution.{info['ext']}"
    container_name = f"sandbox-container-{uuid.uuid4()}"

    # 3. Use a temporary directory on the host to store files
    with tempfile.TemporaryDirectory() as temp_dir:
        code_filepath = os.path.join(temp_dir, code_filename)
        with open(code_filepath, "w") as f:
            f.write(code)

        stdin_filepath = os.path.join(temp_dir, "input.txt")
        with open(stdin_filepath, "w") as f:
            f.write(stdin)

        container_id = None
        try:
            # 4. Start the container as root
            run_cmd = [
                "docker", "run",
                "--name", container_name,
                "--memory", f"{memory_limit_mb}m",
                "--memory-swap", f"{memory_limit_mb}m", # Prevent swapping
                "-d", # Detached mode
                image_name,
                "sleep", "3600" # Keep it running
            ]
            container_id = subprocess.check_output(run_cmd).decode('utf-8').strip()

            # 5. Copy files into the container
            subprocess.run(["docker", "cp", code_filepath, f"{container_id}:/sandbox/temp/{code_filename}"], check=True)
            subprocess.run(["docker", "cp", stdin_filepath, f"{container_id}:/sandbox/temp/input.txt"], check=True)

            # 6. Compilation Step (for C/C++)
            if info['compiler']:
                compile_cmd = f"{info['compiler']} -o {info['executable']} {code_filename}"
                compile_proc = subprocess.run(
                    ["docker", "exec", container_id, "/bin/sh", "-c", compile_cmd],
                    capture_output=True
                )
                if compile_proc.returncode != 0:
                    return {
                        "stdout": "", "stderr": compile_proc.stderr.decode('utf-8'), "err": "Compilation Error",
                        "timetaken": 0, "memorytaken": 0, "success": False
                    }

            # 7. Execution Step
            exec_path = info['executable']
            if language == 'python':
                run_cmd_main = f"python3 {exec_path}"
            else:
                run_cmd_main = f"./{exec_path}"
            
            run_cmd_container = f"timeout {time_limit_s}s /usr/bin/time -v {run_cmd_main} < input.txt"
            
            exec_proc = subprocess.run(
                ["docker", "exec", container_id, "/bin/sh", "-c", run_cmd_container],
                capture_output=True
            )
            
            exit_code = exec_proc.returncode
            stdout_output = exec_proc.stdout.decode('utf-8')
            stderr_output = exec_proc.stderr.decode('utf-8')

            # 8. Parse resource usage from stderr
            time_taken_match = re.search(r"User time \(seconds\): ([\d\.]+)", stderr_output)
            mem_taken_match = re.search(r"Maximum resident set size \(kbytes\): (\d+)", stderr_output)
            
            time_taken = float(time_taken_match.group(1)) if time_taken_match else 0.0
            mem_taken = float(mem_taken_match.group(1)) / 1024 if mem_taken_match else 0.0

            clean_stderr = re.sub(r"Command being timed:.*\n(.|\n)*", "", stderr_output, 1).strip()
            
            # 9. Determine the result
            if exit_code == 124:
                return {
                    "stdout": "", "stderr": "", "err": f"Time Limit Exceeded (> {time_limit_s}s)",
                    "timetaken": time_limit_s * 1000, "memorytaken": mem_taken, "success": False
                }
            elif exit_code == 137:
                 return {
                    "stdout": stdout_output, "stderr": clean_stderr, "err": f"Memory Limit Exceeded (> {memory_limit_mb} MB)",
                    "timetaken": time_taken, "memorytaken": mem_taken, "success": False
                }
            elif exit_code == 0:
                return {
                    "stdout": stdout_output, "stderr": clean_stderr, "err": "",
                    "timetaken": time_taken, "memorytaken": mem_taken, "success": True
                }
            else:
                return {
                    "stdout": stdout_output, "stderr": clean_stderr, "err": f"Runtime Error (Exit Code: {exit_code})",
                    "timetaken": time_taken, "memorytaken": mem_taken, "success": False
                }

        finally:
            # 10. Clean up the container
            if container_id:
                subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)


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

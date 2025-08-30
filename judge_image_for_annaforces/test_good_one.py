# from judge_image_for_annaforces.good_one import execute_code
from good_one import execute_code


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

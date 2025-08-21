from services.judge_service import grade_submission
from services.submission_service import add_submission_to_user, add_submission_to_problem


python_code = r'''
line = input()
# while 1: print()
a, b = map(int, line.split())
print(a + b)
'''
result = grade_submission(code=python_code, language='python', problem_id=1)

# Removed the if condition to always add the submission
add_submission_to_user(1, 1, result)
add_submission_to_problem(1, 1, result)
print(result)
import os
import unittest

class TestModelStructure(unittest.TestCase):

    def test_problems_model_structure(self):
        path = 'E:\\NEW\\backend-for-annaforces\\models\\problems'
        self.assertTrue(os.path.isdir(path), f"Directory not found: {path}")
        self.assertTrue(os.path.exists(os.path.join(path, '__init__.py')), f"__init__.py not found in {path}")
        # Assuming a main model file like problem.py exists
        self.assertTrue(os.path.exists(os.path.join(path, 'problem.py')), f"problem.py not found in {path}")

    def test_users_model_structure(self):
        path = 'E:\\NEW\\backend-for-annaforces\\models\\users'
        self.assertTrue(os.path.isdir(path), f"Directory not found: {path}")
        self.assertTrue(os.path.exists(os.path.join(path, '__init__.py')), f"__init__.py not found in {path}")
        self.assertTrue(os.path.exists(os.path.join(path, 'user.py')), f"user.py not found in {path}")

    def test_submissions_model_structure(self):
        path = 'E:\\NEW\\backend-for-annaforces\\models\\submissions'
        self.assertTrue(os.path.isdir(path), f"Directory not found: {path}")
        self.assertTrue(os.path.exists(os.path.join(path, '__init__.py')), f"__init__.py not found in {path}")
        self.assertTrue(os.path.exists(os.path.join(path, 'submission.py')), f"submission.py not found in {path}")

    def test_contests_model_structure(self):
        path = 'E:\\NEW\\backend-for-annaforces\\models\\contests'
        self.assertTrue(os.path.isdir(path), f"Directory not found: {path}")
        self.assertTrue(os.path.exists(os.path.join(path, '__init__.py')), f"__init__.py not found in {path}")
        self.assertTrue(os.path.exists(os.path.join(path, 'contest.py')), f"contest.py not found in {path}")

if __name__ == '__main__':
    unittest.main()

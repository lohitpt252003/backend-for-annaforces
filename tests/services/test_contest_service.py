import pytest
import sys
import os
import importlib.util

import importlib
contest_service_module = importlib.import_module("backend-for-annaforces.services.contest_service")

def test_contest_service_module_exists():
    assert True

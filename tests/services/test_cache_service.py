import pytest
import sys
import os
import importlib.util

import importlib
cache_service_module = importlib.import_module("backend-for-annaforces.services.cache_service")

def test_cache_service_module_exists():
    assert True

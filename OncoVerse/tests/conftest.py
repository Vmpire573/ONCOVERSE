"""Use an isolated throwaway SQLite database for the automated suite."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
_test_directory = tempfile.TemporaryDirectory(prefix="oncoverse-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_test_directory.name) / 'tests.db'}"

import os

# Must be set before any module reads Settings (which is @lru_cache'd on
# first access), so this has to happen at import time, before test modules
# import from app.*.
os.environ.setdefault("FORGE_MASTER_KEY", "test-only-master-key-do-not-use-in-prod")
os.environ.setdefault("FORGE_DATA_DIR", "/tmp/forge-test-data")

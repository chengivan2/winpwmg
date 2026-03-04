import hashlib
import re
from datetime import datetime, timedelta

def hash_password(password):
    """Simple SHA-256 hashing for the master password."""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_master_password(password):
    """
    Must be 8 characters or more and contain letters and numbers.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    return True, ""

def is_locked_out(lockout_time_str):
    if not lockout_time_str:
        return False
    lockout_until = datetime.fromisoformat(lockout_time_str)
    return datetime.now() < lockout_until

def get_lockout_remaining(lockout_time_str):
    if not lockout_time_str:
        return 0
    lockout_until = datetime.fromisoformat(lockout_time_str)
    remaining = lockout_until - datetime.now()
    return max(0, int(remaining.total_seconds() / 60))

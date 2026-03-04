from datetime import datetime, timedelta
import auth
import database
import os

def test_validation():
    print("Testing password validation...")
    tests = [
        ("pass", False),
        ("password123", True),
        ("OnlyLetters", False),
        ("12345678", False),
        ("Valid123", True),
    ]
    for pwd, expected in tests:
        valid, _ = auth.validate_master_password(pwd)
        assert valid == expected, f"Failed for {pwd}"
    print("Validation tests passed.")

def test_lockout():
    print("Testing lockout logic...")
    # Mock lockout string
    future = (datetime.now() + timedelta(minutes=5)).isoformat()
    past = (datetime.now() - timedelta(minutes=5)).isoformat()
    
    assert auth.is_locked_out(future) == True
    assert auth.is_locked_out(past) == False
    assert auth.is_locked_out(None) == False
    
    rem = auth.get_lockout_remaining(future)
    assert 4 <= rem <= 5, f"Expected ~5 min, got {rem}"
    print("Lockout logic tests passed.")

def run_tests():
    test_validation()
    test_lockout()

if __name__ == "__main__":
    run_tests()

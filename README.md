# CLI Password Manager - Developer Documentation

A secure, CLI-based password manager built with Python and SQLite 3.

## Project Structure

- `main.py`: Entry point. Manages CLI loops, state transitions, and user interaction.
- `database.py`: Data access layer. Handles all SQLite transactions and schema management.
- `auth.py`: Security layer. Contains hashing logic, validation rules, and lockout state checkers.
- `utils.py`: UI utility layer for pretty-printing and terminal control.
- `verify_logic.py`: Unit tests for critical authentication and lockout logic.

## Security Implementation

### Authentication
- Passwords are hashed using SHA-256 (via `auth.py`). 
- Master password must be at least 8 characters and contain both letters and numbers.

### Lockout Policies
1. **Login Lockout**: 4 attempts allowed. If exceeded, the user is locked out for 4 hours.
2. **Sensitive Action Lockout**: 5 attempts allowed during View/Update/Delete. If exceeded, that specific record is locked for 2 hours.

## Database Schema

The application uses two primary tables in `pwmg.db`:

### `users`
Tracks the master password and primary login lockout state.
- `master_password_hash`: SHA-256 hash.
- `login_lockout_until`: ISO format timestamp.

### `vault`
Stores the credentials.
- `url`: Full URL identifier.
- `password`: Stored as plain text (standard requirement for this task, can be extended with AES).
- `sensitive_lockout_until`: Tracks lockout for that specific credential.

## Development Setup

1. **Python Version**: Recommended Python 3.x.
2. **Running**: Use the `py` launcher.
   ```bash
   py main.py
   ```
3. **Testing**: Run the logic verification script.
   ```bash
   py verify_logic.py
   ```

## Design Decisions
- **Line-Bounded Boxes**: Implemented in `utils.py` to provide a premium feel to the CLI output.
- **ISO Timestamps**: Used for lockout tracking to simplify time delta calculations across sessions.

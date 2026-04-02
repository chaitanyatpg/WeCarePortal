# Test Scripts

This directory contains utility scripts for testing and debugging the MyCarePortal application.

## Scripts Overview

### Authentication & Database Testing
- **`test_authentication.py`** - Test user authentication and role management
- **`test_database_connection.py`** - Test Django setup and database connectivity
- **`debug_user_authentication.py`** - Debug authentication issues with external database

### AWS S3 Testing
- **`test_s3_connection.py`** - Test S3 configuration and media file handling

### Utility Scripts
- **`generate_password_hash.py`** - Generate Django-compatible password hashes
- **`check_and_reset_users.py`** - Check existing users and reset passwords

## Usage

### Prerequisites
1. Ensure virtual environment is activated:
   ```bash
   source venv38/bin/activate
   ```

2. Set required environment variables (or use .env file):
   ```bash
   export SECRET_KEY='pye6yse*@_#*@hhjr(lajgmzfa)zkb0qhlzlml^8-j7+)84alp'
   export DATABASE_URL='postgresql://postgres:password@host:port/database'
   export AWS_ACCESS_KEY_ID='your_key_here'
   export AWS_SECRET_ACCESS_KEY='your_secret_here'
   ```

### Running Tests

#### Basic Database Connection Test
```bash
./venv38/bin/python tests/test_database_connection.py
```

#### Authentication Test
```bash
./venv38/bin/python tests/test_authentication.py
```

#### S3 Configuration Test
```bash
./venv38/bin/python tests/test_s3_connection.py
```

#### Debug Authentication Issues
```bash
export DATABASE_URL='your_external_database_url'
./venv38/bin/python tests/debug_user_authentication.py
```

#### Generate Password Hash
```bash
./venv38/bin/python tests/generate_password_hash.py
```

## Notes

- All scripts use the Railway production database configuration
- Scripts are designed for debugging and testing purposes only
- Some scripts modify database data - use with caution in production
- Default test user: `kumarmanu@yahoo.com` with password `WeCare@123`

## Environment Variables

Required environment variables:
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `AWS_ACCESS_KEY_ID` - AWS access key for S3
- `AWS_SECRET_ACCESS_KEY` - AWS secret key for S3

Optional:
- `DEBUG` - Django debug mode (default: True for tests)
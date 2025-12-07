
# Django Blog Authentication System Documentation

## Overview
This authentication system provides complete user management functionality for the Django Blog platform, including registration, login, logout, and profile management.

## Features
1. **User Registration**
   - Email verification (uniqueness)
   - Password strength validation
   - Automatic profile creation
   - Terms of service agreement

2. **Login System**
   - Login with username or email
   - Remember me functionality
   - Password reset capability
   - Session management

3. **Profile Management**
   - View and edit profile information
   - Upload profile picture
   - Change password
   - View user activity (posts & comments)

4. **Security Features**
   - CSRF protection
   - Password hashing (Argon2/PBKDF2)
   - Secure session handling
   - Password reset via email

## Installation & Setup

### Prerequisites
```bash
pip install django pillow django-taggit
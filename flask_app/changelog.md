# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-05-29

### Added
- Initial project structure for Flask application.
- Basic Flask SPA setup with a single entry point (`index.html`) and static file serving.
- Collapsible sidebar with HTML, CSS, and JavaScript.
- Two sample Flask Blueprints (`sample_module1`, `sample_module2`) with basic routes and templates.
- User authentication system using Flask-Login:
    - User registration with password hashing.
    - User login and logout functionality.
    - Protected routes using `@login_required`.
    - In-memory user store for demonstration.
    - Login and registration forms using Flask-WTF and Flask-Bootstrap.
- Role-based authorization:
    - User model extended with a `role` attribute ('user', 'admin').
    - `@admin_required` decorator to restrict access to admin users.
    - Sample admin-only section (`sample_module2`).
    - Dynamic display of navigation and user information based on role.
    - Automatic creation of a default 'admin' user for testing.

### Fixed
- Resolved `jinja2.exceptions.UndefinedError: 'login_form' is undefined` on the `/login` page by ensuring consistent variable naming for the login form object between the `login` route in `app/auth/routes.py` and the `auth/login.html` template (now consistently uses `login_form`).

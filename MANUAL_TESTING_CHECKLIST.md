# Manual Testing Checklist

This checklist covers key manual tests for authentication, authorization, and user management features.

## 1. Admin User Functionality (`admin@example.com`)

*   **[ ] Setup**:
    *   Ensure the application is running.
    *   Run the `flask init-db` command to create/reset the database and ensure `admin@example.com` (password: `password`) and roles ("admin", "editor", "viewer") exist.
*   **[ ] Login**:
    *   Navigate to the login page (`/login`).
    *   Log in with `admin@example.com` and password `password`.
    *   **Expected**: Successful login, redirected to homepage.
*   **[ ] Admin Panel Visibility**:
    *   Check the side panel.
    *   **Expected**: "Admin Tools" section with "User Management" and "Add New User" links is visible.
*   **[ ] Access User Management**:
    *   Click "User Management" link.
    *   **Expected**: User Management page (`/admin/users`) loads, displaying a table with at least the `admin@example.com` user.
*   **[ ] Add New User (Editor)**:
    *   From User Management, click "Add New User" (or navigate to `/admin/add_user`).
    *   Enter email: `editor@example.com`, password: `password`.
    *   Select "editor" role from the multi-select.
    *   Ensure "Active" is checked.
    *   Click "Create User".
    *   **Expected**: Success message flashed. `editor@example.com` appears in the User Management list with the "editor" role.
*   **[ ] Edit User Roles (Editor)**:
    *   In User Management, find `editor@example.com`.
    *   Click "Edit Roles".
    *   Add the "viewer" role (Ctrl/Cmd + click to select multiple).
    *   Click "Update Roles".
    *   **Expected**: Success message flashed. `editor@example.com` now shows both "editor" and "viewer" roles in the User Management list.
*   **[ ] Initiate Password Reset (Editor)**:
    *   In User Management, find `editor@example.com`.
    *   Click "Reset Password" button.
    *   Confirm the action in the browser dialog.
    *   **Expected**: Success message flashed. Check the application console for an email-like output containing a password reset link for `editor@example.com`.
*   **[ ] Attempt to Delete Self**:
    *   In User Management, find `admin@example.com`.
    *   Observe the "Delete" button.
    *   **Expected**: The "Delete" button for `admin@example.com` should be disabled and have a tooltip like "You cannot delete yourself." Attempting to manually craft a POST request should also fail or be explicitly disallowed in the route.
*   **[ ] Delete User (Editor)**:
    *   In User Management, find `editor@example.com`.
    *   Click "Delete" button.
    *   Confirm the action in the browser dialog.
    *   **Expected**: Success message flashed. `editor@example.com` is removed from the User Management list.
*   **[ ] Logout**:
    *   Click "Logout" link in the side panel.
    *   **Expected**: Successful logout, redirected to homepage (or login page). Side panel no longer shows admin-specific links or user email.

## 2. Non-Admin User Functionality (e.g., `viewer@example.com`)

*   **[ ] Setup (Admin Task)**:
    *   Log in as `admin@example.com`.
    *   Navigate to "Add New User".
    *   Create user `viewer@example.com`, password: `password`, role: "viewer", active: true.
    *   Log out.
*   **[ ] Login (Viewer)**:
    *   Navigate to the login page.
    *   Log in with `viewer@example.com` and password `password`.
    *   **Expected**: Successful login, redirected to homepage.
*   **[ ] Admin Panel Non-Visibility**:
    *   Check the side panel.
    *   **Expected**: "Admin Tools" section is NOT visible.
*   **[ ] Attempt Direct Admin URL Access**:
    *   Manually navigate to `/admin/users`.
    *   **Expected**: Access denied. This might be a Flask-Security-Too default "Unauthorized" page, a redirect to login, or a custom error page (e.g., 403). The key is no access to admin functionality.
    *   Manually navigate to `/admin/add_user`.
    *   **Expected**: Access denied, similar to above.
*   **[ ] Logout**:
    *   Click "Logout" link in the side panel.
    *   **Expected**: Successful logout.

## 3. Public/Anonymous User Functionality

*   **[ ] Initial State**:
    *   Ensure you are logged out. If logged in, click "Logout".
    *   Access the site's homepage.
*   **[ ] Admin Panel Non-Visibility**:
    *   Check the side panel.
    *   **Expected**: "Admin Tools" section is NOT visible. Login link should be visible.
*   **[ ] Attempt Direct Admin URL Access**:
    *   Manually navigate to `/admin/users`.
    *   **Expected**: Access denied. Usually redirected to the login page (`/login?next=/admin/users`).
    *   Manually navigate to `/admin/add_user`.
    *   **Expected**: Access denied, redirected to login.
*   **[ ] Access Login Page**:
    *   Click the "Login" link in the side panel (or navigate to `/login`).
    *   **Expected**: Login page loads correctly.

## 4. General UI and Responsiveness

*   **[ ] Responsiveness (Conceptual)**:
    *   Resize the browser window to simulate different screen sizes (desktop, tablet, mobile).
    *   **Expected**:
        *   The side panel should be hidden by default (as per current design) and toggleable with the button.
        *   Content in the main area should reflow and be readable.
        *   Bootstrap's grid system and components should adapt (e.g., tables might become scrollable horizontally if too wide, buttons stack, etc.).
        *   No major layout breaks or overlapping content.
*   **[ ] Flashed Messages**:
    *   Perform actions that trigger flashed messages (e.g., successful login, adding a user, errors on forms, successful logout).
    *   **Expected**: Messages appear correctly styled (e.g., Bootstrap alerts for success, danger, warning) and are dismissible if they have a close button.
*   **[ ] Form Usability**:
    *   Interact with all forms (Login, Add User, Edit Roles).
    *   Test form validation by submitting empty required fields or invalid data (e.g., invalid email format).
    *   **Expected**:
        *   Validation messages appear next to the respective fields or in a summary.
        *   Forms submit correctly with valid data.
        *   Fields are clearly labeled.
        *   Multi-select for roles is usable (Ctrl/Cmd + click).
*   **[ ] Navigation**:
    *   Test all navigation links in the side panel (Home, Products, Services, Contact, Admin links if admin, Login/Logout).
    *   Test "Cancel" buttons on forms (e.g., Edit Roles).
    *   **Expected**: All links navigate to the correct pages.

---
This checklist should be executed after each major change to ensure core functionality remains intact.

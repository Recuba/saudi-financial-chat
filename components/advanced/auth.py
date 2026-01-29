"""
Authentication Component.

Provides authentication using streamlit-authenticator.
Falls back to demo mode when not configured or when the package is not installed.
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable, List, Tuple
from functools import wraps
import hashlib
from datetime import datetime, timedelta

# Check if streamlit-authenticator is available
try:
    import streamlit_authenticator as stauth
    from streamlit_authenticator.utilities.hasher import Hasher
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    stauth = None
    Hasher = None


# Default authentication configuration structure
DEFAULT_AUTH_CONFIG: Dict[str, Any] = {
    "cookie": {
        "name": "saudi_financial_chat_auth",
        "key": "some_random_key_change_in_production",
        "expiry_days": 30,
    },
    "credentials": {
        "usernames": {
            "demo_user": {
                "name": "Demo User",
                "password": "",  # Will be hashed
                "email": "demo@example.com",
                "role": "user",
            }
        }
    },
    "pre-authorized": {
        "emails": []
    }
}

# Session state keys
AUTH_STATUS_KEY = "authentication_status"
AUTH_USERNAME_KEY = "username"
AUTH_NAME_KEY = "name"
AUTH_ROLE_KEY = "user_role"


def get_auth_config() -> Dict[str, Any]:
    """
    Get authentication configuration.

    This should be customized to load from environment variables or config file.

    Returns:
        Authentication configuration dictionary
    """
    # Check for config in session state (could be loaded from file/env)
    if "auth_config" in st.session_state:
        return st.session_state["auth_config"]

    # Return default config for demo purposes
    return DEFAULT_AUTH_CONFIG


def set_auth_config(config: Dict[str, Any]) -> None:
    """
    Set authentication configuration.

    Args:
        config: Authentication configuration dictionary
    """
    st.session_state["auth_config"] = config


def hash_password(password: str) -> str:
    """
    Hash a password for storage.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    if AUTH_AVAILABLE and Hasher is not None:
        return Hasher([password]).generate()[0]
    else:
        # Fallback hash (not recommended for production)
        return hashlib.sha256(password.encode()).hexdigest()


def _is_demo_mode() -> bool:
    """Check if running in demo mode (no real auth configured)."""
    config = get_auth_config()

    # Demo mode if no credentials or only demo user
    credentials = config.get("credentials", {}).get("usernames", {})
    if not credentials:
        return True

    if len(credentials) == 1 and "demo_user" in credentials:
        return True

    return False


def _demo_login(username: str, password: str) -> Tuple[bool, str]:
    """
    Demo login for testing purposes.

    Args:
        username: Username
        password: Password (ignored in demo mode)

    Returns:
        Tuple of (success, message)
    """
    if username.strip():
        # Accept any non-empty username in demo mode
        st.session_state[AUTH_STATUS_KEY] = True
        st.session_state[AUTH_USERNAME_KEY] = username
        st.session_state[AUTH_NAME_KEY] = username.title()
        st.session_state[AUTH_ROLE_KEY] = "demo"
        return True, "Demo login successful"

    return False, "Please enter a username"


def check_authentication() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if user is authenticated.

    Returns:
        Tuple of (is_authenticated, username, name)
    """
    is_authenticated = st.session_state.get(AUTH_STATUS_KEY, False)
    username = st.session_state.get(AUTH_USERNAME_KEY, None)
    name = st.session_state.get(AUTH_NAME_KEY, None)

    return is_authenticated, username, name


def get_current_user() -> Dict[str, Any]:
    """
    Get current authenticated user information.

    Returns:
        Dictionary with user information or None if not authenticated
    """
    is_auth, username, name = check_authentication()

    if not is_auth:
        return None

    return {
        "username": username,
        "name": name,
        "role": st.session_state.get(AUTH_ROLE_KEY, "user"),
        "authenticated_at": st.session_state.get("authenticated_at", None),
    }


def render_login_form(
    key: str = "login_form",
    title: str = "Login",
    fields: Optional[Dict[str, str]] = None,
    show_register: bool = False,
    show_forgot_password: bool = False,
) -> Tuple[bool, Optional[str]]:
    """
    Render the login form.

    Args:
        key: Unique key for the form
        title: Form title
        fields: Custom field labels {"username": "...", "password": "..."}
        show_register: Show registration link
        show_forgot_password: Show forgot password link

    Returns:
        Tuple of (login_successful, username)
    """
    # Check if already authenticated
    is_auth, username, _ = check_authentication()
    if is_auth:
        return True, username

    # Default field labels
    if fields is None:
        fields = {
            "username": "Username",
            "password": "Password",
            "login": "Login",
        }

    # Demo mode notice
    if _is_demo_mode():
        st.info("Demo mode: Enter any username to continue. No password required.")

    st.subheader(title)

    # Use streamlit-authenticator if available and configured
    if AUTH_AVAILABLE and not _is_demo_mode():
        config = get_auth_config()

        try:
            authenticator = stauth.Authenticate(
                config["credentials"],
                config["cookie"]["name"],
                config["cookie"]["key"],
                config["cookie"]["expiry_days"],
                config.get("pre-authorized", {})
            )

            # Render login widget
            name, authentication_status, username = authenticator.login(
                location="main",
                fields=fields
            )

            if authentication_status:
                st.session_state[AUTH_STATUS_KEY] = True
                st.session_state[AUTH_USERNAME_KEY] = username
                st.session_state[AUTH_NAME_KEY] = name
                st.session_state["authenticated_at"] = datetime.now().isoformat()

                # Get role from config
                user_config = config["credentials"]["usernames"].get(username, {})
                st.session_state[AUTH_ROLE_KEY] = user_config.get("role", "user")

                return True, username

            elif authentication_status is False:
                st.error("Username/password is incorrect")

            return False, None

        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.info("Falling back to demo mode.")

    # Fallback / Demo login form
    with st.form(key=f"{key}_form"):
        input_username = st.text_input(
            fields.get("username", "Username"),
            key=f"{key}_username"
        )

        if not _is_demo_mode():
            input_password = st.text_input(
                fields.get("password", "Password"),
                type="password",
                key=f"{key}_password"
            )
        else:
            input_password = ""

        submit = st.form_submit_button(fields.get("login", "Login"))

        if submit:
            if _is_demo_mode():
                success, message = _demo_login(input_username, input_password)
                if success:
                    st.session_state["authenticated_at"] = datetime.now().isoformat()
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                # Basic auth check against config
                config = get_auth_config()
                credentials = config.get("credentials", {}).get("usernames", {})

                if input_username in credentials:
                    stored_hash = credentials[input_username].get("password", "")
                    # Compare hashed passwords
                    input_hash = hash_password(input_password)

                    if stored_hash == input_hash or stored_hash == input_password:
                        user_data = credentials[input_username]
                        st.session_state[AUTH_STATUS_KEY] = True
                        st.session_state[AUTH_USERNAME_KEY] = input_username
                        st.session_state[AUTH_NAME_KEY] = user_data.get("name", input_username)
                        st.session_state[AUTH_ROLE_KEY] = user_data.get("role", "user")
                        st.session_state["authenticated_at"] = datetime.now().isoformat()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password")
                else:
                    st.error("User not found")

    # Additional links
    col1, col2 = st.columns(2)

    if show_register:
        with col1:
            st.markdown("[Register](#)", help="Registration not available in this version")

    if show_forgot_password:
        with col2:
            st.markdown("[Forgot Password?](#)", help="Password reset not available in this version")

    return False, None


def render_logout_button(
    key: str = "logout_button",
    label: str = "Logout",
    location: str = "sidebar"
) -> bool:
    """
    Render a logout button.

    Args:
        key: Unique key for the button
        label: Button label
        location: Where to render ('sidebar' or 'main')

    Returns:
        True if logout was clicked
    """
    is_auth, username, name = check_authentication()

    if not is_auth:
        return False

    container = st.sidebar if location == "sidebar" else st

    with container:
        # Show current user info
        st.write(f"Logged in as: **{name or username}**")

        if st.button(label, key=key):
            # Clear session state
            st.session_state[AUTH_STATUS_KEY] = False
            st.session_state[AUTH_USERNAME_KEY] = None
            st.session_state[AUTH_NAME_KEY] = None
            st.session_state[AUTH_ROLE_KEY] = None
            st.session_state.pop("authenticated_at", None)

            # Clear authenticator cookie if available
            if AUTH_AVAILABLE and not _is_demo_mode():
                config = get_auth_config()
                try:
                    authenticator = stauth.Authenticate(
                        config["credentials"],
                        config["cookie"]["name"],
                        config["cookie"]["key"],
                        config["cookie"]["expiry_days"],
                        config.get("pre-authorized", {})
                    )
                    authenticator.logout(location="unrendered")
                except Exception:
                    pass

            st.success("Logged out successfully!")
            st.rerun()
            return True

    return False


def require_auth(
    roles: Optional[List[str]] = None,
    redirect_message: str = "Please log in to access this page.",
    show_login: bool = True
) -> Callable:
    """
    Decorator to require authentication for a function.

    Args:
        roles: Optional list of required roles
        redirect_message: Message to show if not authenticated
        show_login: Whether to show login form if not authenticated

    Returns:
        Decorator function

    Usage:
        @require_auth(roles=["admin"])
        def admin_page():
            st.write("Admin content")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_auth, username, name = check_authentication()

            if not is_auth:
                st.warning(redirect_message)

                if show_login:
                    success, _ = render_login_form()
                    if not success:
                        st.stop()
                else:
                    st.stop()

            # Check roles if specified
            if roles:
                user_role = st.session_state.get(AUTH_ROLE_KEY, "user")

                # Demo role has access to everything
                if user_role != "demo" and user_role not in roles:
                    st.error(f"Access denied. Required role: {', '.join(roles)}")
                    st.stop()

            return func(*args, **kwargs)

        return wrapper

    return decorator


def render_user_info(
    key: str = "user_info",
    show_role: bool = True,
    show_login_time: bool = False,
    location: str = "sidebar"
) -> None:
    """
    Render current user information.

    Args:
        key: Unique key for the component
        show_role: Show user role
        show_login_time: Show when user logged in
        location: Where to render ('sidebar' or 'main')
    """
    user = get_current_user()

    if not user:
        return

    container = st.sidebar if location == "sidebar" else st

    with container:
        with st.container():
            st.markdown(f"**{user.get('name', user.get('username'))}**")

            if show_role:
                role = user.get("role", "user")
                role_badge = {
                    "admin": "Administrator",
                    "user": "User",
                    "demo": "Demo Mode",
                }.get(role, role.title())
                st.caption(f"Role: {role_badge}")

            if show_login_time and user.get("authenticated_at"):
                st.caption(f"Since: {user['authenticated_at'][:16]}")


def create_user(
    username: str,
    password: str,
    name: str,
    email: str = "",
    role: str = "user"
) -> bool:
    """
    Create a new user in the configuration.

    Args:
        username: Username (must be unique)
        password: Plain text password (will be hashed)
        name: Display name
        email: Email address
        role: User role

    Returns:
        True if user created successfully
    """
    config = get_auth_config()
    credentials = config.get("credentials", {}).get("usernames", {})

    if username in credentials:
        st.error(f"Username '{username}' already exists")
        return False

    # Hash password
    hashed_password = hash_password(password)

    # Add user to config
    credentials[username] = {
        "name": name,
        "password": hashed_password,
        "email": email,
        "role": role,
    }

    config["credentials"]["usernames"] = credentials
    set_auth_config(config)

    return True


def render_auth_status_badge(location: str = "sidebar") -> None:
    """
    Render a small authentication status badge.

    Args:
        location: Where to render ('sidebar' or 'main')
    """
    is_auth, username, name = check_authentication()

    container = st.sidebar if location == "sidebar" else st

    with container:
        if is_auth:
            role = st.session_state.get(AUTH_ROLE_KEY, "user")
            if role == "demo":
                st.success(f"Demo: {name or username}", icon="")
            else:
                st.success(f"Logged in: {name or username}", icon="")
        else:
            st.info("Not logged in", icon="")

"""
Authentication module for admin access
"""

import streamlit as st
import hashlib
import os

# Admin credentials (sử dụng environment variables cho production)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = hashlib.sha256(
    os.getenv("ADMIN_PASSWORD", "phishing2024").encode()
).hexdigest()

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == ADMIN_USERNAME
            and hashlib.sha256(st.session_state["password"].encode()).hexdigest()
            == ADMIN_PASSWORD_HASH
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password", on_change=password_entered)
        st.error("😕 Username hoặc password không đúng")
        return False
    else:
        # Password correct.
        return True

def logout():
    """Clear authentication state"""
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    st.rerun()

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get("password_correct", False)
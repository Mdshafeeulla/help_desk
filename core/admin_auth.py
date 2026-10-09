"""Shared local admin account setup and login for administrative views."""

import hashlib
import hmac
import json
from pathlib import Path
import secrets


_ACCOUNT_FILE = Path("data/admin_account.json")
_PBKDF2_ITERATIONS = 600_000


def _read_account() -> dict | None:
    try:
        account = json.loads(_ACCOUNT_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as error:
        import streamlit as st

        st.error(f"Unable to read the saved admin account: {error}")
        st.stop()

    if not isinstance(account, dict) or not all(
        isinstance(account.get(key), str)
        for key in ("username", "salt", "password_hash")
    ):
        import streamlit as st

        st.error("The saved admin account file is invalid.")
        st.stop()
    return account


def _save_account(username: str, password: str) -> None:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    _ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
    account = json.dumps({
            "username": username,
            "salt": salt.hex(),
            "password_hash": password_hash.hex(),
            "iterations": _PBKDF2_ITERATIONS,
        })
    with _ACCOUNT_FILE.open("x", encoding="utf-8") as account_file:
        account_file.write(account)


def require_admin_access() -> None:
    """Require the locally configured admin account before showing the console."""
    import streamlit as st

    account = _read_account()

    if st.session_state.get("admin_authenticated"):
        with st.sidebar:
            st.caption(f"Signed in as {account['username']}")
            if st.button("Log out", key="admin_logout"):
                st.session_state.pop("admin_authenticated", None)
                st.rerun()
        return

    if account is None:
        st.title("Set up the Admin Account")
        st.info(
            "Create the admin account once. Its password is stored locally as a "
            "salted hash and is never written in plain text."
        )
        with st.form("admin_account_setup"):
            username = st.text_input("Admin username", value="MSU")
            password = st.text_input("Create admin password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create admin account", type="primary")

        if submitted:
            if not username.strip():
                st.error("Enter a username.")
            elif len(password) < 12:
                st.error("Choose a password with at least 12 characters.")
            elif not hmac.compare_digest(password, confirm_password):
                st.error("The passwords do not match.")
            else:
                try:
                    _save_account(username.strip(), password)
                except FileExistsError:
                    st.info("The admin account was already created. Please sign in.")
                    st.rerun()
                else:
                    st.success(
                        "Admin account created. Sign in with your new credentials."
                    )
                    st.rerun()
        st.stop()

    st.title("Admin and Monitoring Login")
    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary")

    if submitted:
        salt = bytes.fromhex(account["salt"])
        iterations = account.get("iterations", _PBKDF2_ITERATIONS)
        supplied_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
        )
        valid_user = hmac.compare_digest(username, account["username"])
        valid_password = hmac.compare_digest(
            supplied_hash.hex(), account["password_hash"]
        )
        if valid_user and valid_password:
            st.session_state["admin_authenticated"] = True
            st.rerun()
        st.error("Invalid username or password.")
    st.stop()

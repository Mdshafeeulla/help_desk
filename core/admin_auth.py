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


def _render_auth_header(st, title: str, description: str) -> None:
    st.markdown(
        """
        <style>
            .auth-heading {
                text-align: center;
                padding: 2.5rem 0 1rem;
            }
            .auth-kicker {
                color: #a5b4fc;
                font-size: 0.78rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.8rem;
            }
            .auth-heading h1 {
                color: #f1f5f9;
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                margin: 0 0 0.5rem;
            }
            .auth-heading p {
                color: #94a3b8;
                font-size: 0.95rem;
                line-height: 1.5;
                margin: 0 auto;
                max-width: 28rem;
            }
            @media (max-width: 640px) {
                .auth-heading { padding-top: 1.5rem; }
                .auth-heading h1 { font-size: 1.65rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="auth-heading">
            <div class="auth-kicker">🔒 MSU Corp Admin Portal</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 18% 12%, rgba(242, 167, 195, 0.12), transparent 28rem),
                    radial-gradient(circle at 82% 88%, rgba(217, 130, 164, 0.07), transparent 24rem),
                    #09090c;
            }
            .auth-visual {
                height: 100%;
                min-height: 31rem;
                overflow: hidden;
                border: 1px solid rgba(255, 214, 229, 0.12);
                border-radius: 20px;
                background: linear-gradient(145deg, rgba(38, 29, 35, 0.96), rgba(17, 15, 19, 0.98));
                box-shadow: 0 22px 55px rgba(0, 0, 0, 0.38);
            }
            .auth-visual [data-testid="stImage"] {
                width: 100%;
                height: 100%;
            }
            .auth-visual [data-testid="stImage"] img {
                width: 100%;
                height: 31rem;
                object-fit: cover;
            }
            .auth-heading {
                padding-top: 1.5rem !important;
            }
            [data-testid="stForm"] {
                border: 1px solid rgba(255, 214, 229, 0.12) !important;
                border-radius: 18px;
                background: rgba(17, 15, 19, 0.94);
                padding: 1.5rem;
                box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
            }
            [data-testid="stFormSubmitButton"] button {
                background: linear-gradient(110deg, #f2a7c3, #d982a4) !important;
                border: 1px solid rgba(255, 214, 229, 0.42) !important;
                color: #24141b !important;
                border-radius: 11px;
                font-weight: 700;
            }
            @media (max-width: 720px) {
                .auth-visual { display: none; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    visual_path = Path(__file__).resolve().parent.parent / "assets" / "admin_security.svg"
    visual, form = st.columns([1.15, 0.85], gap="large")

    if account is None:
        with visual:
            st.markdown('<div class="auth-visual">', unsafe_allow_html=True)
            if visual_path.exists():
                st.image(str(visual_path), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with form:
            _render_auth_header(
                st,
                "Create your admin account",
                "Set up secure access to manage documents and monitor the knowledge base.",
            )
            with st.container(border=True):
                with st.form("admin_account_setup"):
                    username = st.text_input(
                        "Admin username",
                        value="MSU",
                        help="This username will be used whenever you sign in.",
                    )
                    password = st.text_input(
                        "Create password",
                        type="password",
                        help="Use at least 12 characters.",
                    )
                    confirm_password = st.text_input(
                        "Confirm password",
                        type="password",
                    )
                    submitted = st.form_submit_button(
                        "Create admin account",
                        type="primary",
                        use_container_width=True,
                    )
                st.caption("Your password is stored locally as a salted hash.")

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

    with visual:
        st.markdown('<div class="auth-visual">', unsafe_allow_html=True)
        if visual_path.exists():
            st.image(str(visual_path), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with form:
        _render_auth_header(
            st,
            "Welcome back",
            "Sign in to manage support documents and view system monitoring.",
        )
        with st.container(border=True):
            with st.form("admin_login"):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your admin username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button(
                    "Sign in to Admin Console",
                    type="primary",
                    use_container_width=True,
                )
            st.caption("Authorized administrators only")

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

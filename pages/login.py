import streamlit as st

st.set_page_config(page_title="Login", layout="centered", initial_sidebar_state="collapsed")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

USER_USERNAME = "user"
USER_PASSWORD = "user123"

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(8, 145, 178, 0.30), transparent 32%),
                radial-gradient(circle at bottom right, rgba(249, 115, 22, 0.22), transparent 28%),
                linear-gradient(135deg, #07111f 0%, #0b172a 52%, #10233b 100%);
            color: #e5eef8;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }

        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
            gap: 0.2rem;
        }

        .login-shell {
            max-width: 520px;
            margin: 4.5rem auto 0;
            padding: 0 0.6rem 2rem;
        }

        .login-card {
            padding: 2rem 2rem 1.4rem;
            border-radius: 28px;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.88) 0%, rgba(15, 23, 42, 0.72) 100%);
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 22px 60px rgba(2, 6, 23, 0.38);
            backdrop-filter: blur(14px);
        }

        .login-icon {
            width: 68px;
            height: 68px;
            margin: 0 auto 1rem;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(249, 115, 22, 0.24));
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }

        .card-label {
            color: #93c5fd;
            font-size: 0.86rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
            text-align: center;
        }

        .card-title {
            color: #f8fbff;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
            text-align: center;
        }

        .card-text {
            color: #bfd2e6;
            line-height: 1.65;
            text-align: center;
            margin-bottom: 1.4rem;
        }

        .creds-box {
            margin-top: 1.2rem;
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(148, 163, 184, 0.10);
            border: 1px solid rgba(148, 163, 184, 0.16);
            color: #dbeafe;
            font-size: 0.95rem;
            line-height: 1.7;
            text-align: center;
        }

        .creds-box strong {
            color: #ffffff;
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 22px;
            padding: 1.2rem 1.2rem 0.5rem;
        }

        div[data-testid="stTextInput"] label p {
            color: #d8e6f5;
            font-weight: 600;
        }

        div[data-baseweb="input"] {
            background: rgba(255, 255, 255, 0.10);
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.30);
        }

        div[data-baseweb="input"] input {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            caret-color: #ffffff !important;
            font-weight: 600;
        }

        div[data-baseweb="input"] input::placeholder {
            color: #cbd5e1 !important;
            -webkit-text-fill-color: #cbd5e1 !important;
            opacity: 1;
        }

        .stForm [data-testid="stFormSubmitButton"] button {
            width: auto;
            min-width: 150px;
            border: none;
            border-radius: 14px;
            padding: 0.78rem 1rem;
            background: #0ea5e9;
            color: white;
            font-weight: 700;
            font-size: 1rem;
            box-shadow: 0 12px 28px rgba(14, 165, 233, 0.30);
        }

        .stForm [data-testid="stFormSubmitButton"] button:hover {
            background: #0284c7;
        }

        button[title*="password"],
        button[title*="Password"] {
            width: 2.6rem !important;
            min-width: 2.6rem !important;
            height: 2.6rem !important;
            padding: 0 !important;
            border: none !important;
            border-radius: 999px !important;
            background: transparent !important;
            box-shadow: none !important;
        }

        button[title*="password"] svg,
        button[title*="Password"] svg {
            fill: #cbd5e1 !important;
        }

        [data-testid="InputInstructions"] {
            display: none !important;
        }

        @media (max-width: 760px) {
            .login-card {
                padding: 1.3rem;
                border-radius: 22px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="login-shell">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="login-card">
        <div class="login-icon">🔐</div>
        <div class="card-label">Welcome Back</div>
        <div class="card-title">Login</div>
        <div class="card-text">Enter your username and password to continue.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    login_clicked = st.form_submit_button("🔐 Login")

if login_clicked:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.role = "admin"
        st.success("Admin login successful")
        st.switch_page("app_ollama.py")
    elif username == USER_USERNAME and password == USER_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.role = "user"
        st.success("User login successful")
        st.switch_page("app_ollama.py")
    else:
        st.error("Invalid username or password")

st.markdown(
    """
    <div class="creds-box">
        Admin: <strong>admin</strong> / <strong>admin123</strong><br>
        User: <strong>user</strong> / <strong>user123</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

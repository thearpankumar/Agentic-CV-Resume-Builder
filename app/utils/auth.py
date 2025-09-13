import hashlib
import secrets
import streamlit as st

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

def show_password_dialog(title: str, is_new_user: bool = False) -> tuple[str, bool]:
    """Show password input dialog using form to prevent resets"""
    st.markdown(f"### {title}")
    
    if is_new_user:
        with st.form("password_form", clear_on_submit=True):
            password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Create Account")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                if password and confirm_password:
                    if password == confirm_password:
                        if len(password) >= 6:
                            return password, True
                        else:
                            st.error("Password must be at least 6 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in both password fields")
            
            if cancel:
                return "", False
    else:
        with st.form("login_form", clear_on_submit=True):
            password = st.text_input("Enter Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Login")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                if password:
                    return password, True
                else:
                    st.error("Please enter your password")
            
            if cancel:
                return "", False
    
    return "", None

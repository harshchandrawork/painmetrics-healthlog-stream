import hashlib

import streamlit as st


def authenticated_user_id() -> str:
    if not st.user.is_logged_in:
        raise RuntimeError("Sign in before saving health logs.")

    issuer = st.user.get("iss")
    subject = st.user.get("sub")
    if not issuer or not subject:
        raise RuntimeError("The identity provider did not return a stable user ID.")

    identity = f"{issuer}\0{subject}".encode("utf-8")
    return f"oidc:{hashlib.sha256(identity).hexdigest()}"

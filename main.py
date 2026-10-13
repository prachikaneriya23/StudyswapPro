import os
import re
import uuid
import streamlit as st
import database as db

st.set_page_config(page_title="Study Swap Pro", page_icon="📚", layout="wide")
db.init_db()

# Simple Regex Email Validator
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def is_valid_email(email):
    return re.match(EMAIL_REGEX, email) is not None

def human_uploader(name, email):
    return name if name else email

def note_card(note, show_delete=False):
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"### {note['title']}")
            meta_bits = []
            if note["subject"]:
                meta_bits.append(f"**Subject:** {note['subject']}")
            meta_bits.append(f"**Uploaded by:** {human_uploader(note['uploader_name'], note['uploader_email'])}")
            meta_bits.append(f"**Date:** {note['upload_date']}")
            st.caption(" · ".join(meta_bits))
            if note["description"]:
                st.write(note["description"])

            file_path = os.path.join(db.UPLOAD_DIR, note["stored_filename"])
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=f.read(),
                        file_name=note["original_filename"],
                        mime="application/pdf",
                        key=f"dl_{note['id']}",
                    )
            else:
                st.warning("File missing on server.")

        with col2:
            if show_delete:
                if st.button("🗑️ Delete", key=f"del_{note['id']}"):
                    ok = db.delete_note(note["id"], user_email)
                    if ok:
                        st.success("Note deleted.")
                        st.rerun()
                    else:
                        st.error("Could not delete this note.")

# ----------------------------------------------------------------------------
# Authentication Flow
# ----------------------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("📚 Study Swap Pro")
    st.subheader("Share and find study notes with students everywhere")
    
    tab_login, tab_register, tab_forgot = st.tabs(["Log In", "Sign Up", "Forgot Password"])

    # --- TAB 1: LOG IN ---
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email address *", placeholder="student@university.edu").strip().lower()
            password = st.text_input("Password *", type="password")
            submitted = st.form_submit_button("Log In", type="primary")

            if submitted:
                if not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                elif not password:
                    st.error("Please enter your password.")
                else:
                    user = db.verify_user(email, password)
                    if user:
                        st.session_state.user = {"email": user["email"], "name": user["name"]}
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

    # --- TAB 2: SIGN UP ---
    with tab_register:
        with st.form("signup_form"):
            new_email = st.text_input("Email address *", placeholder="student@university.edu").strip().lower()
            new_name = st.text_input("Full Name", placeholder="Alex Smith").strip()
            new_password = st.text_input("Password *", type="password")
            confirm_password = st.text_input("Confirm Password *", type="password")
            submitted = st.form_submit_button("Create Account", type="primary")

            if submitted:
                if not is_valid_email(new_email):
                    st.error("Please enter a valid email address.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success = db.create_user(new_email, new_name, new_password)
                    if success:
                        st.success("Account created successfully! Please log in.")
                    else:
                        st.error("An account with this email already exists.")

    # --- TAB 3: FORGOT PASSWORD ---
    with tab_forgot:
        st.write("Generate a reset key to create a new password.")
        
        with st.form("request_key_form"):
            reset_email = st.text_input("Enter your registered email").strip().lower()
            key_submitted = st.form_submit_button("Generate Reset Key")
            if key_submitted:
                if is_valid_email(reset_email):
                    key = db.generate_reset_key(reset_email)
                    if key:
                        st.info(f"Your Reset Key is: **{key}** (In production, send this via email)")
                    else:
                        st.error("Email not found.")
                else:
                    st.error("Please enter a valid email address.")

        with st.form("reset_pass_form"):
            email_for_reset = st.text_input("Email *").strip().lower()
            reset_key = st.text_input("Reset Key *").strip()
            updated_password = st.text_input("New Password *", type="password")
            reset_submitted = st.form_submit_button("Update Password", type="primary")

            if reset_submitted:
                if db.reset_password(email_for_reset, reset_key, updated_password):
                    st.success("Password updated successfully! You can now log in.")
                else:
                    st.error("Invalid email or reset key.")

    st.stop()

user_email = st.session_state.user["email"]
user_name = st.session_state.user["name"]

# ----------------------------------------------------------------------------
# Logged-in App Code
# ----------------------------------------------------------------------------

with st.sidebar:
    st.markdown(f"### 👋 {user_name or user_email}")
    st.caption(user_email)
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()
    st.divider()
    page = st.radio("Navigate", ["🔍 Search Notes", "⬆️ Upload Note", "📁 My Notes"])

st.title("📚 Study Swap Pro")

# ---------------------------- Search page -----------------------------------
if page == "🔍 Search Notes":
    st.header("Search notes")
    query = st.text_input("Search by title, subject, or keyword", placeholder="e.g. Thermodynamics, Data Structures...")

    if query:
        results = db.search_notes(query)
        st.write(f"**{len(results)}** result(s) found for \"{query}\"")
    else:
        results = db.get_all_notes()
        st.write(f"Showing all **{len(results)}** shared note(s)")

    if not results:
        st.info("No notes found. Be the first to upload one!")
    for note in results:
        note_card(note, show_delete=(note["uploader_email"] == user_email))

# ---------------------------- Upload page ------------------------------------
elif page == "⬆️ Upload Note":
    st.header("Upload a new note")
    with st.form("upload_form", clear_on_submit=True):
        title = st.text_input("Title *", placeholder="e.g. Unit 3 - Operating Systems Notes")
        subject = st.text_input("Subject", placeholder="e.g. Computer Science")
        description = st.text_area("Description (optional)", placeholder="Briefly describe what's in these notes")
        pdf_file = st.file_uploader("PDF file *", type=["pdf"])
        submitted = st.form_submit_button("Upload", type="primary")

        if submitted:
            if not title.strip():
                st.error("Please give your note a title.")
            elif pdf_file is None:
                st.error("Please attach a PDF file.")
            else:
                stored_filename = f"{uuid.uuid4().hex}.pdf"
                dest_path = os.path.join(db.UPLOAD_DIR, stored_filename)
                with open(dest_path, "wb") as f:
                    f.write(pdf_file.getbuffer())

                db.add_note(
                    title=title.strip(),
                    subject=subject.strip(),
                    description=description.strip(),
                    uploader_email=user_email,
                    uploader_name=user_name,
                    original_filename=pdf_file.name,
                    stored_filename=stored_filename,
                )
                st.success("Your note has been uploaded and is now searchable by everyone!")

# ---------------------------- My notes page -----------------------------------
elif page == "📁 My Notes":
    st.header("Notes you've uploaded")
    my_notes = db.get_notes_by_user(user_email)
    if not my_notes:
        st.info("You haven't uploaded any notes yet. Go to 'Upload Note' to add one.")
    for note in my_notes:
        note_card(note, show_delete=True)
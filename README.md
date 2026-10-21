# 📚 Study Swap Pro

> **A collaborative study-notes platform where students can securely share, discover, download, and manage academic notes.**

Study Swap Pro is a **Streamlit-based student note-sharing application** designed to make academic resources easier to find and exchange.

Students can create an account, upload PDF notes, search shared resources by title or subject, download notes, and manage the notes they have uploaded — all through a simple and responsive web interface.

---

## ✨ Features

### 🔐 User Authentication
- Student registration and login
- Email format validation
- Password confirmation during registration
- Secure password hashing using **bcrypt**
- Session-based authentication with Streamlit
- Logout functionality

### 🔑 Password Recovery
- Generate a temporary password-reset key
- Reset passwords using the generated key
- Reset keys are cleared after a successful password change

> **Production note:** The current implementation displays the reset key directly in the application. A production deployment should deliver reset keys through a verified email workflow.

### 📤 Upload Study Notes
- Upload PDF study materials
- Add a title and subject
- Add an optional description
- Automatically generate unique stored filenames
- Associate every uploaded note with its uploader

### 🔎 Search Notes
Search the shared notes collection using:
- Note title
- Subject
- Description/keywords

If no search query is entered, users can browse all available notes.

### 📥 Download Notes
- Download uploaded PDFs directly from the application
- Preserve the original uploaded filename
- Display note metadata before downloading

### 👤 My Notes
Each authenticated user can:
- View their uploaded notes
- Download their own notes
- Delete notes they own

The application also performs an ownership check before allowing deletion.

### 🗃️ Local Database
Study Swap Pro uses **SQLite** for lightweight persistent storage.

The database stores:
- User accounts
- Password hashes
- Password-reset keys
- Note metadata
- Upload information
- Ownership information
- Upload timestamps

---

## 🖥️ Application Flow

```text
                    ┌─────────────────────┐
                    │    Study Swap Pro   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
          Authentication                 Logged In
                │                             │
       ┌────────┼────────┐            ┌───────┼────────┐
       │        │        │            │       │        │
     Login    Sign Up  Reset       Search   Upload   My Notes
       │        │        │            │       │        │
       └────────┴────────┘            │       │        │
                │                     │       │        │
                └─────────────────────┴───────┴────────┘
                                      │
                              ┌───────▼────────┐
                              │   SQLite DB    │
                              │    + PDFs      │
                              └────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core application language |
| **Streamlit** | Web application interface |
| **SQLite** | Local database |
| **bcrypt** | Secure password hashing |
| **Secrets** | Secure reset-key generation |
| **UUID** | Unique uploaded-file names |
| **Regular Expressions** | Email validation |

---

## 📂 Project Structure

```text
StudyswapPro/
│
├── main.py              # Streamlit application and UI
├── database.py          # Database, authentication, and note operations
├── notes.db             # SQLite database
├── uploads/             # Uploaded PDF files
└── README.md            # Project documentation
```

### `main.py`

Handles the application's user interface and application flow, including:

- Login
- Registration
- Password recovery
- Navigation
- Note searching
- PDF uploading
- PDF downloading
- Personal note management
- Note deletion

### `database.py`

Provides the application's persistence and security layer, including:

- SQLite connection management
- Database initialization
- User creation
- Password hashing
- User authentication
- Password reset
- Note creation
- Note searching
- Note retrieval
- User-specific note retrieval
- Ownership-based note deletion

---

## ⚙️ Requirements

Make sure you have **Python 3.9+** installed.

Install the required dependencies:

```bash
pip install streamlit bcrypt
```

---

## 🚀 Installation

### 1. Clone the repository

Clone the project to your local machine using Git.

```bash
git clone <repository-url>
cd StudyswapPro
```

### 2. Create a virtual environment

It is recommended to use a virtual environment.

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit bcrypt
```

### 4. Run the application

```bash
streamlit run main.py
```

Streamlit will start the local development server and provide a URL for accessing the application in your browser.

---

## 🔐 Security

Study Swap Pro includes several security-oriented implementation choices:

### Password Hashing

Passwords are **not stored as plain text**. The application hashes passwords using bcrypt before storing them in SQLite.

```python
hashed = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
)
```

### Authentication

Users must successfully authenticate before accessing the main note-sharing functionality.

### Ownership Validation

A user can delete a note only when their authenticated email matches the email associated with the uploaded note.

This prevents users from deleting another student's notes through the application's deletion flow.

### Unique File Storage

Uploaded PDFs receive UUID-based filenames to avoid filename collisions.

```text
original_file.pdf
        ↓
UUID-generated filename
        ↓
uploads/<unique-id>.pdf
```

---

## 📚 How to Use

### 1. Create an Account

Open the application and select **Sign Up**.

Provide:

- Email address
- Full name
- Password
- Password confirmation

Once registration succeeds, log in with your credentials.

---

### 2. Search for Notes

Navigate to:

```text
🔍 Search Notes
```

Enter keywords such as:

```text
Data Structures
Thermodynamics
Operating Systems
Machine Learning
Database
```

Search results can match the note's:

- Title
- Subject
- Description

---

### 3. Upload a Note

Navigate to:

```text
⬆️ Upload Note
```

Enter:

- Note title
- Subject
- Description
- PDF file

Click **Upload** to add the resource to the shared collection.

---

### 4. Download Notes

Search for a note and click:

```text
⬇️ Download PDF
```

The file is downloaded using its original filename.

---

### 5. Manage Your Notes

Navigate to:

```text
📁 My Notes
```

Here you can view the notes you uploaded and delete resources that belong to you.

---

## 🗄️ Database Design

The application currently maintains two primary SQLite tables.

### Users

```text
users
├── email
├── name
├── password_hash
└

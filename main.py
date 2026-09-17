from tkinter import *
from tkinter import messagebox, simpledialog
import os
import pyperclip

from password_logic import generate_password, validate_fields
from crypto_utils import generate_salt, derive_key, encrypt_password, decrypt_password, key_is_correct
import db

SALT_FILE = "salt.bin"
CHECK_FILE = "check.token"

# ---------------------------- MASTER PASSWORD / KEY SETUP ------------------------------- #

def unlock() -> bytes:
    """On first run: create a master password and store a salt + a 'check' value
    (never the password itself). On later runs: ask for the master password and
    verify it against the check value before unlocking the vault."""
    root_check = Tk()
    root_check.withdraw()  # hide the blank root window while we show dialogs

    if not os.path.exists(SALT_FILE):
        password = simpledialog.askstring(
            "Create Master Password",
            "No vault found yet. Choose a master password to protect it:",
            show="*",
        )
        if not password:
            messagebox.showerror("Password Manager", "A master password is required.")
            raise SystemExit

        salt = generate_salt()
        with open(SALT_FILE, "wb") as f:
            f.write(salt)

        key = derive_key(password, salt)
        check_token = encrypt_password("verify", key)
        with open(CHECK_FILE, "w") as f:
            f.write(check_token)
    else:
        password = simpledialog.askstring(
            "Unlock Password Manager",
            "Enter your master password:",
            show="*",
        )
        if not password:
            raise SystemExit

        with open(SALT_FILE, "rb") as f:
            salt = f.read()
        key = derive_key(password, salt)

        with open(CHECK_FILE) as f:
            check_token = f.read()

        if not key_is_correct(key, check_token):
            messagebox.showerror("Password Manager", "Incorrect master password.")
            raise SystemExit

    root_check.destroy()
    return key


db.init_db()
ENCRYPTION_KEY = unlock()

# ---------------------------- PASSWORD GENERATOR ------------------------------- #

def generate():
    password = generate_password(12)
    password_E.delete(0, END)
    password_E.insert(0, password)
    pyperclip.copy(password)


# ---------------------------- SAVE PASSWORD ------------------------------- #

def save():
    website = website_E.get()
    username = email_E.get()
    password = password_E.get()

    if not validate_fields(website, username, password):
        messagebox.showinfo(title="Oops", message="Please don't leave any fields empty!")
        return

    is_ok = messagebox.askokcancel(
        title=website,
        message=f"These are the details entered:\nUsername: {username}\nPassword: {password}\nIs it ok to save?",
    )
    if not is_ok:
        return

    encrypted = encrypt_password(password, ENCRYPTION_KEY)
    db.add_entry(website, username, encrypted)

    website_E.delete(0, END)
    password_E.delete(0, END)
    website_E.focus()


# ---------------------------- SEARCH / RETRIEVE PASSWORD ------------------------------- #

def search():
    website = website_E.get()
    if not website.strip():
        messagebox.showinfo(title="Oops", message="Enter a website to search for.")
        return

    result = db.get_entry(website)
    if result is None:
        messagebox.showinfo(title="Not Found", message=f"No details for '{website}' exist.")
        return

    found_website, username, encrypted_password = result
    password = decrypt_password(encrypted_password, ENCRYPTION_KEY)
    pyperclip.copy(password)
    messagebox.showinfo(
        title=found_website,
        message=f"Username: {username}\nPassword: {password}\n\n(password copied to clipboard)",
    )


# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)
window.resizable(False, False)

canvas = Canvas(width=200, height=200, highlightthickness=0)
lock_img = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=lock_img)
canvas.grid(column=0, row=0, columnspan=3)

# Labels

website = Label(text="Website:", font=("Arial", 12))
website.grid(column=0, row=1, sticky="e")

email = Label(text="Email/Username:", font=("Arial", 12))
email.grid(column=0, row=2, sticky="e")

password = Label(text="Password:", font=("Arial", 12))
password.grid(column=0, row=3, sticky="e")

# Entries

website_E = Entry(width=21)
website_E.grid(column=1, row=1, sticky="we")
website_E.focus()

search_button = Button(text="Search", command=search)
search_button.grid(column=2, row=1, sticky="we")

email_E = Entry(width=35)
email_E.grid(column=1, row=2, columnspan=2, sticky="we")

password_E = Entry(width=21)
password_E.grid(column=1, row=3, sticky="we")

# Buttons

generate_button = Button(text="Generate Password", command=generate)
generate_button.grid(column=2, row=3, sticky="we")

add_button = Button(text="Add", command=save)
add_button.grid(column=1, row=4, columnspan=2, sticky="we")

window.mainloop()

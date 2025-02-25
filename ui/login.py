import customtkinter as ctk
from PIL import Image, ImageTk
import os

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login, db):
        """Initialize the login screen."""
        super().__init__(master)
        self.master = master
        self.on_login = on_login
        self.db = db
        
        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="CryptoJandie",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="The smartest crypto portfolio tracker on the block",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Username entry
        self.username_label = ctk.CTkLabel(
            self.main_frame,
            text="Username:",
            font=ctk.CTkFont(size=14)
        )
        self.username_label.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            width=300,
            placeholder_text="Enter your username"
        )
        self.username_entry.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Password label
        self.password_label = ctk.CTkLabel(
            self.main_frame,
            text="Password:",
            font=ctk.CTkFont(size=14)
        )
        self.password_label.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.main_frame,
            width=300,
            placeholder_text="Enter your password",
            show="*"
        )
        self.password_entry.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Login / Register",
            command=self.handle_login,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_button.grid(row=6, column=0, padx=20, pady=(10, 10), sticky="ew")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        self.status_label.grid(row=7, column=0, padx=20, pady=(5, 20), sticky="ew")
        
    def handle_login(self):
        """Handle login button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.configure(text="Please enter both username and password.")
            return

        # Check if user exists
        user = self.db.get_user(username)

        if user:
            # Existing user: check password
            if user.get('password') != password:
                self.status_label.configure(text="Incorrect password.")
                return

            # Correct password, update last login
            self.db.update_user_login(user['id'])
            self.status_label.configure(text=f"Welcome back, {username}!")
        else:
            # New user: create account with standard default password 'password123'
            user_id = self.db.add_user(username)
            if user_id:
                user = {'id': user_id, 'username': username, 'password': 'password123'}
                self.status_label.configure(text=f"New account created for {username}!\nDefault password is 'password123'.")
            else:
                self.status_label.configure(text="Error creating user account.")
                return

        # Call the login callback
        self.on_login(user) 
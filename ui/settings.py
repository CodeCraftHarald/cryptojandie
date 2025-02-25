import customtkinter as ctk
from PIL import Image, ImageTk
import os
import json
import tkinter as tk
from tkinter import messagebox

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, user, db, app_instance):
        """Initialize the settings screen."""
        super().__init__(master)
        self.master = master
        self.user = user
        self.db = db
        self.app_instance = app_instance
        
        # Load user settings
        self.load_settings()
        
        # Configure layout
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_columnconfigure(0, weight=1)
        
        # Create title
        self.create_title()
        
        # Create content
        self.create_content()
        
    def load_settings(self):
        """Load user settings from database."""
        # Default settings
        self.settings = {
            "appearance_mode": "dark",
            "color_theme": "blue",
            "currency": "USD",
            "api_cooldown": 60,
            "notifications_enabled": True,
            "price_alert_threshold": 5.0
        }
        
        # Get user settings from database
        if self.user and 'settings' in self.user:
            # Merge with defaults
            if isinstance(self.user['settings'], dict):
                self.settings.update(self.user['settings'])
            elif isinstance(self.user['settings'], str):
                try:
                    user_settings = json.loads(self.user['settings'])
                    if isinstance(user_settings, dict):
                        self.settings.update(user_settings)
                except json.JSONDecodeError:
                    pass
        
    def save_settings(self):
        """Save settings to database."""
        if not self.user:
            return
            
        # Update database
        self.cursor = self.db.connection.cursor()
        self.cursor.execute(
            "UPDATE users SET settings = ? WHERE id = ?",
            (json.dumps(self.settings), self.user['id'])
        )
        self.db.connection.commit()
        
        # Apply settings to app
        self.apply_settings()
        
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
        
    def apply_settings(self):
        """Apply settings to the application."""
        # Apply appearance mode
        ctk.set_appearance_mode(self.settings["appearance_mode"])
        
        # Apply color theme
        ctk.set_default_color_theme(self.settings["color_theme"])
        
        # Update API cooldown if app_instance has API
        if hasattr(self.app_instance, 'api'):
            self.app_instance.api.cooldown_period = self.settings["api_cooldown"]
        
    def create_title(self):
        """Create title section."""
        self.title_frame = ctk.CTkFrame(self)
        self.title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Configure title layout
        self.title_frame.grid_columnconfigure(0, weight=1)
        self.title_frame.grid_columnconfigure(1, weight=0)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Save button
        self.save_button = ctk.CTkButton(
            self.title_frame,
            text="Save Settings",
            command=self.save_settings,
            width=120
        )
        self.save_button.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="e")
        
    def create_content(self):
        """Create content with settings options."""
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure content layout
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Appearance settings
        self.appearance_section = self.create_section("Appearance Settings")
        self.appearance_section.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Appearance mode setting
        appearance_frame = ctk.CTkFrame(self.appearance_section)
        appearance_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        appearance_label = ctk.CTkLabel(
            appearance_frame,
            text="Appearance Mode:",
            font=ctk.CTkFont(size=14)
        )
        appearance_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        appearance_options = ["dark", "light", "system"]
        self.appearance_var = ctk.StringVar(value=self.settings["appearance_mode"])
        
        appearance_dropdown = ctk.CTkOptionMenu(
            appearance_frame,
            values=appearance_options,
            variable=self.appearance_var,
            command=self.on_appearance_change,
            width=200
        )
        appearance_dropdown.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")
        
        # Color theme setting
        theme_frame = ctk.CTkFrame(self.appearance_section)
        theme_frame.pack(fill="x", expand=True, padx=10, pady=(0, 10))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Color Theme:",
            font=ctk.CTkFont(size=14)
        )
        theme_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        theme_options = ["blue", "green", "dark-blue"]
        self.theme_var = ctk.StringVar(value=self.settings["color_theme"])
        
        theme_dropdown = ctk.CTkOptionMenu(
            theme_frame,
            values=theme_options,
            variable=self.theme_var,
            command=self.on_theme_change,
            width=200
        )
        theme_dropdown.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")
        
        # API Settings
        self.api_section = self.create_section("API Settings")
        self.api_section.grid(row=1, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # API cooldown setting
        cooldown_frame = ctk.CTkFrame(self.api_section)
        cooldown_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        cooldown_label = ctk.CTkLabel(
            cooldown_frame,
            text="API Cooldown Period (seconds):",
            font=ctk.CTkFont(size=14)
        )
        cooldown_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        self.cooldown_var = ctk.IntVar(value=self.settings["api_cooldown"])
        
        cooldown_slider = ctk.CTkSlider(
            cooldown_frame,
            from_=30,
            to=300,
            number_of_steps=27,  # (300-30)/10 = 27 steps of 10 seconds
            variable=self.cooldown_var,
            command=self.on_cooldown_change
        )
        cooldown_slider.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="ew")
        
        self.cooldown_value_label = ctk.CTkLabel(
            cooldown_frame,
            text=f"{self.settings['api_cooldown']} seconds",
            font=ctk.CTkFont(size=12)
        )
        self.cooldown_value_label.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="w")
        
        cooldown_info = ctk.CTkLabel(
            cooldown_frame,
            text="Note: CoinGecko API has rate limits. Setting this too low may result in API errors.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=500
        )
        cooldown_info.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Display Settings
        self.display_section = self.create_section("Display Settings")
        self.display_section.grid(row=2, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Currency setting
        currency_frame = ctk.CTkFrame(self.display_section)
        currency_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        currency_label = ctk.CTkLabel(
            currency_frame,
            text="Currency:",
            font=ctk.CTkFont(size=14)
        )
        currency_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        currency_options = ["USD", "EUR", "GBP", "JPY"]  # Currently only USD is fully supported
        self.currency_var = ctk.StringVar(value=self.settings["currency"])
        
        currency_dropdown = ctk.CTkOptionMenu(
            currency_frame,
            values=currency_options,
            variable=self.currency_var,
            command=self.on_currency_change,
            width=200,
            state="disabled"  # Disable until other currencies are supported
        )
        currency_dropdown.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")
        
        currency_info = ctk.CTkLabel(
            currency_frame,
            text="Note: Currently only USD is fully supported.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        currency_info.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Notification Settings
        self.notification_section = self.create_section("Notification Settings")
        self.notification_section.grid(row=3, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Enable notifications
        notifications_frame = ctk.CTkFrame(self.notification_section)
        notifications_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        self.notifications_var = ctk.BooleanVar(value=self.settings["notifications_enabled"])
        
        notifications_switch = ctk.CTkSwitch(
            notifications_frame,
            text="Enable Price Alerts",
            variable=self.notifications_var,
            command=self.on_notifications_change,
            onvalue=True,
            offvalue=False
        )
        notifications_switch.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Price alert threshold
        threshold_frame = ctk.CTkFrame(self.notification_section)
        threshold_frame.pack(fill="x", expand=True, padx=10, pady=(0, 10))
        
        threshold_label = ctk.CTkLabel(
            threshold_frame,
            text="Price Alert Threshold (%):",
            font=ctk.CTkFont(size=14)
        )
        threshold_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        self.threshold_var = ctk.DoubleVar(value=self.settings["price_alert_threshold"])
        
        threshold_slider = ctk.CTkSlider(
            threshold_frame,
            from_=1.0,
            to=20.0,
            number_of_steps=19,
            variable=self.threshold_var,
            command=self.on_threshold_change
        )
        threshold_slider.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="ew")
        
        self.threshold_value_label = ctk.CTkLabel(
            threshold_frame,
            text=f"{self.settings['price_alert_threshold']}%",
            font=ctk.CTkFont(size=12)
        )
        self.threshold_value_label.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="w")
        
        threshold_info = ctk.CTkLabel(
            threshold_frame,
            text="You will receive alerts when asset prices change by more than this percentage.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=500
        )
        threshold_info.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Account Settings
        self.account_section = self.create_section("Account Settings")
        self.account_section.grid(row=4, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Account info
        account_frame = ctk.CTkFrame(self.account_section)
        account_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        username_label = ctk.CTkLabel(
            account_frame,
            text=f"Username: {self.user['username']}",
            font=ctk.CTkFont(size=14)
        )
        username_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # New password label
        new_password_label = ctk.CTkLabel(
            account_frame,
            text="New Password:",
            font=ctk.CTkFont(size=14)
        )
        new_password_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # New password entry
        self.new_password_entry = ctk.CTkEntry(
            account_frame,
            width=300,
            placeholder_text="Enter new password",
            show="*"
        )
        self.new_password_entry.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="ew")
        
        # Confirm password label
        confirm_password_label = ctk.CTkLabel(
            account_frame,
            text="Confirm Password:",
            font=ctk.CTkFont(size=14)
        )
        confirm_password_label.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Confirm password entry
        self.confirm_password_entry = ctk.CTkEntry(
            account_frame,
            width=300,
            placeholder_text="Confirm new password",
            show="*"
        )
        self.confirm_password_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Update password button
        update_password_button = ctk.CTkButton(
            account_frame,
            text="Update Password",
            command=self.update_password,
            width=150
        )
        update_password_button.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="w")
        
        # About section
        self.about_section = self.create_section("About CryptoJandie")
        self.about_section.grid(row=5, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # About info
        about_frame = ctk.CTkFrame(self.about_section)
        about_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        app_name = ctk.CTkLabel(
            about_frame,
            text="CryptoJandie",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        app_name.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        app_version = ctk.CTkLabel(
            about_frame,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=12)
        )
        app_version.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        app_desc = ctk.CTkLabel(
            about_frame,
            text="The smartest crypto portfolio tracker on the block.",
            font=ctk.CTkFont(size=12)
        )
        app_desc.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")
        
        app_copyright = ctk.CTkLabel(
            about_frame,
            text="© 2024 CryptoJandie. All rights reserved.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        app_copyright.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")
        
    def create_section(self, title):
        """Create a section with title."""
        section_frame = ctk.CTkFrame(self.content_frame)
        
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=20, pady=10)
        
        return section_frame
        
    def on_appearance_change(self, value):
        """Handle appearance mode change."""
        self.settings["appearance_mode"] = value
        ctk.set_appearance_mode(value)
        
    def on_theme_change(self, value):
        """Handle color theme change."""
        self.settings["color_theme"] = value
        # Note: Theme change requires app restart to fully apply
        messagebox.showinfo("Theme Changed", "Theme changes will fully apply after restarting the application.")
        
    def on_cooldown_change(self, value):
        """Handle API cooldown change."""
        # Round to nearest 10
        cooldown = round(value / 10) * 10
        self.settings["api_cooldown"] = int(cooldown)
        self.cooldown_var.set(cooldown)
        self.cooldown_value_label.configure(text=f"{cooldown} seconds")
        
    def on_currency_change(self, value):
        """Handle currency change."""
        self.settings["currency"] = value
        
    def on_notifications_change(self):
        """Handle notifications toggle."""
        self.settings["notifications_enabled"] = self.notifications_var.get()
        
    def on_threshold_change(self, value):
        """Handle threshold change."""
        # Round to 1 decimal place
        threshold = round(value * 10) / 10
        self.settings["price_alert_threshold"] = threshold
        self.threshold_var.set(threshold)
        self.threshold_value_label.configure(text=f"{threshold}%")
        
    def update_password(self):
        """Update the user's password."""
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill in both password fields.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Update the password in the database
        self.db.update_user_password(self.user['id'], new_password)
        # Update the password in the current user session
        self.user['password'] = new_password
        messagebox.showinfo("Success", "Password updated successfully.") 
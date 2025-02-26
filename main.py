import customtkinter as ctk
import os
import sys
import threading
import time
from datetime import datetime
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox

# Import our modules
from database import Database
from api import CryptoAPI
from ui.login import LoginScreen
from ui.dashboard import PortfolioDashboard
from ui.assets import AssetManagement
from ui.analysis import AnalysisDashboard
from ui.settings import SettingsPage

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Options: "dark" (default), "light", "system"
ctk.set_default_color_theme("blue")  # Options: "blue" (default), "green", "dark-blue"

class CryptoJandieApp:
    def __init__(self, root):
        """Initialize the main application."""
        self.root = root
        self.root.title("CryptoJandie - Crypto Portfolio Tracker")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize database and API
        self.db = Database()
        self.db.initialize_default_assets()
        self.api = CryptoAPI()
        
        # Configure the root layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Current user data
        self.current_user = None
        
        # Current active frame
        self.current_frame = None
        
        # Show login screen
        self.show_login_screen()
        
    def show_login_screen(self):
        """Show the login screen."""
        # Destroy current frame if exists
        if self.current_frame:
            self.current_frame.destroy()
            
        # Create and show login screen
        self.current_frame = LoginScreen(self.root, self.on_login, self.db)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_login(self, user):
        """Handle user login."""
        self.current_user = user
        print(f"User logged in: {user['username']}")
        
        # Delay to show login success message before switching screens
        self.root.after(1000, self.show_main_app)
        
    def show_main_app(self):
        """Show the main application after login."""
        # Destroy current frame
        if self.current_frame:
            self.current_frame.destroy()
            
        # Create the main app layout
        self.create_main_layout()
        
    def create_main_layout(self):
        """Create the main application layout with tabbed interface."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure layout
        self.main_frame.grid_rowconfigure(0, weight=0)  # Header
        self.main_frame.grid_rowconfigure(1, weight=1)  # Content
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create header with navigation
        self.create_header()
        
        # Create tabview for different sections
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Add tabs
        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_assets = self.tabview.add("Assets")
        self.tab_analysis = self.tabview.add("Analysis")
        self.tab_settings = self.tabview.add("Settings")
        
        # Track loaded states
        self.analysis_loaded = False
        self.settings_loaded = False
        
        # Configure tabs
        for tab in [self.tab_dashboard, self.tab_assets, self.tab_analysis, self.tab_settings]:
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
        
        # Load dashboard content
        print("Initializing Dashboard...")
        self.dashboard = PortfolioDashboard(
            self.tab_dashboard, 
            self.current_user, 
            self.db, 
            self.api,
            self.refresh_prices
        )
        self.dashboard.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Load assets management content
        print("Initializing Assets Management...")
        self.assets = AssetManagement(
            self.tab_assets,
            self.current_user,
            self.db,
            self.api,
            self.refresh_prices
        )
        self.assets.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Create placeholder frames for Analysis and Settings that will be loaded on demand
        self.analysis_frame = ctk.CTkFrame(self.tab_analysis)
        self.analysis_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Add loading message for Analysis
        analysis_loading_label = ctk.CTkLabel(
            self.analysis_frame,
            text="Analysis Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        analysis_loading_label.pack(pady=(100, 10))
        
        analysis_loading_message = ctk.CTkLabel(
            self.analysis_frame,
            text="Loading analysis content...",
            font=ctk.CTkFont(size=14)
        )
        analysis_loading_message.pack(pady=10)
        
        self.settings_frame = ctk.CTkFrame(self.tab_settings)
        self.settings_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Add loading message for Settings
        settings_loading_label = ctk.CTkLabel(
            self.settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        settings_loading_label.pack(pady=(100, 10))
        
        settings_loading_message = ctk.CTkLabel(
            self.settings_frame,
            text="Loading settings content...",
            font=ctk.CTkFont(size=14)
        )
        settings_loading_message.pack(pady=10)
        
        # Set up tab change event to load content when tabs are selected
        self.tabview.configure(command=self.on_tab_change)
        
        # Set current frame for future destruction
        self.current_frame = self.main_frame
        
        # Default to Dashboard tab
        self.tabview.set("Dashboard")
        
        # Check for tab content loading after a short delay to allow UI to initialize
        self.root.after(500, self.check_initial_tab)
        
    def on_tab_change(self):
        """Handle tab change events to load content dynamically."""
        current_tab = self.tabview.get()
        
        # Load Analysis content when Analysis tab is selected
        if current_tab == "Analysis" and not self.analysis_loaded:
            print("Loading Analysis Dashboard due to tab selection...")
            self.root.after(100, self.load_analysis_page)  # Short delay for UI to update
            self.analysis_loaded = True
            
        # Load Settings content when Settings tab is selected
        elif current_tab == "Settings" and not self.settings_loaded:
            print("Loading Settings Page due to tab selection...")
            self.root.after(100, self.load_settings_page)  # Short delay for UI to update
            self.settings_loaded = True
        
    def create_header(self):
        """Create application header with navigation and user info."""
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.main_frame, height=60)
        self.header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Prevent header from resizing with window
        self.header_frame.grid_propagate(False)
        
        # Configure header layout
        self.header_frame.grid_columnconfigure(0, weight=1)  # App title
        self.header_frame.grid_columnconfigure(1, weight=0)  # User info
        self.header_frame.grid_columnconfigure(2, weight=0)  # Logout button
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="CryptoJandie",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=0, sticky="w")
        
        # User info
        self.user_label = ctk.CTkLabel(
            self.header_frame,
            text=f"Logged in as: {self.current_user['username']}",
            font=ctk.CTkFont(size=12)
        )
        self.user_label.grid(row=0, column=1, padx=20, pady=0, sticky="e")
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self.header_frame,
            text="Logout",
            command=self.logout,
            width=100,
            height=30
        )
        self.logout_button.grid(row=0, column=2, padx=20, pady=0, sticky="e")
        
    def load_analysis_page(self):
        """Load the analysis dashboard page."""
        try:
            # Remove the placeholder
            self.analysis_frame.destroy()
            
            # Create the actual Analysis Dashboard
            self.analysis = AnalysisDashboard(
                self.tab_analysis,
                self.current_user,
                self.db,
                self.api
            )
            self.analysis.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
            print("Analysis Dashboard loaded successfully")
        except Exception as e:
            print(f"Error loading Analysis Dashboard: {str(e)}")
            # Show error message to user
            messagebox.showerror("Error", f"Could not load Analysis Dashboard: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def load_settings_page(self):
        """Load the settings page."""
        try:
            # Remove the placeholder
            self.settings_frame.destroy()
            
            # Create the actual Settings Page
            self.settings_page = SettingsPage(
                self.tab_settings,
                self.current_user,
                self.db,
                self
            )
            self.settings_page.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
            print("Settings Page loaded successfully")
        except Exception as e:
            print(f"Error loading Settings Page: {str(e)}")
            # Show error message to user
            messagebox.showerror("Error", f"Could not load Settings Page: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def logout(self):
        """Handle user logout."""
        self.current_user = None
        self.show_login_screen()
        
    def refresh_prices(self):
        """Refresh cryptocurrency prices from API."""
        # Get all assets
        self.cursor = self.db.connection.cursor()
        self.cursor.execute("SELECT id, coingecko_id FROM assets WHERE coingecko_id IS NOT NULL")
        assets = self.cursor.fetchall()
        
        # Filter out assets without CoinGecko ID
        assets_with_id = [asset for asset in assets if asset['coingecko_id']]
        
        if not assets_with_id:
            return
            
        # Check API cooldown
        if not self.api.can_make_request():
            remaining = int(self.api.get_remaining_cooldown())
            print(f"API cooldown active. Please wait {remaining} seconds.")
            return
            
        # Split assets into batches to avoid too long URLs
        batch_size = 50
        asset_batches = [assets_with_id[i:i + batch_size] for i in range(0, len(assets_with_id), batch_size)]
        
        updated_count = 0
        
        # Process each batch
        for batch in asset_batches:
            coingecko_ids = [asset['coingecko_id'] for asset in batch]
            
            # Get prices from API
            prices, error = self.api.get_multiple_prices(coingecko_ids)
            
            if error:
                print(f"API Error: {error}")
                continue
                
            if not prices:
                continue
                
            # Update prices in database
            for asset in batch:
                asset_id = asset['id']
                coingecko_id = asset['coingecko_id']
                
                if coingecko_id in prices:
                    price_data = prices[coingecko_id]
                    self.db.add_price(asset_id, price_data['price_usd'], "api")
                    self.db.update_asset_market_cap(asset_id, price_data.get('market_cap', 0))
                    updated_count += 1
                    
        print(f"Updated prices for {updated_count} assets")

    def check_initial_tab(self):
        """Check if initial tab content is loaded and load if not."""
        current_tab = self.tabview.get()
        
        if current_tab == "Analysis" and not self.analysis_loaded:
            print("Loading Analysis Dashboard due to initial tab check...")
            self.root.after(100, self.load_analysis_page)
            self.analysis_loaded = True
        elif current_tab == "Settings" and not self.settings_loaded:
            print("Loading Settings Page due to initial tab check...")
            self.root.after(100, self.load_settings_page)
            self.settings_loaded = True

if __name__ == "__main__":
    root = ctk.CTk()
    app = CryptoJandieApp(root)
    root.mainloop() 
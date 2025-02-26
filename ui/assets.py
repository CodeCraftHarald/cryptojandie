import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from utils import format_currency, format_percentage, calculate_weighted_average, parse_csv_data, convert_comma_to_period, parse_numeric_input

class AssetManagement(ctk.CTkFrame):
    def __init__(self, master, user, db, api, refresh_callback):
        """Initialize the asset management screen."""
        super().__init__(master)
        self.master = master
        self.user = user
        self.db = db
        self.api = api
        self.refresh_callback = refresh_callback
        self.sort_by = "value"  # Default sort
        self.sort_ascending = False
        self.current_prices = {}
        
        # Configure layout
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_columnconfigure(0, weight=1)
        
        # Create header
        self.create_header()
        
        # Create content area with tabs
        self.create_content()
        
        # Load data
        self.load_assets_data()
        
    def create_header(self):
        """Create header with title and action buttons."""
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Configure header layout
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_columnconfigure(2, weight=0)
        self.header_frame.grid_columnconfigure(3, weight=0)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Manage Your Assets",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Add Asset button
        self.add_button = ctk.CTkButton(
            self.header_frame,
            text="Add Asset",
            command=self.show_add_asset_dialog,
            width=100
        )
        self.add_button.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")
        
        # Import CSV button
        self.import_button = ctk.CTkButton(
            self.header_frame,
            text="Import CSV",
            command=self.import_csv,
            width=100
        )
        self.import_button.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="e")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.header_frame,
            text="Refresh Prices",
            command=self.refresh_data,
            width=120
        )
        self.refresh_button.grid(row=0, column=3, padx=(0, 20), pady=10, sticky="e")
        
    def create_content(self):
        """Create content area with tabs."""
        self.content_frame = ctk.CTkTabview(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Create tabs
        self.tab_holdings = self.content_frame.add("Holdings")
        self.tab_history = self.content_frame.add("Transaction History")
        
        # Configure holdings tab
        self.tab_holdings.grid_rowconfigure(0, weight=0)  # Sort options
        self.tab_holdings.grid_rowconfigure(1, weight=1)  # Holdings list
        self.tab_holdings.grid_columnconfigure(0, weight=1)
        
        # Create sort options
        self.create_sort_options()
        
        # Create holdings list
        self.create_holdings_list()
        
        # Configure history tab
        self.tab_history.grid_rowconfigure(0, weight=1)  # History list
        self.tab_history.grid_columnconfigure(0, weight=1)
        
        # Create transaction history list
        self.create_transaction_list()
        
    def create_sort_options(self):
        """Create sort options panel."""
        self.sort_frame = ctk.CTkFrame(self.tab_holdings)
        self.sort_frame.grid(row=0, column=0, padx=0, pady=(10, 10), sticky="ew")
        
        # Configure sort layout
        self.sort_frame.grid_columnconfigure(0, weight=0)
        self.sort_frame.grid_columnconfigure(1, weight=1)
        
        # Sort label
        self.sort_label = ctk.CTkLabel(
            self.sort_frame,
            text="Sort by:",
            font=ctk.CTkFont(size=14)
        )
        self.sort_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        
        # Sort options
        sort_options = [
            "Value (High to Low)",
            "Value (Low to High)",
            "Name (A to Z)",
            "Name (Z to A)",
            "Amount (High to Low)",
            "Amount (Low to High)",
            "Profit/Loss (High to Low)",
            "Profit/Loss (Low to High)",
            "Market Cap (High to Low)",
            "Market Cap (Low to High)"
        ]
        
        self.sort_var = ctk.StringVar(value=sort_options[0])
        
        self.sort_dropdown = ctk.CTkOptionMenu(
            self.sort_frame,
            values=sort_options,
            variable=self.sort_var,
            command=self.on_sort_change,
            width=200
        )
        self.sort_dropdown.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="w")
        
    def create_holdings_list(self):
        """Create holdings list with a treeview."""
        # Create a frame to hold the treeview and scrollbars
        self.holdings_frame = ctk.CTkFrame(self.tab_holdings)
        self.holdings_frame.grid(row=1, column=0, padx=0, pady=(0, 0), sticky="nsew")
        
        # Create the treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        rowheight=25,
                        fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", 
                        background="#1f1f1f",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading", 
                relief=[('active', 'flat'), ('pressed', 'flat')])
        
        # Create a frame to hold the treeview
        self.tree_container = tk.Frame(self.holdings_frame, bg="#2b2b2b")
        self.tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollbars
        self.tree_scrollbar_y = tk.Scrollbar(self.tree_container, orient="vertical")
        self.tree_scrollbar_y.pack(side="right", fill="y")
        
        self.tree_scrollbar_x = tk.Scrollbar(self.tree_container, orient="horizontal")
        self.tree_scrollbar_x.pack(side="bottom", fill="x")
        
        # Create the treeview
        self.holdings_tree = ttk.Treeview(
            self.tree_container,
            columns=("symbol", "amount", "value", "price", "purchase", "profit", "profit_pct", "actions"),
            show="headings",
            height=20,
            selectmode="browse",
            yscrollcommand=self.tree_scrollbar_y.set,
            xscrollcommand=self.tree_scrollbar_x.set
        )
        
        # Connect scrollbars
        self.tree_scrollbar_y.config(command=self.holdings_tree.yview)
        self.tree_scrollbar_x.config(command=self.holdings_tree.xview)
        
        # Define columns
        self.holdings_tree.heading("symbol", text="Asset")
        self.holdings_tree.heading("amount", text="Amount")
        self.holdings_tree.heading("value", text="Value (USD)")
        self.holdings_tree.heading("price", text="Current Price")
        self.holdings_tree.heading("purchase", text="Purchase Price")
        self.holdings_tree.heading("profit", text="Profit/Loss")
        self.holdings_tree.heading("profit_pct", text="Profit/Loss %")
        self.holdings_tree.heading("actions", text="Actions")
        
        # Column widths
        self.holdings_tree.column("symbol", width=100, anchor="w")
        self.holdings_tree.column("amount", width=100, anchor="e")
        self.holdings_tree.column("value", width=120, anchor="e")
        self.holdings_tree.column("price", width=120, anchor="e")
        self.holdings_tree.column("purchase", width=120, anchor="e")
        self.holdings_tree.column("profit", width=120, anchor="e")
        self.holdings_tree.column("profit_pct", width=100, anchor="e")
        self.holdings_tree.column("actions", width=120, anchor="center")
        
        # Pack the treeview
        self.holdings_tree.pack(fill="both", expand=True)
        
        # Bind row click event
        self.holdings_tree.bind("<Double-1>", self.on_holding_double_click)
        
    def create_transaction_list(self):
        """Create transaction history list with a treeview."""
        # Create a frame to hold the treeview and scrollbars
        self.transaction_frame = ctk.CTkFrame(self.tab_history)
        self.transaction_frame.grid(row=0, column=0, padx=0, pady=(10, 0), sticky="nsew")
        
        # Create a frame to hold the treeview
        self.trans_tree_container = tk.Frame(self.transaction_frame, bg="#2b2b2b")
        self.trans_tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollbars
        self.trans_scrollbar_y = tk.Scrollbar(self.trans_tree_container, orient="vertical")
        self.trans_scrollbar_y.pack(side="right", fill="y")
        
        self.trans_scrollbar_x = tk.Scrollbar(self.trans_tree_container, orient="horizontal")
        self.trans_scrollbar_x.pack(side="bottom", fill="x")
        
        # Create the treeview
        self.transaction_tree = ttk.Treeview(
            self.trans_tree_container,
            columns=("date", "type", "symbol", "amount", "price", "total", "notes", "actions"),
            show="headings",
            height=20,
            selectmode="browse",
            yscrollcommand=self.trans_scrollbar_y.set,
            xscrollcommand=self.trans_scrollbar_x.set
        )
        
        # Connect scrollbars
        self.trans_scrollbar_y.config(command=self.transaction_tree.yview)
        self.trans_scrollbar_x.config(command=self.transaction_tree.xview)
        
        # Define columns
        self.transaction_tree.heading("date", text="Date")
        self.transaction_tree.heading("type", text="Type")
        self.transaction_tree.heading("symbol", text="Asset")
        self.transaction_tree.heading("amount", text="Amount")
        self.transaction_tree.heading("price", text="Price per Unit")
        self.transaction_tree.heading("total", text="Total Value")
        self.transaction_tree.heading("notes", text="Notes")
        self.transaction_tree.heading("actions", text="Actions")
        
        # Column widths
        self.transaction_tree.column("date", width=150, anchor="w")
        self.transaction_tree.column("type", width=80, anchor="center")
        self.transaction_tree.column("symbol", width=100, anchor="w")
        self.transaction_tree.column("amount", width=100, anchor="e")
        self.transaction_tree.column("price", width=120, anchor="e")
        self.transaction_tree.column("total", width=120, anchor="e")
        self.transaction_tree.column("notes", width=200, anchor="w")
        self.transaction_tree.column("actions", width=80, anchor="center")
        
        # Pack the treeview
        self.transaction_tree.pack(fill="both", expand=True)
        
        # Bind right-click event for context menu
        self.transaction_tree.bind("<Button-3>", self.show_transaction_context_menu)
        # Bind double-click event for delete action
        self.transaction_tree.bind("<Double-1>", self.on_transaction_double_click)
        
    def on_sort_change(self, value):
        """Handle sort option change."""
        if value == "Value (High to Low)":
            self.sort_by = "value"
            self.sort_ascending = False
        elif value == "Value (Low to High)":
            self.sort_by = "value"
            self.sort_ascending = True
        elif value == "Name (A to Z)":
            self.sort_by = "name"
            self.sort_ascending = True
        elif value == "Name (Z to A)":
            self.sort_by = "name"
            self.sort_ascending = False
        elif value == "Amount (High to Low)":
            self.sort_by = "amount"
            self.sort_ascending = False
        elif value == "Amount (Low to High)":
            self.sort_by = "amount"
            self.sort_ascending = True
        elif value == "Profit/Loss (High to Low)":
            self.sort_by = "profit"
            self.sort_ascending = False
        elif value == "Profit/Loss (Low to High)":
            self.sort_by = "profit"
            self.sort_ascending = True
        elif value == "Market Cap (High to Low)":
            self.sort_by = "market_cap"
            self.sort_ascending = False
        elif value == "Market Cap (Low to High)":
            self.sort_by = "market_cap"
            self.sort_ascending = True
        
        # Reload the holdings list with the new sort
        self.load_assets_data()
        
    def load_assets_data(self):
        """Load asset data from database."""
        # Clear existing data
        self.holdings_tree.delete(*self.holdings_tree.get_children())
        self.transaction_tree.delete(*self.transaction_tree.get_children())
        
        # Get user holdings
        holdings_data = self.db.get_user_holdings(self.user['id'])
        
        if not holdings_data:
            return
            
        # Get latest prices for all assets
        asset_ids = [holding['asset_id'] for holding in holdings_data]
        self.current_prices = {}
        
        for asset_id in asset_ids:
            price_data = self.db.get_latest_price(asset_id)
            if price_data:
                self.current_prices[asset_id] = price_data['price_usd']
        
        # Process holdings data
        holdings = []
        
        for holding in holdings_data:
            price = self.current_prices.get(holding['asset_id'], 0)
            amount = holding['amount']
            purchase_price = holding['purchase_price_per_unit']
            
            value = amount * price
            profit_loss = value - (amount * purchase_price)
            profit_loss_pct = (profit_loss / (amount * purchase_price)) * 100 if purchase_price > 0 else 0
            
            holding_data = {
                "id": holding['id'],
                "asset_id": holding['asset_id'],
                "symbol": holding['symbol'],
                "name": holding['name'],
                "amount": amount,
                "price": price,
                "value": value,
                "purchase_price": purchase_price,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "market_cap": holding['market_cap'] or 0
            }
            
            holdings.append(holding_data)
        
        # Sort holdings
        if self.sort_by == "value":
            holdings.sort(key=lambda h: h["value"], reverse=not self.sort_ascending)
        elif self.sort_by == "name":
            holdings.sort(key=lambda h: h["name"], reverse=not self.sort_ascending)
        elif self.sort_by == "amount":
            holdings.sort(key=lambda h: h["amount"], reverse=not self.sort_ascending)
        elif self.sort_by == "profit":
            holdings.sort(key=lambda h: h["profit_loss"], reverse=not self.sort_ascending)
        elif self.sort_by == "market_cap":
            holdings.sort(key=lambda h: h["market_cap"], reverse=not self.sort_ascending)
        
        # Populate holdings treeview
        for holding in holdings:
            row_id = self.holdings_tree.insert(
                "",
                "end",
                values=(
                    f"{holding['symbol']} ({holding['name']})",
                    f"{holding['amount']:.8f}",
                    format_currency(holding['value']),
                    format_currency(holding['price']),
                    format_currency(holding['purchase_price']),
                    format_currency(holding['profit_loss']),
                    format_percentage(holding['profit_loss_pct']),
                    "Update | Delete"
                ),
                tags=(holding['id'],)
            )
            
            # Set row color based on profit/loss
            if holding['profit_loss'] > 0:
                self.holdings_tree.tag_configure(holding['id'], background="#2b2b2b", foreground="#2ecc71")
            elif holding['profit_loss'] < 0:
                self.holdings_tree.tag_configure(holding['id'], background="#2b2b2b", foreground="#e74c3c")
            else:
                self.holdings_tree.tag_configure(holding['id'], background="#2b2b2b", foreground="white")
        
        # Load transaction history
        transactions = self.db.get_user_transactions(self.user['id'])
        
        for transaction in transactions:
            transaction_id = transaction['id']
            self.transaction_tree.insert(
                "",
                "end",
                values=(
                    datetime.fromisoformat(transaction['timestamp']).strftime("%Y-%m-%d %H:%M:%S"),
                    transaction['transaction_type'],
                    transaction['symbol'],
                    f"{transaction['amount']:.8f}",
                    format_currency(transaction['price_per_unit']),
                    format_currency(transaction['amount'] * transaction['price_per_unit']),
                    transaction['notes'] or "",
                    "Edit | Delete"
                ),
                tags=(transaction_id,)
            )
            
    def show_add_asset_dialog(self):
        """Show dialog to add a new asset."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Asset")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.resizable(False, True)
        
        # Configure dialog layout
        dialog.grid_columnconfigure(0, weight=1)
        
        # Dialog title
        title_label = ctk.CTkLabel(
            dialog,
            text="Add New Asset",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Asset selection
        asset_frame = ctk.CTkFrame(dialog)
        asset_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        asset_label = ctk.CTkLabel(
            asset_frame,
            text="Select Asset:",
            font=ctk.CTkFont(size=14)
        )
        asset_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        # Get all assets
        assets_data = []
        self.cursor = self.db.connection.cursor()
        self.cursor.execute("SELECT id, symbol, name FROM assets ORDER BY symbol")
        for row in self.cursor.fetchall():
            assets_data.append({"id": row[0], "symbol": row[1], "name": row[2]})
        
        # Asset dropdown items
        asset_options = [f"{asset['symbol']} - {asset['name']}" for asset in assets_data]
        
        self.asset_var = ctk.StringVar(value=asset_options[0] if asset_options else "")
        
        asset_dropdown = ctk.CTkOptionMenu(
            asset_frame,
            values=asset_options,
            variable=self.asset_var,
            width=400
        )
        asset_dropdown.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Add custom asset option
        custom_asset_button = ctk.CTkButton(
            asset_frame,
            text="Add Custom Asset",
            command=lambda: self.show_custom_asset_dialog(dialog),
            width=400
        )
        custom_asset_button.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Amount entry
        amount_frame = ctk.CTkFrame(dialog)
        amount_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        amount_label = ctk.CTkLabel(
            amount_frame,
            text="Amount:",
            font=ctk.CTkFont(size=14)
        )
        amount_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        amount_entry = ctk.CTkEntry(
            amount_frame,
            width=400,
            placeholder_text="Enter the amount of cryptocurrency"
        )
        amount_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        # Bind comma-to-period conversion for German keyboard users
        amount_entry.bind("<Key>", convert_comma_to_period)
        
        # Purchase price entry
        price_frame = ctk.CTkFrame(dialog)
        price_frame.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        price_label = ctk.CTkLabel(
            price_frame,
            text="Purchase Price Per Unit (USD):",
            font=ctk.CTkFont(size=14)
        )
        price_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        price_entry = ctk.CTkEntry(
            price_frame,
            width=400,
            placeholder_text="Enter the purchase price per unit in USD"
        )
        price_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        # Bind comma-to-period conversion for German keyboard users
        price_entry.bind("<Key>", convert_comma_to_period)
        
        # Notes entry
        notes_frame = ctk.CTkFrame(dialog)
        notes_frame.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        notes_label = ctk.CTkLabel(
            notes_frame,
            text="Notes (optional):",
            font=ctk.CTkFont(size=14)
        )
        notes_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        notes_entry = ctk.CTkTextbox(
            notes_frame,
            width=400,
            height=80
        )
        notes_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="gray",
            width=180
        )
        cancel_button.grid(row=0, column=0, padx=(20, 10), pady=0, sticky="e")
        
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Asset",
            command=lambda: self.add_asset(
                dialog,
                assets_data,
                asset_dropdown.get(),
                amount_entry.get(),
                price_entry.get(),
                notes_entry.get("0.0", "end")
            ),
            width=180
        )
        add_button.grid(row=0, column=1, padx=(10, 20), pady=0, sticky="w")
        
    def show_custom_asset_dialog(self, parent_dialog):
        """Show dialog to add a custom asset."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Custom Asset")
        dialog.geometry("400x400")
        dialog.transient(parent_dialog)
        dialog.resizable(False, True)
        
        # Configure dialog layout
        dialog.grid_columnconfigure(0, weight=1)
        
        # Dialog title
        title_label = ctk.CTkLabel(
            dialog,
            text="Add Custom Asset",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Symbol entry
        symbol_frame = ctk.CTkFrame(dialog)
        symbol_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        symbol_label = ctk.CTkLabel(
            symbol_frame,
            text="Symbol:",
            font=ctk.CTkFont(size=14)
        )
        symbol_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        symbol_entry = ctk.CTkEntry(
            symbol_frame,
            width=300,
            placeholder_text="Enter the asset symbol (e.g., BTC)"
        )
        symbol_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Name entry
        name_frame = ctk.CTkFrame(dialog)
        name_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="Name:",
            font=ctk.CTkFont(size=14)
        )
        name_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        name_entry = ctk.CTkEntry(
            name_frame,
            width=300,
            placeholder_text="Enter the asset name (e.g., Bitcoin)"
        )
        name_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # CoinGecko ID entry
        coingecko_frame = ctk.CTkFrame(dialog)
        coingecko_frame.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        coingecko_label = ctk.CTkLabel(
            coingecko_frame,
            text="CoinGecko ID (optional for API integration):",
            font=ctk.CTkFont(size=14)
        )
        coingecko_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 0), sticky="w")
        
        coingecko_entry = ctk.CTkEntry(
            coingecko_frame,
            width=300,
            placeholder_text="Enter the CoinGecko ID (e.g., bitcoin)"
        )
        coingecko_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="gray",
            width=120
        )
        cancel_button.grid(row=0, column=0, padx=(20, 10), pady=0, sticky="e")
        
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Asset",
            command=lambda: self.add_custom_asset(
                dialog,
                parent_dialog,
                symbol_entry.get(),
                name_entry.get(),
                coingecko_entry.get()
            ),
            width=120
        )
        add_button.grid(row=0, column=1, padx=(10, 20), pady=0, sticky="w")
        
    def add_custom_asset(self, dialog, parent_dialog, symbol, name, coingecko_id):
        """Add a custom asset to the database."""
        symbol = symbol.strip().upper()
        name = name.strip()
        coingecko_id = coingecko_id.strip().lower() if coingecko_id else None
        
        if not symbol or not name:
            messagebox.showerror("Error", "Symbol and name are required.", parent=dialog)
            return
            
        # Add asset to database
        asset_id = self.db.add_asset(symbol, name, coingecko_id)
        
        if asset_id:
            messagebox.showinfo("Success", f"Added {symbol} to the database.", parent=dialog)
            
            # Update asset dropdown in parent dialog
            assets_data = []
            self.cursor = self.db.connection.cursor()
            self.cursor.execute("SELECT id, symbol, name FROM assets ORDER BY symbol")
            for row in self.cursor.fetchall():
                assets_data.append({"id": row[0], "symbol": row[1], "name": row[2]})
            
            asset_options = [f"{asset['symbol']} - {asset['name']}" for asset in assets_data]
            
            # Find the dropdown in the parent dialog and update it
            for child in parent_dialog.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ctk.CTkOptionMenu):
                            subchild.configure(values=asset_options)
                            subchild.set(f"{symbol} - {name}")
            
            dialog.destroy()
        else:
            messagebox.showerror("Error", f"Asset {symbol} already exists in the database.", parent=dialog)
        
    def add_asset(self, dialog, assets_data, asset_option, amount_str, price_str, notes):
        """Add asset to user's portfolio."""
        # Extract asset info from selection
        selected_symbol = asset_option.split(" - ")[0]
        selected_asset = next((a for a in assets_data if a["symbol"] == selected_symbol), None)
        
        if not selected_asset:
            messagebox.showerror("Error", "Please select a valid asset.", parent=dialog)
            return
            
        # Validate amount and price
        try:
            # Use parse_numeric_input to handle comma decimal separators
            amount = float(parse_numeric_input(amount_str))
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.", parent=dialog)
            return
            
        try:
            # Use parse_numeric_input to handle comma decimal separators
            price = float(parse_numeric_input(price_str))
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid purchase price.", parent=dialog)
            return
            
        # Add holding to database
        holding_id = self.db.add_holding(
            self.user['id'],
            selected_asset['id'],
            amount,
            price,
            notes.strip()
        )
        
        if holding_id:
            # Record transaction
            self.db.add_transaction(
                self.user['id'],
                selected_asset['id'],
                "BUY",
                amount,
                price,
                notes.strip()
            )
            
            messagebox.showinfo("Success", f"Added {amount} {selected_symbol} to your portfolio.", parent=dialog)
            dialog.destroy()
            
            # Refresh data
            self.load_assets_data()
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", "Failed to add asset to your portfolio.", parent=dialog)
            
    def show_update_dialog(self, holding_id):
        """Show dialog to update a holding."""
        # Get holding details
        self.cursor = self.db.connection.cursor()
        self.cursor.execute("""
            SELECT h.*, a.symbol, a.name 
            FROM holdings h
            JOIN assets a ON h.asset_id = a.id
            WHERE h.id = ?
        """, (holding_id,))
        holding = self.cursor.fetchone()
        
        if not holding:
            messagebox.showerror("Error", "Holding not found.")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Asset")
        dialog.geometry("500x700")
        dialog.transient(self)
        dialog.resizable(False, True)
        
        # Configure dialog layout
        dialog.grid_columnconfigure(0, weight=1)
        
        # Dialog title
        title_label = ctk.CTkLabel(
            dialog,
            text=f"Update {holding['symbol']} Holdings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Current holdings info
        info_frame = ctk.CTkFrame(dialog)
        info_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Current Holdings:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        current_amount_label = ctk.CTkLabel(
            info_frame,
            text=f"Amount: {holding['amount']:.8f} {holding['symbol']}",
            font=ctk.CTkFont(size=14)
        )
        current_amount_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        current_price_label = ctk.CTkLabel(
            info_frame,
            text=f"Purchase Price: ${holding['purchase_price_per_unit']:.2f} per {holding['symbol']}",
            font=ctk.CTkFont(size=14)
        )
        current_price_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Tabs for different update methods
        update_tabs = ctk.CTkTabview(dialog)
        update_tabs.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        # Add tabs
        tab_update = update_tabs.add("Update Total")
        tab_add = update_tabs.add("Add New Purchase")
        tab_staking = update_tabs.add("Add Staking Income")
        
        # Configure tab layout
        for tab in [tab_update, tab_add, tab_staking]:
            tab.grid_columnconfigure(0, weight=1)
        
        # UPDATE TOTAL TAB
        # New amount entry
        update_amount_frame = ctk.CTkFrame(tab_update)
        update_amount_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        
        update_amount_label = ctk.CTkLabel(
            update_amount_frame,
            text="New Total Amount:",
            font=ctk.CTkFont(size=14)
        )
        update_amount_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        update_amount_entry = ctk.CTkEntry(
            update_amount_frame,
            width=400,
            placeholder_text=f"Enter the new total amount of {holding['symbol']}"
        )
        update_amount_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        # Bind comma-to-period conversion for German keyboard users
        update_amount_entry.bind("<Key>", convert_comma_to_period)
        
        # Notes entry
        update_notes_frame = ctk.CTkFrame(tab_update)
        update_notes_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        update_notes_label = ctk.CTkLabel(
            update_notes_frame,
            text="Notes (optional):",
            font=ctk.CTkFont(size=14)
        )
        update_notes_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        update_notes_entry = ctk.CTkTextbox(
            update_notes_frame,
            width=400,
            height=80
        )
        update_notes_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Update button
        update_button = ctk.CTkButton(
            tab_update,
            text="Update Total Holdings",
            command=lambda: self.update_holding_total(
                dialog,
                holding,
                update_amount_entry.get(),
                update_notes_entry.get("0.0", "end")
            ),
            width=400
        )
        update_button.grid(row=2, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        # ADD NEW PURCHASE TAB
        # Amount entry
        add_amount_frame = ctk.CTkFrame(tab_add)
        add_amount_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        
        add_amount_label = ctk.CTkLabel(
            add_amount_frame,
            text="Additional Amount to Purchase:",
            font=ctk.CTkFont(size=14)
        )
        add_amount_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        add_amount_entry = ctk.CTkEntry(
            add_amount_frame,
            width=400,
            placeholder_text=f"Enter the additional amount of {holding['symbol']} to purchase"
        )
        add_amount_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        # Bind comma-to-period conversion for German keyboard users
        add_amount_entry.bind("<Key>", convert_comma_to_period)
        
        # Price entry
        add_price_frame = ctk.CTkFrame(tab_add)
        add_price_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        add_price_label = ctk.CTkLabel(
            add_price_frame,
            text="Purchase Price Per Unit (USD):",
            font=ctk.CTkFont(size=14)
        )
        add_price_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        add_price_entry = ctk.CTkEntry(
            add_price_frame,
            width=400,
            placeholder_text="Enter the purchase price per unit in USD"
        )
        add_price_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        # Bind comma-to-period conversion for German keyboard users
        add_price_entry.bind("<Key>", convert_comma_to_period)
        
        # Notes entry
        add_notes_frame = ctk.CTkFrame(tab_add)
        add_notes_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        add_notes_label = ctk.CTkLabel(
            add_notes_frame,
            text="Notes (optional):",
            font=ctk.CTkFont(size=14)
        )
        add_notes_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        add_notes_entry = ctk.CTkTextbox(
            add_notes_frame,
            width=400,
            height=80
        )
        add_notes_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Add button
        add_button = ctk.CTkButton(
            tab_add,
            text="Add New Purchase",
            command=lambda: self.add_new_purchase(
                dialog,
                holding,
                add_amount_entry.get(),
                add_price_entry.get(),
                add_notes_entry.get("0.0", "end")
            ),
            width=400
        )
        add_button.grid(row=3, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        # STAKING INCOME TAB
        # Amount entry
        stake_amount_frame = ctk.CTkFrame(tab_staking)
        stake_amount_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        
        stake_amount_label = ctk.CTkLabel(
            stake_amount_frame,
            text="New Total Amount (including staking rewards):",
            font=ctk.CTkFont(size=14)
        )
        stake_amount_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Display current amount for reference
        current_amount_info = ctk.CTkLabel(
            stake_amount_frame,
            text=f"Current amount: {holding['amount']:.8f} {holding['symbol']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        current_amount_info.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        # Helpful information text
        info_text = ctk.CTkLabel(
            stake_amount_frame,
            text="Enter the new total amount after adding staking rewards. The system will calculate the difference as staking income.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=380
        )
        info_text.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")
        
        stake_amount_entry = ctk.CTkEntry(
            stake_amount_frame,
            width=400,
            placeholder_text=f"Enter the new total amount including staking rewards"
        )
        stake_amount_entry.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")
        # Bind comma-to-period conversion for German keyboard users
        stake_amount_entry.bind("<Key>", convert_comma_to_period)
        
        # Notes entry
        stake_notes_frame = ctk.CTkFrame(tab_staking)
        stake_notes_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        stake_notes_label = ctk.CTkLabel(
            stake_notes_frame,
            text="Notes (optional):",
            font=ctk.CTkFont(size=14)
        )
        stake_notes_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        stake_notes_entry = ctk.CTkTextbox(
            stake_notes_frame,
            width=400,
            height=80
        )
        stake_notes_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Staking button
        stake_button = ctk.CTkButton(
            tab_staking,
            text="Add Staking Income",
            command=lambda: self.add_staking_income(
                dialog,
                holding,
                stake_amount_entry.get(),
                stake_notes_entry.get("0.0", "end")
            ),
            width=400
        )
        stake_button.grid(row=4, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        # Cancel button (bottom of dialog)
        cancel_button = ctk.CTkButton(
            dialog,
            text="Cancel",
            command=dialog.destroy,
            fg_color="gray",
            width=400
        )
        cancel_button.grid(row=5, column=0, padx=20, pady=(20, 20), sticky="ew")
        
    def update_holding_total(self, dialog, holding, new_amount_str, notes):
        """Update the total amount of a holding."""
        try:
            # Use parse_numeric_input to handle comma decimal separators
            new_amount = float(parse_numeric_input(new_amount_str))
            if new_amount < 0:
                raise ValueError("Amount cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.", parent=dialog)
            return
            
        # Calculate difference
        amount_diff = new_amount - holding['amount']
        
        # Update holding
        success = self.db.update_holding(
            self.user['id'],  # Make sure user_id is first
            holding['id'],    # holding_id second
            new_amount,
            holding['purchase_price_per_unit'],
            notes=notes.strip() if notes else None
        )
        
        # Record transaction if there's a difference
        if amount_diff != 0:
            transaction_type = "BUY" if amount_diff > 0 else "SELL"
            
            self.db.add_transaction(
                self.user['id'],
                holding['asset_id'],
                transaction_type,
                abs(amount_diff),
                holding['purchase_price_per_unit'],
                f"Manual update: {notes.strip()}" if notes else "Manual update"
            )
            
        messagebox.showinfo("Success", f"Updated {holding['symbol']} holdings to {new_amount}.", parent=dialog)
        dialog.destroy()
        
        # Refresh data
        self.load_assets_data()
        if self.refresh_callback:
            self.refresh_callback()
            
    def add_new_purchase(self, dialog, holding, amount_str, price_str, notes):
        """Add a new purchase to an existing holding."""
        try:
            # Use parse_numeric_input to handle comma decimal separators
            amount = float(parse_numeric_input(amount_str))
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.", parent=dialog)
            return
            
        try:
            # Use parse_numeric_input to handle comma decimal separators
            price = float(parse_numeric_input(price_str))
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid purchase price.", parent=dialog)
            return
            
        # Calculate new total amount
        new_total_amount = holding['amount'] + amount
        
        # Calculate weighted average price
        new_avg_price = calculate_weighted_average(
            holding['amount'], 
            holding['purchase_price_per_unit'],
            amount,
            price
        )
        
        # Update holding
        self.db.update_holding(
            self.user['id'],
            holding['id'],
            new_total_amount,
            new_avg_price,
            notes=notes.strip() if notes else None
        )
        
        # Record transaction
        self.db.add_transaction(
            self.user['id'],
            holding['asset_id'],
            "BUY",
            amount,
            price,
            notes.strip() if notes else None
        )
            
        messagebox.showinfo(
            "Success", 
            f"Added {amount} {holding['symbol']} at ${price}. New total: {new_total_amount}.", 
            parent=dialog
        )
        dialog.destroy()
        
        # Refresh data
        self.load_assets_data()
        if self.refresh_callback:
            self.refresh_callback()
            
    def add_staking_income(self, dialog, holding, amount_str, notes):
        """Add staking income to an existing holding."""
        try:
            # Use parse_numeric_input to handle comma decimal separators
            new_total = float(parse_numeric_input(amount_str))
            
            # Ensure the new total is greater than the current amount
            if new_total <= holding['amount']:
                messagebox.showerror("Error", "New total amount must be greater than the current amount.", parent=dialog)
                return
                
            # Calculate staking income as the difference
            staking_amount = new_total - holding['amount']
            
            # Update holding with new total
            self.db.update_holding(
                self.user['id'],
                holding['id'],
                new_total,
                notes=notes.strip() if notes else None
            )
            
            # Record transaction
            staking_notes = f"Staking income: {notes.strip()}" if notes else "Staking income"
            self.db.add_transaction(
                self.user['id'],
                holding['asset_id'],
                "STAKING",
                staking_amount,
                self.current_prices.get(holding['asset_id'], 0.0),  # Use current market price
                staking_notes
            )
                
            messagebox.showinfo(
                "Success", 
                f"Added {staking_amount:.8f} {holding['symbol']} from staking. New total: {new_total:.8f}", 
                parent=dialog
            )
            dialog.destroy()
            
            # Refresh data
            self.load_assets_data()
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.", parent=dialog)
            return
            
    def show_delete_confirmation(self, holding_id):
        """Show confirmation dialog before deleting a holding."""
        # Get holding details
        self.cursor = self.db.connection.cursor()
        self.cursor.execute("""
            SELECT h.*, a.symbol, a.name 
            FROM holdings h
            JOIN assets a ON h.asset_id = a.id
            WHERE h.id = ?
        """, (holding_id,))
        holding = self.cursor.fetchone()
        
        if not holding:
            messagebox.showerror("Error", "Holding not found.")
            return
            
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete your {holding['symbol']} holding of {holding['amount']} units? This cannot be undone."
        )
        
        if result:
            # Record transaction (SELL everything)
            self.db.add_transaction(
                self.user['id'],
                holding['asset_id'],
                "SELL",
                holding['amount'],
                holding['purchase_price_per_unit'],
                "Deleted holding"
            )
            
            # Delete holding
            success = self.db.delete_holding(self.user['id'], holding_id)
            
            if success:
                messagebox.showinfo("Success", f"Deleted {holding['symbol']} holding.")
                
                # Refresh data
                self.load_assets_data()
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", f"Failed to delete {holding['symbol']} holding. Please check the logs for details.")
        
    def on_holding_double_click(self, event):
        """Handle double-click on a holding row."""
        row_id = self.holdings_tree.identify_row(event.y)
        if not row_id:
            return
            
        # Get the holding ID from the row tags
        holding_id = self.holdings_tree.item(row_id, "tags")[0]
        
        # Get column
        col = self.holdings_tree.identify_column(event.x)
        col_idx = int(col[1:]) - 1
        
        # Check if actions column
        if col_idx == 7:  # Actions column
            # Get the x position relative to the column
            col_width = self.holdings_tree.column(self.holdings_tree["columns"][col_idx], "width")
            x_in_col = event.x - self.holdings_tree.winfo_x() - sum(self.holdings_tree.column(self.holdings_tree["columns"][i], "width") for i in range(col_idx))
            
            # Determine if clicked on Update or Delete
            if x_in_col < col_width / 2:
                self.show_update_dialog(holding_id)
            else:
                self.show_delete_confirmation(holding_id)
        else:
            self.show_update_dialog(holding_id)
            
    def show_transaction_context_menu(self, event):
        """Show context menu for a transaction."""
        # Get the row id at the event position
        row_id = self.transaction_tree.identify_row(event.y)
        if not row_id:
            return
            
        # Select the row
        self.transaction_tree.selection_set(row_id)
        
        # Create the context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit Transaction", command=lambda: self.show_edit_transaction_dialog(row_id))
        menu.add_command(label="Delete Transaction", command=lambda: self.delete_transaction(row_id))
        menu.post(event.x_root, event.y_root)
        
    def show_edit_transaction_dialog(self, row_id):
        """Show dialog to edit a transaction."""
        try:
            # Get the transaction ID from the row tags
            tags = self.transaction_tree.item(row_id, "tags")
            if not tags:
                messagebox.showerror("Error", "Could not identify transaction to edit.")
                return
            
            transaction_id = tags[0]
            
            # Get transaction details
            transaction_values = self.transaction_tree.item(row_id, "values")
            
            dialog = ctk.CTkToplevel(self)
            dialog.title("Edit Transaction")
            dialog.geometry("500x350")  # Make it tall enough for the confirmation button
            dialog.transient(self)
            dialog.resizable(True, True)  # Make the dialog resizable
            
            # Configure dialog layout
            dialog.grid_columnconfigure(0, weight=1)
            dialog.grid_rowconfigure(3, weight=1)  # Make notes area expandable
            
            # Dialog title
            title_label = ctk.CTkLabel(
                dialog,
                text="Edit Transaction",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
            
            # Transaction info
            info_frame = ctk.CTkFrame(dialog)
            info_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
            info_frame.grid_columnconfigure(1, weight=1)
            
            date_label = ctk.CTkLabel(info_frame, text="Date:", font=ctk.CTkFont(size=14))
            date_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 5), sticky="w")
            date_value = ctk.CTkLabel(info_frame, text=transaction_values[0], font=ctk.CTkFont(size=14))
            date_value.grid(row=0, column=1, padx=(0, 20), pady=(10, 5), sticky="w")
            
            type_label = ctk.CTkLabel(info_frame, text="Type:", font=ctk.CTkFont(size=14))
            type_label.grid(row=1, column=0, padx=(20, 10), pady=5, sticky="w")
            type_value = ctk.CTkLabel(info_frame, text=transaction_values[1], font=ctk.CTkFont(size=14))
            type_value.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="w")
            
            asset_label = ctk.CTkLabel(info_frame, text="Asset:", font=ctk.CTkFont(size=14))
            asset_label.grid(row=2, column=0, padx=(20, 10), pady=5, sticky="w")
            asset_value = ctk.CTkLabel(info_frame, text=transaction_values[2], font=ctk.CTkFont(size=14))
            asset_value.grid(row=2, column=1, padx=(0, 20), pady=5, sticky="w")
            
            amount_label = ctk.CTkLabel(info_frame, text="Amount:", font=ctk.CTkFont(size=14))
            amount_label.grid(row=3, column=0, padx=(20, 10), pady=5, sticky="w")
            amount_value = ctk.CTkLabel(info_frame, text=transaction_values[3], font=ctk.CTkFont(size=14))
            amount_value.grid(row=3, column=1, padx=(0, 20), pady=5, sticky="w")
            
            price_label = ctk.CTkLabel(info_frame, text="Price:", font=ctk.CTkFont(size=14))
            price_label.grid(row=4, column=0, padx=(20, 10), pady=5, sticky="w")
            price_value = ctk.CTkLabel(info_frame, text=transaction_values[4], font=ctk.CTkFont(size=14))
            price_value.grid(row=4, column=1, padx=(0, 20), pady=5, sticky="w")
            
            total_label = ctk.CTkLabel(info_frame, text="Total Value:", font=ctk.CTkFont(size=14))
            total_label.grid(row=5, column=0, padx=(20, 10), pady=(5, 10), sticky="w")
            total_value = ctk.CTkLabel(info_frame, text=transaction_values[5], font=ctk.CTkFont(size=14))
            total_value.grid(row=5, column=1, padx=(0, 20), pady=(5, 10), sticky="w")
            
            # Notes entry
            notes_frame = ctk.CTkFrame(dialog)
            notes_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="nsew")
            notes_frame.grid_columnconfigure(0, weight=1)
            notes_frame.grid_rowconfigure(1, weight=1)
            
            notes_label = ctk.CTkLabel(
                notes_frame,
                text="Notes:",
                font=ctk.CTkFont(size=14)
            )
            notes_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
            
            notes_entry = ctk.CTkTextbox(
                notes_frame,
                width=460,
                height=100
            )
            notes_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
            
            # Pre-fill with existing notes
            if transaction_values[6]:
                notes_entry.insert("0.0", transaction_values[6])
            
            # Buttons
            button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            button_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
            
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                fg_color="gray",
                width=180
            )
            cancel_button.grid(row=0, column=0, padx=(20, 10), pady=0, sticky="e")
            
            save_button = ctk.CTkButton(
                button_frame,
                text="Save Changes",
                command=lambda: self.update_transaction(
                    dialog,
                    transaction_id,
                    notes_entry.get("0.0", "end")
                ),
                width=180
            )
            save_button.grid(row=0, column=1, padx=(10, 20), pady=0, sticky="w")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while opening edit dialog: {str(e)}")
    
    def update_transaction(self, dialog, transaction_id, notes):
        """Update a transaction in the database."""
        try:
            # Update the transaction
            success = self.db.update_transaction(
                transaction_id,
                self.user['id'],
                notes.strip() if notes else None
            )
            
            if success:
                messagebox.showinfo("Success", "Transaction updated successfully.", parent=dialog)
                dialog.destroy()
                # Refresh data
                self.load_assets_data()
                # Notify parent to refresh other components
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to update transaction. Please try again.", parent=dialog)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating transaction: {str(e)}", parent=dialog)
        
    def delete_transaction(self, row_id):
        """Delete a transaction from the database."""
        try:
            # Get the transaction ID from the row tags
            tags = self.transaction_tree.item(row_id, "tags")
            if not tags:
                messagebox.showerror("Error", "Could not identify transaction to delete.")
                return
            
            transaction_id = tags[0]
            
            # Get confirmation from the user
            result = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this transaction? This cannot be undone.")
            
            if result:
                # Delete the transaction from the database
                success = self.db.delete_transaction(transaction_id, self.user['id'])
                
                if success:
                    messagebox.showinfo("Success", "Transaction deleted successfully.")
                    # Refresh data
                    self.load_assets_data()
                    # Notify parent to refresh other components
                    if self.refresh_callback:
                        self.refresh_callback()
                else:
                    messagebox.showerror("Error", "Failed to delete transaction. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting transaction: {str(e)}")
        
    def on_transaction_double_click(self, event):
        """Handle double-click on a transaction row."""
        row_id = self.transaction_tree.identify_row(event.y)
        if not row_id:
            return
            
        # Get column
        col = self.transaction_tree.identify_column(event.x)
        col_idx = int(col[1:]) - 1
        
        # Check which column was clicked
        if col_idx == 7:  # Actions column (Delete)
            self.delete_transaction(row_id)
        elif col_idx == 6:  # Notes column
            self.show_edit_transaction_dialog(row_id)
        else:
            # For any other column, show edit dialog
            self.show_edit_transaction_dialog(row_id)
            
    def import_csv(self):
        """Import holdings from a CSV file."""
        file_path = filedialog.askopenfilename(
            title="Import CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
            
        results = parse_csv_data(file_path, self.user['id'], self.db)
        
        # Show results
        success_count = len(results["success"])
        error_count = len(results["errors"])
        
        if success_count > 0:
            success_msg = "\n".join(results["success"][:5])
            if len(results["success"]) > 5:
                success_msg += f"\n...and {len(results["success"]) - 5} more"
                
            messagebox.showinfo("Import Successful", f"Successfully imported {success_count} assets:\n\n{success_msg}")
            
            # Refresh data
            self.load_assets_data()
            if self.refresh_callback:
                self.refresh_callback()
        
        if error_count > 0:
            error_msg = "\n".join(results["errors"][:5])
            if len(results["errors"]) > 5:
                error_msg += f"\n...and {len(results["errors"]) - 5} more"
                
            messagebox.showerror("Import Errors", f"Encountered {error_count} errors:\n\n{error_msg}")
            
    def refresh_data(self):
        """Refresh price data from API."""
        # Call the parent's refresh callback
        if self.refresh_callback:
            self.refresh_callback()
            
        # Reload asset data
        self.load_assets_data() 
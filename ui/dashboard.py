import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils import format_currency, format_percentage, embed_chart, create_pie_chart

class PortfolioDashboard(ctk.CTkFrame):
    def __init__(self, master, user, db, api, refresh_callback):
        """Initialize the dashboard."""
        super().__init__(master)
        self.master = master
        self.user = user
        self.db = db
        self.api = api
        self.refresh_callback = refresh_callback
        self.current_prices = {}
        
        # Configure layout
        self.grid_rowconfigure(0, weight=0)  # Welcome banner
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_columnconfigure(0, weight=1)
        
        # Create welcome banner
        self.create_welcome_banner()
        
        # Create content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure content grid
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        
        # Create left panel - Portfolio Summary
        self.create_portfolio_summary()
        
        # Create right panel - Portfolio Chart
        self.create_portfolio_chart()
        
        # Load data
        self.load_portfolio_data()
        
    def create_welcome_banner(self):
        """Create welcome banner with user info and portfolio summary."""
        self.banner_frame = ctk.CTkFrame(self, fg_color=("#4b6584", "#2d3436"))
        self.banner_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Configure banner layout
        self.banner_frame.grid_columnconfigure(0, weight=1)
        self.banner_frame.grid_columnconfigure(1, weight=0)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.banner_frame,
            text=f"Welcome back, {self.user['username']}!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f5f6fa"
        )
        self.welcome_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Last updated time
        self.last_updated_label = ctk.CTkLabel(
            self.banner_frame,
            text="Last updated: Never",
            font=ctk.CTkFont(size=12),
            text_color="#dcdde1"
        )
        self.last_updated_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.banner_frame,
            text="Refresh Prices",
            command=self.refresh_data,
            width=120
        )
        self.refresh_button.grid(row=0, column=1, rowspan=2, padx=20, pady=10, sticky="e")
        
    def create_portfolio_summary(self):
        """Create portfolio summary panel."""
        self.summary_frame = ctk.CTkFrame(self.content_frame)
        self.summary_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        # Configure summary layout
        self.summary_frame.grid_rowconfigure(0, weight=0)  # Title
        self.summary_frame.grid_rowconfigure(1, weight=1)  # Content
        self.summary_frame.grid_columnconfigure(0, weight=1)
        
        # Summary title
        self.summary_title = ctk.CTkLabel(
            self.summary_frame,
            text="Portfolio Summary",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.summary_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Summary content
        self.summary_content = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.summary_content.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure summary content layout
        self.summary_content.grid_columnconfigure(0, weight=1)
        
        # Total portfolio value
        self.total_value_frame = ctk.CTkFrame(self.summary_content, fg_color=("#4b6584", "#2d3436"))
        self.total_value_frame.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        
        self.total_value_label = ctk.CTkLabel(
            self.total_value_frame,
            text="Total Portfolio Value",
            font=ctk.CTkFont(size=14),
            text_color="#dcdde1"
        )
        self.total_value_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.total_value_amount = ctk.CTkLabel(
            self.total_value_frame,
            text="$0.00",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f5f6fa"
        )
        self.total_value_amount.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # 24h change
        self.change_frame = ctk.CTkFrame(self.summary_content, fg_color=("#4b6584", "#2d3436"))
        self.change_frame.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="ew")
        
        self.change_label = ctk.CTkLabel(
            self.change_frame,
            text="24h Change",
            font=ctk.CTkFont(size=14),
            text_color="#dcdde1"
        )
        self.change_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.change_amount = ctk.CTkLabel(
            self.change_frame,
            text="$0.00 (0.00%)",
            font=ctk.CTkFont(size=18),
            text_color="#f5f6fa"
        )
        self.change_amount.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Assets owned
        self.assets_frame = ctk.CTkFrame(self.summary_content, fg_color=("#4b6584", "#2d3436"))
        self.assets_frame.grid(row=2, column=0, padx=0, pady=(0, 10), sticky="ew")
        
        self.assets_label = ctk.CTkLabel(
            self.assets_frame,
            text="Assets Owned",
            font=ctk.CTkFont(size=14),
            text_color="#dcdde1"
        )
        self.assets_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.assets_count = ctk.CTkLabel(
            self.assets_frame,
            text="0",
            font=ctk.CTkFont(size=18),
            text_color="#f5f6fa"
        )
        self.assets_count.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Total profit/loss
        self.profit_frame = ctk.CTkFrame(self.summary_content, fg_color=("#4b6584", "#2d3436"))
        self.profit_frame.grid(row=3, column=0, padx=0, pady=(0, 0), sticky="ew")
        
        self.profit_label = ctk.CTkLabel(
            self.profit_frame,
            text="Total Profit/Loss",
            font=ctk.CTkFont(size=14),
            text_color="#dcdde1"
        )
        self.profit_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.profit_amount = ctk.CTkLabel(
            self.profit_frame,
            text="$0.00 (0.00%)",
            font=ctk.CTkFont(size=18),
            text_color="#f5f6fa"
        )
        self.profit_amount.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
    def create_portfolio_chart(self):
        """Create portfolio chart panel."""
        self.chart_frame = ctk.CTkFrame(self.content_frame)
        self.chart_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        
        # Configure chart layout
        self.chart_frame.grid_rowconfigure(0, weight=0)  # Title
        self.chart_frame.grid_rowconfigure(1, weight=1)  # Content
        self.chart_frame.grid_columnconfigure(0, weight=1)
        
        # Chart title
        self.chart_title = ctk.CTkLabel(
            self.chart_frame,
            text="Portfolio Distribution",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.chart_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Chart content
        self.chart_content = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        self.chart_content.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Placeholder text
        self.chart_placeholder = ctk.CTkLabel(
            self.chart_content,
            text="No assets found. Add assets to view portfolio distribution.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.chart_placeholder.pack(expand=True)
        
    def load_portfolio_data(self):
        """Load portfolio data from database."""
        # Get user holdings
        holdings_data = self.db.get_user_holdings(self.user['id'])
        holdings = [holding for holding in holdings_data]
        
        if not holdings:
            return
            
        # Get latest prices for all assets
        asset_ids = [holding['asset_id'] for holding in holdings]
        self.current_prices = {}
        
        for asset_id in asset_ids:
            price_data = self.db.get_latest_price(asset_id)
            if price_data:
                self.current_prices[asset_id] = price_data['price_usd']
        
        # Calculate total portfolio value
        total_value = 0
        cost_basis = 0
        
        for holding in holdings:
            price = self.current_prices.get(holding['asset_id'], 0)
            amount = holding['amount']
            value = amount * price
            purchase_value = amount * holding['purchase_price_per_unit']
            
            total_value += value
            cost_basis += purchase_value
        
        # Update UI
        self.total_value_amount.configure(text=format_currency(total_value))
        self.assets_count.configure(text=str(len(holdings)))
        
        # Calculate profit/loss
        profit_loss = total_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0
        
        profit_text = f"{format_currency(profit_loss)} ({format_percentage(profit_loss_pct)})"
        profit_color = "#2ecc71" if profit_loss >= 0 else "#e74c3c"  # Green if positive, red if negative
        
        self.profit_amount.configure(text=profit_text, text_color=profit_color)
        
        # For 24h change, we need historical data, but for now just show a placeholder
        self.change_amount.configure(text="N/A")
        
        # Update last updated time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated_label.configure(text=f"Last updated: {now}")
        
        # Update chart
        self.update_chart(holdings)
        
    def update_chart(self, holdings):
        """Update portfolio distribution chart."""
        # Clear chart content
        for widget in self.chart_content.winfo_children():
            widget.destroy()
        
        # Create pie chart
        fig = create_pie_chart(holdings, self.current_prices)
        
        if fig:
            chart_widget = embed_chart(fig, self.chart_content)
            chart_widget.pack(fill="both", expand=True)
        else:
            # Show placeholder if no chart data
            self.chart_placeholder = ctk.CTkLabel(
                self.chart_content,
                text="No assets found. Add assets to view portfolio distribution.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            self.chart_placeholder.pack(expand=True)
            
    def refresh_data(self):
        """Refresh price data from API."""
        # Call the parent's refresh callback
        if self.refresh_callback:
            self.refresh_callback()
            
        # Reload dashboard data
        self.load_portfolio_data() 
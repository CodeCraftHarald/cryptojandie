import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime, timedelta
import tkinter as tk
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from utils import format_currency, format_percentage, embed_chart, create_pie_chart, create_bar_chart

class AnalysisDashboard(ctk.CTkFrame):
    def __init__(self, master, user, db, api):
        """Initialize the analysis dashboard screen."""
        super().__init__(master)
        self.master = master
        self.user = user
        self.db = db
        self.api = api
        self.current_prices = {}
        self.holdings = []
        
        # Configure layout
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_columnconfigure(0, weight=1)
        
        # Create title
        self.create_title()
        
        # Create content area with charts
        self.create_content()
        
        # Load data
        self.load_data()
        
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
            text="Portfolio Analysis",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.title_frame,
            text="Refresh Data",
            command=self.load_data,
            width=120
        )
        self.refresh_button.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="e")
        
    def create_content(self):
        """Create content area with multiple charts."""
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure content layout
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Portfolio Overview Section
        self.overview_label = ctk.CTkLabel(
            self.content_frame,
            text="Portfolio Overview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.overview_label.grid(row=0, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Summary cards
        self.summary_frame = ctk.CTkFrame(self.content_frame)
        self.summary_frame.grid(row=1, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Configure summary layout
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)
        self.summary_frame.grid_columnconfigure(2, weight=1)
        self.summary_frame.grid_columnconfigure(3, weight=1)
        
        # Create summary cards
        self.create_summary_card(0, "Total Value", "$0.00")
        self.create_summary_card(1, "Total Assets", "0")
        self.create_summary_card(2, "Total Profit/Loss", "$0.00 (0.00%)")
        self.create_summary_card(3, "Most Valuable Asset", "None")
        
        # Allocation Section
        self.allocation_label = ctk.CTkLabel(
            self.content_frame,
            text="Portfolio Allocation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.allocation_label.grid(row=2, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Allocation charts frame
        self.allocation_frame = ctk.CTkFrame(self.content_frame)
        self.allocation_frame.grid(row=3, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Configure allocation layout
        self.allocation_frame.grid_columnconfigure(0, weight=1)
        self.allocation_frame.grid_columnconfigure(1, weight=1)
        self.allocation_frame.grid_rowconfigure(0, weight=1)
        
        # Placeholder for pie chart
        self.pie_chart_frame = ctk.CTkFrame(self.allocation_frame, height=300)
        self.pie_chart_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Placeholder for bar chart
        self.bar_chart_frame = ctk.CTkFrame(self.allocation_frame, height=300)
        self.bar_chart_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        # Performance Metrics Section
        self.performance_label = ctk.CTkLabel(
            self.content_frame,
            text="Performance Metrics",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.performance_label.grid(row=4, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Performance table frame
        self.performance_frame = ctk.CTkFrame(self.content_frame)
        self.performance_frame.grid(row=5, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Create treeview for performance data
        self.create_performance_table()
        
        # Risk Analysis Section
        self.risk_label = ctk.CTkLabel(
            self.content_frame,
            text="Risk Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.risk_label.grid(row=6, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Risk analysis frame
        self.risk_frame = ctk.CTkFrame(self.content_frame, height=300)
        self.risk_frame.grid(row=7, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Diversification Score
        self.diversification_frame = ctk.CTkFrame(self.risk_frame)
        self.diversification_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Diversification label
        self.diversification_label = ctk.CTkLabel(
            self.diversification_frame,
            text="Portfolio Diversification Score",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.diversification_label.pack(pady=(10, 5))
        
        # Diversification score
        self.diversification_score = ctk.CTkLabel(
            self.diversification_frame,
            text="0/10",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#4b6584"
        )
        self.diversification_score.pack(pady=(0, 5))
        
        # Diversification description
        self.diversification_desc = ctk.CTkLabel(
            self.diversification_frame,
            text="Your portfolio needs diversification. Consider adding more assets.",
            font=ctk.CTkFont(size=12),
            wraplength=600
        )
        self.diversification_desc.pack(pady=(0, 10))
        
        # Staking Analysis Section
        self.staking_label = ctk.CTkLabel(
            self.content_frame,
            text="Staking Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.staking_label.grid(row=8, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Staking summary cards
        self.staking_summary_frame = ctk.CTkFrame(self.content_frame)
        self.staking_summary_frame.grid(row=9, column=0, padx=0, pady=(0, 10), sticky="ew")
        
        # Configure staking summary layout
        self.staking_summary_frame.grid_columnconfigure(0, weight=1)
        self.staking_summary_frame.grid_columnconfigure(1, weight=1)
        self.staking_summary_frame.grid_columnconfigure(2, weight=1)
        
        # Create staking summary cards
        self.create_summary_card_in_frame(self.staking_summary_frame, 0, "Total Staking Income", "$0.00")
        self.create_summary_card_in_frame(self.staking_summary_frame, 1, "Monthly Average", "$0.00")
        self.create_summary_card_in_frame(self.staking_summary_frame, 2, "Estimated Annual Yield", "0.00%")
        
        # Staking charts frame
        self.staking_charts_frame = ctk.CTkFrame(self.content_frame)
        self.staking_charts_frame.grid(row=10, column=0, padx=0, pady=(0, 10), sticky="ew")
        
        # Configure staking charts layout
        self.staking_charts_frame.grid_columnconfigure(0, weight=1)
        self.staking_charts_frame.grid_columnconfigure(1, weight=1)
        self.staking_charts_frame.grid_rowconfigure(0, weight=1)
        
        # Placeholder for staking history chart
        self.staking_history_frame = ctk.CTkFrame(self.staking_charts_frame, height=300)
        self.staking_history_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Placeholder for staking forecast chart
        self.staking_forecast_frame = ctk.CTkFrame(self.staking_charts_frame, height=300)
        self.staking_forecast_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        # Staking details table frame
        self.staking_details_frame = ctk.CTkFrame(self.content_frame)
        self.staking_details_frame.grid(row=11, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Create staking details table
        self.create_staking_details_table()
        
        # Recommendations Section
        self.recommendations_label = ctk.CTkLabel(
            self.content_frame,
            text="Recommendations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.recommendations_label.grid(row=12, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Recommendations frame
        self.recommendations_frame = ctk.CTkFrame(self.content_frame)
        self.recommendations_frame.grid(row=13, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Recommendations text
        self.recommendations_text = ctk.CTkTextbox(self.recommendations_frame, height=150)
        self.recommendations_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.recommendations_text.insert("0.0", "Recommendations will appear here after analyzing your portfolio.")
        self.recommendations_text.configure(state="disabled")
        
    def create_summary_card(self, column, title, value):
        """Create a summary card with title and value."""
        card = ctk.CTkFrame(self.summary_frame, fg_color=("#4b6584", "#2d3436"))
        card.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="#dcdde1"
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f5f6fa"
        )
        value_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Store reference to value label for updates
        setattr(self, f"{title.lower().replace('/', '_').replace(' ', '_')}_value", value_label)
        
    def create_performance_table(self):
        """Create performance metrics table."""
        # Create a frame to hold the treeview
        self.tree_container = tk.Frame(self.performance_frame, bg="#2b2b2b")
        self.tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create the treeview style
        style = tk.ttk.Style()
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
        
        # Create the treeview
        self.performance_tree = tk.ttk.Treeview(
            self.tree_container,
            columns=("asset", "value", "allocation", "profit_loss", "profit_loss_pct", "price"),
            show="headings",
            height=10
        )
        
        # Define columns
        self.performance_tree.heading("asset", text="Asset")
        self.performance_tree.heading("value", text="Value (USD)")
        self.performance_tree.heading("allocation", text="Allocation %")
        self.performance_tree.heading("profit_loss", text="Profit/Loss")
        self.performance_tree.heading("profit_loss_pct", text="Profit/Loss %")
        self.performance_tree.heading("price", text="Current Price")
        
        # Column widths
        self.performance_tree.column("asset", width=150, anchor="w")
        self.performance_tree.column("value", width=100, anchor="e")
        self.performance_tree.column("allocation", width=100, anchor="e")
        self.performance_tree.column("profit_loss", width=120, anchor="e")
        self.performance_tree.column("profit_loss_pct", width=100, anchor="e")
        self.performance_tree.column("price", width=120, anchor="e")
        
        # Pack the treeview
        self.performance_tree.pack(fill="both", expand=True)
        
    def create_summary_card_in_frame(self, parent_frame, column, title, value):
        """Create a summary card with title and value in a specific frame."""
        card = ctk.CTkFrame(parent_frame, fg_color=("#4b6584", "#2d3436"))
        card.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="#dcdde1"
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f5f6fa"
        )
        value_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Store reference to value label for updates
        var_name = f"{title.lower().replace('/', '_').replace(' ', '_')}_value"
        setattr(self, var_name, value_label)

    def create_staking_details_table(self):
        """Create staking details table."""
        # Create a frame to hold the treeview
        self.staking_tree_container = tk.Frame(self.staking_details_frame, bg="#2b2b2b")
        self.staking_tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create the treeview style
        style = tk.ttk.Style()
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
        
        # Create the treeview
        self.staking_tree = tk.ttk.Treeview(
            self.staking_tree_container,
            columns=("asset", "total_rewards", "last_reward", "avg_monthly", "estimated_apy"),
            show="headings",
            height=5
        )
        
        # Define columns
        self.staking_tree.heading("asset", text="Asset")
        self.staking_tree.heading("total_rewards", text="Total Rewards")
        self.staking_tree.heading("last_reward", text="Last Reward")
        self.staking_tree.heading("avg_monthly", text="Monthly Average")
        self.staking_tree.heading("estimated_apy", text="Est. APY")
        
        # Column widths
        self.staking_tree.column("asset", width=150, anchor="w")
        self.staking_tree.column("total_rewards", width=120, anchor="e")
        self.staking_tree.column("last_reward", width=120, anchor="e")
        self.staking_tree.column("avg_monthly", width=120, anchor="e")
        self.staking_tree.column("estimated_apy", width=120, anchor="e")
        
        # Create scrollbar
        staking_scrollbar = tk.Scrollbar(self.staking_tree_container, orient="vertical", command=self.staking_tree.yview)
        self.staking_tree.configure(yscrollcommand=staking_scrollbar.set)
        staking_scrollbar.pack(side="right", fill="y")
        
        # Pack the treeview
        self.staking_tree.pack(fill="both", expand=True)
        
    def load_data(self):
        """Load and analyze portfolio data."""
        # Get user holdings
        holdings_data = self.db.get_user_holdings(self.user['id'])
        
        if not holdings_data:
            self.show_no_data_message()
            return
            
        # Get latest prices for all assets
        asset_ids = [holding['asset_id'] for holding in holdings_data]
        self.current_prices = {}
        
        for asset_id in asset_ids:
            price_data = self.db.get_latest_price(asset_id)
            if price_data:
                self.current_prices[asset_id] = price_data['price_usd']
        
        # Process holdings data
        self.holdings = []
        total_value = 0
        total_cost = 0
        
        for holding in holdings_data:
            price = self.current_prices.get(holding['asset_id'], 0)
            amount = holding['amount']
            purchase_price = holding['purchase_price_per_unit']
            
            value = amount * price
            cost = amount * purchase_price
            profit_loss = value - cost
            profit_loss_pct = (profit_loss / cost) * 100 if cost > 0 else 0
            
            holding_data = {
                "id": holding['id'],
                "asset_id": holding['asset_id'],
                "symbol": holding['symbol'],
                "name": holding['name'],
                "amount": amount,
                "price": price,
                "value": value,
                "purchase_price": purchase_price,
                "cost": cost,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "market_cap": holding['market_cap'] or 0
            }
            
            self.holdings.append(holding_data)
            total_value += value
            total_cost += cost
        
        # Sort holdings by value (descending)
        self.holdings.sort(key=lambda h: h["value"], reverse=True)
        
        # Calculate allocation percentages
        for holding in self.holdings:
            holding["allocation"] = (holding["value"] / total_value) * 100 if total_value > 0 else 0
        
        # Update UI
        self.update_summary(total_value, len(self.holdings), total_value - total_cost, 
                           ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0)
        self.update_charts()
        self.update_performance_table()
        
        # Load and analyze staking data
        self.load_staking_data()
        
        self.analyze_portfolio()
        
    def load_staking_data(self):
        """Load and analyze staking transaction data."""
        if not self.user:
            return
            
        # Get all staking transactions for this user
        self.cursor = self.db.connection.cursor()
        self.cursor.execute("""
            SELECT t.*, a.symbol, a.name 
            FROM transactions t
            JOIN assets a ON t.asset_id = a.id
            WHERE t.user_id = ? AND t.transaction_type = 'STAKING'
            ORDER BY t.timestamp
        """, (self.user['id'],))
        
        staking_transactions = [dict(row) for row in self.cursor.fetchall()]
        
        if not staking_transactions:
            self.show_no_staking_data_message()
            return
            
        # Process staking data
        total_staking_income = 0
        staking_by_asset = {}
        staking_by_month = {}
        
        for tx in staking_transactions:
            asset_id = tx['asset_id']
            symbol = tx['symbol']
            amount = tx['amount']
            timestamp = datetime.fromisoformat(tx['timestamp'])
            month_key = timestamp.strftime("%Y-%m")
            
            # Current value of this staking reward
            current_price = self.current_prices.get(asset_id, 0)
            current_value = amount * current_price
            total_staking_income += current_value
            
            # Aggregate by asset
            if asset_id not in staking_by_asset:
                staking_by_asset[asset_id] = {
                    'symbol': symbol,
                    'name': tx['name'],
                    'total_amount': 0,
                    'total_value': 0,
                    'transactions': [],
                    'last_timestamp': None
                }
            
            staking_by_asset[asset_id]['total_amount'] += amount
            staking_by_asset[asset_id]['total_value'] += current_value
            staking_by_asset[asset_id]['transactions'].append(tx)
            
            # Track the most recent staking timestamp
            if (staking_by_asset[asset_id]['last_timestamp'] is None or 
                timestamp > datetime.fromisoformat(staking_by_asset[asset_id]['last_timestamp'])):
                staking_by_asset[asset_id]['last_timestamp'] = tx['timestamp']
            
            # Aggregate by month
            if month_key not in staking_by_month:
                staking_by_month[month_key] = {
                    'total_value': 0,
                    'by_asset': {}
                }
            
            staking_by_month[month_key]['total_value'] += current_value
            
            if asset_id not in staking_by_month[month_key]['by_asset']:
                staking_by_month[month_key]['by_asset'][asset_id] = {
                    'symbol': symbol,
                    'amount': 0,
                    'value': 0
                }
            
            staking_by_month[month_key]['by_asset'][asset_id]['amount'] += amount
            staking_by_month[month_key]['by_asset'][asset_id]['value'] += current_value
        
        # Calculate average monthly staking income
        months_with_staking = len(staking_by_month)
        avg_monthly_income = total_staking_income / months_with_staking if months_with_staking > 0 else 0
        
        # Calculate APY estimates for each asset
        for asset_id, data in staking_by_asset.items():
            holding = next((h for h in self.holdings if h['asset_id'] == asset_id), None)
            if holding:
                # Calculate APY based on current holdings and staking rewards
                total_staked_amount = holding['amount']
                monthly_staking_amount = self.calculate_monthly_average_staking(data['transactions'])
                
                if total_staked_amount > 0 and monthly_staking_amount > 0:
                    # Calculate annual yield: (Monthly rewards * 12) / Total staked amount
                    monthly_staking_value = monthly_staking_amount * self.current_prices.get(asset_id, 0)
                    annual_staking_value = monthly_staking_value * 12
                    total_staked_value = total_staked_amount * self.current_prices.get(asset_id, 0)
                    estimated_apy = (annual_staking_value / total_staked_value) * 100 if total_staked_value > 0 else 0
                    
                    staking_by_asset[asset_id]['apy'] = estimated_apy
                else:
                    staking_by_asset[asset_id]['apy'] = 0
            else:
                staking_by_asset[asset_id]['apy'] = 0
        
        # Store staking data
        self.staking_data = {
            'total_income': total_staking_income,
            'monthly_average': avg_monthly_income,
            'by_asset': staking_by_asset,
            'by_month': staking_by_month,
            'transactions': staking_transactions
        }
        
        # Update staking UI
        self.update_staking_summary(total_staking_income, avg_monthly_income)
        self.update_staking_charts()
        self.update_staking_table()
        
    def calculate_monthly_average_staking(self, transactions):
        """Calculate the average monthly staking amount for a set of transactions."""
        if not transactions:
            return 0
            
        # Group transactions by month
        by_month = {}
        for tx in transactions:
            timestamp = datetime.fromisoformat(tx['timestamp'])
            month_key = timestamp.strftime("%Y-%m")
            
            if month_key not in by_month:
                by_month[month_key] = 0
                
            by_month[month_key] += tx['amount']
        
        # Calculate average
        total_amount = sum(by_month.values())
        num_months = len(by_month)
        
        return total_amount / num_months if num_months > 0 else 0
        
    def show_no_staking_data_message(self):
        """Show message when no staking data is available."""
        # Update staking summary
        self.total_staking_income_value.configure(text="$0.00")
        self.monthly_average_value.configure(text="$0.00")
        self.estimated_annual_yield_value.configure(text="0.00%")
        
        # Clear staking charts
        for widget in self.staking_history_frame.winfo_children():
            widget.destroy()
        for widget in self.staking_forecast_frame.winfo_children():
            widget.destroy()
            
        # Add messages to chart frames
        no_data_label1 = ctk.CTkLabel(
            self.staking_history_frame,
            text="No staking data available.\nAdd staking income transactions to see analysis.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        no_data_label1.pack(expand=True)
        
        no_data_label2 = ctk.CTkLabel(
            self.staking_forecast_frame,
            text="No staking forecast available.\nAdd staking income to generate forecasts.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        no_data_label2.pack(expand=True)
        
        # Clear staking table
        for item in self.staking_tree.get_children():
            self.staking_tree.delete(item)
            
    def update_staking_summary(self, total_income, monthly_average):
        """Update staking summary cards with current data."""
        # Calculate average APY across all assets
        if hasattr(self, 'staking_data') and 'by_asset' in self.staking_data:
            apy_values = [data.get('apy', 0) for data in self.staking_data['by_asset'].values()]
            avg_apy = sum(apy_values) / len(apy_values) if apy_values else 0
        else:
            avg_apy = 0
            
        # Update summary cards
        self.total_staking_income_value.configure(text=format_currency(total_income))
        self.monthly_average_value.configure(text=format_currency(monthly_average))
        self.estimated_annual_yield_value.configure(text=format_percentage(avg_apy))
        
    def update_staking_charts(self):
        """Update staking charts with current data."""
        # Clear existing charts
        for widget in self.staking_history_frame.winfo_children():
            widget.destroy()
        for widget in self.staking_forecast_frame.winfo_children():
            widget.destroy()
            
        if not hasattr(self, 'staking_data') or not self.staking_data:
            return
            
        # Create historical staking chart
        staking_history_fig = self.create_staking_history_chart(width=400, height=300)
        if staking_history_fig:
            staking_history = embed_chart(staking_history_fig, self.staking_history_frame)
            staking_history.pack(fill="both", expand=True)
            
            history_title = ctk.CTkLabel(
                self.staking_history_frame,
                text="Staking Rewards History",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            history_title.pack(side="top", pady=(10, 0))
            
        # Create staking forecast chart
        staking_forecast_fig = self.create_staking_forecast_chart(width=400, height=300)
        if staking_forecast_fig:
            staking_forecast = embed_chart(staking_forecast_fig, self.staking_forecast_frame)
            staking_forecast.pack(fill="both", expand=True)
            
            forecast_title = ctk.CTkLabel(
                self.staking_forecast_frame,
                text="Staking Income Forecast (12 Months)",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            forecast_title.pack(side="top", pady=(10, 0))
            
    def create_staking_history_chart(self, width=800, height=500):
        """Create a time series chart for staking rewards history."""
        if not hasattr(self, 'staking_data') or not self.staking_data:
            return None
            
        # Prepare data
        months = sorted(self.staking_data['by_month'].keys())
        values = [self.staking_data['by_month'][month]['total_value'] for month in months]
        
        # Add current month if not in data
        current_month = datetime.now().strftime("%Y-%m")
        if current_month not in months:
            months.append(current_month)
            values.append(0)
            
        # Format month labels
        month_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months]
        
        # Create figure
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create line chart
        ax.plot(month_labels, values, marker='o', linestyle='-', color='#3498db', linewidth=2)
        
        # Add value labels
        for i, v in enumerate(values):
            ax.text(i, v, f"${v:.0f}", ha='center', va='bottom', fontsize=8)
        
        # Format
        ax.set_title('Staking Rewards Over Time', fontsize=14)
        ax.set_xlabel('Month')
        ax.set_ylabel('Value (USD)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        
        return fig
        
    def create_staking_forecast_chart(self, width=800, height=500):
        """Create a forecast chart for future staking rewards."""
        if not hasattr(self, 'staking_data') or not self.staking_data:
            return None
            
        # Get current monthly average
        monthly_avg = self.staking_data.get('monthly_average', 0)
        
        if monthly_avg <= 0:
            return None
            
        # Generate forecast for next 12 months
        months = []
        forecast_values = []
        cumulative_values = []
        cumulative_total = 0
        
        current_date = datetime.now()
        for i in range(12):
            next_month = current_date + timedelta(days=30 * (i + 1))
            month_label = next_month.strftime("%b %Y")
            months.append(month_label)
            
            # Simple forecast model using the monthly average
            # In a more sophisticated model, you could apply growth rates or seasonality
            forecast_value = monthly_avg
            forecast_values.append(forecast_value)
            
            cumulative_total += forecast_value
            cumulative_values.append(cumulative_total)
        
        # Create figure
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create bar chart for monthly forecast
        ax.bar(months, forecast_values, color='#2ecc71', alpha=0.6, label='Monthly Income')
        
        # Create line chart for cumulative income
        ax2 = ax.twinx()
        ax2.plot(months, cumulative_values, marker='o', linestyle='-', color='#e74c3c', linewidth=2, label='Cumulative Income')
        
        # Format
        ax.set_title('Forecasted Staking Income', fontsize=14)
        ax.set_xlabel('Month')
        ax.set_ylabel('Monthly Income (USD)')
        ax2.set_ylabel('Cumulative Income (USD)')
        ax.tick_params(axis='x', rotation=45)
        
        # Add legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        fig.tight_layout()
        
        return fig
        
    def update_staking_table(self):
        """Update staking details table with current data."""
        # Clear existing data
        for item in self.staking_tree.get_children():
            self.staking_tree.delete(item)
            
        if not hasattr(self, 'staking_data') or not self.staking_data:
            return
            
        # Add staking data by asset
        for asset_id, data in self.staking_data['by_asset'].items():
            symbol = data['symbol']
            name = data['name']
            total_amount = data['total_amount']
            last_timestamp = datetime.fromisoformat(data['last_timestamp']).strftime("%Y-%m-%d")
            
            # Calculate average monthly rewards
            monthly_avg = self.calculate_monthly_average_staking(data['transactions'])
            monthly_value = monthly_avg * self.current_prices.get(asset_id, 0)
            
            # Get estimated APY
            estimated_apy = data.get('apy', 0)
            
            self.staking_tree.insert(
                "",
                "end",
                values=(
                    f"{symbol} ({name})",
                    f"{total_amount:.8f} {symbol}",
                    f"{last_timestamp}",
                    format_currency(monthly_value),
                    format_percentage(estimated_apy)
                )
            )

    def show_no_data_message(self):
        """Show message when no holdings data is available."""
        # Clear existing data
        self.update_summary(0, 0, 0, 0)
        
        # Clear charts
        for widget in self.pie_chart_frame.winfo_children():
            widget.destroy()
        for widget in self.bar_chart_frame.winfo_children():
            widget.destroy()
            
        # Add messages to chart frames
        no_data_label1 = ctk.CTkLabel(
            self.pie_chart_frame,
            text="No portfolio data available.\nAdd assets to see analysis.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        no_data_label1.pack(expand=True)
        
        no_data_label2 = ctk.CTkLabel(
            self.bar_chart_frame,
            text="No portfolio data available.\nAdd assets to see analysis.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        no_data_label2.pack(expand=True)
        
        # Clear performance table
        for item in self.performance_tree.get_children():
            self.performance_tree.delete(item)
            
        # Show no staking data message
        self.show_no_staking_data_message()
            
        # Update diversification score
        self.diversification_score.configure(text="0/10")
        self.diversification_desc.configure(
            text="Your portfolio is empty. Add assets to see diversification analysis."
        )
        
        # Update recommendations
        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("0.0", "end")
        self.recommendations_text.insert("0.0", "Add assets to your portfolio to receive recommendations.")
        self.recommendations_text.configure(state="disabled")

    def update_summary(self, total_value, asset_count, total_profit, total_profit_pct):
        """Update summary cards with current data."""
        self.total_value_value.configure(text=format_currency(total_value))
        self.total_assets_value.configure(text=str(asset_count))
        
        profit_text = f"{format_currency(total_profit)} ({format_percentage(total_profit_pct)})"
        profit_color = "#2ecc71" if total_profit >= 0 else "#e74c3c"
        self.total_profit_loss_value.configure(text=profit_text, text_color=profit_color)
        
        if self.holdings:
            top_asset = self.holdings[0]
            top_asset_text = f"{top_asset['symbol']} ({format_currency(top_asset['value'])})"
            self.most_valuable_asset_value.configure(text=top_asset_text)
        else:
            self.most_valuable_asset_value.configure(text="None")
            
    def update_charts(self):
        """Update portfolio charts."""
        # Clear existing charts
        for widget in self.pie_chart_frame.winfo_children():
            widget.destroy()
        for widget in self.bar_chart_frame.winfo_children():
            widget.destroy()
            
        if not self.holdings:
            return
            
        # Create pie chart for allocation
        pie_fig = create_pie_chart(self.holdings, self.current_prices, width=400, height=300)
        if pie_fig:
            pie_chart = embed_chart(pie_fig, self.pie_chart_frame)
            pie_chart.pack(fill="both", expand=True)
            
            pie_title = ctk.CTkLabel(
                self.pie_chart_frame,
                text="Asset Allocation",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            pie_title.pack(side="top", pady=(10, 0))
        
        # Create bar chart for asset values
        bar_fig = create_bar_chart(self.holdings, self.current_prices, width=400, height=300)
        if bar_fig:
            bar_chart = embed_chart(bar_fig, self.bar_chart_frame)
            bar_chart.pack(fill="both", expand=True)
            
            bar_title = ctk.CTkLabel(
                self.bar_chart_frame,
                text="Top Assets by Value",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            bar_title.pack(side="top", pady=(10, 0))
            
    def update_performance_table(self):
        """Update performance metrics table."""
        # Clear existing data
        for item in self.performance_tree.get_children():
            self.performance_tree.delete(item)
            
        if not self.holdings:
            return
            
        # Add holdings to table
        for holding in self.holdings:
            item_id = self.performance_tree.insert(
                "",
                "end",
                values=(
                    f"{holding['symbol']} ({holding['name']})",
                    format_currency(holding['value']),
                    format_percentage(holding['allocation']),
                    format_currency(holding['profit_loss']),
                    format_percentage(holding['profit_loss_pct']),
                    format_currency(holding['price'])
                ),
                tags=(
                    "profit" if holding['profit_loss'] >= 0 else "loss",
                )
            )
            
        # Configure tag colors
        self.performance_tree.tag_configure("profit", foreground="#2ecc71")
        self.performance_tree.tag_configure("loss", foreground="#e74c3c")
        
    def analyze_portfolio(self):
        """Analyze portfolio and provide recommendations."""
        if not self.holdings:
            return
            
        # Calculate diversification score (0-10)
        diversification_score = self.calculate_diversification_score()
        
        # Update diversification score
        self.diversification_score.configure(text=f"{diversification_score}/10")
        
        # Update diversification description
        if diversification_score >= 8:
            desc = "Your portfolio is well-diversified across different assets."
            self.diversification_score.configure(text_color="#2ecc71")
        elif diversification_score >= 5:
            desc = "Your portfolio has decent diversification, but could be improved."
            self.diversification_score.configure(text_color="#f39c12")
        else:
            desc = "Your portfolio needs better diversification. Consider adding more varied assets."
            self.diversification_score.configure(text_color="#e74c3c")
            
        self.diversification_desc.configure(text=desc)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(diversification_score)
        
        # Update recommendations text
        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("0.0", "end")
        self.recommendations_text.insert("0.0", recommendations)
        self.recommendations_text.configure(state="disabled")
        
    def calculate_diversification_score(self):
        """Calculate a diversification score (0-10) based on portfolio composition."""
        # Number of assets (more assets = higher score)
        asset_count = len(self.holdings)
        
        # Calculate concentration (Herfindahl-Hirschman Index)
        hhi = sum(holding["allocation"] ** 2 for holding in self.holdings) / 100
        
        # Number of assets score (max 5 points)
        asset_score = min(5, asset_count / 2)
        
        # Concentration score (max 5 points)
        # Lower HHI is better (less concentrated)
        concentration_score = 5 * (1 - (hhi / 1))
        
        # Total score
        total_score = asset_score + concentration_score
        
        # Cap at 10
        return min(10, round(total_score))
        
    def generate_recommendations(self, diversification_score):
        """Generate portfolio recommendations."""
        recommendations = []
        
        # Get total portfolio value
        total_value = sum(holding["value"] for holding in self.holdings)
        
        # Check for overconcentration
        for holding in self.holdings:
            if holding["allocation"] > 30:
                recommendations.append(f"• Consider reducing your {holding['symbol']} position, which makes up {format_percentage(holding['allocation'])} of your portfolio.")
                
        # Check for underperforming assets
        for holding in self.holdings:
            if holding["profit_loss_pct"] < -20 and holding["value"] > total_value * 0.05:
                recommendations.append(f"• Your {holding['symbol']} position is down {format_percentage(abs(holding['profit_loss_pct']))}. Consider re-evaluating this investment.")
                
        # Check for diversification
        if diversification_score < 5:
            recommendations.append("• Your portfolio lacks diversification. Consider adding more varied assets to reduce risk.")
            
        if asset_count := len(self.holdings) < 5:
            recommendations.append(f"• You only have {asset_count} assets. Adding more assets can help reduce risk through diversification.")
            
        # Check for missing major cryptos
        major_cryptos = ["BTC", "ETH"]
        missing_major = [crypto for crypto in major_cryptos if crypto not in [h["symbol"] for h in self.holdings]]
        
        if missing_major:
            recommendations.append(f"• Consider adding {', '.join(missing_major)} to your portfolio as they are major cryptocurrencies.")
        
        # Staking recommendations
        if hasattr(self, 'staking_data') and self.staking_data:
            # Check for assets that could be staked but aren't
            stakable_assets = ["ETH", "SOL", "ADA", "DOT", "ATOM", "NEAR", "OSMO", "TRX"]
            holdings_symbols = [h["symbol"] for h in self.holdings]
            
            # Find assets that are in portfolio but not in staking transactions
            staked_assets = list(data['symbol'] for data in self.staking_data['by_asset'].values())
            potential_staking = [symbol for symbol in stakable_assets 
                              if symbol in holdings_symbols and symbol not in staked_assets]
            
            if potential_staking:
                recommendations.append(f"• Consider staking your {', '.join(potential_staking)} holdings to earn passive income.")
                
            # Check if staking income is low compared to holdings
            if self.staking_data['monthly_average'] < total_value * 0.005:  # Less than 0.5% monthly return
                recommendations.append("• Your staking income appears low relative to your portfolio value. Consider exploring higher-yield staking options.")
            
        # If no recommendations, add a positive message
        if not recommendations:
            if diversification_score >= 8:
                recommendations.append("Your portfolio is well-diversified and balanced. Continue monitoring market conditions and making regular adjustments as needed.")
            else:
                recommendations.append("Your portfolio is in good standing. Consider regular rebalancing to maintain optimal allocation.")
                
        return "\n\n".join(recommendations) 
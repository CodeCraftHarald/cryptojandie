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
        
        # Recommendations Section
        self.recommendations_label = ctk.CTkLabel(
            self.content_frame,
            text="Recommendations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.recommendations_label.grid(row=8, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Recommendations frame
        self.recommendations_frame = ctk.CTkFrame(self.content_frame)
        self.recommendations_frame.grid(row=9, column=0, padx=0, pady=(0, 20), sticky="ew")
        
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
        
        self.analyze_portfolio()
        
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
            
        # If no recommendations, add a positive message
        if not recommendations:
            if diversification_score >= 8:
                recommendations.append("Your portfolio is well-diversified and balanced. Continue monitoring market conditions and making regular adjustments as needed.")
            else:
                recommendations.append("Your portfolio is in good standing. Consider regular rebalancing to maintain optimal allocation.")
                
        return "\n\n".join(recommendations) 
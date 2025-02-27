import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime, timedelta
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils import format_currency, format_percentage, embed_chart

class StakingDashboard(ctk.CTkFrame):
    def __init__(self, master, user, db, api):
        """Initialize the staking dashboard screen."""
        super().__init__(master)
        self.master = master
        self.user = user
        self.db = db
        self.api = api
        self.current_prices = {}
        
        # Configure layout
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_columnconfigure(0, weight=1)
        
        # Create title
        self.create_title()
        
        # Create content area with staking charts and tables
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
            text="Staking Analysis",
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
        """Create content area with staking charts and tables."""
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configure content layout
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Staking Overview Section
        self.overview_label = ctk.CTkLabel(
            self.content_frame,
            text="Staking Overview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.overview_label.grid(row=0, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Staking summary cards
        self.staking_summary_frame = ctk.CTkFrame(self.content_frame)
        self.staking_summary_frame.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="ew")
        
        # Configure staking summary layout
        self.staking_summary_frame.grid_columnconfigure(0, weight=1)
        self.staking_summary_frame.grid_columnconfigure(1, weight=1)
        self.staking_summary_frame.grid_columnconfigure(2, weight=1)
        
        # Create staking summary cards
        self.create_summary_card(self.staking_summary_frame, 0, "Total Staking Income", "$0.00")
        self.create_summary_card(self.staking_summary_frame, 1, "Monthly Average", "$0.00")
        self.create_summary_card(self.staking_summary_frame, 2, "Estimated Annual Yield", "0.00%")
        
        # Staking charts Section
        self.charts_label = ctk.CTkLabel(
            self.content_frame,
            text="Staking Charts",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.charts_label.grid(row=2, column=0, padx=0, pady=(20, 10), sticky="w")
        
        # Staking charts frame
        self.staking_charts_frame = ctk.CTkFrame(self.content_frame)
        self.staking_charts_frame.grid(row=3, column=0, padx=0, pady=(0, 10), sticky="ew")
        
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
        
        # Staking Details Section
        self.details_label = ctk.CTkLabel(
            self.content_frame,
            text="Staking Details",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.details_label.grid(row=4, column=0, padx=0, pady=(20, 10), sticky="w")
        
        # Staking details table frame
        self.staking_details_frame = ctk.CTkFrame(self.content_frame)
        self.staking_details_frame.grid(row=5, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Create staking details table
        self.create_staking_details_table()
        
        # Recommendations Section
        self.recommendations_label = ctk.CTkLabel(
            self.content_frame,
            text="Staking Recommendations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.recommendations_label.grid(row=6, column=0, padx=0, pady=(10, 10), sticky="w")
        
        # Recommendations frame
        self.recommendations_frame = ctk.CTkFrame(self.content_frame)
        self.recommendations_frame.grid(row=7, column=0, padx=0, pady=(0, 20), sticky="ew")
        
        # Recommendations text
        self.recommendations_text = ctk.CTkTextbox(self.recommendations_frame, height=150)
        self.recommendations_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.recommendations_text.insert("0.0", "Staking recommendations will appear here after analyzing your staking data.")
        self.recommendations_text.configure(state="disabled")
        
    def create_summary_card(self, parent_frame, column, title, value):
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
            height=10
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
        """Load and analyze staking data."""
        # Get all assets to check current prices
        self.cursor = self.db.connection.cursor()
        self.cursor.execute("SELECT id FROM assets")
        assets = self.cursor.fetchall()
        
        # Get latest prices using the proper method
        self.current_prices = {}
        for asset in assets:
            asset_id = asset['id']
            price_data = self.db.get_latest_price(asset_id)
            if price_data:
                self.current_prices[asset_id] = price_data['price_usd']
        
        self.load_staking_data()
        
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
        
        # Get user holdings to calculate APY
        self.cursor.execute("""
            SELECT h.*, a.symbol, a.name 
            FROM holdings h
            JOIN assets a ON h.asset_id = a.id
            WHERE h.user_id = ?
        """, (self.user['id'],))
        holdings = [dict(row) for row in self.cursor.fetchall()]
        
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
            # Find holding for this asset
            holding = next((h for h in holdings if h['asset_id'] == asset_id), None)
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
        
        # Update UI
        self.update_staking_summary(total_staking_income, avg_monthly_income)
        self.update_staking_charts()
        self.update_staking_table()
        self.generate_staking_recommendations()
        
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
            
        # Update recommendations
        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("0.0", "end")
        self.recommendations_text.insert("0.0", "Add staking transactions to see recommendations.")
        self.recommendations_text.configure(state="disabled")
            
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
            
    def generate_staking_recommendations(self):
        """Generate staking-specific recommendations."""
        if not hasattr(self, 'staking_data') or not self.staking_data:
            return
            
        recommendations = []
        
        # Get staking assets
        staked_assets = list(data['symbol'] for data in self.staking_data['by_asset'].values())
        
        # Get list of common stakable assets
        stakable_assets = ["ETH", "SOL", "ADA", "DOT", "ATOM", "NEAR", "OSMO", "TRX", "MATIC", "AVAX", "BNB"]
        
        # Get all user holdings to check for potential staking opportunities
        self.cursor.execute("""
            SELECT h.*, a.symbol, a.name 
            FROM holdings h
            JOIN assets a ON h.asset_id = a.id
            WHERE h.user_id = ?
        """, (self.user['id'],))
        holdings = [dict(row) for row in self.cursor.fetchall()]
        
        # Find stakable assets that user holds but hasn't staked
        holdings_symbols = [h["symbol"] for h in holdings]
        potential_staking = [symbol for symbol in stakable_assets 
                          if symbol in holdings_symbols and symbol not in staked_assets]
        
        if potential_staking:
            recommendations.append(f"• Consider staking your {', '.join(potential_staking)} holdings to earn passive income.")
            
        # Check APY rates for optimization opportunities
        low_apy_assets = []
        if hasattr(self, 'staking_data') and 'by_asset' in self.staking_data:
            for asset_id, data in self.staking_data['by_asset'].items():
                apy = data.get('apy', 0)
                symbol = data['symbol']
                
                # Check if APY is lower than typical rates
                if symbol == "ETH" and apy < 3.5:
                    low_apy_assets.append(symbol)
                elif symbol == "SOL" and apy < 5.5:
                    low_apy_assets.append(symbol)
                elif symbol == "ADA" and apy < 4.0:
                    low_apy_assets.append(symbol)
                elif symbol == "DOT" and apy < 12.0:
                    low_apy_assets.append(symbol)
                elif apy < 3.0:  # General low APY threshold
                    low_apy_assets.append(symbol)
        
        if low_apy_assets:
            recommendations.append(f"• Your staking yield for {', '.join(low_apy_assets)} appears lower than average. Consider exploring alternative staking providers for better rates.")
            
        # Check staking frequency
        irregular_staking = []
        for asset_id, data in self.staking_data['by_asset'].items():
            transactions = data['transactions']
            symbol = data['symbol']
            
            # Sort transactions by timestamp
            sorted_txs = sorted(transactions, key=lambda x: datetime.fromisoformat(x['timestamp']))
            
            if len(sorted_txs) > 2:
                # Calculate time gaps between rewards
                gaps = []
                for i in range(1, len(sorted_txs)):
                    prev_time = datetime.fromisoformat(sorted_txs[i-1]['timestamp'])
                    curr_time = datetime.fromisoformat(sorted_txs[i]['timestamp'])
                    gap_days = (curr_time - prev_time).days
                    gaps.append(gap_days)
                
                # Check for irregularity in staking rewards
                avg_gap = sum(gaps) / len(gaps)
                max_gap = max(gaps)
                
                if max_gap > avg_gap * 2:
                    irregular_staking.append(symbol)
        
        if irregular_staking:
            recommendations.append(f"• Your staking rewards for {', '.join(irregular_staking)} show irregular intervals. Check if your staking setup is still active and properly configured.")
            
        # Check if staking rewards are being claimed/compounded
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m")
        inactive_staking = []
        
        for asset_id, data in self.staking_data['by_asset'].items():
            last_reward_time = datetime.fromisoformat(data['last_timestamp'])
            if (datetime.now() - last_reward_time).days > 45:  # No rewards in 45+ days
                inactive_staking.append(data['symbol'])
                
        if inactive_staking:
            recommendations.append(f"• You haven't received staking rewards for {', '.join(inactive_staking)} in over 45 days. Check if your staking is still active.")
            
        # Calculate potential yearly income based on current staking rate
        if self.staking_data['monthly_average'] > 0:
            yearly_projection = self.staking_data['monthly_average'] * 12
            recommendations.append(f"• At your current staking rate, you're projected to earn approximately {format_currency(yearly_projection)} in staking rewards over the next year.")
        
        # If no specific recommendations, add general advice
        if not recommendations:
            recommendations.append("Your staking setup appears to be well-configured. Continue monitoring for optimal yields and consider compounding your rewards for maximum growth.")
            
        # Update recommendations text
        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("0.0", "end")
        self.recommendations_text.insert("0.0", "\n\n".join(recommendations))
        self.recommendations_text.configure(state="disabled") 
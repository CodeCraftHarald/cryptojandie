import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime, timedelta
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        
        # Add alternating row colors
        style.map('Treeview', 
                  background=[('selected', '#3498db'), 
                              ('alternate', '#333333')])
        
        # Create the treeview with additional column for confidence level
        self.staking_tree = tk.ttk.Treeview(
            self.staking_tree_container,
            columns=("asset", "total_rewards", "last_reward", "avg_monthly", "estimated_apy", "confidence"),
            show="headings",
            height=10
        )
        
        # Define columns
        self.staking_tree.heading("asset", text="Asset")
        self.staking_tree.heading("total_rewards", text="Total Rewards")
        self.staking_tree.heading("last_reward", text="Last Reward")
        self.staking_tree.heading("avg_monthly", text="Monthly Average")
        self.staking_tree.heading("estimated_apy", text="Est. APY")
        self.staking_tree.heading("confidence", text="Confidence")
        
        # Column widths
        self.staking_tree.column("asset", width=150, anchor="w")
        self.staking_tree.column("total_rewards", width=120, anchor="e")
        self.staking_tree.column("last_reward", width=120, anchor="e")
        self.staking_tree.column("avg_monthly", width=120, anchor="e")
        self.staking_tree.column("estimated_apy", width=100, anchor="e")
        self.staking_tree.column("confidence", width=90, anchor="center")
        
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
                
                # Calculate average monthly staking using improved method
                monthly_staking_amount = self.calculate_monthly_average_staking(data['transactions'])
                
                # Calculate APY only if we have staking and holdings data
                if total_staked_amount > 0 and monthly_staking_amount > 0:
                    # Get staking period information
                    earliest_timestamp = min(datetime.fromisoformat(tx['timestamp']) for tx in data['transactions'])
                    latest_timestamp = max(datetime.fromisoformat(tx['timestamp']) for tx in data['transactions'])
                    
                    # Check if we have at least a month of staking data for more accurate APY
                    days_staking = (latest_timestamp - earliest_timestamp).days
                    
                    if days_staking >= 30:  # At least a month of data
                        # Calculate annual yield more accurately based on actual period
                        monthly_staking_value = monthly_staking_amount * self.current_prices.get(asset_id, 0)
                        annual_staking_value = monthly_staking_value * 12
                        total_staked_value = total_staked_amount * self.current_prices.get(asset_id, 0)
                        
                        # Handle case where staked value is very small to prevent huge APY values
                        if total_staked_value > 0 and total_staked_value >= (monthly_staking_value / 10):
                            estimated_apy = (annual_staking_value / total_staked_value) * 100
                            
                            # Cap unreasonable APY values (optional)
                            if estimated_apy > 1000:  # Cap at 1000% (10x) APY
                                estimated_apy = 1000
                        else:
                            # Set a conservative default if staked value is too small
                            estimated_apy = 0
                    else:
                        # For short staking periods, use a more conservative estimate
                        # Annualize based on the days we have data
                        if days_staking > 0:
                            total_staking_value = data['total_value']
                            annualization_factor = 365.0 / days_staking
                            annual_staking_value = total_staking_value * annualization_factor
                            total_staked_value = total_staked_amount * self.current_prices.get(asset_id, 0)
                            
                            if total_staked_value > 0:
                                estimated_apy = (annual_staking_value / total_staked_value) * 100
                                # Cap unreasonable values from short periods
                                if estimated_apy > 500:
                                    estimated_apy = 500
                            else:
                                estimated_apy = 0
                        else:
                            estimated_apy = 0
                        
                    staking_by_asset[asset_id]['apy'] = estimated_apy
                    
                    # Also store the confidence level in the APY calculation
                    if days_staking >= 180:  # 6+ months
                        staking_by_asset[asset_id]['apy_confidence'] = "high"
                    elif days_staking >= 60:  # 2+ months
                        staking_by_asset[asset_id]['apy_confidence'] = "medium"
                    else:
                        staking_by_asset[asset_id]['apy_confidence'] = "low"
                else:
                    staking_by_asset[asset_id]['apy'] = 0
                    staking_by_asset[asset_id]['apy_confidence'] = "none"
            else:
                staking_by_asset[asset_id]['apy'] = 0
                staking_by_asset[asset_id]['apy_confidence'] = "none"
        
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
        
        # Find earliest and latest transaction dates for time range calculation
        earliest_date = None
        latest_date = None
        
        for tx in transactions:
            timestamp = datetime.fromisoformat(tx['timestamp'])
            month_key = timestamp.strftime("%Y-%m")
            
            # Track earliest and latest dates
            if earliest_date is None or timestamp < earliest_date:
                earliest_date = timestamp
            if latest_date is None or timestamp > latest_date:
                latest_date = timestamp
            
            if month_key not in by_month:
                by_month[month_key] = 0
            
            by_month[month_key] += tx['amount']
        
        # Calculate average
        total_amount = sum(by_month.values())
        
        # Calculate the number of months in the date range
        if earliest_date and latest_date:
            # Calculate months between earliest and latest transaction
            month_diff = (latest_date.year - earliest_date.year) * 12 + (latest_date.month - earliest_date.month)
            # Include partial months by adding 1
            months_in_range = month_diff + 1
            
            # Check if we're missing months in the range (months without staking)
            current_year_month = earliest_date.strftime("%Y-%m")
            end_year_month = latest_date.strftime("%Y-%m")
            
            expected_months = []
            while current_year_month <= end_year_month:
                expected_months.append(current_year_month)
                # Move to next month
                year = int(current_year_month.split('-')[0])
                month = int(current_year_month.split('-')[1])
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                current_year_month = f"{year:04d}-{month:02d}"
            
            # Include months with no staking in the calculation
            for month in expected_months:
                if month not in by_month:
                    by_month[month] = 0
        else:
            months_in_range = 1  # Default if can't determine date range
        
        # Use actual number of months from the date range, not just months with transactions
        num_months = len(by_month)
        
        # Return the average (total divided by number of months)
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
        
        # Create figure with a better style
        plt.style.use('dark_background')
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create gradient-filled line chart
        line = ax.plot(month_labels, values, marker='o', linestyle='-', color='#3498db', linewidth=2.5, markersize=6, markerfacecolor='white', markeredgecolor='#3498db')[0]
        
        # Create gradient fill area
        # Get the current line data
        x = line.get_xdata()
        y = line.get_ydata()
        
        # Fill area under the curve with gradient
        ax.fill_between(x, y, color='#3498db', alpha=0.3)
        
        # Add value labels with better formatting
        for i, v in enumerate(values):
            if v > 0:  # Only show labels for non-zero values
                ax.annotate(
                    format_currency(v),
                    (i, v),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle="round,pad=0.3", fc='#34495e', ec="none", alpha=0.7)
                )
        
        # Format axes
        ax.set_title('Staking Rewards Over Time', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_ylabel('Value (USD)', fontsize=12, fontweight='bold', labelpad=10)
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
        
        # Add gridlines with better styling
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: format_currency(x)))
        
        # Set background color
        ax.set_facecolor('#1e272e')
        fig.patch.set_facecolor('#1e272e')
        
        # Add a horizontal line at zero
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        
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
        
        # Create figure with a better style
        plt.style.use('dark_background')
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create custom colormap for gradient bars
        color_gradient = []
        for i in range(len(months)):
            # Create a gradient effect from lighter to darker green
            alpha = 0.5 + (i / len(months)) * 0.5
            color_gradient.append((*matplotlib.colors.to_rgb('#2ecc71'), alpha))
        
        # Create bar chart for monthly forecast with gradient colors
        bars = ax.bar(months, forecast_values, color=color_gradient, label='Monthly Income')
        
        # Create line chart for cumulative income with improved styling
        ax2 = ax.twinx()
        cumulative_line = ax2.plot(
            months, 
            cumulative_values, 
            marker='o', 
            linestyle='-', 
            color='#e74c3c', 
            linewidth=2.5, 
            markersize=6,
            markerfacecolor='white',
            markeredgecolor='#e74c3c',
            label='Cumulative Income'
        )[0]
        
        # Annotate cumulative values at specific points (start, middle, end)
        ax2.annotate(
            format_currency(cumulative_values[0]),
            (0, cumulative_values[0]),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=9,
            color='white',
            bbox=dict(boxstyle="round,pad=0.3", fc='#c0392b', ec="none", alpha=0.7)
        )
        
        middle_idx = len(cumulative_values) // 2
        ax2.annotate(
            format_currency(cumulative_values[middle_idx]),
            (middle_idx, cumulative_values[middle_idx]),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=9,
            color='white',
            bbox=dict(boxstyle="round,pad=0.3", fc='#c0392b', ec="none", alpha=0.7)
        )
        
        ax2.annotate(
            format_currency(cumulative_values[-1]),
            (len(cumulative_values)-1, cumulative_values[-1]),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold',
            color='white',
            bbox=dict(boxstyle="round,pad=0.3", fc='#c0392b', ec="none", alpha=0.7)
        )
        
        # Add bar value labels for a few key bars
        for i in [0, len(bars)//2, len(bars)-1]:
            height = bars[i].get_height()
            ax.annotate(
                format_currency(height),
                xy=(bars[i].get_x() + bars[i].get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', 
                va='bottom',
                fontsize=9,
                color='white',
                bbox=dict(boxstyle="round,pad=0.2", fc='#27ae60', ec="none", alpha=0.7)
            )
        
        # Format axes
        ax.set_title('Forecasted Staking Income', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_ylabel('Monthly Income (USD)', fontsize=12, fontweight='bold', color='#2ecc71', labelpad=10)
        ax2.set_ylabel('Cumulative Income (USD)', fontsize=12, fontweight='bold', color='#e74c3c', labelpad=10)
        
        # Format tick labels
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.tick_params(axis='y', colors='#2ecc71', labelsize=10)
        ax2.tick_params(axis='y', colors='#e74c3c', labelsize=10)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: format_currency(x)))
        ax2.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: format_currency(x)))
        
        # Add gridlines with better styling
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        
        # Set background color
        ax.set_facecolor('#1e272e')
        fig.patch.set_facecolor('#1e272e')
        
        # Add legend with better styling
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        legend = ax.legend(
            lines1 + lines2, 
            labels1 + labels2, 
            loc='upper left', 
            framealpha=0.7,
            facecolor='#2c3e50',
            edgecolor='none',
            fontsize=10
        )
        legend.get_texts()[0].set_color('#2ecc71')
        legend.get_texts()[1].set_color('#e74c3c')
        
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
            
            # Get estimated APY and confidence level
            estimated_apy = data.get('apy', 0)
            confidence_level = data.get('apy_confidence', 'none')
            
            # Format confidence level for display
            if confidence_level == "high":
                confidence_display = "High"
            elif confidence_level == "medium":
                confidence_display = "Medium"
            elif confidence_level == "low":
                confidence_display = "Low"
            else:
                confidence_display = "N/A"
            
            # Insert data into treeview
            row_id = self.staking_tree.insert(
                "",
                "end",
                values=(
                    f"{symbol} ({name})",
                    f"{total_amount:.8f} {symbol}",
                    f"{last_timestamp}",
                    format_currency(monthly_value),
                    format_percentage(estimated_apy),
                    confidence_display
                )
            )
            
            # Apply color-coding for APY confidence levels
            if confidence_level == "high":
                self.staking_tree.item(row_id, tags=("high_confidence",))
            elif confidence_level == "medium":
                self.staking_tree.item(row_id, tags=("medium_confidence",))
            elif confidence_level == "low":
                self.staking_tree.item(row_id, tags=("low_confidence",))
            
        # Configure tag colors
        self.staking_tree.tag_configure("high_confidence", background="#2b2b2b", foreground="#27ae60")
        self.staking_tree.tag_configure("medium_confidence", background="#2b2b2b", foreground="#f39c12")
        self.staking_tree.tag_configure("low_confidence", background="#2b2b2b", foreground="#e74c3c")
            
    def generate_staking_recommendations(self):
        """Generate staking-specific recommendations."""
        if not hasattr(self, 'staking_data') or not self.staking_data:
            return
            
        recommendations = []
        
        # Add explanation about APY confidence levels
        recommendations.append("APY Confidence Levels Explained:")
        recommendations.append("• High: 6+ months of staking data - most reliable APY estimate")
        recommendations.append("• Medium: 2-6 months of data - reasonably accurate estimate")
        recommendations.append("• Low: Less than 2 months - preliminary estimate, may change significantly")
        recommendations.append("• N/A: Insufficient data to calculate APY\n")
        
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
            
        # Check APY rates and confidence for optimization opportunities
        low_apy_assets = []
        low_confidence_assets = []
        
        for asset_id, data in self.staking_data['by_asset'].items():
            apy = data.get('apy', 0)
            symbol = data['symbol']
            confidence = data.get('apy_confidence', 'none')
            
            # Low confidence assets - may need more data
            if confidence in ['low', 'none'] and symbol in staked_assets:
                low_confidence_assets.append(symbol)
            
            # Check if APY is lower than typical rates (only for medium/high confidence)
            if confidence in ['medium', 'high']:
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
            
        if low_confidence_assets:
            recommendations.append(f"• We need more staking history for {', '.join(low_confidence_assets)} to provide accurate APY estimates. Continue recording staking rewards to improve analysis accuracy.")
            
        # Check staking frequency
        irregular_staking = []
        for asset_id, data in self.staking_data['by_asset'].items():
            transactions = data['transactions']
            symbol = data['symbol']
            
            # Only analyze if we have enough transactions
            if len(transactions) > 2:
                # Sort transactions by timestamp
                sorted_txs = sorted(transactions, key=lambda x: datetime.fromisoformat(x['timestamp']))
                
                # Calculate time gaps between rewards
                gaps = []
                for i in range(1, len(sorted_txs)):
                    prev_time = datetime.fromisoformat(sorted_txs[i-1]['timestamp'])
                    curr_time = datetime.fromisoformat(sorted_txs[i]['timestamp'])
                    gap_days = (curr_time - prev_time).days
                    gaps.append(gap_days)
                
                # Check for irregularity in staking rewards
                if len(gaps) >= 2:  # Need at least 2 gaps to check consistency
                    avg_gap = sum(gaps) / len(gaps)
                    max_gap = max(gaps)
                    std_dev = (sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)) ** 0.5
                    
                    # Check if max gap is significantly larger than average or high standard deviation
                    if max_gap > avg_gap * 2 or std_dev > avg_gap * 0.5:
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
            
            # Suggest compounding for significant staking rewards
            if yearly_projection > 500:  # Only suggest if meaningful amount
                recommendations.append(f"• Consider compounding your staking rewards by re-staking them regularly to maximize your earnings. This could significantly increase your returns over time.")
        
        # If no specific recommendations, add general advice
        if len(recommendations) <= 5:  # Only have the confidence level explanation
            recommendations.append("Your staking setup appears to be well-configured. Continue monitoring for optimal yields and consider compounding your rewards for maximum growth.")
            
        # Update recommendations text
        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("0.0", "end")
        self.recommendations_text.insert("0.0", "\n\n".join(recommendations))
        self.recommendations_text.configure(state="disabled") 
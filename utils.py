import csv
import datetime
import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

def format_currency(value, currency="$"):
    """Format a number as currency."""
    if value is None:
        return f"{currency}0.00"
    
    if value >= 1_000_000_000:
        return f"{currency}{value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{currency}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{currency}{value/1_000:.2f}K"
    else:
        return f"{currency}{value:.2f}"

def format_percentage(value):
    """Format a number as percentage."""
    if value is None:
        return "0.00%"
    return f"{value:.2f}%"

def calculate_weighted_average(existing_amount, existing_price, new_amount, new_price):
    """Calculate weighted average purchase price."""
    if existing_amount + new_amount == 0:
        return 0
    return ((existing_amount * existing_price) + (new_amount * new_price)) / (existing_amount + new_amount)

def parse_csv_data(file_path, user_id, db):
    """Parse CSV data for import."""
    try:
        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            results = {"success": [], "errors": []}
            
            for row in reader:
                try:
                    symbol = row.get('symbol', '').strip().upper()
                    amount = float(row.get('amount', 0))
                    purchase_price = float(row.get('purchase_price', 0))
                    notes = row.get('notes', '')
                    
                    if not symbol or amount <= 0:
                        results["errors"].append(f"Invalid data for row: {row}")
                        continue
                    
                    # Check if asset exists
                    asset = db.get_asset_by_symbol(symbol)
                    if not asset:
                        results["errors"].append(f"Asset not found: {symbol}")
                        continue
                    
                    # Add holding
                    holding_id = db.add_holding(user_id, asset['id'], amount, purchase_price, notes)
                    
                    if holding_id:
                        # Record transaction
                        db.add_transaction(user_id, asset['id'], "BUY", amount, purchase_price, notes)
                        results["success"].append(f"Added {amount} {symbol} at ${purchase_price}")
                    else:
                        results["errors"].append(f"Failed to add holding for {symbol}")
                        
                except Exception as e:
                    results["errors"].append(f"Error processing row: {row} - {str(e)}")
                    
            return results
    except Exception as e:
        return {"success": [], "errors": [f"Error reading CSV file: {str(e)}"]}

def create_pie_chart(holdings, current_prices, width=800, height=500):
    """Create a pie chart for portfolio distribution."""
    if not holdings:
        return None
        
    # Prepare data
    data = []
    labels = []
    colors = plt.cm.tab20.colors
    
    total_value = 0
    for holding in holdings:
        # Access as dictionary keys instead of attributes
        asset_id = holding['asset_id'] if isinstance(holding, dict) else holding.asset_id
        amount = holding['amount'] if isinstance(holding, dict) else holding.amount
        
        price = current_prices.get(asset_id, 0)
        value = amount * price
        total_value += value
        
    for i, holding in enumerate(holdings):
        # Access as dictionary keys instead of attributes
        asset_id = holding['asset_id'] if isinstance(holding, dict) else holding.asset_id
        amount = holding['amount'] if isinstance(holding, dict) else holding.amount
        symbol = holding['symbol'] if isinstance(holding, dict) else holding.symbol
        
        price = current_prices.get(asset_id, 0)
        value = amount * price
        percentage = (value / total_value) * 100 if total_value > 0 else 0
        
        if percentage > 1:  # Only show assets with more than 1% in the pie chart
            data.append(value)
            labels.append(f"{symbol} ({percentage:.1f}%)")
    
    # Create figure
    fig = Figure(figsize=(width/100, height/100), dpi=100)
    ax = fig.add_subplot(111)
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        data, 
        labels=labels, 
        autopct='%1.1f%%',
        startangle=90,
        colors=colors[:len(data)]
    )
    
    # Format
    ax.set_title('Portfolio Distribution', fontsize=14)
    fig.tight_layout()
    
    return fig

def create_bar_chart(holdings, current_prices, width=800, height=500):
    """Create a bar chart for asset values."""
    if not holdings:
        return None
        
    # Prepare data
    symbols = []
    values = []
    
    # Sort holdings by value (descending)
    def get_value(h):
        # Access as dictionary keys instead of attributes
        asset_id = h['asset_id'] if isinstance(h, dict) else h.asset_id
        amount = h['amount'] if isinstance(h, dict) else h.amount
        return amount * current_prices.get(asset_id, 0)
        
    sorted_holdings = sorted(
        holdings,
        key=get_value,
        reverse=True
    )
    
    # Take top 15 holdings
    for holding in sorted_holdings[:15]:
        # Access as dictionary keys instead of attributes
        asset_id = holding['asset_id'] if isinstance(holding, dict) else holding.asset_id
        amount = holding['amount'] if isinstance(holding, dict) else holding.amount
        symbol = holding['symbol'] if isinstance(holding, dict) else holding.symbol
        
        price = current_prices.get(asset_id, 0)
        value = amount * price
        
        symbols.append(symbol)
        values.append(value)
    
    # Create figure
    fig = Figure(figsize=(width/100, height/100), dpi=100)
    ax = fig.add_subplot(111)
    
    # Create bar chart
    bars = ax.bar(symbols, values, color=plt.cm.tab20.colors[:len(symbols)])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f"${height:.0f}",
            ha='center',
            va='bottom',
            rotation=45,
            fontsize=8
        )
    
    # Format
    ax.set_title('Top Asset Values (USD)', fontsize=14)
    ax.set_xlabel('Assets')
    ax.set_ylabel('Value (USD)')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    
    return fig

def embed_chart(fig, master):
    """Embed a matplotlib figure in a Tkinter window."""
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.draw()
    return canvas.get_tk_widget() 
import sqlite3
import os
import json
from datetime import datetime

class Database:
    def __init__(self, db_path="cryptojandie.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Establish connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.connection.cursor()
        
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            settings TEXT DEFAULT '{}'
        )
        ''')
        
        # Assets table - stores information about supported cryptocurrencies
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            coingecko_id TEXT,
            market_cap REAL DEFAULT 0,
            last_updated TIMESTAMP
        )
        ''')
        
        # Prices table - stores price data for cryptocurrencies
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            asset_id INTEGER NOT NULL,
            price_usd REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        )
        ''')
        
        # Holdings table - stores user holdings
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            purchase_price_per_unit REAL NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        )
        ''')
        
        # Transactions table - stores history of all transactions
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            price_per_unit REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        )
        ''')
        
        self.connection.commit()
        
    def initialize_default_assets(self):
        """Initialize the database with default cryptocurrency assets."""
        default_assets = [
            ("BTC", "Bitcoin", "bitcoin"),
            ("ETH", "Ethereum", "ethereum"),
            ("WBETH", "Wrapped Beacon ETH", "wrapped-beacon-eth"),
            ("SOL", "Solana", "solana"),
            ("BNSOL", "Binance Staked SOL", "binance-staked-sol"),
            ("BNB", "Binance Coin", "binancecoin"),
            ("SXP", "Swipe", "swipe"),
            ("XRP", "XRP", "ripple"),
            ("SUI", "Sui", "sui"),
            ("LINK", "Chainlink", "chainlink"),
            ("BERA", "Bera", "bera"),
            ("DOGE", "Dogecoin", "dogecoin"),
            ("ADA", "Cardano", "cardano"),
            ("TRX", "TRON", "tron"),
            ("KAITO", "Kaito", "kaito"),
            ("NEAR", "NEAR Protocol", "near"),
            ("OSMO", "Osmosis", "osmosis"),
            ("BAND", "Band Protocol", "band-protocol"),
            ("DOT", "Polkadot", "polkadot"),
            ("POL", "Polkadex", "polkadex"),
            ("S", "Shardeum", "shardeum"),
            ("LAYER", "Layer", "layer"),
            ("SOLV", "Solv Protocol", "solv-protocol"),
            ("APT", "Aptos", "aptos"),
            ("1000CAT", "1000CAT", "1000cat"),
            ("ANIME", "Anime", "anime"),
            ("TIA", "Celestia", "celestia"),
            ("PNUT", "Peanut", "peanut"),
            ("INJ", "Injective", "injective-protocol"),
            ("ICP", "Internet Computer", "internet-computer"),
            ("FLOKI", "Floki", "floki"),
            ("MANTA", "Manta Network", "manta-network"),
            ("QTUM", "Qtum", "qtum"),
            ("BIO", "Biometry", "biometry"),
            ("TRUMP", "Trump", "trump"),
            ("ATOM", "Cosmos", "cosmos"),
            ("TAO", "Bittensor", "bittensor"),
            ("BCH", "Bitcoin Cash", "bitcoin-cash"),
            ("AVAX", "Avalanche", "avalanche-2"),
            ("ZIL", "Zilliqa", "zilliqa"),
            ("FET", "Fetch.ai", "fetch-ai"),
            ("LTC", "Litecoin", "litecoin"),
            ("OM", "MANTRA", "mantra"),
            ("EOS", "EOS", "eos"),
            ("REZ", "Rezilient", "rezilient"),
            ("PEPE", "Pepe", "pepe"),
            ("ACT", "ACTS", "acts"),
            ("BTTC", "BitTorrent-Chain", "bittorrent-chain"),
            ("CYBER", "CyberConnect", "cyberconnect"),
            ("NEXO", "NEXO", "nexo"),
            ("SPACE", "Space ID", "space-id"),
            ("IRIS", "IRISnet", "iris-network")
        ]
        
        for symbol, name, coingecko_id in default_assets:
            self.cursor.execute(
                "INSERT OR IGNORE INTO assets (symbol, name, coingecko_id) VALUES (?, ?, ?)",
                (symbol, name, coingecko_id)
            )
        
        self.connection.commit()
        
    def add_user(self, username):
        """Add a new user to the database."""
        try:
            self.cursor.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Username already exists
            return None
            
    def get_user(self, username):
        """Get user by username."""
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        return dict(self.cursor.fetchone()) if self.cursor.fetchone() else None
        
    def update_user_login(self, user_id):
        """Update user's last login time."""
        self.cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
        self.connection.commit()
        
    def add_price(self, asset_id, price_usd, source="manual"):
        """Add a new price entry for an asset."""
        self.cursor.execute(
            "INSERT INTO prices (asset_id, price_usd, source) VALUES (?, ?, ?)",
            (asset_id, price_usd, source)
        )
        self.connection.commit()
        return self.cursor.lastrowid
        
    def get_latest_price(self, asset_id):
        """Get the latest price for an asset."""
        self.cursor.execute(
            "SELECT * FROM prices WHERE asset_id = ? ORDER BY timestamp DESC LIMIT 1",
            (asset_id,)
        )
        result = self.cursor.fetchone()
        return dict(result) if result else None
        
    def get_asset_by_symbol(self, symbol):
        """Get asset by its symbol."""
        self.cursor.execute(
            "SELECT * FROM assets WHERE symbol = ?",
            (symbol,)
        )
        result = self.cursor.fetchone()
        return dict(result) if result else None
        
    def add_asset(self, symbol, name, coingecko_id=None):
        """Add a new cryptocurrency asset."""
        try:
            self.cursor.execute(
                "INSERT INTO assets (symbol, name, coingecko_id) VALUES (?, ?, ?)",
                (symbol, name, coingecko_id)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Asset symbol already exists
            return None
            
    def update_asset_market_cap(self, asset_id, market_cap):
        """Update market cap for an asset."""
        self.cursor.execute(
            "UPDATE assets SET market_cap = ?, last_updated = ? WHERE id = ?",
            (market_cap, datetime.now(), asset_id)
        )
        self.connection.commit()
        
    def add_holding(self, user_id, asset_id, amount, purchase_price_per_unit, notes=None):
        """Add a new holding for a user."""
        self.cursor.execute(
            "INSERT INTO holdings (user_id, asset_id, amount, purchase_price_per_unit, notes) VALUES (?, ?, ?, ?, ?)",
            (user_id, asset_id, amount, purchase_price_per_unit, notes)
        )
        self.connection.commit()
        return self.cursor.lastrowid
        
    def update_holding(self, holding_id, amount, purchase_price_per_unit=None, notes=None):
        """Update an existing holding."""
        query = "UPDATE holdings SET amount = ?"
        params = [amount]
        
        if purchase_price_per_unit is not None:
            query += ", purchase_price_per_unit = ?"
            params.append(purchase_price_per_unit)
            
        if notes is not None:
            query += ", notes = ?"
            params.append(notes)
            
        query += " WHERE id = ?"
        params.append(holding_id)
        
        self.cursor.execute(query, params)
        self.connection.commit()
        
    def delete_holding(self, holding_id):
        """Delete a holding."""
        self.cursor.execute(
            "DELETE FROM holdings WHERE id = ?",
            (holding_id,)
        )
        self.connection.commit()
        
    def get_user_holdings(self, user_id):
        """Get all holdings for a user with asset information."""
        self.cursor.execute("""
            SELECT h.*, a.symbol, a.name, a.market_cap 
            FROM holdings h
            JOIN assets a ON h.asset_id = a.id
            WHERE h.user_id = ?
        """, (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]
        
    def add_transaction(self, user_id, asset_id, transaction_type, amount, price_per_unit, notes=None):
        """Record a transaction."""
        self.cursor.execute(
            "INSERT INTO transactions (user_id, asset_id, transaction_type, amount, price_per_unit, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, asset_id, transaction_type, amount, price_per_unit, notes)
        )
        self.connection.commit()
        return self.cursor.lastrowid
        
    def get_user_transactions(self, user_id, limit=100):
        """Get transactions for a user with asset information."""
        self.cursor.execute("""
            SELECT t.*, a.symbol, a.name
            FROM transactions t
            JOIN assets a ON t.asset_id = a.id
            WHERE t.user_id = ?
            ORDER BY t.timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        return [dict(row) for row in self.cursor.fetchall()] 
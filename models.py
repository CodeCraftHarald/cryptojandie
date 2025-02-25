from datetime import datetime
import json

class User:
    def __init__(self, id=None, username=None, created_at=None, last_login=None, settings=None, password=None):
        self.id = id
        self.username = username
        self.created_at = created_at if created_at else datetime.now()
        self.last_login = last_login
        self.settings = settings if settings else {}
        self.password = password
        
    @classmethod
    def from_db(cls, db_dict):
        """Create a User instance from database dictionary."""
        if not db_dict:
            return None
            
        settings = db_dict.get('settings')
        if isinstance(settings, str):
            try:
                settings = json.loads(settings)
            except:
                settings = {}
                
        return cls(
            id=db_dict.get('id'),
            username=db_dict.get('username'),
            created_at=db_dict.get('created_at'),
            last_login=db_dict.get('last_login'),
            settings=settings,
            password=db_dict.get('password')
        )
        
    def to_dict(self):
        """Convert User to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'settings': self.settings,
            'password': self.password
        }

class Asset:
    def __init__(self, id=None, symbol=None, name=None, coingecko_id=None, market_cap=0, last_updated=None):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.coingecko_id = coingecko_id
        self.market_cap = market_cap
        self.last_updated = last_updated
        
    @classmethod
    def from_db(cls, db_dict):
        """Create an Asset instance from database dictionary."""
        if not db_dict:
            return None
            
        return cls(
            id=db_dict.get('id'),
            symbol=db_dict.get('symbol'),
            name=db_dict.get('name'),
            coingecko_id=db_dict.get('coingecko_id'),
            market_cap=db_dict.get('market_cap', 0),
            last_updated=db_dict.get('last_updated')
        )
        
    def to_dict(self):
        """Convert Asset to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'coingecko_id': self.coingecko_id,
            'market_cap': self.market_cap,
            'last_updated': self.last_updated
        }

class Price:
    def __init__(self, id=None, asset_id=None, price_usd=None, timestamp=None, source=None):
        self.id = id
        self.asset_id = asset_id
        self.price_usd = price_usd
        self.timestamp = timestamp if timestamp else datetime.now()
        self.source = source
        
    @classmethod
    def from_db(cls, db_dict):
        """Create a Price instance from database dictionary."""
        if not db_dict:
            return None
            
        return cls(
            id=db_dict.get('id'),
            asset_id=db_dict.get('asset_id'),
            price_usd=db_dict.get('price_usd'),
            timestamp=db_dict.get('timestamp'),
            source=db_dict.get('source')
        )
        
    def to_dict(self):
        """Convert Price to dictionary."""
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'price_usd': self.price_usd,
            'timestamp': self.timestamp,
            'source': self.source
        }

class Holding:
    def __init__(self, id=None, user_id=None, asset_id=None, amount=None, 
                 purchase_price_per_unit=None, purchase_date=None, notes=None,
                 symbol=None, name=None, market_cap=None):
        self.id = id
        self.user_id = user_id
        self.asset_id = asset_id
        self.amount = amount
        self.purchase_price_per_unit = purchase_price_per_unit
        self.purchase_date = purchase_date if purchase_date else datetime.now()
        self.notes = notes
        
        # Additional fields from asset join
        self.symbol = symbol
        self.name = name
        self.market_cap = market_cap
        
    @classmethod
    def from_db(cls, db_dict):
        """Create a Holding instance from database dictionary."""
        if not db_dict:
            return None
            
        return cls(
            id=db_dict.get('id'),
            user_id=db_dict.get('user_id'),
            asset_id=db_dict.get('asset_id'),
            amount=db_dict.get('amount'),
            purchase_price_per_unit=db_dict.get('purchase_price_per_unit'),
            purchase_date=db_dict.get('purchase_date'),
            notes=db_dict.get('notes'),
            symbol=db_dict.get('symbol'),
            name=db_dict.get('name'),
            market_cap=db_dict.get('market_cap')
        )
        
    def to_dict(self):
        """Convert Holding to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'asset_id': self.asset_id,
            'amount': self.amount,
            'purchase_price_per_unit': self.purchase_price_per_unit,
            'purchase_date': self.purchase_date,
            'notes': self.notes,
            'symbol': self.symbol,
            'name': self.name,
            'market_cap': self.market_cap
        }
        
    def current_value(self, current_price):
        """Calculate current value of the holding."""
        return self.amount * current_price
        
    def profit_loss(self, current_price):
        """Calculate profit/loss in USD and percentage."""
        current_value = self.current_value(current_price)
        cost_basis = self.amount * self.purchase_price_per_unit
        profit_loss_usd = current_value - cost_basis
        
        if cost_basis == 0:
            profit_loss_pct = 0
        else:
            profit_loss_pct = (profit_loss_usd / cost_basis) * 100
            
        return {
            "usd": profit_loss_usd,
            "percentage": profit_loss_pct
        }

class Transaction:
    def __init__(self, id=None, user_id=None, asset_id=None, transaction_type=None, 
                 amount=None, price_per_unit=None, timestamp=None, notes=None,
                 symbol=None, name=None):
        self.id = id
        self.user_id = user_id
        self.asset_id = asset_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.price_per_unit = price_per_unit
        self.timestamp = timestamp if timestamp else datetime.now()
        self.notes = notes
        
        # Additional fields from asset join
        self.symbol = symbol
        self.name = name
        
    @classmethod
    def from_db(cls, db_dict):
        """Create a Transaction instance from database dictionary."""
        if not db_dict:
            return None
            
        return cls(
            id=db_dict.get('id'),
            user_id=db_dict.get('user_id'),
            asset_id=db_dict.get('asset_id'),
            transaction_type=db_dict.get('transaction_type'),
            amount=db_dict.get('amount'),
            price_per_unit=db_dict.get('price_per_unit'),
            timestamp=db_dict.get('timestamp'),
            notes=db_dict.get('notes'),
            symbol=db_dict.get('symbol'),
            name=db_dict.get('name')
        )
        
    def to_dict(self):
        """Convert Transaction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'asset_id': self.asset_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'price_per_unit': self.price_per_unit,
            'timestamp': self.timestamp,
            'notes': self.notes,
            'symbol': self.symbol,
            'name': self.name
        }
        
    def total_value(self):
        """Calculate total value of the transaction."""
        return self.amount * self.price_per_unit 
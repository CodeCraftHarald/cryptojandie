import requests
import time
from datetime import datetime, timedelta

class CryptoAPI:
    def __init__(self):
        """Initialize the Crypto API handler."""
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.last_request_time = None
        self.cooldown_period = 60  # 1 minute cooldown (in seconds)
        
    def can_make_request(self):
        """Check if cooldown period has passed since last request."""
        if self.last_request_time is None:
            return True
            
        elapsed_time = time.time() - self.last_request_time
        return elapsed_time >= self.cooldown_period
        
    def get_remaining_cooldown(self):
        """Get remaining cooldown time in seconds."""
        if self.last_request_time is None:
            return 0
            
        elapsed_time = time.time() - self.last_request_time
        remaining = self.cooldown_period - elapsed_time
        return max(0, remaining)
    
    def update_request_time(self):
        """Update the last request time to current time."""
        self.last_request_time = time.time()
        
    def get_price(self, coingecko_id):
        """Get current price for a cryptocurrency by its CoinGecko ID."""
        if not self.can_make_request():
            return None, f"API cooldown active. Please wait {int(self.get_remaining_cooldown())} seconds."
            
        try:
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                "ids": coingecko_id,
                "vs_currencies": "usd",
                "include_market_cap": "true"
            }
            
            self.update_request_time()
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if coingecko_id in data:
                    return {
                        "price_usd": data[coingecko_id]["usd"],
                        "market_cap": data[coingecko_id].get("usd_market_cap", 0)
                    }, None
                else:
                    return None, "Cryptocurrency not found in API response."
            else:
                return None, f"API request failed with status code {response.status_code}."
                
        except Exception as e:
            return None, f"API request error: {str(e)}"
            
    def get_multiple_prices(self, coingecko_ids):
        """Get current prices for multiple cryptocurrencies."""
        if not self.can_make_request():
            return None, f"API cooldown active. Please wait {int(self.get_remaining_cooldown())} seconds."
            
        try:
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                "ids": ",".join(coingecko_ids),
                "vs_currencies": "usd",
                "include_market_cap": "true"
            }
            
            self.update_request_time()
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = {}
                
                for coin_id in coingecko_ids:
                    if coin_id in data:
                        results[coin_id] = {
                            "price_usd": data[coin_id]["usd"],
                            "market_cap": data[coin_id].get("usd_market_cap", 0)
                        }
                
                return results, None
            else:
                return None, f"API request failed with status code {response.status_code}."
                
        except Exception as e:
            return None, f"API request error: {str(e)}"
            
    def search_cryptocurrency(self, query):
        """Search for a cryptocurrency by name or symbol."""
        if not self.can_make_request():
            return None, f"API cooldown active. Please wait {int(self.get_remaining_cooldown())} seconds."
            
        try:
            url = f"{self.coingecko_base_url}/search"
            params = {
                "query": query
            }
            
            self.update_request_time()
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                coins = data.get("coins", [])
                return coins, None
            else:
                return None, f"API request failed with status code {response.status_code}."
                
        except Exception as e:
            return None, f"API request error: {str(e)}" 
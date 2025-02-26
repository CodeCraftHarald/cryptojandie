#!/usr/bin/env python
"""
Fix utility for updating CoinGecko IDs in the database.
This script will update the CoinGecko IDs for the following assets:
1. Bera - updated to "bera"
2. S (Sonic prev FTM) - updated to "fantom"
3. POL (Polygon) - updated to "polygon"
4. SPACE (Space Token) - updated to "space"
"""

import sqlite3
from database import Database

def main():
    print("Starting CoinGecko IDs fix utility...")
    
    # Initialize database
    db = Database()
    
    # 1. Fix Bera's CoinGecko ID
    print("\nFixing Bera CoinGecko ID...")
    success_bera = db.fix_bera_asset()
    if success_bera:
        print("✓ Updated BERA asset successfully")
    else:
        print("✗ Failed to update BERA asset - it may already be updated or not exist")
    
    # 2. Fix S's CoinGecko ID
    print("\nFixing S (Sonic prev FTM) CoinGecko ID...")
    success_s = db.fix_s_asset()
    if success_s:
        print("✓ Updated S asset successfully")
    else:
        print("✗ Failed to update S asset - it may already be updated or not exist")
    
    # 3. Fix POL's CoinGecko ID
    print("\nFixing POL (Polygon) CoinGecko ID...")
    success_pol = db.fix_pol_asset()
    if success_pol:
        print("✓ Updated POL asset successfully")
    else:
        print("✗ Failed to update POL asset - it may already be updated or not exist")
    
    # 4. Fix SPACE's CoinGecko ID
    print("\nFixing SPACE (Space Token) CoinGecko ID...")
    success_space = db.fix_space_asset()
    if success_space:
        print("✓ Updated SPACE asset successfully")
    else:
        print("✗ Failed to update SPACE asset - it may already be updated or not exist")
    
    # Display summary
    print("\nUpdate summary:")
    print(f"BERA: {'✓ Success' if success_bera else '✗ Failed/Not needed'}")
    print(f"S:    {'✓ Success' if success_s else '✗ Failed/Not needed'}")
    print(f"POL:  {'✓ Success' if success_pol else '✗ Failed/Not needed'}")
    print(f"SPACE:{'✓ Success' if success_space else '✗ Failed/Not needed'}")
    
    # Check if any holdings exist for these assets and display them
    print("\nChecking for holdings with these assets...")
    
    # Get all users
    db.cursor.execute("SELECT id, username FROM users")
    users = db.cursor.fetchall()
    
    for user_row in users:
        user_id = user_row[0]
        username = user_row[1]
        
        # Check if user has any of these assets
        db.cursor.execute("""
            SELECT a.symbol, a.name, a.coingecko_id, h.amount 
            FROM holdings h
            JOIN assets a ON h.asset_id = a.id
            WHERE h.user_id = ? AND a.symbol IN ('BERA', 'S', 'POL', 'SPACE')
        """, (user_id,))
        
        holdings = db.cursor.fetchall()
        
        if holdings:
            print(f"\nUser '{username}' has the following updated assets:")
            for holding in holdings:
                symbol, name, coingecko_id, amount = holding
                print(f"  {symbol} ({name}): {amount:.8f} - CoinGecko ID: {coingecko_id}")
    
    print("\nCoinGecko IDs fix utility completed successfully.")

if __name__ == "__main__":
    main() 
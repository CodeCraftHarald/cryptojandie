# CryptoJandie - Crypto Portfolio Tracker

The smartest crypto portfolio tracker on the block.

![Dark Mode UI](https://via.placeholder.com/800x450.png?text=CryptoJandie+Screenshot)

## Overview

CryptoJandie is a comprehensive cryptocurrency portfolio tracker built with Python. It allows users to track their cryptocurrency holdings, manage assets, and analyze their portfolio performance over time.

## Features

- **Dark Mode Interface**: Easy on the eyes for those late-night crypto sessions
- **Real-time Portfolio Tracking**: View your assets and their current values in USD
- **Multiple Data Input Methods**: Manual entry or API-based price retrieval
- **Comprehensive Asset Management**: Add, update, and remove crypto assets
- **Advanced Portfolio Analysis**: Track portfolio growth, market cap distribution, and more
- **Staking Analytics**: Track staking rewards, calculate APY, and get staking recommendations
- **CSV Import**: Easily import your existing portfolio data
- **Weighted Average Calculation**: Automatically calculates weighted average purchase price when adding new assets
- **Visual Analytics**: Charts and graphs for portfolio distribution and performance
- **Asset History**: Detailed transaction history with timestamps
- **Multiple Sorting Options**: Organize assets by various criteria

## Requirements

- Python 3.13.2
- SQLite database (included with Python)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cryptojandie.git
   cd cryptojandie
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv cryptojandie-env
   # On Windows:
   cryptojandie-env\Scripts\activate
   # On macOS/Linux:
   source cryptojandie-env/bin/activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## Usage

### Login/Registration
- Enter your username to log in or create a new account
- Your portfolio data is stored locally and will be available when you log in again

### Dashboard
- View your portfolio overview with total value, profit/loss, and asset distribution
- Refresh prices with the "Refresh Prices" button
- See a visual breakdown of your portfolio with the pie chart

### Asset Management
- Add new assets to your portfolio
- Update existing holdings
- Remove assets you no longer hold
- Import assets from a CSV file
- Sort your assets by various criteria
- View your transaction history

### Analysis Dashboard
- Analyze portfolio performance
- Track growth over time
- View market cap distribution

### Staking Dashboard
- Track your staking rewards for all assets
- View total staking income and monthly averages
- See estimated annual yields (APY) for each staked asset
- Visualize staking rewards history with charts
- Get a 12-month forecast of potential staking income
- Receive personalized staking recommendations
- Find opportunities to optimize your staking strategy

### CSV Import Format
To import assets from a CSV file, use the following format:
```
symbol,amount,purchase_price,notes
BTC,0.5,30000,Bitcoin investment
ETH,5,2000,Ethereum staking
```

## Supported Cryptocurrencies

CryptoJandie comes pre-loaded with 50+ cryptocurrencies including:

BTC, ETH, WBETH, SOL, BNSOL, BNB, SXP, XRP, SUI, LINK, BERA, DOGE, ADA, TRX, KAITO, NEAR, OSMO, BAND, DOT, POL, S, LAYER, SOLV, APT, 1000CAT, ANIME, TIA, PNUT, INJ, ICP, FLOKI, MANTA, QTUM, BIO, TRUMP, ATOM, TAO, BCH, AVAX, ZIL, FET, LTC, OM, EOS, REZ, PEPE, ACT, BTTC, CYBER, NEXO, SPACE, IRIS, and more that you can add manually.

## Supported Staking Assets

CryptoJandie helps you track staking rewards for popular proof-of-stake cryptocurrencies including:
ETH, SOL, ADA, DOT, ATOM, NEAR, OSMO, TRX, MATIC, AVAX, BNB, and more.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgements

- CoinGecko API for cryptocurrency price data
- CustomTkinter for the modern dark-themed UI components

## Data Model

CryptoJandie uses a SQLite database with the following tables:

**users**: Stores user accounts with fields:
  - id: INTEGER PRIMARY KEY
  - username: TEXT UNIQUE
  - created_at: TIMESTAMP (account creation time)
  - last_login: TIMESTAMP (last login time)
  - settings: JSON string with user-specific settings
  - password: Hashed password (using PBKDF2-HMAC-SHA256 with salt)

**assets**: Contains supported cryptocurrency details:
  - id, symbol, name, coingecko_id, market_cap, last_updated

**prices**: Records real-time price data:
  - id, asset_id, price_usd, timestamp, source

**holdings**: Represents a user's portfolio entries:
  - id, user_id, asset_id, amount, purchase_price_per_unit, purchase_date, notes

**transactions**: Logs buying/selling actions and staking rewards:
  - id, user_id, asset_id, transaction_type, amount, price_per_unit, timestamp, notes
  - transaction_type can be: BUY, SELL, STAKING

## Security Enhancements

- Passwords are stored in hashed and salted form using PBKDF2-HMAC-SHA256, rather than as plaintext.
- All SQL queries are parameterized and include user_id-based filtering to ensure that users can only access their own data.
- Robust password update and verification mechanisms are integrated into the login and settings flows.

## Session Management

- Upon successful login, secure user sessions are created. Session tokens (or in-memory session objects) are used to maintain user state.
- This mechanism helps in preventing unauthorized access and ensures that each user's session is isolated and managed securely.

## Architecture Overview

CryptoJandie is a desktop application built using Python and CustomTkinter. It integrates with the CoinGecko API for real-time cryptocurrency pricing and offers:

- CSV portfolio data import
- Interactive data visualizations with Matplotlib
- Comprehensive asset management and portfolio tracking
- Staking analytics and reward tracking
- A secure backend with SQLite, including extensive security measures for password handling and session management

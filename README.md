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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- CoinGecko API for cryptocurrency price data
- CustomTkinter for the modern dark-themed UI components

#!/usr/bin/env python3
import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1JC_SMTlWNBwuqDne3MJ229CAOWRw5KMDZeQM8_Vcr4s"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")
    
    if not os.path.exists(token_path):
        print("token.json not found")
        sys.exit(1)
        
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build("sheets", "v4", credentials=creds)
    
    btc_price = 76279.88
    btc_amount = 450.00
    btc_qty = round(btc_amount / btc_price, 8)
    
    print(f"BTC Price: ${btc_price}, Purchase Amount: ${btc_amount}, Quantity: {btc_qty}")
    
    # 1. Update Portfolio tab Row 11 (BTC) and formulas
    # We will write:
    # A11: 'BTC', B11: 'Bitcoin', C11: 'Cryptocurrency', D11: btc_qty, E11: btc_price, F11: btc_price
    # G11: '=D11*F11', H11: '=D11*E11', I11: '=G11-H11', J11: '=I11/H11', K11: '=G11/$I$19'
    portfolio_body = {
        "values": [
            ["BTC", "Bitcoin", "Cryptocurrency", btc_qty, btc_price, btc_price, "=D11*F11", "=D11*E11", "=G11-H11", "=I11/H11", "=G11/$I$19"]
        ]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Portfolio!A11:K11",
        valueInputOption="USER_ENTERED",
        body=portfolio_body
    ).execute()
    print("Portfolio Row 11 (BTC) updated.")
    
    # 2. Update summary formulas:
    # Row 13 (Total Cost): I13 -> '=SUM(H2:H11)'
    # Row 14 (Total Gain/Loss): I14 -> '=SUM(I2:I11)'
    # Row 16 (Total Equity): I16 -> '=SUM(G2:G11)'
    # Row 17 (Cash Flow): I17 -> 529.37 (since $979.37 - $450 = $529.37)
    formulas_body = {
        "data": [
            {"range": "Portfolio!I13", "values": [["=SUM(H2:H11)"]]},
            {"range": "Portfolio!I14", "values": [["=SUM(I2:I11)"]]},
            {"range": "Portfolio!I16", "values": [["=SUM(G2:G11)"]]},
            {"range": "Portfolio!I17", "values": [[529.37]]}
        ]
    }
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": formulas_body["data"]}
    ).execute()
    print("Summary formulas and Cash Flow updated in Portfolio tab.")
    
    # 3. Append to Transaction tab
    # Headers: ['Ticker', 'Stock Name', 'Transaction', 'Date', 'Quantity', 'Price', 'Dividend', 'Total Amount']
    transaction_body = {
        "values": [
            ["BTC", "Bitcoin", "Buy", "26/05/2026", btc_qty, btc_price, "", btc_amount]
        ]
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Transaction!A:H",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=transaction_body
    ).execute()
    print("BTC Buy Transaction appended to Transaction tab.")
    
    # 4. Update the portfolio_targets.json with the new cash level $529.37
    targets_path = os.path.join(script_dir, "portfolio_targets.json")
    if os.path.exists(targets_path):
        with open(targets_path, "r", encoding="utf-8") as f:
            targets_data = json.load(f)
        targets_data["cash"] = 529.37
        targets_data["updated"] = "2026-05-26T23:08:00.000000"
        with open(targets_path, "w", encoding="utf-8") as f:
            json.dump(targets_data, f, indent=2, ensure_ascii=False)
        print("portfolio_targets.json cash buffer updated to $529.37.")

if __name__ == "__main__":
    main()

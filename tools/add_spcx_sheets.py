#!/usr/bin/env python3
import os
import sys
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
    
    # 1. Update Portfolio tab Row 10 (SPCX) and formulas
    # We will write:
    # A10: 'SPCX', B10: 'SpaceX', C10: 'Aerospace & Defense', D10: 1, E10: 480.63, F10: 480.63
    # G10: '=D10*F10', H10: '=D10*E10', I10: '=G10-H10', J10: '=I10/H10', K10: '=G10/$I$19'
    portfolio_body = {
        "values": [
            ["SPCX", "SpaceX", "Aerospace & Defense", 1, 480.63, 480.63, "=D10*F10", "=D10*E10", "=G10-H10", "=I10/H10", "=G10/$I$19"]
        ]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Portfolio!A10:K10",
        valueInputOption="USER_ENTERED",
        body=portfolio_body
    ).execute()
    print("Portfolio Row 10 (SPCX) updated.")
    
    # 2. Update summary formulas:
    # Row 13 (Total Cost): I13 -> '=SUM(H2:H10)'
    # Row 14 (Total Gain/Loss): I14 -> '=SUM(I2:I10)'
    # Row 16 (Total Equity): I16 -> '=SUM(G2:G10)'
    # Row 17 (Cash Flow): I17 -> 979.37 (since $1460 - $480.63 = $979.37)
    formulas_body = {
        "data": [
            {"range": "Portfolio!I13", "values": [["=SUM(H2:H10)"]]},
            {"range": "Portfolio!I14", "values": [["=SUM(I2:I10)"]]},
            {"range": "Portfolio!I16", "values": [["=SUM(G2:G10)"]]},
            {"range": "Portfolio!I17", "values": [[979.37]]}
        ]
    }
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": formulas_body["data"]}
    ).execute()
    print("Summary formulas and Cash Flow updated in Portfolio tab.")
    
    # 3. Append to Transaction tab
    # Headers: ['Ticker', 'Stock Name', 'Transaction', 'Date', 'Quantity', 'Price', 'Dividend', 'Total Amount']
    # Date should be Gregorian serial format or a text date like '26/05/2026'
    transaction_body = {
        "values": [
            ["SPCX", "SpaceX", "Buy", "26/05/2026", 1, 480.63, "", 480.63]
        ]
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Transaction!A:H",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=transaction_body
    ).execute()
    print("SPCX Buy Transaction appended to Transaction tab.")
    
    # 4. Update the portfolio_targets.json with the new cash level $979.37
    targets_path = os.path.join(script_dir, "portfolio_targets.json")
    if os.path.exists(targets_path):
        with open(targets_path, "r", encoding="utf-8") as f:
            targets_data = json.load(f)
        targets_data["cash"] = 979.37
        targets_data["updated"] = "2026-05-26T22:55:00.000000"
        with open(targets_path, "w", encoding="utf-8") as f:
            json.dump(targets_data, f, indent=2, ensure_ascii=False)
        print("portfolio_targets.json cash buffer updated to $979.37.")

if __name__ == "__main__":
    import json
    main()

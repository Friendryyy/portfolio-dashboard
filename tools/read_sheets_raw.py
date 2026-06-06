#!/usr/bin/env python3
import os
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
        return
        
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build("sheets", "v4", credentials=creds)
    
    res = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Portfolio!A:K",
        valueRenderOption="UNFORMATTED_VALUE"
    ).execute()
    
    vals = res.get("values", [])
    print("--- PORTFOLIO ROW-BY-ROW DETAILS ---")
    headers = vals[0] if vals else []
    print(f"Headers: {headers}")
    for idx, row in enumerate(vals[1:]):
        if row and any(x for x in row):
            # Print row index and first few fields
            print(f"Row {idx+2}: {row}")

if __name__ == "__main__":
    main()

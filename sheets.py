# sheets.py
import requests
from datetime import datetime
import streamlit as st

NOCODEAPI_URL = st.secrets["nocodeapi"]["url"]

def save_score_to_sheet(user, score, category):
    timestamp = datetime.now().isoformat()
    row = [[user, score, category, timestamp]]
    payload = {
        "tabId": "Sheet1",
        "data": row
    }
    r = requests.post(f"{NOCODEAPI_URL}/append", json=payload)
    r.raise_for_status()

def load_scores_from_sheet():
    r = requests.get(f"{NOCODEAPI_URL}?tabId=Sheet1")
    r.raise_for_status()
    data = r.json()
    rows = data.get("data", [])[1:]  # Skip header
    scores = [
        {"user": row[0], "score": int(row[1]), "category": row[2], "timestamp": row[3]}
        for row in rows if len(row) == 4
    ]
    return sorted(scores, key=lambda x: x["score"], reverse=True)

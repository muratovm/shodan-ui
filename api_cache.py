import sqlite3
from datetime import datetime
import pandas as pd
import json

class APICache:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS api_cache (
            query TEXT PRIMARY KEY, 
            timestamp INTEGER,
            results TEXT)"""
        )
        self.conn.commit()

    def save_results(self, query, results):
        timestamp = int(datetime.now().timestamp())
        json_string = json.dumps(results)
        self.cursor.execute(
            "INSERT OR REPLACE INTO api_cache (query, timestamp, results) VALUES (?, ?, ?)", (query, timestamp,json_string)
        )
        self.conn.commit()
    
    def get_results(self, query):
        self.cursor.execute("SELECT results FROM api_cache WHERE query=?", (query,))
        results = self.cursor.fetchone()
        if results:
            return results[0]
        return None
    
    def get_dataframe(self):
        #select all elements
        self.cursor.execute("SELECT * FROM api_cache")
        results = self.cursor.fetchall()
        results = pd.DataFrame(results, columns=['query', 'timestamp', 'results'])
        return results
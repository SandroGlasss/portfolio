import sqlite3
import json
from datetime import datetime

def backup_database():
    # Connect to your database
    conn = sqlite3.connect('instance/portfolio.db')
    cursor = conn.cursor()
    
    # Get all data
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    
    cursor.execute("SELECT * FROM article")
    articles = cursor.fetchall()
    
    cursor.execute("SELECT * FROM comment")
    comments = cursor.fetchall()
    
    # Store data in a dictionary
    backup = {
        'users': users,
        'articles': articles,
        'comments': comments
    }
    
    # Save to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'backup_{timestamp}.json', 'w') as f:
        json.dump(backup, f)
    
    conn.close()
    print(f"Backup created: backup_{timestamp}.json")

if __name__ == "__main__":
    backup_database()
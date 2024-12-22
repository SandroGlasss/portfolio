import sqlite3
import json
from datetime import datetime

def restore_database():
    try:
        # Load backup data
        with open('backup_20241220_100300.json', 'r') as f:
            backup = json.load(f)
        
            # Connect to new database
            conn = sqlite3.connect('instance/portfolio.db')
            cursor = conn.cursor()
            
            # Restore users
            for user in backup['users']:
                cursor.execute("""
                    INSERT INTO user (id, username, password, role)
                    VALUES (?, ?, ?, 'admin')
                """, (user[0], user[1], user[2]))
            
            # Restore articles
            for article in backup['articles']:
                cursor.execute("""
                    INSERT INTO article (id, title, content, publication, date_published, 
                                       category, user_id, image_filename)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, article)
            
            # Restore comments
            for comment in backup['comments']:
                cursor.execute("""
                    INSERT INTO comment (id, content, created_at, article_id, user_id)
                    VALUES (?, ?, ?, ?, ?)
                """, comment)
            
            conn.commit()
            conn.close()
            print("Database restored successfully!")
        
    except Exception as e:
        print(f"Error restoring database: {e}")

if __name__ == "__main__":
    restore_database()
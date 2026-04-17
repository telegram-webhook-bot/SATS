import sqlite3
from datetime import datetime

DB_PATH = "sats_bot.db"

def fix_remaining_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns_to_add = [
        ("signals", "status", "TEXT DEFAULT 'ACTIVE'"),
        ("signals", "score", "REAL"),
    ]
    
    for table, column, definition in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            print(f"➕ 新增 {table}.{column} 欄位...")
            
            # 更新舊數據
            if column == "status":
                cursor.execute(f"UPDATE {table} SET {column} = 'ACTIVE' WHERE {column} IS NULL")
                print(f"   📝 更新 {table}.{column} 預設值...")
            elif column == "score":
                cursor.execute(f"UPDATE {table} SET {column} = 0.0 WHERE {column} IS NULL")
                print(f"   📝 更新 {table}.{column} 預設值...")
            
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️ 警告 {table}.{column}: {e}")
            else:
                print(f"✓ {table}.{column} 已存在")
    
    conn.close()
    print("\n✅ 所有欄位修復完成！請重新執行 python view_history.py")

if __name__ == "__main__":
    fix_remaining_columns()
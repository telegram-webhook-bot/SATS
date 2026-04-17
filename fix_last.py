import sqlite3
from datetime import datetime

DB_PATH = "sats_bot.db"

def fix_final_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns_to_add = [
        ("symbol_stats", "last_updated", "TIMESTAMP"),
        ("tp_sl_events", "triggered_at", "TIMESTAMP"),
    ]
    
    for table, column, dtype in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {dtype}")
            print(f"➕ 新增 {table}.{column} 欄位...")
            
            # 更新舊數據為當前時間
            cursor.execute(f"UPDATE {table} SET {column} = ?", (datetime.now().isoformat(),))
            print(f"   📝 更新 {table} 舊數據時間戳...")
            
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️ 警告 {table}.{column}: {e}")
            else:
                print(f"✓ {table}.{column} 已存在")
    
    conn.close()
    print("\n✅ 所有欄位修復完成！請重新執行 python view_history.py")

if __name__ == "__main__":
    fix_final_columns()
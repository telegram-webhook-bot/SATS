import sqlite3
import os

DB_PATH = 'sats_bot.db'

def fix_database():
    if not os.path.exists(DB_PATH):
        print(f"錯誤：找不到資料庫檔案 {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔍 開始檢查並修復資料庫結構...")
    
    # 1. 修復 signals 表
    try:
        # 檢查 signal_type 是否存在
        cursor.execute("PRAGMA table_info(signals)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'signal_type' not in columns:
            print("➕ 新增 signals.signal_type 欄位...")
            cursor.execute("ALTER TABLE signals ADD COLUMN signal_type TEXT DEFAULT 'LONG'")
        
        if 'entry_price' not in columns:
            print("➕ 新增 signals.entry_price 欄位...")
            cursor.execute("ALTER TABLE signals ADD COLUMN entry_price REAL")
            
        if 'score' not in columns:
            print("➕ 新增 signals.score 欄位...")
            cursor.execute("ALTER TABLE signals ADD COLUMN score REAL")
            
    except Exception as e:
        print(f"修復 signals 表時出錯：{e}")

    # 2. 修復 trade_closes 表
    try:
        cursor.execute("PRAGMA table_info(trade_closes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'pnl' not in columns:
            print("➕ 新增 trade_closes.pnl 欄位...")
            cursor.execute("ALTER TABLE trade_closes ADD COLUMN pnl REAL")
            
        if 'pnl_percent' not in columns:
            print("➕ 新增 trade_closes.pnl_percent 欄位...")
            cursor.execute("ALTER TABLE trade_closes ADD COLUMN pnl_percent REAL")
            
        if 'exit_reason' not in columns:
            print("➕ 新增 trade_closes.exit_reason 欄位...")
            cursor.execute("ALTER TABLE trade_closes ADD COLUMN exit_reason TEXT")
            
    except Exception as e:
        print(f"修復 trade_closes 表時出錯：{e}")

    # 3. 修復 symbol_stats 表
    try:
        cursor.execute("PRAGMA table_info(symbol_stats)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'winning_trades' not in columns:
            print("➕ 新增 symbol_stats.winning_trades 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN winning_trades INTEGER DEFAULT 0")
            
        if 'losing_trades' not in columns:
            print("➕ 新增 symbol_stats.losing_trades 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN losing_trades INTEGER DEFAULT 0")
            
        if 'win_rate' not in columns:
            print("➕ 新增 symbol_stats.win_rate 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN win_rate REAL DEFAULT 0.0")
            
        if 'total_pnl' not in columns:
            print("➕ 新增 symbol_stats.total_pnl 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN total_pnl REAL DEFAULT 0.0")
            
        if 'avg_pnl' not in columns:
            print("➕ 新增 symbol_stats.avg_pnl 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN avg_pnl REAL DEFAULT 0.0")
            
        if 'max_profit' not in columns:
            print("➕ 新增 symbol_stats.max_profit 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN max_profit REAL DEFAULT 0.0")
            
        if 'max_loss' not in columns:
            print("➕ 新增 symbol_stats.max_loss 欄位...")
            cursor.execute("ALTER TABLE symbol_stats ADD COLUMN max_loss REAL DEFAULT 0.0")
            
    except Exception as e:
        print(f"修復 symbol_stats 表時出錯：{e}")

    # 4. 修復 tp_sl_events 表
    try:
        cursor.execute("PRAGMA table_info(tp_sl_events)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tp_level' not in columns:
            print("➕ 新增 tp_sl_events.tp_level 欄位...")
            cursor.execute("ALTER TABLE tp_sl_events ADD COLUMN tp_level TEXT")
            
        if 'trigger_price' not in columns:
            print("➕ 新增 tp_sl_events.trigger_price 欄位...")
            cursor.execute("ALTER TABLE tp_sl_events ADD COLUMN trigger_price REAL")
            
        if 'pnl_locked' not in columns:
            print("➕ 新增 tp_sl_events.pnl_locked 欄位...")
            cursor.execute("ALTER TABLE tp_sl_events ADD COLUMN pnl_locked REAL")
            
    except Exception as e:
        print(f"修復 tp_sl_events 表時出錯：{e}")

    conn.commit()
    conn.close()
    print("✅ 資料庫修復完成！請重新執行 python view_history.py")

if __name__ == "__main__":
    fix_database()
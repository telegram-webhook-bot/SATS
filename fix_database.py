#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SATS Bot 資料庫結構自動修復工具
自動偵測並新增缺失欄位，解決版本升級帶來的相容性問題
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "sats_bot.db"
BACKUP_PATH = f"sats_bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def get_connection():
    """獲取資料庫連線"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 錯誤：找不到資料庫檔案 {DB_PATH}")
        print("   請確認您已在該目錄下運行過 SATS Bot")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        print(f"❌ 無法連接資料庫：{e}")
        return None

def backup_database():
    """備份資料庫"""
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✓ 已備份資料庫至：{BACKUP_PATH}")
        return True
    return False

def get_table_columns(conn, table_name):
    """獲取表的所有欄位"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def add_column_if_missing(conn, table_name, column_name, column_type, default_value=None):
    """如果欄位不存在則新增"""
    columns = get_table_columns(conn, table_name)
    
    if column_name not in columns:
        print(f"  ⚠️  {table_name} 表缺少欄位：{column_name}")
        
        # 建構 ALTER TABLE 語句
        if default_value is not None:
            if isinstance(default_value, str):
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'"
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
        else:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            print(f"  ✓ 已新增欄位：{column_name} ({column_type})")
            return True
        except Exception as e:
            print(f"  ❌ 新增欄位失敗：{e}")
            return False
    else:
        print(f"  ✓ {table_name}.{column_name} 已存在")
        return True

def fix_signals_table(conn):
    """修復 signals 表"""
    print("\n🔧 檢查 signals 表...")
    
    columns_to_add = [
        ("signal_type", "TEXT", "LONG"),
        ("entry_price", "REAL", "0.0"),
        ("score", "REAL", "0.0"),
        ("status", "TEXT", "PENDING"),
        ("exit_price", "REAL", "0.0"),
        ("pnl", "REAL", "0.0"),
        ("pnl_percent", "REAL", "0.0"),
        ("exit_reason", "TEXT", ""),
        ("closed_at", "TEXT", "")
    ]
    
    success = True
    for col_name, col_type, default in columns_to_add:
        if not add_column_if_missing(conn, "signals", col_name, col_type, default):
            success = False
    
    return success

def fix_trade_closes_table(conn):
    """修復 trade_closes 表"""
    print("\n🔧 檢查 trade_closes 表...")
    
    columns_to_add = [
        ("signal_type", "TEXT", "LONG"),
        ("entry_price", "REAL", "0.0"),
        ("exit_price", "REAL", "0.0"),
        ("pnl", "REAL", "0.0"),
        ("pnl_percent", "REAL", "0.0"),
        ("exit_reason", "TEXT", "")
    ]
    
    success = True
    for col_name, col_type, default in columns_to_add:
        if not add_column_if_missing(conn, "trade_closes", col_name, col_type, default):
            success = False
    
    return success

def fix_symbol_stats_table(conn):
    """修復 symbol_stats 表"""
    print("\n🔧 檢查 symbol_stats 表...")
    
    columns_to_add = [
        ("winning_trades", "INTEGER", "0"),
        ("losing_trades", "INTEGER", "0"),
        ("win_rate", "REAL", "0.0"),
        ("total_pnl", "REAL", "0.0"),
        ("avg_pnl", "REAL", "0.0"),
        ("max_profit", "REAL", "0.0"),
        ("max_loss", "REAL", "0.0")
    ]
    
    success = True
    for col_name, col_type, default in columns_to_add:
        if not add_column_if_missing(conn, "symbol_stats", col_name, col_type, default):
            success = False
    
    return success

def fix_tp_sl_events_table(conn):
    """修復 tp_sl_events 表"""
    print("\n🔧 檢查 tp_sl_events 表...")
    
    columns_to_add = [
        ("tp_level", "TEXT", ""),
        ("price", "REAL", "0.0"),
        ("triggered_at", "TEXT", "")
    ]
    
    success = True
    for col_name, col_type, default in columns_to_add:
        if not add_column_if_missing(conn, "tp_sl_events", col_name, col_type, default):
            success = False
    
    return success

def update_existing_records(conn):
    """更新現有記錄以填充新欄位"""
    print("\n🔄 更新現有數據...")
    
    cursor = conn.cursor()
    
    # 嘗試從 trade_closes 更新 signals 的 pnl 相關欄位
    try:
        cursor.execute("""
            UPDATE signals 
            SET pnl = (SELECT pnl FROM trade_closes WHERE trade_closes.signal_id = signals.id),
                pnl_percent = (SELECT pnl_percent FROM trade_closes WHERE trade_closes.signal_id = signals.id),
                exit_price = (SELECT exit_price FROM trade_closes WHERE trade_closes.signal_id = signals.id),
                exit_reason = (SELECT exit_reason FROM trade_closes WHERE trade_closes.signal_id = signals.id),
                closed_at = (SELECT closed_at FROM trade_closes WHERE trade_closes.signal_id = signals.id)
            WHERE status != 'PENDING' AND pnl IS NULL
        """)
        conn.commit()
        print(f"  ✓ 更新了 {cursor.rowcount} 筆 signals 記錄")
    except Exception as e:
        print(f"  ⚠️ 更新 signals 記錄時出錯（可忽略）：{e}")
    
    # 計算 symbol_stats
    try:
        cursor.execute("""
            UPDATE symbol_stats 
            SET winning_trades = (
                SELECT COUNT(*) FROM trade_closes tc 
                JOIN signals s ON tc.signal_id = s.id 
                WHERE s.symbol = symbol_stats.symbol AND tc.pnl > 0
            ),
            losing_trades = (
                SELECT COUNT(*) FROM trade_closes tc 
                JOIN signals s ON tc.signal_id = s.id 
                WHERE s.symbol = symbol_stats.symbol AND tc.pnl <= 0
            ),
            total_pnl = (
                SELECT COALESCE(SUM(tc.pnl), 0) FROM trade_closes tc 
                JOIN signals s ON tc.signal_id = s.id 
                WHERE s.symbol = symbol_stats.symbol
            )
        """)
        conn.commit()
        
        # 計算勝率
        cursor.execute("""
            UPDATE symbol_stats 
            SET win_rate = CASE 
                WHEN total_trades > 0 THEN ROUND(winning_trades * 100.0 / total_trades, 2)
                ELSE 0
            END,
            avg_pnl = CASE 
                WHEN total_trades > 0 THEN ROUND(total_pnl / total_trades, 2)
                ELSE 0
            END
        """)
        conn.commit()
        print("  ✓ 已更新 symbol_stats 統計數據")
    except Exception as e:
        print(f"  ⚠️ 更新 symbol_stats 時出錯（可忽略）：{e}")

def main():
    print("=" * 80)
    print("🔧 SATS Bot 資料庫結構自動修復工具")
    print("=" * 80)
    print()
    
    # 備份
    if not backup_database():
        print("❌ 備份失敗，終止操作")
        return
    
    # 連接資料庫
    conn = get_connection()
    if not conn:
        return
    
    try:
        # 修復各表
        results = []
        results.append(("signals", fix_signals_table(conn)))
        results.append(("trade_closes", fix_trade_closes_table(conn)))
        results.append(("symbol_stats", fix_symbol_stats_table(conn)))
        results.append(("tp_sl_events", fix_tp_sl_events_table(conn)))
        
        # 更新數據
        update_existing_records(conn)
        
        # 報告
        print("\n" + "=" * 80)
        print("📋 修復報告")
        print("=" * 80)
        
        all_success = all(result[1] for result in results)
        
        if all_success:
            print("✅ 所有表結構修復成功！")
            print("\n現在可以執行：python view_history.py")
        else:
            print("⚠️ 部分表修復失敗，請檢查上方錯誤訊息")
            print("   如需協助，請提供錯誤訊息給開發者")
        
        # 顯示當前表結構
        print("\n📊 當前資料庫結構:")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            columns = get_table_columns(conn, table_name)
            print(f"  {table_name}: {', '.join(columns)}")
        
    except Exception as e:
        print(f"\n❌ 修復過程發生錯誤：{e}")
        print(f"   可還原備份：{BACKUP_PATH}")
    finally:
        conn.close()
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

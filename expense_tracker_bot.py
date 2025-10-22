# -*- coding: utf-8 -*-
# Expense Tracker Bot - Railway Ready Version

import os
import sqlite3
import time
from datetime import datetime
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB = "expenses.db"

# --- Database ---
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            note TEXT,
            ts INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Functions ---
def add_expense(user_id, amount, category, note):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO expenses(user_id, amount, category, note, ts) VALUES(?,?,?,?,?)",
              (user_id, amount, category, note, int(time.time())))
    conn.commit()
    conn.close()

def get_summary(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (user_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return "No expenses recorded yet."
    summary = "💰 *Expense Summary:*\n\n"
    for cat, total in rows:
        summary += f"• {cat}: {total:.2f}\n"
    return summary

# --- Commands ---
def help_cmd(update, context):
    update.message.reply_text(
        "📘 *Expense Tracker Bot*\n\n"
        "/add 150 food lunch - Add expense\n"
        "/summary - Show total summary\n"
        "/help - Show this help\n",
        parse_mode=ParseMode.MARKDOWN
    )

def add_cmd(update, context):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /add <amount> <category> [note]")
        return
    try:
        amount = float(args[0])
    except ValueError:
        update.message.reply_text("❌ Amount must be a number")
        return
    category = args[1]
    note = " ".join(args[2:]) if len(args) > 2 else ""
    add_expense(update.effective_user.id, amount, category, note)
    update.message.reply_text(f"✅ Added {amount} to {category}")

def summary_cmd(update, context):
    update.message.reply_text(get_summary(update.effective_user.id), parse_mode=ParseMode.MARKDOWN)

# --- Main ---
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("add", add_cmd))
    dp.add_handler(CommandHandler("summary", summary_cmd))
    updater.start_polling()
    print("🤖 Expense Tracker Bot running...")
    updater.idle()

if __name__ == "__main__":
    main()

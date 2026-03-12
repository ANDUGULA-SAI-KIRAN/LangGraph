from fastmcp import FastMCP
import os
import sqlite3
import json
from datetime import datetime

# Paths
DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

def load_categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

init_db()

@mcp.tool()
def add_expense(amount: float, category: str, subcategory: str = "other", note: str = "", date: str = None):
    """
    Add a new expense. 
    - date: Format 'YYYY-MM-DD'. If omitted, today's date is used.
    - category/subcategory: Must match the provided categories list.
    """
    # Default to today
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Validation against JSON
    cats = load_categories()
    if category not in cats:
        return {"error": f"Invalid category. Must be one of: {list(cats.keys())}"}
    if subcategory not in cats[category]:
        return {"error": f"Invalid subcategory for {category}. Valid: {cats[category]}"}

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "success", "id": cur.lastrowid, "message": f"Logged ${amount} for {subcategory}"}

@mcp.tool()
def search_expenses(query: str):
    """Search for expenses by matching text in the note or category fields."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "SELECT * FROM expenses WHERE note LIKE ? OR category LIKE ? OR subcategory LIKE ? ORDER BY date DESC",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def summarize_spending(start_date: str, end_date: str):
    """Provides a breakdown of spending by category and total for a date range."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT category, SUM(amount) as total, COUNT(*) as count 
            FROM expenses 
            WHERE date BETWEEN ? AND ? 
            GROUP BY category
            """,
            (start_date, end_date)
        )
        results = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
        total_sum = sum(item['total'] for item in results)
        return {"period": f"{start_date} to {end_date}", "breakdown": results, "total_period_spending": total_sum}

@mcp.tool()
def delete_expense(expense_id: int):
    """Delete an expense entry by its ID."""
    with sqlite3.connect(DB_PATH) as c:
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        return {"status": "deleted", "id": expense_id}

@mcp.resource("expense://categories")
def get_category_list() -> str:
    """Returns the valid categories and subcategories JSON."""
    with open(CATEGORIES_PATH, "r") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()
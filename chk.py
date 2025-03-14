"""
Expense Tracker using Python

Develop an Expense Tracker that helps users log daily expenses. 
Use Tkinter for the GUI and SQLite to save expense records. 
Add features like monthly summaries and category-based expense tracking.

Key Features:

Add/Edit/Delete Expenses
Monthly Summary Report
Category-based Analysis
"""

import sqlite3
import ttkbootstrap as tb  # Modern UI styling
import matplotlib.pyplot as plt
from ttkbootstrap.widgets import DateEntry
from tkinter import ttk, messagebox

# Database Setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    amount REAL,
    category TEXT,
    description TEXT
)""")
conn.commit()
conn.close()

# Expense Tracker Class
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker 💰")
        self.root.geometry("900x550")

        # UI Theme
        self.style = tb.Style("flatly")

        # Input Frame
        input_frame = tb.Frame(root, padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Date Entry
        tb.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=12)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Amount Entry
        tb.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=5, pady=5)
        self.amount_entry = tb.Entry(input_frame, width=12)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Category Selection
        tb.Label(input_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = tb.Combobox(input_frame, values=["Food", "Transport", "Bills", "Shopping", "Others"], width=12)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)
        self.category_entry.set("Food")  # Default selection

        # Description Entry
        tb.Label(input_frame, text="Description:").grid(row=1, column=2, padx=5, pady=5)
        self.desc_entry = tb.Entry(input_frame, width=20)
        self.desc_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        button_frame = tb.Frame(root, padding=10)
        button_frame.pack(fill="x")
        
        tb.Button(button_frame, text="➕ Add Expense", command=self.add_expense).pack(side="left", padx=10, pady=5)
        tb.Button(button_frame, text="🗑 Delete Expense", command=self.delete_expense).pack(side="left", padx=10, pady=5)
        tb.Button(button_frame, text="📊 Monthly Summary", command=self.monthly_summary).pack(side="left", padx=10, pady=5)
        tb.Button(button_frame, text="📈 Category Analysis", command=self.category_analysis).pack(side="left", padx=10, pady=5)

        # Expense Table
        self.tree = ttk.Treeview(root, columns=("ID", "Date", "Amount", "Category", "Description"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")

        for col in ("ID", "Date", "Amount", "Category", "Description"):
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Load existing expenses
        self.load_expenses()

    def add_expense(self):
        date = self.date_entry.entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        description = self.desc_entry.get()

        if not (date and amount and category):
            messagebox.showerror("Input Error", "Please fill all required fields!")
            return

        try:
            amount = float(amount)  # Validate numeric input
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number!")
            return

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                       (date, amount, category, description))
        conn.commit()
        conn.close()
        self.load_expenses()

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select an expense to delete")
            return

        item_id = self.tree.item(selected_item)['values'][0]

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        self.load_expenses()

    def load_expenses(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def monthly_summary(self):
        month = self.date_entry.entry.get()[:7]  # Extract YYYY-MM
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month + "%",))
        total = cursor.fetchone()[0]
        conn.close()
        messagebox.showinfo("Monthly Summary", f"Total Expense for {month}: {total if total else 0} USD")

    def category_analysis(self):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("Category Analysis", "No data available!")
            return

        categories, amounts = zip(*data)

        # Create Pie Chart
        plt.figure(figsize=(10, 4))

        # Pie Chart
        plt.subplot(1, 2, 1)
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Expense Distribution by Category")

        # Bar Graph
        plt.subplot(1, 2, 2)
        plt.bar(categories, amounts, color=['blue', 'green', 'red', 'purple', 'orange'])
        plt.xlabel("Category")
        plt.ylabel("Total Amount Spent")
        plt.title("Expenses by Category")

        plt.tight_layout()
        plt.show()

# Run the Application
if __name__ == "__main__":
    root = tb.Window(themename="flatly")  # ttkbootstrap-enhanced window
    app = ExpenseTracker(root)
    root.mainloop()

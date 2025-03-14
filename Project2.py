import sqlite3  # Database handling
import tkinter as tk  # GUI library
from tkinter import ttk, messagebox  # Additional UI components
import matplotlib.pyplot as plt  # Data visualization
from datetime import datetime  # Handling date operations

# Database Setup Function
def setup_database():
    """Creates the database and the 'expenses' table if it doesn't exist."""
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
        """Initializes the GUI components."""
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x500")

        # Labels & Entry Fields
        tk.Label(root, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Amount:").grid(row=1, column=0, padx=10, pady=5)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(root, text="Category:").grid(row=2, column=0, padx=10, pady=5)
        self.category_entry = tk.Entry(root)
        self.category_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(root, text="Description:").grid(row=3, column=0, padx=10, pady=5)
        self.desc_entry = tk.Entry(root)
        self.desc_entry.grid(row=3, column=1, padx=10, pady=5)

        # Buttons for functionality
        tk.Button(root, text="Add Expense", command=self.add_expense).grid(row=4, column=0, padx=10, pady=5)
        tk.Button(root, text="Delete Expense", command=self.delete_expense).grid(row=4, column=1, padx=10, pady=5)
        tk.Button(root, text="Monthly Summary", command=self.monthly_summary).grid(row=4, column=2, padx=10, pady=5)
        tk.Button(root, text="Category Analysis", command=self.category_analysis).grid(row=4, column=3, padx=10, pady=5)

        # Expense List Display
        self.tree = ttk.Treeview(root, columns=("ID", "Date", "Amount", "Category", "Description"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")
        self.tree.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

        self.load_expenses()  # Load existing expenses into the list

    def add_expense(self):
        """Adds a new expense entry to the database."""
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        description = self.desc_entry.get()

        if date and amount and category:  # Ensure required fields are filled
            conn = sqlite3.connect("expenses.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                           (date, float(amount), category, description))
            conn.commit()
            conn.close()
            self.load_expenses()  # Refresh expense list
        else:
            messagebox.showerror("Input Error", "Please fill all fields")

    def delete_expense(self):
        """Deletes the selected expense entry from the database."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select an expense to delete")
            return
        
        item_id = self.tree.item(selected_item)['values'][0]  # Get selected expense ID
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        self.load_expenses()  # Refresh list after deletion

    def load_expenses(self):
        """Loads all expenses from the database into the table view."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def monthly_summary(self):
        """Displays the total expenses for the given month."""
        month = self.date_entry.get()[:7]  # Extract YYYY-MM from input
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month + "%",))
        total = cursor.fetchone()[0]
        conn.close()

        messagebox.showinfo("Monthly Summary", f"Total Expense for {month}: {total if total else 0}")

    def category_analysis(self):
        """Displays a pie chart & bar chart for expense distribution."""
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        category_data = cursor.fetchall()

        cursor.execute("SELECT SUBSTR(date, 1, 7) AS month, SUM(amount) FROM expenses GROUP BY month ORDER BY month")
        monthly_data = cursor.fetchall()
        conn.close()

        if not category_data and not monthly_data:
            messagebox.showinfo("Analysis", "No data available")
            return

        # Prepare category data
        categories, amounts = zip(*category_data) if category_data else ([], [])
        
        # Prepare monthly data
        months, month_totals = zip(*monthly_data) if monthly_data else ([], [])

        # Create subplots
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        fig.subplots_adjust(wspace=0.5)  # Adjust horizontal space between plots

        # Pie Chart
        axs[0].pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        axs[0].set_title("Expense Distribution by Category")

        # Bar Chart
        axs[1].bar(months, month_totals, color='skyblue')
        axs[1].set_title("Monthly Expense Trend")
        axs[1].set_ylabel("Total Expenses ($)")
        axs[1].set_xticklabels(months, rotation=45)

        plt.show()

# Run the application
if __name__ == "__main__":
    setup_database()  # Create database & table if not present
    root = tk.Tk()  # Initialize Tkinter
    app = ExpenseTracker(root)  # Create the application object
    root.mainloop()  # Run the Tkinter event loop

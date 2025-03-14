"""
Expense Tracker using Python

Develop an Expense Tracker that helps users log daily expenses. 
Use Tkinter for the GUI and SQLite to save expense records. 
Add features like monthly summaries and category-based expense tracking.

Key Features:
- Add/Edit/Delete Expenses
- Monthly Summary Report
- Category-based Analysis
"""

import sqlite3  # For database operations
import ttkbootstrap as tb  # Modern UI styling for Tkinter
import matplotlib.pyplot as plt  # For creating charts
from ttkbootstrap.widgets import DateEntry  # For date input
from tkinter import ttk, messagebox  # Tkinter widgets and message boxes

# Database Setup
conn = sqlite3.connect("expenses.db")  # Connect to SQLite database (creates if it doesn't exist)
cursor = conn.cursor()
# Create a table named 'expenses' if it doesn't already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each expense
    date TEXT,                            -- Date of the expense
    amount REAL,                          -- Amount spent
    category TEXT,                        -- Category of the expense
    description TEXT                      -- Additional description
)""")
conn.commit()  # Save changes to the database
conn.close()  # Close the database connection

# Expense Tracker Class
class ExpenseTracker:
    def __init__(self, root):
        self.root = root  # Root window for the application
        self.root.title("Expense Tracker 💰")  # Set window title
        self.root.geometry("900x550")  # Set window size

        # UI Theme (using ttkbootstrap for modern styling)
        self.style = tb.Style("flatly")

        # Input Frame (to hold input fields)
        input_frame = tb.Frame(root, padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Date Entry
        tb.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)  # Label for date
        self.date_entry = DateEntry(input_frame, width=12)  # Date picker widget
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Amount Entry
        tb.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=5, pady=5)  # Label for amount
        self.amount_entry = tb.Entry(input_frame, width=12)  # Text entry for amount
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Category Selection
        tb.Label(input_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)  # Label for category
        self.category_entry = tb.Combobox(input_frame, values=["Food", "Transport", "Bills", "Shopping", "Others"], width=12)  # Dropdown for categories
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)
        self.category_entry.set("Food")  # Default selection

        # Description Entry
        tb.Label(input_frame, text="Description:").grid(row=1, column=2, padx=5, pady=5)  # Label for description
        self.desc_entry = tb.Entry(input_frame, width=20)  # Text entry for description
        self.desc_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons Frame (to hold action buttons)
        button_frame = tb.Frame(root, padding=10)
        button_frame.pack(fill="x")
        
        # Add Expense Button
        tb.Button(button_frame, text="➕ Add Expense", command=self.add_expense).pack(side="left", padx=10, pady=5)
        # Delete Expense Button
        tb.Button(button_frame, text="🗑 Delete Expense", command=self.delete_expense).pack(side="left", padx=10, pady=5)
        # Monthly Summary Button
        tb.Button(button_frame, text="📊 Monthly Summary", command=self.monthly_summary).pack(side="left", padx=10, pady=5)
        # Category Analysis Button
        tb.Button(button_frame, text="📈 Category Analysis", command=self.category_analysis).pack(side="left", padx=10, pady=5)

        # Expense Table (to display expenses in a table format)
        self.tree = ttk.Treeview(root, columns=("ID", "Date", "Amount", "Category", "Description"), show="headings")
        self.tree.heading("ID", text="ID")  # Column for ID
        self.tree.heading("Date", text="Date")  # Column for Date
        self.tree.heading("Amount", text="Amount")  # Column for Amount
        self.tree.heading("Category", text="Category")  # Column for Category
        self.tree.heading("Description", text="Description")  # Column for Description

        # Set column widths and alignment
        for col in ("ID", "Date", "Amount", "Category", "Description"):
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Load existing expenses into the table
        self.load_expenses()

    def add_expense(self):
        # Get input values
        date = self.date_entry.entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        description = self.desc_entry.get()

        # Validate input fields
        if not (date and amount and category):
            messagebox.showerror("Input Error", "Please fill all required fields!")
            return

        # Validate amount is a number
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number!")
            return

        # Save expense to the database
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                       (date, amount, category, description))
        conn.commit()
        conn.close()
        self.load_expenses()  # Refresh the table

    def delete_expense(self):
        # Get selected item from the table
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select an expense to delete")
            return

        # Get the ID of the selected expense
        item_id = self.tree.item(selected_item)['values'][0]

        # Delete the expense from the database
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        self.load_expenses()  # Refresh the table

    def load_expenses(self):
        # Clear existing data in the table
        self.tree.delete(*self.tree.get_children())

        # Fetch all expenses from the database
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        # Insert fetched data into the table
        for row in rows:
            self.tree.insert("", "end", values=row)

    def monthly_summary(self):
        # Extract year and month from the selected date
        month = self.date_entry.entry.get()[:7]  # Format: YYYY-MM

        # Fetch total expenses for the selected month
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month + "%",))
        total = cursor.fetchone()[0]
        conn.close()

        # Show the total in a message box
        messagebox.showinfo("Monthly Summary", f"Total Expense for {month}: {total if total else 0} USD")

    def category_analysis(self):
        # Fetch category-wise total expenses from the database
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = cursor.fetchall()
        conn.close()

        # Check if data is available
        if not data:
            messagebox.showinfo("Category Analysis", "No data available!")
            return

        # Separate categories and amounts for plotting
        categories, amounts = zip(*data)

        # Create a figure for charts
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
        plt.show()  # Display the charts

# Run the Application
if __name__ == "__main__":
    root = tb.Window(themename="flatly")  # Create a ttkbootstrap-enhanced window
    app = ExpenseTracker(root)  # Initialize the ExpenseTracker class
    root.mainloop()  # Start the Tkinter event loop

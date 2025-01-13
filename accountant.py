import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import webbrowser


# Database Setup
def initialize_database():
    with sqlite3.connect("shop.db") as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS Sellers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            date TEXT,
            total_amount REAL,
            outstanding REAL
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            amount REAL,
            date TEXT,
            type TEXT,
            FOREIGN KEY(customer_id) REFERENCES Customers(id)
        )''')


initialize_database()


# Seller Login
class SellerLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Confectionery Shop - Seller Login")
        self.geometry("400x300")
        self.resizable(False, False)

        tk.Label(self, text="Username:", font=("Arial", 12)).pack(pady=10)
        self.username = tk.Entry(self, font=("Arial", 12))
        self.username.pack()

        tk.Label(self, text="Password:", font=("Arial", 12)).pack(pady=10)
        self.password = tk.Entry(self, show="*", font=("Arial", 12))
        self.password.pack()

        tk.Button(self, text="Login", font=("Arial", 12), command=self.login).pack(pady=10)
        tk.Button(self, text="Register", font=("Arial", 12), command=self.register).pack()

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sellers WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()

        if user:
            self.destroy()
            ShopDashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Sellers (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Registration successful")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")


# Main Dashboard
class ShopDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Confectionery Shop - Dashboard")
        self.geometry("1000x600")

        self.tab_control = ttk.Notebook(self)

        # Customer Section
        self.customer_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.customer_tab, text="Customers")
        self.setup_customer_section()

        # Developer Section
        self.dev_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.dev_tab, text="Developer")
        self.setup_dev_section()

        self.tab_control.pack(expand=1, fill="both")
        self.load_customers()

    def setup_customer_section(self):
        tk.Label(self.customer_tab, text="Customer Management", font=("Arial", 16)).pack(pady=10)

        # Search Bar
        tk.Label(self.customer_tab, text="Search by Name:", font=("Arial", 12)).pack(pady=5)
        self.search_entry = tk.Entry(self.customer_tab, font=("Arial", 12))
        self.search_entry.pack()
        tk.Button(self.customer_tab, text="Search", font=("Arial", 12), command=self.search_customer).pack(pady=5)

        # Customer Table
        columns = ("id", "name", "phone", "date", "total", "outstanding")
        self.customer_table = ttk.Treeview(self.customer_tab, columns=columns, show="headings", height=15)

        for col in columns:
            self.customer_table.heading(col, text=col.capitalize())
            self.customer_table.column(col, width=120, anchor="center")

        self.customer_table.pack(fill="both", expand=True, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.customer_tab, orient="vertical", command=self.customer_table.yview)
        self.customer_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        tk.Button(self.customer_tab, text="Add Customer", font=("Arial", 12), command=self.add_customer).pack(side="left", padx=20, pady=10)
        tk.Button(self.customer_tab, text="Delete Customer", font=("Arial", 12), command=self.delete_customer).pack(side="left", padx=20, pady=10)

    def setup_dev_section(self):
        tk.Label(self.dev_tab, text="Developer: Harshit Mishra", font=("Arial", 16)).pack(pady=10)
        website_link = tk.Label(self.dev_tab, text="Website: mishraharshit.vercel.app", font=("Arial", 12), fg="blue", cursor="hand2")
        website_link.pack()
        website_link.bind("<Button-1>", lambda e: webbrowser.open("https://mishraharshit.vercel.app"))

    def load_customers(self):
        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Customers")
            customers = cursor.fetchall()

        for row in self.customer_table.get_children():
            self.customer_table.delete(row)

        for customer in customers:
            self.customer_table.insert("", "end", values=customer)

    def add_customer(self):
        AddCustomerPopup(self)

    def delete_customer(self):
        selected_item = self.customer_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No customer selected")
            return

        customer_id = self.customer_table.item(selected_item, "values")[0]
        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Customers WHERE id = ?", (customer_id,))
            conn.commit()

        self.load_customers()
        messagebox.showinfo("Success", "Customer deleted")

    def search_customer(self):
        search_term = self.search_entry.get()
        if not search_term:
            self.load_customers()
            return

        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Customers WHERE name LIKE ?", (f"%{search_term}%",))
            customers = cursor.fetchall()

        for row in self.customer_table.get_children():
            self.customer_table.delete(row)

        for customer in customers:
            self.customer_table.insert("", "end", values=customer)


# Add Customer Popup
class AddCustomerPopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Customer")
        self.geometry("400x300")
        self.resizable(False, False)

        tk.Label(self, text="Name:", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=10)
        self.name = tk.Entry(self, font=("Arial", 12))
        self.name.grid(row=0, column=1, pady=10)

        tk.Label(self, text="Phone:", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10)
        self.phone = tk.Entry(self, font=("Arial", 12))
        self.phone.grid(row=1, column=1, pady=10)

        tk.Label(self, text="Total Amount:", font=("Arial", 12)).grid(row=2, column=0, pady=10, padx=10)
        self.total_amount = tk.Entry(self, font=("Arial", 12))
        self.total_amount.grid(row=2, column=1, pady=10)

        tk.Label(self, text="Outstanding:", font=("Arial", 12)).grid(row=3, column=0, pady=10, padx=10)
        self.outstanding = tk.Entry(self, font=("Arial", 12))
        self.outstanding.grid(row=3, column=1, pady=10)

        tk.Button(self, text="Add", font=("Arial", 12), command=self.add_customer).grid(row=4, column=0, columnspan=2, pady=20)

    def add_customer(self):
        name = self.name.get()
        phone = self.phone.get()
        total_amount = self.total_amount.get()
        outstanding = self.outstanding.get()

        if not name or not phone or not total_amount or not outstanding:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            total_amount = float(total_amount)
            outstanding = float(outstanding)
        except ValueError:
            messagebox.showerror("Error", "Total Amount and Outstanding must be numeric")
            return

        date = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Customers (name, phone, date, total_amount, outstanding) VALUES (?, ?, ?, ?, ?)",
                           (name, phone, date, total_amount, outstanding))
            conn.commit()

        self.destroy()
        messagebox.showinfo("Success", "Customer added")
        self.master.load_customers()


# Run Application
if __name__ == "__main__":
    app = SellerLogin()
    app.mainloop()
      

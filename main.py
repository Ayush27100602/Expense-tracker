import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DB_NAME = "expenses.db"
CATEGORIES = [
    "Food", "Travel", "Education", "Shopping",
    "Entertainment", "Bills", "Health","Others"
]

# Modern, calm color palette
BG = "#F3F6FB"
SIDEBAR = "#17243A"
PRIMARY = "#4169E1"
TEXT = "#1F2A44"
MUTED = "#718096"
WHITE = "#FFFFFF"
GREEN = "#159A72"
RED = "#D94F5C"


def create_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL
            )
        """)


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1240x780")
        self.root.minsize(1080, 700)
        self.root.configure(bg=BG)
        self.selected_id = None

        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.chart_type_var = tk.StringVar(value="Bar Chart")

        self.setup_style()
        self.build_layout()
        self.load_expenses()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background=WHITE, foreground=TEXT,
            rowheight=34, fieldbackground=WHITE, borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading", background="#E9EEF8",
            foreground=TEXT, font=("Segoe UI", 10, "bold"),
            relief="flat", padding=(8, 10)
        )
        style.map("Treeview", background=[("selected", "#DCE7FF")],
                  foreground=[("selected", TEXT)])
        style.configure(
            "TCombobox", padding=8, fieldbackground=WHITE,
            background=WHITE, foreground=TEXT
        )

    def build_layout(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="◈  SpendWise", bg=SIDEBAR, fg=WHITE,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=22, pady=(28, 4))
        tk.Label(sidebar, text="PERSONAL FINANCE", bg=SIDEBAR, fg="#91A2BD",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 34))

        self.side_nav(sidebar, "▦   Dashboard", active=True)
        self.side_nav(sidebar, "↗   Expense Records")
        self.side_nav(sidebar, "◔   Spending Insights")

        tk.Frame(sidebar, bg="#34435B", height=1).pack(fill="x", padx=20, pady=22)
        tk.Label(sidebar, text="Track today.\nPlan tomorrow.", bg=SIDEBAR,
                 fg="#C5D0E2", justify="left",
                 font=("Segoe UI", 11)).pack(anchor="w", padx=24, pady=5)
        tk.Label(sidebar, text="Local data • SQLite", bg=SIDEBAR, fg="#91A2BD",
                 font=("Segoe UI", 9)).pack(side="bottom", anchor="w", padx=22, pady=20)

        # Main content
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=28, pady=22)

        top = tk.Frame(main, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text="Dashboard", bg=BG, fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(side="left")
        tk.Label(top, text="Overview of your spending", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left", padx=16, pady=(10, 0))
        self.make_button(top, "＋  Add Expense", PRIMARY,
                         self.focus_form).pack(side="right")

        # Summary cards
        cards = tk.Frame(main, bg=BG)
        cards.pack(fill="x", pady=(22, 18))
        self.total_value = self.make_stat_card(cards, "TOTAL SPENDING", "₹0.00", PRIMARY)
        self.count_value = self.make_stat_card(cards, "TRANSACTIONS", "0", GREEN)
        self.avg_value = self.make_stat_card(cards, "AVERAGE EXPENSE", "₹0.00", "#8B5CF6")

        # Form card
        form = tk.Frame(main, bg=WHITE, highlightthickness=1,
                        highlightbackground="#E5EAF3")
        form.pack(fill="x", pady=(0, 18))
        tk.Label(form, text="Add or edit an expense", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).grid(
                     row=0, column=0, columnspan=8, sticky="w", padx=18, pady=(15, 10))

        self.date_entry = self.make_field(form, "Date (YYYY-MM-DD)", self.date_var, 0, 1, width=16)
        self.category_combo = ttk.Combobox(
            form, textvariable=self.category_var, values=CATEGORIES,
            state="readonly", width=17, font=("Segoe UI", 10)
        )
        self.add_field_label(form, "Category", 2, 1)
        self.category_combo.grid(row=2, column=1, padx=(10, 12), pady=(0, 14), sticky="ew")
        self.description_entry = self.make_field(form, "Description", self.description_var, 4, 1, width=22)
        self.amount_entry = self.make_field(form, "Amount (₹)", self.amount_var, 6, 1, width=14)

        actions = tk.Frame(form, bg=WHITE)
        actions.grid(row=3, column=0, columnspan=8, sticky="e", padx=16, pady=(0, 14))
        self.make_button(actions, "Save Expense", GREEN, self.add_expense).pack(side="left", padx=4)
        self.make_button(actions, "Update Selected", PRIMARY, self.update_expense).pack(side="left", padx=4)
        self.make_button(actions, "Delete", RED, self.delete_expense).pack(side="left", padx=4)
        self.make_button(actions, "Clear", "#64748B", self.clear_fields).pack(side="left", padx=4)

        for c in (1, 3, 5, 7):
            form.grid_columnconfigure(c, weight=1)

        # Records card
        records = tk.Frame(main, bg=WHITE, highlightthickness=1,
                           highlightbackground="#E5EAF3")
        records.pack(fill="both", expand=True)
        toolbar = tk.Frame(records, bg=WHITE)
        toolbar.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(toolbar, text="Recent transactions", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(toolbar, text="Search", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(22, 6))
        search = tk.Entry(toolbar, textvariable=self.search_var, width=20,
                          relief="flat", bg=BG, fg=TEXT,
                          font=("Segoe UI", 10), insertbackground=TEXT)
        search.pack(side="left", ipady=7)
        search.bind("<KeyRelease>", lambda _e: self.load_expenses())
        tk.Label(toolbar, text="Category", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(12, 6))
        filter_combo = ttk.Combobox(toolbar, textvariable=self.filter_var,
                                    values=["All"] + CATEGORIES,
                                    state="readonly", width=14)
        filter_combo.pack(side="left")
        filter_combo.bind("<<ComboboxSelected>>", lambda _e: self.load_expenses())

        chart_controls = tk.Frame(toolbar, bg=WHITE)
        chart_controls.pack(side="right")
        ttk.Combobox(chart_controls, textvariable=self.chart_type_var,
                     values=["Bar Chart", "Pie Chart"], state="readonly",
                     width=12).pack(side="left", padx=(0, 7))
        self.make_button(chart_controls, "View Chart", "#334155",
                         self.show_chart).pack(side="left")

        table_frame = tk.Frame(records, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 15))
        columns = ("id", "date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {"id": "ID", "date": "DATE", "category": "CATEGORY",
                    "description": "DESCRIPTION", "amount": "AMOUNT (₹)"}
        widths = {"id": 55, "date": 125, "category": 140,
                  "description": 300, "amount": 130}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col],
                             anchor="w" if col == "description" else "center")
        self.tree.tag_configure("even", background=WHITE)
        self.tree.tag_configure("odd", background="#F8FAFE")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.select_expense)

    def side_nav(self, parent, text, active=False):
        bg = "#2C3D59" if active else SIDEBAR
        fg = WHITE if active else "#B5C2D5"
        tk.Label(parent, text=text, bg=bg, fg=fg, anchor="w",
                 font=("Segoe UI", 10, "bold" if active else "normal"),
                 padx=18, pady=12).pack(fill="x", padx=12, pady=3)

    def make_stat_card(self, parent, title, value, accent):
        card = tk.Frame(parent, bg=WHITE, highlightthickness=1,
                        highlightbackground="#E5EAF3")
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(side="left", fill="both", expand=True, padx=15, pady=13)
        tk.Label(inner, text=title, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        val = tk.Label(inner, text=value, bg=WHITE, fg=TEXT,
                       font=("Segoe UI", 19, "bold"))
        val.pack(anchor="w", pady=(4, 0))
        return val

    def add_field_label(self, parent, title, col, row):
        tk.Label(parent, text=title, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).grid(
                     row=row, column=col, sticky="w", padx=10, pady=(0, 4))

    def make_field(self, parent, title, variable, col, row, width=18):
        self.add_field_label(parent, title, col, row)
        entry = tk.Entry(parent, textvariable=variable, width=width,
                         relief="flat", bg=BG, fg=TEXT,
                         font=("Segoe UI", 10), insertbackground=TEXT)
        entry.grid(row=row + 1, column=col, padx=(10, 12),
                   pady=(0, 14), ipady=8, sticky="ew")
        return entry

    def make_button(self, parent, text, color, command):
        return tk.Button(parent, text=text, command=command,
                         bg=color, fg=WHITE, activebackground=color,
                         activeforeground=WHITE, relief="flat", bd=0,
                         cursor="hand2", padx=13, pady=8,
                         font=("Segoe UI", 9, "bold"))

    def focus_form(self):
        self.date_entry.focus_set()

    def db_rows(self):
        with sqlite3.connect(DB_NAME) as conn:
            return conn.execute(
                "SELECT id, date, category, description, amount "
                "FROM expenses ORDER BY date DESC, id DESC"
            ).fetchall()

    def add_expense(self):
        values = self.get_validated_form()
        if values is None:
            return
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                values
            )
        self.clear_fields()
        self.load_expenses()
        messagebox.showinfo("Saved", "Expense added successfully.")

    def get_validated_form(self):
        date = self.date_var.get().strip()
        category = self.category_var.get().strip()
        description = self.description_var.get().strip()
        amount_text = self.amount_var.get().strip()
        if not all((date, category, description, amount_text)):
            messagebox.showwarning("Missing details", "Please fill in all fields.")
            return None
        try:
            datetime.strptime(date, "%Y-%m-%d")
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Use date YYYY-MM-DD and enter an amount greater than zero."
            )
            return None
        return date, category, description, amount

    def load_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = self.search_var.get().strip().lower()
        category = self.filter_var.get()
        rows = self.db_rows()
        shown = []
        for row in rows:
            if category != "All" and row[2] != category:
                continue
            if query and not any(query in str(value).lower() for value in row):
                continue
            shown.append(row)
        for index, row in enumerate(shown):
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], f"{row[4]:.2f}"
            ), tags=("even" if index % 2 == 0 else "odd",))
        self.update_summary()

    def select_expense(self, _event=None):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        if not values:
            return
        self.selected_id = int(values[0])
        self.date_var.set(values[1])
        self.category_var.set(values[2])
        self.description_var.set(values[3])
        self.amount_var.set(values[4])

    def update_expense(self):
        if self.selected_id is None:
            messagebox.showwarning("Select record", "Select an expense from the table first.")
            return
        values = self.get_validated_form()
        if values is None:
            return
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "UPDATE expenses SET date=?, category=?, description=?, amount=? WHERE id=?",
                (*values, self.selected_id)
            )
        self.clear_fields()
        self.load_expenses()
        messagebox.showinfo("Updated", "Expense updated successfully.")

    def delete_expense(self):
        if self.selected_id is None:
            messagebox.showwarning("Select record", "Select an expense from the table first.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete the selected expense?"):
            return
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DELETE FROM expenses WHERE id=?", (self.selected_id,))
        self.clear_fields()
        self.load_expenses()

    def clear_fields(self):
        self.selected_id = None
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.category_var.set("")
        self.description_var.set("")
        self.amount_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def update_summary(self):
        rows = self.db_rows()
        total = sum(float(row[4]) for row in rows)
        count = len(rows)
        average = total / count if count else 0
        self.total_value.config(text=f"₹{total:,.2f}")
        self.count_value.config(text=str(count))
        self.avg_value.config(text=f"₹{average:,.2f}")

    def category_totals(self):
        with sqlite3.connect(DB_NAME) as conn:
            return conn.execute(
                "SELECT category, SUM(amount) FROM expenses "
                "GROUP BY category HAVING SUM(amount) > 0 ORDER BY SUM(amount) DESC"
            ).fetchall()

    def show_chart(self):
        data = self.category_totals()
        if not data:
            messagebox.showinfo("No data", "Add some expenses before viewing a chart.")
            return

        chart_window = tk.Toplevel(self.root)
        chart_window.title("Spending Insights")
        chart_window.geometry("760x560")
        chart_window.configure(bg=BG)

        tk.Label(chart_window, text="Spending by Category", bg=BG, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(pady=(18, 2))
        tk.Label(chart_window, text="Based on all saved expenses", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(pady=(0, 8))

        figure = Figure(figsize=(7.2, 4.5), dpi=100, facecolor=BG)
        ax = figure.add_subplot(111)
        labels = [row[0] for row in data]
        amounts = [float(row[1]) for row in data]

        if self.chart_type_var.get() == "Pie Chart":
            ax.pie(amounts, labels=labels, autopct="%1.1f%%",
                   startangle=90, pctdistance=0.72,
                   wedgeprops={"linewidth": 2, "edgecolor": "white"})
            ax.axis("equal")
        else:
            bars = ax.bar(labels, amounts)
            ax.set_ylabel("Amount (₹)")
            ax.set_xlabel("Category")
            ax.tick_params(axis="x", rotation=25)
            ax.grid(axis="y", linestyle="--", alpha=0.25)
            ax.set_axisbelow(True)
            for bar, amount in zip(bars, amounts):
                ax.annotate(f"₹{amount:,.0f}",
                            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            xytext=(0, 4), textcoords="offset points",
                            ha="center", fontsize=8)
        ax.set_facecolor(WHITE)
        figure.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(figure, master=chart_window)
        canvas.draw()   
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=18, pady=12)


if __name__ == "__main__":
    create_database()
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop() 


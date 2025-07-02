import json
from datetime import datetime
from datetime import date
from openpyxl import Workbook




today = date.today().isoformat()

class Expense:
    num_exp = 0

    def __init__(self, name, category, price, date_added=None):
        self.name = name
        self.category = category
        self.price = price
        self.date = date_added if date_added else date.today().isoformat()
        Expense.num_exp += 1

    @classmethod
    def get_num_exp(cls):
        return Expense.num_exp
    
    def __str__(self):
        return f"Name : {self.name} | Category : {self.category} | Price : {self.price} | Date : {self.date}"
    
class Wallet:
    def __init__(self):
        self.expenses = []

    def add_expense(self, expense):
        self.expenses.append(expense)
        print("Expense added sucessfully!")

    def list_expenses(self):
        if not self.expenses:
            print("No expenses yet!")
        else:
            print("List of your expenses: ")
            for expense in sorted(self.expenses, key=lambda e: e.date):
                print(expense)

    @property
    def total_exp(self):
        return sum(expense.price for expense in self.expenses)
    
    def write_file(self):
        data = []
        for expense in self.expenses:
            data.append({
                "name" : expense.name,
                "category" : expense.category,
                "price" : expense.price,
                "date" : expense.date
                })
        with open("my_expenses.json","w")as f:
            json.dump(data,f)

    def read_file(self):
        self.expenses = []
        Expense.num_exp = 0 
        try:
            with open("my_expenses.json","r")as f:
                data = json.load(f)
                for item in data:
                    e = Expense(item["name"],item["category"].strip().lower().title(),float(item["price"]),item["date"])
                    self.expenses.append(e)
        except FileNotFoundError:
            print("No previous data found, Starting fresh.")


    def reset_data(self):
        self.expenses = []
        Expense.num_exp = 0
        with open("my_expenses.json", "w")as f:
            json.dump([],f)
        print("All expense data has been reset, Starting fresh!")

    def filter_by_date(self, target_date):
        print(f"Expenses filtered by date {target_date}: ")
        results = [e for e in self.expenses if e.date == target_date]
        if results:
            for e in results:
                print(e)
        else:
            print(f"No expenses found on {target_date}.")
            
    def show_summary(self):
        if not self.expenses:
            print("No expenses yet!")
            return
    
        dates = [datetime.strptime(e.date, "%Y-%m-%d").date() for e in self.expenses]
        start_date = min(dates)
        end_date = max(dates)
        print(f"\n=== Expense Summary ===")

        print(f"\nFrom {start_date} to {end_date}")

        total = self.total_exp
        summary = {}
        for expense in self.expenses:
            cat = expense.category.lower()
            if cat in summary:
                summary[cat]["total"] += expense.price
                summary[cat]["count"] += 1
            else:
                summary[cat] = {"total": expense.price, "count": 1}

        print("\n - - - Category wise spending - - - ")
        for cat, data in sorted(summary.items(), key=lambda item: item[1]["total"], reverse=True):
            percent = (data["total"] / total) * 100
            print(f"Category: {cat.capitalize()} | Number of expenses: {data['count']} | Total Spent: ₹{data['total']:.2f} | ({percent:.2f}%)")

        print(f"\nTotal amount spent: ₹{total:.2f}")

        biggest = max(self.expenses, key=lambda e: e.price)
        print(f"Biggest expense: {biggest.name} in {biggest.category} category, costing ₹{biggest.price:.2f} on {biggest.date}")

        today = date.today()
        iso_today = today.isoformat()
        year, week_num, _ = today.isocalendar()

        spent_today = 0
        spent_week = 0
        spent_month = 0
        spent_last_week = 0

        for e in self.expenses:
            dt = datetime.strptime(e.date, "%Y-%m-%d").date()
            if dt == today:
                spent_today += e.price
            if dt.isocalendar()[:2] == (year, week_num):
                spent_week += e.price
            if dt.isocalendar()[:2] == (year, week_num - 1):
                spent_last_week += e.price
            if dt.year == today.year and dt.month == today.month:
                spent_month += e.price

        print("\n- - - Recent data - - - ")
        print(f"Spent today ({iso_today}): ₹{spent_today:.2f}")
        print(f"Spent this week (ISO week {week_num}): ₹{spent_week:.2f}")
        print(f"Spent this month ({today.strftime('%Y-%m')}): ₹{spent_month:.2f}")
        print("")

        if spent_last_week > 0:
            diff = spent_week - spent_last_week
            if diff > 0:
                print(f"Hint: Your spending increased by ₹{diff} compared to last week.")
            elif diff < 0:
                print(f"Hint: Your spending decreased by ₹{abs(diff)} compared to last week.")
            else:
                print("Hint: Your spending is about the same as last week.")
        else:
            print("Hint: Not enough data to compare with last week.")


    def write_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"
        ws.append(["Name", "Category", "Price", "Date"])
        for expense in self.expenses:
            ws.append([expense.name, expense.category, expense.price, expense.date])
        wb.save(f"my_expenses.xlsx")


# ========= MAIN MENU ===========

wallet = Wallet()
wallet.read_file()

while True:
    print("\n=== Expense Tracker Menu ===")
    print("1. Add new expense")
    print("2. List all expenses")
    print("3. Filter by date")
    print("4. Show total spent")
    print("5. Show total number of expenses")
    print("6. Summary of the expenses")
    print("7. Reset Data")
    print("8. Save & Exit")

    choice = input("Enter your choice: ")
    if choice == "1":
        name = input("Enter the name: ")
        category = input("Enter the category: ").strip().lower().title()
        try:
            price = float(input("Enter the price: "))
            if price < 0:
                print("Price must be positive!")
                continue
            expense = Expense(name, category, price)
            wallet.add_expense(expense)
        except ValueError:
            print("Invalid value entered!")

    elif choice == "2":
        wallet.list_expenses()
    elif choice == "3":
        date_input = input("Enter the date(YYYY-MM-DD):")
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            wallet.filter_by_date(date_input)
        except ValueError:
            print("Invalid date format! Use YYYY-MM-DD.")
    elif choice == "4":
        print(f"Total amount spent ₹{wallet.total_exp:.2f}")
    elif choice == "5":
        print(f"Total number of expenses are: {Expense.get_num_exp()}")
    elif choice == "6":
        wallet.show_summary()
    elif choice == "7":
        confirm = input("Are you sure to delete all data? (YES/NO): ")
        if confirm.upper() == "YES":
            wallet.reset_data()
        else:
            print("Reset cancelled")
    elif choice == "8":
        wallet.write_file()
        wallet.write_excel()
        print("Data Saved, Thankyou :)")
        break
    else:
        print("Invalid input!")


# SpendWise — Expense Tracker

A desktop expense-tracking application built with Python. SpendWise provides a Tkinter GUI, stores records locally in SQLite, and visualizes spending by category with bar and pie charts.

## Features

- Add, view, update, and delete expense records
- Store expenses locally in an SQLite database
- Search expenses and filter by category
- View total spending, transaction count, and average expense
- Visualize spending by category with bar or pie charts
- Validate dates and positive expense amounts

## Tech Stack

- **Python 3**
- **Tkinter** — desktop GUI
- **SQLite** — local database
- **Matplotlib** — charts

## Requirements

- Python 3.9 or newer recommended
- Tkinter (usually included with standard Python installations; Linux users may need to install their distribution's Tk package)
- Matplotlib

## Setup and Run

1. Install Python from https://www.python.org/downloads/
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install the dependency:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Run the application:

   ```bash
   python main.py
   ```

The application creates `expenses.db` in the working directory when it starts. Expense data is stored locally on your computer.

## Project Structure

```text
SpendWise-GitHub-Repository/
├── main.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Database

The application creates an `expenses` table with these fields:

| Field | Description |
|---|---|
| `id` | Auto-incrementing primary key |
| `date` | Expense date (`YYYY-MM-DD`) |
| `category` | Expense category |
| `description` | Expense description |
| `amount` | Expense amount |

## Notes

- The database file `expenses.db` is created automatically and is excluded from Git by `.gitignore`.
- Back up `expenses.db` if you want to preserve your locally saved expense records.
- This is a local desktop application; it does not automatically import transactions from payment apps.

## License

See `LICENSE`.

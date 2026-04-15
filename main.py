import os
import sys
import sqlite3
from pathlib import Path
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 1. Initialize UI and AI Client
console = Console()

# Fetches the key directly from your shell environment
API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

# 2. Database Path Logic (XDG Standard)
db_dir = Path(os.path.expanduser("~/.local/share/otto"))
db_dir.mkdir(parents=True, exist_ok=True)
db_path = db_dir / "tasks.db"

# 3. Database Initialization
def init_db():
    """Sets up the SQLite table with the unique Otto schema."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # We use a relational schema to store your AI-generated metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            energy INTEGER,       -- AI-calculated cognitive load (1-5)
            impact INTEGER,       -- AI-calculated importance (1-100)
            category TEXT,        -- Domain inferred by Groq
            otto_note TEXT,       -- AI generated witty tip
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    return conn

# Connect to the DB and show status
conn = init_db()

def run_health_check():
    """Runs a full diagnostic on Otto's environment and dependencies."""
    console.print(Panel("[bold cyan]Otto System Diagnostic[/bold cyan]", expand=False))

    health_table = Table(show_header=False, box=None, padding=(0, 2))

    # --- Check AI Engine ---
    if API_KEY:
        health_table.add_row("AI Engine", f"[green]✓ Connected[/green] [dim](...{API_KEY[-4:]})[/dim]")
    else:
        health_table.add_row("AI Engine", "[red]✗ GROQ_API_KEY missing from shell[/red]")

    # --- Check Database Integrity ---
    if db_path.exists():
        try:
            test_conn = sqlite3.connect(str(db_path))
            test_conn.execute("SELECT 1")
            health_table.add_row("Database", "[green]✓ Healthy[/green]")
            test_conn.close()
        except sqlite3.Error:
            health_table.add_row("Database", "[red]✗ File Corrupted[/red]")
    else:
        health_table.add_row("Database", "[yellow]! Not Initialized[/yellow]")

    # --- Check OS / Environment ---
    shell_env = os.environ.get('SHELL', 'Unknown')
    health_table.add_row("Context", f"[blue]Linux[/blue] [dim]({shell_env})[/dim]")

    console.print(health_table)
    console.print("[dim]" + "─" * 40 + "[/dim]")

# 4. Execution Logic (Command Router)
if len(sys.argv) < 2:
    console.print("[bold yellow]Usage:[/bold yellow] otto { health | list | add }")
    sys.exit(0)

command = sys.argv[1].lower()

if command in ["health", "status"]:
    run_health_check()

elif command == "list":
    console.print("[cyan]Querying database...[/cyan]")

elif command == "add":
    console.print("[green]Awaiting neural input...[/green]")

else:
    console.print(f"[bold red]Unknown command:[/bold red] '{command}'")
    sys.exit(1)

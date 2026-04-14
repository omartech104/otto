import os
import sqlite3
from pathlib import Path
from groq import Groq
from rich.console import Console

# 1. Initialize UI and AI Client
console = Console()

# Fetches the key directly from your shell environment (~/.bashrc or ~/.zshrc)
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    console.print("[bold red]Error:[/bold red] GROQ_API_KEY not found in environment.")
    exit(1)

client = Groq(api_key=api_key)

# 2. Database Path Logic (XDG Standard)
# Stores data in ~/.local/share/otto/ to keep your home directory clean
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
console.print(f"[bold cyan]Otto Engine Online[/bold cyan] | DB: [dim]{db_path}[/dim]")

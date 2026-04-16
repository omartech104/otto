import os
import sys
import sqlite3
import json
from pathlib import Path
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 1. Initialize UI and AI Client
console = Console()
API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

# 2. Database Path Logic
db_dir = Path(os.path.expanduser("~/.local/share/otto"))
db_dir.mkdir(parents=True, exist_ok=True)
db_path = db_dir / "tasks.db"

# 3. Database Initialization
def init_db():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            energy INTEGER,       
            impact INTEGER,       
            category TEXT,        
            otto_note TEXT,       
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

def run_health_check():
    console.print(Panel("[bold cyan]Otto System Diagnostic[/bold cyan]", expand=False))
    health_table = Table(show_header=False, box=None, padding=(0, 2))

    if API_KEY:
        health_table.add_row("AI Engine", f"[green]✓ Connected[/green] [dim](...{API_KEY[-4:]})[/dim]")
    else:
        health_table.add_row("AI Engine", "[red]✗ GROQ_API_KEY missing[/red]")

    if db_path.exists():
        try:
            test_conn = sqlite3.connect(str(db_path))
            test_conn.execute("SELECT 1")
            health_table.add_row("Database", "[green]✓ Healthy[/green]")
            test_conn.close()
        except sqlite3.Error:
            health_table.add_row("Database", "[red]✗ File Corrupted[/red]")
    
    shell_env = os.environ.get('SHELL', 'Unknown')
    health_table.add_row("Context", f"[blue]Linux[/blue] [dim]({shell_env})[/dim]")
    console.print(health_table)

def prompt_otto(task_input):
    system_instructions = (
        "You are Otto, a witty and efficient task manager. "
        "Analyze the user's task and return ONLY a JSON object with: "
        "'task', 'energy' (1-5), 'impact' (1-100), 'category', and 'otto_note'. "
        "Return raw JSON only."
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": task_input}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]Error reaching the brain:[/bold red] {e}")
        return None

def list_tasks():
    cursor = conn.cursor()
    # FIX: We must fetch ALL columns we want to display, including otto_note
    cursor.execute("SELECT id, task, energy, impact, status, otto_note FROM tasks ORDER BY impact DESC")
    rows = cursor.fetchall()
    
    if not rows:
        console.print("[yellow]No tasks found. Use 'otto add' to create one.[/yellow]")
        return

    table = Table(title="Otto Task Board", header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Task", style="white")
    table.add_column("Energy", justify="center")
    table.add_column("Impact", justify="center")
    table.add_column("Status", justify="right")
    table.add_column("Otto's Note", style="dim italic")

    for row in rows:
        # row[0]=id, row[1]=task, row[2]=energy, row[3]=impact, row[4]=status, row[5]=otto_note
        table.add_row(
            str(row[0]),
            row[1],
            "⚡" * row[2],
            f"{row[3]}%",
            row[4],
            row[5]
        )
    console.print(table)

def add_task():
    if len(sys.argv) < 3:
        console.print("[bold red]Error:[/bold red] Provide a description.")
        return

    user_input = " ".join(sys.argv[2:])
    with console.status("[bold cyan]Otto is thinking...", spinner="dots"):
        raw_json = prompt_otto(user_input)

    if raw_json:
        try:
            data = json.loads(raw_json)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task, energy, impact, category, otto_note)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['task'], data['energy'], data['impact'], data['category'], data['otto_note']))
            conn.commit()
            console.print(f"[green]✓ Task Saved:[/green] {data['task']}")
        except Exception as e:
            console.print(f"[red]Database Error: {e}[/red]")
    else:
        console.print("[red]AI returned no data.[/red]")

# Command Router
if len(sys.argv) < 2:
    console.print("[bold yellow]Usage:[/bold yellow] otto { health | list | add }")
    sys.exit(0)

command = sys.argv[1].lower()

if command in ["health", "status"]:
    run_health_check()
elif command == "list":
    list_tasks()
elif command == "add":
    add_task()
else:
    console.print(f"[bold red]Unknown command:[/bold red] '{command}'")
    sys.exit(1)

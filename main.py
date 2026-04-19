import os
import sys
import sqlite3
import json
import pyfiglet
import typer
from typing import Optional
from pathlib import Path
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# 1. Initialize Typer and UI
app = typer.Typer(help="Otto: Your witty AI-powered task manager.")
console = Console()

# 2. Configuration & AI Client
API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

# 3. Database Path Logic
db_dir = Path(os.path.expanduser("~/.local/share/otto"))
db_dir.mkdir(parents=True, exist_ok=True)
db_path = db_dir / "tasks.db"

# 4. Database Initialization
def get_db_conn():
    conn = sqlite3.connect(str(db_path))
    conn.execute('''
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

def prompt_otto(task_input):
    system_instructions = (
        "You are Otto, a witty and efficient task manager. "
        "Analyze the user's task and return ONLY a JSON object with: "
        "'task', 'energy' (1-5), 'impact' (1-100), 'category', and 'otto_note' (a short ,witty AI generated tip). "
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

# --- Commands ---

@app.command()
def health():
    """Check the status of the AI engine and local database."""
    console.print(Panel("[bold cyan]Otto System Diagnostic[/bold cyan]", expand=False))
    health_table = Table(show_header=False, box=None, padding=(0, 2))

    if API_KEY:
        health_table.add_row("AI Engine", f"[green]✓ Connected[/green] [dim](...{API_KEY[-4:]})[/dim]")
    else:
        health_table.add_row("AI Engine", "[red]✗ GROQ_API_KEY missing[/red]")

    try:
        conn = get_db_conn()
        conn.execute("SELECT 1")
        health_table.add_row("Database", "[green]✓ Healthy[/green]")
        conn.close()
    except sqlite3.Error:
        health_table.add_row("Database", "[red]✗ File Corrupted or Inaccessible[/red]")
    
    shell_env = os.environ.get('SHELL', 'Unknown')
    health_table.add_row("Context", f"[blue]Linux[/blue] [dim]({shell_env})[/dim]")
    console.print(health_table)

@app.command(name="list")
def list_tasks():
    """Display all tasks sorted by impact."""
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, energy, impact, status, otto_note FROM tasks ORDER BY impact DESC")
    rows = cursor.fetchall()
    conn.close()
    
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
        table.add_row(
            str(row[0]),
            row[1],
            "⚡" * row[2],
            f"{row[3]}%",
            row[4],
            row[5]
        )
    console.print(table)

@app.command()
def add(description: str = typer.Argument(..., help="The task you want Otto to analyze and add.")):
    """Add a new task with AI-generated energy and impact scores."""
    with console.status("[bold cyan]Otto is thinking...", spinner="dots"):
        raw_json = prompt_otto(description)

    if raw_json:
        try:
            data = json.loads(raw_json)
            conn = get_db_conn()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task, energy, impact, category, otto_note)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['task'], data['energy'], data['impact'], data['category'], data['otto_note']))
            conn.commit()
            conn.close()
            console.print(f"[green]✓ Task Saved:[/green] {data['task']}")
        except Exception as e:
            console.print(f"[red]Database Error: {e}[/red]")
    else:
        console.print("[red]AI returned no data.[/red]")

@app.command()
def delete(task_id: int = typer.Argument(..., help="The ID of the task to remove.")):
    """Delete a task from the database by its ID."""
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    console.print(f"[green]✓ Task Deleted:[/green] {task_id}")

@app.command()
def clear():
    """Wipe all tasks from the database. Use with caution!"""
    if typer.confirm("Are you sure you want to delete ALL tasks?"):
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
        console.print("[green]✓ All Tasks Deleted.[/green]")

@app.command()
def finish(task_id: int = typer.Argument(..., help="The ID of the task to mark complete.")):
    """Complete a task and get a witty congratulation from Otto."""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT task FROM tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    
    if not result:
        console.print(f"[bold red]Error:[/bold red] Task ID {task_id} not found.")
        conn.close()
        return

    task_name = result[0]
    cursor.execute("UPDATE tasks SET status = 'complete' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    console.print(Panel(f"[bold green]✓ Task Finished:[/bold green] {task_name}", expand=False))

    try:
        with console.status("[italic]Otto is writing a victory speech...", spinner="aesthetic"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Otto, a witty task manager. Give a very short, one-sentence, clever, and slightly sarcastic congratulation for finishing a task."
                    },
                    {
                        "role": "user", 
                        "content": f"I just finished this task: {task_name}"
                    }
                ],
                temperature=0.8
            )
            message = response.choices[0].message.content
            console.print(f"[bold magenta]Otto:[/bold magenta] [italic]{message}[/italic]\n")
    except Exception:
        console.print("[dim italic]Otto nods in silent approval.[/dim italic]\n")

@app.command()
def chat():
    """Enter the Neural Link (interactive chat mode)."""
    try:
        username = os.getlogin().capitalize()
    except Exception:
        username = "User"

    os.system('clear' if os.name == 'posix' else 'cls')
    ascii_banner = pyfiglet.figlet_format("OTTO", font="block")
    console.print(f"[bold magenta]{ascii_banner}[/bold magenta]")
    console.print(f"[dim]Neural link established. Welcome back, {username}.[/dim]")
    console.print("[dim]Type 'exit' to quit or 'clear' to wipe the screen.[/dim]\n")

    while True:
        try:
            user_query = console.input("[bold cyan]> [/bold cyan]").strip()
        except EOFError:
            break

        if not user_query:
            continue

        if user_query.lower() in ["exit", "quit"]:
            console.print(f"[yellow]Shutting down neural link... Goodbye, {username}.[/yellow]")
            break
        
        if user_query.lower() == "clear":
            os.system('clear' if os.name == 'posix' else 'cls')
            console.print(f"[bold magenta]{ascii_banner}[/bold magenta]")
            continue

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT task, energy, impact, status, otto_note FROM tasks")
        rows = cursor.fetchall()
        conn.close()
        
        task_list_str = "Currently, the database is empty."
        if rows:
            task_list_str = "\n".join([
                f"- {r[0]} | Energy: {r[1]}/5 | Impact: {r[2]}% | Status: {r[3]}" 
                for r in rows
            ])

        system_instructions = (
            f"You are Otto, a witty and efficient task management AI. "
            f"The user's name is {username}. You have access to their SQLite task list. "
            "Answer questions concisely, cleverly, and with a touch of sarcasm. "
            "Use Markdown to format your response."
        )

        try:
            with console.status("[dim]Processing...", spinner="dots"):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": f"Task List:\n{task_list_str}\n\nUser Question: {user_query}"}
                    ]
                )
                answer = response.choices[0].message.content
                if answer:
                    console.print("\n")
                    console.print(Markdown(answer))
                    console.print("\n")
                else:
                    console.print("[yellow]Otto is lost in thought... (Empty API response).[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Neural Link Error:[/bold red] {e}")

if __name__ == "__main__":
    app()

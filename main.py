import os
import sys
import sqlite3
import json
import pyfiglet
from pathlib import Path
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

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

def delete_task(task_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    console.print(f"[green]✓ Task Deleted:[/green] {task_id}")

def clear_tasks():
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    console.print("[green]✓ All Tasks Deleted.[/green]")

def mark_task_complete(task_id):
    """Updates task status and gets a witty AI congratulation."""
    cursor = conn.cursor()
    
    # 1. Verify the task exists and get its name for the AI context
    cursor.execute("SELECT task FROM tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    
    if not result:
        console.print(f"[bold red]Error:[/bold red] Task ID {task_id} not found.")
        return

    task_name = result[0]

    # 2. Update status in the database
    cursor.execute("UPDATE tasks SET status = 'complete' WHERE id = ?", (task_id,))
    conn.commit()
    
    console.print(Panel(f"[bold green]✓ Task Finished:[/bold green] {task_name}", expand=False))

    # 3. Generate a custom witty congratulation
    # We call the API directly here to avoid the JSON constraint of prompt_otto
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
                temperature=0.8 # Higher temperature for more variety in wit
            )
            message = response.choices[0].message.content
            console.print(f"[bold magenta]Otto:[/bold magenta] [italic]{message}[/italic]\n")
    except Exception:
        # Fallback if the API fails or is offline
        console.print("[dim italic]Otto nods in silent approval.[/dim italic]\n")

def start_chat():
    """Enters a persistent, interactive chat mode with an Otto splash screen."""
    
    # Dynamically fetch the system username (e.g., Omar)
    try:
        username = os.getlogin().capitalize()
    except Exception:
        username = "User"

    # 1. Clear the terminal for the 'App' experience
    os.system('clear' if os.name == 'posix' else 'cls')

    # 2. Render the ASCII Banner
    # 'block' font mirrors the heavy, pixelated look of your reference image
    ascii_banner = pyfiglet.figlet_format("OTTO", font="block")
    console.print(f"[bold magenta]{ascii_banner}[/bold magenta]")
    
    console.print(f"[dim]Neural link established. Welcome back, {username}.[/dim]")
    console.print("[dim]Type 'exit' to quit or 'clear' to wipe the screen.[/dim]\n")

    while True:
        # 3. Minimalist Input Prompt
        try:
            user_query = console.input("[bold cyan]> [/bold cyan]").strip()
        except EOFError: # Handles Ctrl+D
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

        # 4. Refresh Task Context from SQLite
        cursor = conn.cursor()
        cursor.execute("SELECT task, energy, impact, status, otto_note FROM tasks")
        rows = cursor.fetchall()
        
        task_list_str = "Currently, the database is empty."
        if rows:
            task_list_str = "\n".join([
                f"- {r[0]} | Energy: {r[1]}/5 | Impact: {r[2]}% | Status: {r[3]}" 
                for r in rows
            ])

        # 5. Define the Persona & Generate Response
        system_instructions = (
            f"You are Otto, a witty and efficient task management AI. "
            f"The user's name is {username}. You have access to their SQLite task list. "
            "Answer questions concisely, cleverly, and with a touch of sarcasm. "
            "Use Markdown (headers, bolding, lists) to format your response for the terminal."
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
                
                # FIX: Explicitly handle the potential None type from the API 
                answer = response.choices[0].message.content

                if answer:
                    # Render properly using Rich's Markdown parser
                    md = Markdown(answer)
                    console.print("\n")
                    console.print(md)
                    console.print("\n")
                else:
                    console.print("[yellow]Otto is lost in thought... (Empty API response).[/yellow]")
                
        except Exception as e:
            console.print(f"[bold red]Neural Link Error:[/bold red] {e}")

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
elif command == "delete":
    if len(sys.argv) < 3:
        console.print("[bold red]Error:[/bold red] Provide a task ID.")
        sys.exit(1)
    delete_task(sys.argv[2])
elif command == "clear":
    clear_tasks()
elif command == "finish":
    if len(sys.argv) < 3:
        console.print("[bold red]Error:[/bold red] Provide a task ID.")
        sys.exit(1)
    mark_task_complete(sys.argv[2])
elif command == "chat":
    start_chat()
else:
    console.print(f"[bold red]Unknown command:[/bold red] '{command}'")
    sys.exit(1)

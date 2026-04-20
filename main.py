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
    """Diagnostic check of AI connection, database health, and environment."""
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
    """List all tasks sorted by their impact score. Shows ID, energy, and Otto's notes."""
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
def add(description: str = typer.Argument(..., help="Detailed description of the task for Otto's analysis.")):
    """Add a new task. Otto will automatically determine its energy, impact, and category."""
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
def delete(task_ids: Optional[list[int]] = typer.Argument(None, help="The ID(s) of the task(s) to remove. Supports bulk deletion.")):
    """Remove one or more tasks from the database permanently."""
    if not task_ids:
        console.print("[bold red]Error:[/bold red] Please provide at least one task ID to delete.")
        return
    
    conn = get_db_conn()
    cursor = conn.cursor()
    
    deleted_count = 0
    for task_id in task_ids:
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            console.print(f"[green]✓ Task Deleted:[/green] {task_id}")
            deleted_count += 1
        else:
            console.print(f"[bold red]Error:[/bold red] Task ID {task_id} not found.")

    conn.commit()
    conn.close()

    if deleted_count > 0:
        console.print(f"[green]✓ Successfully deleted {deleted_count} tasks.[/green]")
    else:
        console.print("[yellow]No tasks were deleted.[/yellow]")

@app.command()
def clear():
    """Wipe the entire task list. Requires confirmation."""
    if typer.confirm("Are you sure you want to delete ALL tasks?"):
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
        console.print("[green]✓ All Tasks Deleted.[/green]")

@app.command()
def finish(task_ids: Optional[list[int]] = typer.Argument(None, help="The ID(s) of the task to mark as finished. Supports bulk completion.")):
    """Complete tasks and get a witty congratulation from Otto for each."""
    if not task_ids:
        console.print("[bold red]Error:[/bold red] Please provide at least one task ID to finish.")
        return

    conn = get_db_conn()
    cursor = conn.cursor()

    tasks_finished = []
    for task_id in task_ids:
        cursor.execute("SELECT task FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()

        if not result:
            console.print(f"[bold red]Error:[/bold red] Task ID {task_id} not found.")
            continue

        task_name = result[0]
        cursor.execute("UPDATE tasks SET status = 'complete' WHERE id = ?", (task_id,))
        tasks_finished.append(task_name)

    conn.commit()
    conn.close()

    for task_name in tasks_finished:
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
def edit(
    task_id: int = typer.Argument(..., help="The ID of the task you wish to modify."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New task description. Triggers AI re-analysis of energy, impact, and category."),
    energy: Optional[int] = typer.Option(None, "--energy", "-e", min=1, max=5, help="Override energy requirement (1=Low, 5=Extreme)."),
    impact: Optional[int] = typer.Option(None, "--impact", "-i", min=1, max=100, help="Override impact score (1-100%)."),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Manually set a new category."),
    otto_note: Optional[str] = typer.Option(None, "--note", "-n", help="Manually update Otto's witty remark.")
):
    """Update specific fields of an existing task. If description is changed, Otto re-analyzes the rest."""
    conn = get_db_conn()
    cursor = conn.cursor()

    # Fetch current task details
    cursor.execute("SELECT task, energy, impact, category, otto_note FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()

    if not existing_task:
        console.print(f"[bold red]Error:[/bold red] Task ID {task_id} not found.")
        conn.close()
        return

    # Unpack existing data
    current_description, current_energy, current_impact, current_category, current_otto_note = existing_task

    # Prepare for update
    updates = {}
    if description is not None:
        updates['task'] = description
    if energy is not None:
        updates['energy'] = energy
    if impact is not None:
        updates['impact'] = impact
    if category is not None:
        updates['category'] = category
    if otto_note is not None:
        updates['otto_note'] = otto_note

    # Re-analyze with AI if description changed and other AI-related fields are not explicitly set
    if 'task' in updates and (energy is None and impact is None and category is None and otto_note is None):
        console.print("[bold cyan]Description updated. Otto is re-analyzing...", spinner="dots")
        raw_json = prompt_otto(updates['task'])
        if raw_json:
            try:
                ai_data = json.loads(raw_json)
                updates['energy'] = ai_data.get('energy', current_energy)
                updates['impact'] = ai_data.get('impact', current_impact)
                updates['category'] = ai_data.get('category', current_category)
                updates['otto_note'] = ai_data.get('otto_note', current_otto_note)
                console.print("[green]✓ AI re-analysis complete.[/green]")
            except json.JSONDecodeError:
                console.print("[bold red]Warning:[/bold red] AI response could not be parsed. Task description updated, but other fields remain unchanged.")
            except Exception as e:
                console.print(f"[bold red]Warning:[/bold red] Error during AI re-analysis: {e}. Task description updated, but other fields remain unchanged.")
        else:
            console.print("[bold red]Warning:[/bold red] AI returned no data for re-analysis. Task description updated, but other fields remain unchanged.")

    if not updates:
        console.print("[yellow]No changes specified.[/yellow]")
        conn.close()
        return

    # Construct the SET part of the SQL query
    set_clauses = [f"{key} = ?" for key in updates.keys()]
    set_clause_str = ", ".join(set_clauses)
    
    # Prepare values for the query
    values = list(updates.values())
    values.append(task_id) # Add task_id for the WHERE clause

    try:
        cursor.execute(f"UPDATE tasks SET {set_clause_str} WHERE id = ?", values)
        conn.commit()
        console.print(f"[green]✓ Task ID {task_id} updated successfully.[/green]")
    except Exception as e:
        console.print(f"[bold red]Database Error:[/bold red] {e}")
    finally:
        conn.close()
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

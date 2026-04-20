# Otto 🤖

Otto is a witty and efficient AI-powered task manager for your terminal. It doesn't just track your tasks; it analyzes them using AI to provide energy ratings, impact scores, and slightly sarcastic encouragement.

## Features

-   **Neural Link (Chat Mode):** Enter a persistent, interactive chat mode to manage your tasks and get advice.
-   **AI Analysis:** Uses Groq (Llama 3.3) to evaluate task energy requirements and potential impact.
-   **Witty Personality:** Otto provides clever tips and sarcastic congratulations upon finishing tasks.
-   **Prioritization:** Tasks are automatically ranked by their impact.
-   **Simple CLI:** Clean, intuitive commands for managing your workflow.
-   **System Health Checks:** Built-in diagnostics to verify AI and database connectivity.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/omartech104/otto.git
    cd otto
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set your Groq API Key:**
    Get an API key from [Groq](https://console.groq.com/) and add it to your environment:
    ```bash
    export GROQ_API_KEY='your_api_key_here'
    ```

## Usage

Otto uses a simple command structure: `python main.py <command>`.

### Available Commands

-   **`chat`**: Enter the interactive Neural Link session.
    ```bash
    python main.py chat
    ```

-   **`health`** (or **`status`**): Check the status of your AI connection and database.
    ```bash
    python main.py health
    ```

-   **`add`**: Add a new task with AI analysis.
    ```bash
    python main.py add "Write documentation for the new API"
    ```

-   **`list`**: Display all tasks sorted by impact, including IDs, categories, and Otto's notes.
    ```bash
    python main.py list
    ```

-   **`edit`**: Modify an existing task.
    ```bash
    # Update description (triggers AI re-analysis)
    python main.py edit <task_id> --description "New description"
    
    # Manually update specific fields
    python main.py edit <task_id> --energy 3 --impact 80 --category "Work"
    ```

-   **`finish`**: Mark one or more tasks as complete.
    ```bash
    # Single task
    python main.py finish <task_id>
    
    # Bulk finish
    python main.py finish <task_id_1> <task_id_2> <task_id_3>
    ```

-   **`delete`**: Remove one or more tasks.
    ```bash
    # Single task
    python main.py delete <task_id>
    
    # Bulk delete
    python main.py delete <task_id_1> <task_id_2>
    ```


-   **`clear`**: Wipe all tasks from the database.
    ```bash
    python main.py clear
    ```

## Storage

Otto stores your tasks locally in an SQLite database located at:
`~/.local/share/otto/tasks.db`

## License

This project is licensed under the [MIT License](LICENSE).

# Otto 🤖

Otto is a witty and efficient AI-powered task manager for your terminal. It doesn't just track your tasks; it analyzes them using AI to provide energy ratings, impact scores, and slightly sarcastic encouragement.

## Features

- **AI Analysis:** Uses Groq (Llama 3) to evaluate task energy requirements and potential impact.
- **Witty Personality:** Otto provides clever tips and sarcastic congratulations upon finishing tasks.
- **Prioritization:** Tasks are automatically ranked by their impact.
- **Simple CLI:** Clean, intuitive commands for managing your workflow.
- **System Health Checks:** Built-in diagnostics to verify API and database connectivity.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/otto.git
    cd otto
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
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

-   **`health`**: Check the status of your AI connection and database.
    ```bash
    python main.py health
    ```

-   **`add`**: Add a new task with AI analysis.
    ```bash
    python main.py add "Write documentation for the new API"
    ```

-   **`list`**: Display all pending tasks sorted by impact.
    ```bash
    python main.py list
    ```

-   **`finish`**: Mark a task as complete and receive Otto's "congratulations."
    ```bash
    python main.py finish <task_id>
    ```

-   **`delete`**: Remove a specific task.
    ```bash
    python main.py delete <task_id>
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

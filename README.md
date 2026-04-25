# Otto 🤖
> **The AI Task Manager that's judging your life choices.**

Otto is a witty, high-performance, and slightly cynical AI-powered task manager for your terminal. While most task managers just sit there quietly, Otto analyzes your life choices using **Llama 3.3** (via Groq) to provide energy ratings, impact scores, and the kind of feedback you'd expect from a disappointed mentor.

---

## ✨ Features

- **🧠 Neural Link (Chat Mode):** Step into an interactive session where Otto manages your tasks and provides life advice (mostly sarcastic). He has full access to your stats, so expect judgment.
- **📊 Performance Reviews:** Use the `review` command to get a brutal, AI-generated assessment of your productivity. Otto looks at your completion rates and tells you how you're *really* doing.
- **🛡️ Graceful Failure:** Otto doesn't crash when his brain is offline. He handles missing API keys, database issues, and connection timeouts with poise (and a bit of snark).
- **⏳ Temporal Awareness:** Otto tracks how long your tasks have been rotting. Tasks older than 3 days are highlighted as "stale" because, let's face it, you're procrastinating.
- **⚡ AI-Driven Analysis:** Every task you add is evaluated for its **Energy Requirement** (1-5 ⚡) and **Impact Score** (1-100%). Otto sorts your list by impact so you stop doing the easy stuff first.
- **🏆 Collective Victories:** Finish multiple tasks at once and get a single, punchy, AI-generated backhanded compliment.
- **🛠️ Self-Healing Core:** Built-in migrations and health checks to ensure your database and AI brain are always in sync.

---

## 🛠️ Prerequisites

- **Python 3.9+**
- **Groq API Key:** Required for AI analysis. Get one at [console.groq.com](https://console.groq.com/).

---

## 🚀 Installation

1. **Clone the brain:**
   ```bash
   git clone https://github.com/omartech104/otto.git
   cd otto
   ```

2. **Prepare the environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Feed the AI:**
   Export your API key:
   ```bash
   export GROQ_API_KEY='your_api_key_here'
   ```

### 💡 Pro-Tip: Add an Alias
To summon Otto from anywhere, add this to your `.bashrc` or `.zshrc`:
```bash
alias otto='/path/to/otto/venv/bin/python /path/to/otto/main.py'
```

---

## 🎮 Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `add` | `python main.py add "description"` | Add a task for Otto to judge. |
| `list` | `python main.py list [--all]` | View pending or all tasks (sorted by impact). |
| `finish` | `python main.py finish <id>...` | Mark one or more tasks as completed. |
| `chat` | `python main.py chat` | Enter the interactive Neural Link. |
| `review` | `python main.py review` | Get a performance review from Otto. |
| `edit` | `python main.py edit <id> [options]` | Manually update a task or trigger re-analysis. |
| `delete` | `python main.py delete <id>...` | Remove tasks permanently. |
| `health` | `python main.py health` | Diagnostic check of AI and database. |
| `clear` | `python main.py clear` | Wipe the entire database (requires confirmation). |

---

## 📂 Storage
Your tasks are stored locally in a SQLite database at:
`~/.local/share/otto/tasks.db`

## ⚖️ License
Licensed under the [MIT License](LICENSE). Otto doesn't care what you do with the code, as long as you actually finish your tasks.

# Otto 🤖
**The Task Manager with an Attitude Problem.**

Otto is a witty, efficient, and slightly judgmental AI-powered task manager for your terminal. While most task managers just sit there quietly, Otto analyzes your life choices using Llama 3.3 to provide energy ratings, impact scores, and the kind of feedback you'd expect from a disappointed mentor.

---

## ✨ Features

- **🧠 Neural Link (Chat Mode):** Step into an interactive session where Otto manages your tasks and provides life advice (mostly sarcastic). He now has full access to your stats, so expect judgment.
- **📊 Performance Reviews:** Use the `review` command to get a brutal, AI-generated assessment of your productivity. Otto looks at your completion rates and tells you how you're *really* doing.
- **⏳ Temporal Awareness:** Otto tracks how long your tasks have been rotting. Tasks older than 3 days are highlighted as "stale" because, let's face it, you're procrastinating.
- **⚡ AI-Driven Analysis:** Every task you add is evaluated for its **Energy Requirement** (1-5 ⚡) and **Impact Score** (1-100%). Otto sorts your list by impact so you stop doing the easy stuff first.
- **🏆 Collective Victories:** Finish multiple tasks at once and get a single, punchy, AI-generated backhanded compliment.
- **🛠️ Self-Healing Core:** Built-in migrations and health checks to ensure your database and AI brain are always in sync.

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
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Feed the AI:**
   Get an API key from [Groq](https://console.groq.com/) and export it:
   ```bash
   export GROQ_API_KEY='your_api_key_here'
   ```

---

## 🎮 How to use Otto

### The Essentials
- **`list`**: View your pending tasks. Otto sorts them by impact.
  - `python main.py list` (Pending only)
  - `python main.py list --all` (Show your finished work too)
- **`add`**: Add a task and let Otto judge it.
  - `python main.py add "Fix the broken production server"`
- **`finish`**: Mark tasks as done.
  - `python main.py finish 1 4 7` (Bulk completion supported)

### The Personality
- **`chat`**: Enter the interactive Neural Link.
  - `python main.py chat`
- **`review`**: Get your productivity performance review.
  - `python main.py review`

### Maintenance & Management
- **`edit`**: Change a task. If you change the description, Otto re-analyzes everything.
  - `python main.py edit 2 --description "Actually just order pizza"`
- **`delete`**: Remove mistakes.
  - `python main.py delete 5`
- **`health`**: Check if Otto's brain is still connected.
  - `python main.py health`
- **`clear`**: Wipe the slate clean (requires confirmation).
  - `python main.py clear`

---

## 📦 Storage
Your tasks are stored locally in a highly secure (well, it's SQLite) database at:
`~/.local/share/otto/tasks.db`

## ⚖️ License
Licensed under the [MIT License](LICENSE). Otto doesn't care what you do with the code, as long as you actually finish your tasks.

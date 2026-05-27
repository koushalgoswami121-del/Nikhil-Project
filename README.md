# Coach AI — AI Interviewer

Practice interview questions with AI scoring. Supports **text** and **voice** interview modes.

---

## Baby steps — run the project (Windows)

### Step 1: Install Python

1. Download Python 3.12 from [python.org](https://www.python.org/downloads/).
2. During install, check **“Add python.exe to PATH”**.
3. Open **PowerShell** and check it works:
   ```powershell
   python --version
   ```
   You should see something like `Python 3.12.x`.

### Step 2: Get the code from GitHub

1. Install [Git](https://git-scm.com/download/win) if you don’t have it.
2. Open PowerShell and go where you want the project (example: Desktop):
   ```powershell
   cd $env:USERPROFILE\Desktop
   ```
3. Clone the repo (replace with your repo URL if different):
   ```powershell
   git clone https://github.com/koushalgoswami121-del/Nikhil-Project.git
   cd Nikhil-Project
   ```
   > If your folder name has a **space** (e.g. `Nikhil-koushal AI`), that’s OK — the app supports it now.

### Step 3: API key (for voice interviews only)

1. In the project folder, copy the example env file:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` in Notepad and paste your Gemini key from [Google AI Studio](https://aistudio.google.com/apikey):
   ```
   GEMINI_API_KEY=your_real_key_here
   ```
3. Save the file.  
   **Text interviews work without this key.** Voice/TTS needs it.

### Step 4: Start the app

**Easiest way:** double-click **`start.bat`** in the project folder.

**Or** in PowerShell inside the project folder:
```powershell
.\start.bat
```

Wait until you see:
```text
Running on http://127.0.0.1:8080
```

### Step 5: Open in the browser

1. Open **Chrome** or **Edge**.
2. Go to: **http://127.0.0.1:8080**
3. Click **Create Profile** → register username/password.
4. Log in → pick a **job role** → choose **Text interview** (this shows the indigo question UI).
5. Complete the camera check → answer questions → see your summary.

### Step 6: If you already cloned before — get latest UI fix

In the project folder:
```powershell
git pull
.\start.bat
```

---

## Troubleshooting

| Problem | What to do |
|--------|------------|
| Page looks ugly / no colors | You need **internet** — styling loads from `cdn.tailwindcss.com`. |
| `can't open file ... AI\.venv\...` | Run `git pull` for the latest fix, or use `.\start.bat` instead of `python app.py`. |
| Friend doesn’t see your UI | They must choose **Text interview**, not Voice. Voice uses a different screen. |
| Voice doesn’t speak | Add `GEMINI_API_KEY` in `.env` and restart. |
| Port in use | Close other terminals running the app, or change port in `app.py`. |

**Manual start** (if `start.bat` fails):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

---

## Text vs voice UI

| Mode | Screen |
|------|--------|
| **Text interview** | Indigo **Learning Mode** (`question.html`) |
| **Voice interview** | Dark studio (`voice_room.html`) |

---

## Project files (quick map)

| File | Purpose |
|------|---------|
| `app.py` | Main Flask server |
| `start.bat` | One-click setup + run on Windows |
| `templates/` | HTML pages (UI) |
| `requirements.txt` | Python packages |
| `.env` | Your API key (not on GitHub — create locally) |

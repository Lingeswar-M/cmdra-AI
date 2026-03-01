# cmdraAI

Offline desktop assistant for Windows with a PyQt5 UI and action-based automation.

## What It Does

- File actions: create, open, read, write, move, rename, delete (with confirmation)
- System actions: open common apps (Chrome, Brave, VS Code, Notepad, CMD, Settings, Task Manager, Word, Excel, PowerPoint), lock screen, disk usage
- Browser actions: open website, search Google, search YouTube, open Gmail
- Media actions: volume and brightness controls
- Fuzzy command handling for common typos
- Mini dock bubble mode: auto-collapse after task completion timeout, click bubble to expand

## Requirements

- Windows 10 or Windows 11
- Python 3.10.x

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run (source)

```powershell
python main.py
```

## Build EXE

```powershell
.\venv\Scripts\pyinstaller.exe cmdra.spec
```

Build output:

- `dist\cmdraAI.exe`

## Project Structure

```text
cmdraAI/
├── main.py
├── config.py
├── requirements.txt
├── cmdra.spec
├── actions/
├── brain/
├── security/
├── services/
├── ui/
├── utils/
├── assets/
└── website/
```

## Notes

- The app is action-oriented and offline. Chat conversation is intentionally limited.
- Dangerous delete operations require explicit confirmation.

## License

MIT (or your preferred license file)

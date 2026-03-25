# classroom-downloader

A command-line tool to download files from Google Classroom to your local machine.

---

## How to contribute / add new stuff for yourself

### 1. Fork and clone the project

Go to the GitHub repo and click **Fork**, then clone your fork:

```bash
git clone https://github.com/your-username/classroom-downloader
cd classroom-downloader
```

### 2. Requirements

- Python 3.10+
- `pip`

### 3. Project structure

```bash
├── classroom
│   ├── __init__.py
│   ├── display.py   # all colors and print functions
│   ├── logic.py     # Google API calls and download logic
│   ├── main.py      # entry point and argument parser
│   └── utils.py     # user input helpers (pick, prompt)
├── Documentation.md
└── Installation.md
```

Each file has (or trying to have) a single responsibility if you're changing how something looks, that's `display.py`. If you're changing how something is fetched or downloaded, that's `logic.py`.

---

### 4. Set up a local development environment

```bash
# Linux
python -m venv venv
source venv/bin/activate
pip install -e .

# Windows
python -m venv venv
venv\Scripts\activate
pip install -e .
```

`pip install -e .` installs the package in editable mode meaning the `classroom` command will reflect your changes instantly without needing to reinstall.

---

### 5. Making changes

#### Adding a new command

Every new command follows the same three steps in `main.py`:

**Step 1**: Write the function:
```python
def cmd_something(args):
    # your logic here
    pass
```

**Step 2**: Register it in `build_parser()`:
```python
something_parser = sub.add_parser("something", help="What it does")
something_parser.add_argument("action", nargs="?", help="Optional action")
```

**Step 3**: Handle it in `main()`:
```python
elif args.command == "something":
    cmd_something(args)
```

That's it. The command is now available as `classroom something`.

#### Adding a new downloadable file type

In `logic.py`, add a line to the `DOWNLOADABLE_TYPES` dictionary:

```python
DOWNLOADABLE_TYPES = {
    "application/pdf":  ".pdf",
    "video/mp4":        ".mp4",
    "your/mime-type":   ".ext",   # <-- add here
}
```

You can find the MIME type for any file format at [mime.io](https://mime.io).

#### Changing colors or display

All colors and print functions live in `display.py`. The color variables at the top use ANSI codes:

```python
R  = "\033[0m"        # reset
G  = "\033[38;5;114m" # green
RD = "\033[38;5;203m" # red
# etc.
```

To change a color, swap the ANSI code. To add a new style of message, add a new function following the existing pattern:

```python
def show_something(msg): print(f"  {Y}[?]{R} {msg}")
```

---

### 6. Test your changes

With the virtual environment active and `pip install -e .` already run, just use the `classroom` command directly:

```bash
classroom
classroom get
```

Any code changes are picked up immediately no reinstall needed.

---

### 7. Build and publish?
IDK

## Notes

- Supported file types: PDF, MP4, MOV, MKV, WEBM, DOCX, PPTX, ZIP
- Files that already exist at the destination are skipped automatically
- Your auth token is stored at `~/.getlectures_token.json`
- Delete this file to force re-authentication
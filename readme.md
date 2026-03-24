# classroom-downloader

A command-line tool to download PDFs from Google Classroom to your local machine.

---

## Installation

### Requirements
- Python 3.10+
- `pipx` (recommended) or `pip`

### Linux

```bash
# Install pipx if you don't have it
sudo apt install pipx
pipx ensurepath

# Install classroom-downloader
pipx install classroom-downloader
```

### Windows

```powershell
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Restart your terminal, then:
pipx install classroom-downloader
```

---

## Usage

Run the tool:

```bash
classroom
```

On first run it will open a browser window to authenticate with your Google account. Once authenticated a token is saved locally so you won't need to log in again.

### Steps

1. **Pick a course** — choose from your active Google Classroom courses
2. **Pick a topic** — select a topic within that course
3. **Pick materials** — choose which materials to download, or select all
4. **Pick files** — choose specific files within each material, or download all
5. **Confirm** — review the summary and confirm the download location

PDFs are saved to `~/Downloads/lectures` by default. You can change this when prompted.

### Upgrading

```bash
pipx upgrade classroom-downloader
```

---

## Notes

- Only PDF files are downloaded — other file types are skipped
- Files that already exist at the destination are skipped automatically
- Your auth token is stored at `~/.getlectures_token.json`
  - Delete this file to force re-authentication

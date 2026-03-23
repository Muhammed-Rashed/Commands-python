"""
Google Classroom Downloader
================================
Interactively prompts the user for course, topic, keyword, and download location.

SETUP (one-time):
  1. Go to https://console.cloud.google.com/
  2. Create a project Enable "Google Classroom API" and "Google Drive API"
  3. Create OAuth 2.0 credentials (Desktop App) Download as credentials.json
  4. Place credentials.json in /opt/classroom-downloader/
  5. Run: pip install google-auth google-auth-oauthlib google-api-python-client

USAGE:
  getlectures
"""

import os
import io

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def prompt(question, default=None):
    """Prompt the user for input, showing a default value if provided."""
    if default:
        answer = input(f"  {question} [{default}]: ").strip()
        return answer if answer else default
    else:
        while True:
            answer = input(f"  {question}: ").strip()
            if answer:
                return answer
            print("  ⚠️  This field is required, please enter a value.")


def pick_from_list(label, items, name_key):
    """Let the user pick an item from a numbered list."""
    print(f"\n  Available {label}s:")
    for i, item in enumerate(items, 1):
        print(f"    {i}) {item[name_key]}")
    while True:
        choice = input(f"\n  Enter the number of your {label} (or type part of the name): ").strip()
        # Numeric choice
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            print("  ⚠️  Invalid number, try again.")
        else:
            # Text search
            matches = [i for i in items if choice.lower() in i[name_key].lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"  ⚠️  Multiple matches found, please be more specific:")
                for m in matches:
                    print(f"      - {m[name_key]}")
            else:
                print(f"  ⚠️  No match found for '{choice}', try again.")

def get_credentials():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    token_path = os.path.join(SCRIPT_DIR, "token.json")
    creds_path = os.path.join(SCRIPT_DIR, "credentials.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds

def list_courses(service):
    courses = []
    page_token = None
    while True:
        resp = service.courses().list(pageToken=page_token, courseStates=["ACTIVE"]).execute()
        courses.extend(resp.get("courses", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return courses


def list_topics(service, course_id):
    resp = service.courses().topics().list(courseId=course_id).execute()
    return resp.get("topic", [])


def get_course_materials(service, course_id, topic_id, keyword):
    materials = []
    page_token = None
    while True:
        resp = service.courses().courseWorkMaterials().list(
            courseId=course_id,
            pageToken=page_token
        ).execute()
        for m in resp.get("courseWorkMaterial", []):
            if m.get("topicId") == topic_id:
                if not keyword or keyword.lower() in m.get("title", "").lower():
                    materials.append(m)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return materials

def extract_drive_files(material):
    file_ids = []
    for mat in material.get("materials", []):
        df = mat.get("driveFile", {}).get("driveFile", {})
        if df.get("id"):
            file_ids.append((df["id"], df.get("title", "unknown")))
    return file_ids


def is_pdf(drive_service, file_id):
    meta = drive_service.files().get(fileId=file_id, fields="mimeType,name").execute()
    return meta.get("mimeType") == "application/pdf", meta.get("name", file_id)


def download_pdf(drive_service, file_id, filename, dest_dir):
    from googleapiclient.http import MediaIoBaseDownload

    os.makedirs(dest_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in " ._-()" else "_" for c in filename)
    if not safe_name.endswith(".pdf"):
        safe_name += ".pdf"
    filepath = os.path.join(dest_dir, safe_name)

    if os.path.exists(filepath):
        print(f"    ⏭  Already exists, skipping: {safe_name}")
        return 0

    request = drive_service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    with open(filepath, "wb") as f:
        f.write(buf.getvalue())
    print(f"    ✅ Downloaded: {safe_name}")
    return 1

def main():
    from googleapiclient.discovery import build

    print("\n╔══════════════════════════════════════════╗")
    print("║     Google Classroom PDF Downloader      ║")
    print("╚══════════════════════════════════════════╝\n")

    print("🔐 Authenticating with Google...")
    creds     = get_credentials()
    classroom = build("classroom", "v1", credentials=creds)
    drive     = build("drive",     "v3", credentials=creds)
    print("   Authenticated successfully!\n")

    print("📚 Fetching your active courses...")
    courses = list_courses(classroom)
    if not courses:
        print("❌ No active courses found.")
        return
    course = pick_from_list("course", courses, "name")
    print(f"\n   ✔ Selected course: {course['name']}")

    print("\n📂 Fetching topics in this course...")
    topics = list_topics(classroom, course["id"])
    if not topics:
        print("❌ No topics found in this course.")
        return
    topic = pick_from_list("topic", topics, "name")
    print(f"\n   ✔ Selected topic: {topic['name']}")

    print("\n🔍 Filter materials by keyword (optional):")
    keyword = input("  Enter keyword to filter material titles (or press Enter to get all): ").strip()
    if not keyword:
        print("   No filter applied — fetching all materials in this topic.")

    print("\n📁 Where should the PDFs be saved?")
    default_dir = os.path.join(os.path.expanduser("~"), "Downloads", "lectures")
    download_dir = prompt("Download folder path", default=default_dir)
    download_dir = os.path.expanduser(download_dir)  # support ~/... paths

    print(f"""
┌─────────────────────────────────────────────────┐
│                    Summary                      │
├─────────────────────────────────────────────────┤
│ Course  : {course['name']:<38}│
│ Topic   : {topic['name']:<38}│
│ Keyword : {(keyword or '(none)'):<38}│
│ Save to : {download_dir:<38}│
└─────────────────────────────────────────────────┘""")

    confirm = input("\n  Proceed? (Y/n): ").strip().lower()
    if confirm == "n":
        print("\n  Cancelled.")
        return

    print(f"\n📄 Fetching materials...")
    materials = get_course_materials(classroom, course["id"], topic["topicId"], keyword)
    print(f"   Found {len(materials)} matching material(s)\n")

    pdf_count = 0
    for mat in materials:
        print(f"  📎 {mat.get('title', 'Untitled')}")
        for file_id, title in extract_drive_files(mat):
            ok, name = is_pdf(drive, file_id)
            if ok:
                pdf_count += download_pdf(drive, file_id, name, download_dir)
            else:
                print(f"    ⏭  Skipping non-PDF: {name}")

    print(f"\n🎉 Done! Downloaded {pdf_count} new PDF(s) to:\n   {download_dir}\n")

if __name__ == "__main__":
    main()
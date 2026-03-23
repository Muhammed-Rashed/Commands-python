#!/usr/bin/env python3

import os
import io
import importlib.resources

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

TOKEN_PATH = os.path.join(os.path.expanduser("~"), ".getlectures_token.json")

def prompt(question, default=None):
    if default:
        answer = input(f"  {question} [{default}]: ").strip()
        return answer if answer else default
    else:
        while True:
            answer = input(f"  {question}: ").strip()
            if answer:
                return answer
            print("This field is required, please enter a value.")


def pick_from_list(label, items, name_key):
    """Pick a single item from a numbered list."""
    print(f"\n  Available {label}s:")
    for i, item in enumerate(items, 1):
        print(f"    {i}) {item[name_key]}")
    while True:
        choice = input(f"\n  Enter the number of your {label} (or type part of the name): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            print(" Invalid number, try again.")
        else:
            matches = [i for i in items if choice.lower() in i[name_key].lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f" Multiple matches, please be more specific:")
                for m in matches:
                    print(f"      - {m[name_key]}")
            else:
                print(f" No match for '{choice}', try again.")

def pick_files_from_material(mat):
    all_files = []
    for m in mat.get("materials", []):
        df = m.get("driveFile", {}).get("driveFile", {})
        if df.get("id"):
            all_files.append((df["id"], df.get("title", "unknown")))

    if not all_files:
        print(f"  No files found in '{mat.get('title', 'Untitled')}'")
        return []

    print(f"\n  '{mat.get('title', 'Untitled')}' contains {len(all_files)} file(s):")
    for i, (fid, name) in enumerate(all_files, 1):
        print(f"      {i}) {name}")

    print(f"\n  A) Download ALL files")
    print(f"  S) Skip this material")
    print(f"  Or enter numbers separated by commas (e.g. 1,3)")

    while True:
        choice = input("\n  Your choice: ").strip().lower()
        if choice == "a":
            return all_files
        elif choice == "s":
            print(f"  Skipped.")
            return []
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                for idx in indices:
                    if idx < 0 or idx >= len(all_files):
                        print(f"  Number {idx + 1} is out of range, try again.")
                        break
                else:
                    return [all_files[i] for i in indices]
            except ValueError:
                print("  Please enter 'A' for all, 'S' to skip, or numbers like 1,2,3")

def pick_materials(materials):
    """Let the user pick which materials to download, or all of them."""
    print(f"\n  Available materials ({len(materials)} found):")
    for i, mat in enumerate(materials, 1):
        pdf_count = sum(
            1 for m in mat.get("materials", [])
            if m.get("driveFile", {}).get("driveFile", {}).get("id")
        )
        print(f"    {i}) {mat.get('title', 'Untitled')}  ({pdf_count} file(s))")

    print(f"\n  Options:")
    print(f"    A) Download ALL materials")
    print(f"    Or enter numbers separated by commas (e.g. 1,3,5)")

    while True:
        choice = input("\n  Your choice: ").strip().lower()
        if choice == "a":
            return materials
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected = []
                valid = True
                for idx in indices:
                    if 0 <= idx < len(materials):
                        selected.append(materials[idx])
                    else:
                        print(f" Number {idx + 1} is out of range, try again.")
                        valid = False
                        break
                if valid and selected:
                    return selected
            except ValueError:
                print(" Please enter 'A' for all, or numbers like 1,2,3")

def get_credentials():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            with importlib.resources.open_text("classroom", "credentials.json") as f:
                import json, tempfile
                creds_data = f.read()
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
                tmp.write(creds_data)
                tmp_path = tmp.name
            try:
                flow = InstalledAppFlow.from_client_secrets_file(tmp_path, SCOPES)
                os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
                creds = flow.run_local_server(port=0)
            finally:
                os.unlink(tmp_path)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds

def list_courses(service):
    courses, page_token = [], None
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


def get_course_materials(service, course_id, topic_id):
    """Get ALL materials under a topic, no keyword filter."""
    materials, page_token = [], None
    while True:
        resp = service.courses().courseWorkMaterials().list(
            courseId=course_id, pageToken=page_token
        ).execute()
        for m in resp.get("courseWorkMaterial", []):
            if m.get("topicId") == topic_id:
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
    print(f"Downloaded: {safe_name}")
    return 1

def main():
    from googleapiclient.discovery import build

    print("\n╔══════════════════════════════════════════╗")
    print("║     Google Classroom PDF Downloader      ║")
    print("╚══════════════════════════════════════════╝\n")

    print("Authenticating with Google...")
    creds     = get_credentials()
    classroom = build("classroom", "v1", credentials=creds)
    drive     = build("drive",     "v3", credentials=creds)
    print("   Authenticated successfully!\n")

    print("Fetching your active courses...")
    courses = list_courses(classroom)
    if not courses:
        print("No active courses found.")
        return
    course = pick_from_list("course", courses, "name")
    print(f"\nSelected course: {course['name']}")

    print("\nFetching topics in this course...")
    topics = list_topics(classroom, course["id"])
    if not topics:
        print("No topics found in this course.")
        return
    topic = pick_from_list("topic", topics, "name")
    print(f"\nSelected topic: {topic['name']}")

    print("\nFetching materials in this topic...")
    materials = get_course_materials(classroom, course["id"], topic["topicId"])
    if not materials:
        print("No materials found in this topic.")
        return
    selected_materials = pick_materials(materials)
    print(f"\n Selected {len(selected_materials)} material(s) to explore\n")

    # Drill into each material and pick files
    files_to_download = []
    for mat in selected_materials:
        chosen = pick_files_from_material(mat)
        files_to_download.extend(chosen)

    if not files_to_download:
        print("\nNo files selected. Exiting.")
        return

    print("\nWhere should the PDFs be saved?")
    default_dir = os.path.join(os.path.expanduser("~"), "Downloads", "lectures")
    download_dir = prompt("Download folder path", default=default_dir)
    download_dir = os.path.expanduser(download_dir)

    print(f"""
┌─────────────────────────────────────────────────┐
│                    Summary                      │
├─────────────────────────────────────────────────┤
│ Course    : {course['name']:<36}│
│ Topic     : {topic['name']:<36}│
│ Materials : {str(len(selected_materials)) + ' selected':<36}│
│ Save to   : {download_dir:<36}│
└─────────────────────────────────────────────────┘""")

    confirm = input("\n  Proceed? (Y/n): ").strip().lower()
    if confirm == "n":
        print("\n  Cancelled.")
        return

    print()
    pdf_count = 0
    for file_id, name in files_to_download:
            ok, real_name = is_pdf(drive, file_id)
            if ok:
                pdf_count += download_pdf(drive, file_id, real_name, download_dir)
            else:
                print(f"Skipping non-PDF: {real_name}")

    print(f"\nDone! Downloaded {pdf_count} new PDF(s) to:\n   {download_dir}\n")


if __name__ == "__main__":
    main()
import os
import io
import importlib.resources
from .colors import G, B, Y, C, R, RD, DM, W

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
]

DOWNLOADABLE_TYPES = {
    "application/pdf":   ".pdf",
    "video/mp4":         ".mp4",
    "video/quicktime":   ".mov",
    "video/x-matroska":  ".mkv",
    "video/webm":        ".webm",
    "application/zip":   ".zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
}

TOKEN_PATH = os.path.join(os.path.expanduser("~"), ".getlectures_token.json")

def is_authenticated():
    from google.oauth2.credentials import Credentials
    if not os.path.exists(TOKEN_PATH):
        return False
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return creds.valid or (creds.expired and creds.refresh_token is not None)

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

def logout():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
        print(f"{G}[Deleted local credentials file: {TOKEN_PATH}]{R}")
    else:
        print(f"{RD}[No local credentials file found ({TOKEN_PATH}).]{R}")


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
    material, page_token = [], None
    while True:
        resp = service.courses().courseWorkMaterials().list(
            courseId=course_id, pageToken=page_token
        ).execute()
        for mat in resp.get("courseWorkMaterial", []):
            if mat.get("topicId") == topic_id:
                material.append(mat)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return material

def get_announcement_materials(service, course_id):
    materials, page_token = [], None
    while True:
        resp = service.courses().announcements().list(
            courseId=course_id, pageToken=page_token
        ).execute()
        for announcement in resp.get("announcements", []):
            for mat in announcement.get("materials", []):
                df = mat.get("driveFile", {}).get("driveFile", {})
                if df.get("id"):
                    materials.append((df["id"], df.get("title", "unknown")))
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

def is_downloadable(drive_service, file_id):
    meta = drive_service.files().get(fileId=file_id, fields="mimeType,name").execute()
    mime = meta.get("mimeType", "")
    name = meta.get("name", file_id)
    ext  = DOWNLOADABLE_TYPES.get(mime)
    return ext is not None, name, mime


def download_file(drive_service, file_id, filename, dest_dir):
    from googleapiclient.http import MediaIoBaseDownload

    os.makedirs(dest_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in " ._-()" else "_" for c in filename)
    filepath  = os.path.join(dest_dir, safe_name)

    if os.path.exists(filepath):
        print(f"  {Y}[~]{R} Already exists, skipping: {DM}{safe_name}{R}")
        return 0

    request = drive_service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    with open(filepath, "wb") as f:
        f.write(buf.getvalue())
    print(f"  {G}[+]{R} {W}{safe_name}{R}")
    return 1
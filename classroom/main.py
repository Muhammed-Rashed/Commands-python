import argparse
import os
from googleapiclient.discovery import build
from . import display
from .colors import G, B, Y, C, R, RD, DM, W
from . import logic
from .utils import prompt, pick_from_list, pick_materials, pick_files_from_material, pick_announcement_files
from .settings import settings

def cmd_get(args):
    display.show_status("Authenticating with Google...")
    creds     = logic.get_credentials()
    classroom = build("classroom", "v1", credentials=creds)
    drive     = build("drive",     "v3", credentials=creds)
    display.show_success("Authenticated!\n")

    display.show_status("Fetching your active courses...")
    courses = logic.list_courses(classroom)
    if not courses:
        display.show_error("No active courses found.")
        return

    course = pick_from_list("course", courses, "name")
    display.show_status("Fetching topics...")
    topics = logic.list_topics(classroom, course["id"])
    if not topics:
        display.show_error("No topics found in this course.")
        return

    topic = pick_from_list("topic", topics, "name")
    display.show_status("Fetching materials...")
    materials = logic.get_course_materials(classroom, course["id"], topic["topicId"])
    if not materials:
        display.show_error("No materials found in this topic.")
        return

    selected_materials = pick_materials(materials)

    files_to_download = []
    for mat in selected_materials:
        files_to_download.extend(pick_files_from_material(mat))

    if not files_to_download:
        display.show_error("No files selected. Exiting.")
        return

    default_dir  = os.path.join(os.path.expanduser("~"), "Downloads", "lectures")
    download_dir = prompt("Download folder path", default=default_dir)
    download_dir = os.path.expanduser(download_dir)

    display.show_summary(course, topic, selected_materials, download_dir)

    confirm = input("  Proceed? (Y/n): ").strip().lower()
    if confirm == "n":
        display.show_error("Cancelled.")
        return

    count = 0
    for file_id, name in files_to_download:
        ok, real_name, mime = logic.is_downloadable(drive, file_id)
        if ok:
            count += logic.download_file(drive, file_id, real_name, download_dir)
        else:
            display.show_warning(f"Skipping unsupported file type: {real_name} ({mime})")

    display.show_success(f"Done! Downloaded {count} file(s) to:\n     {download_dir}\n")


# -- Add new commands here --

# def cmd_drive(args):
#     pass

# def cmd_list(args):
#     pass


def build_parser():
    parser = argparse.ArgumentParser(
        prog="classroom",
        description="Google Classroom PDF Downloader",
    )

    sub = parser.add_subparsers(dest="command")

    # -- classroom get --
    get_parser = sub.add_parser("get", help="Download files from Classroom")
    get_parser.add_argument(
        "filter",
        nargs="?",
        choices=["pdfs", "all"],
        default="pdfs",
        help="What to download (default: pdfs)",
    )

    return parser

def authenticate():
    display.show_status("Authenticating with Google...")
    creds     = logic.get_credentials()
    classroom = build("classroom", "v1", credentials=creds)
    drive     = build("drive",     "v3", credentials=creds)
    display.show_success("Authenticated!\n")
    return classroom, drive


def main():
    classroom = None
    drive = None

    while True:
        display.MainMenu()
        choice = input("  Your choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        elif choice == "3":
            settings()
            continue

        elif choice != "1":
            display.show_error("Invalid choice.")
            continue

        if classroom is None or drive is None:
            classroom, drive = authenticate()

        display.show_status("Fetching your active courses...")
        courses = logic.list_courses(classroom)
        if not courses:
            display.show_error("No active courses found.")
            continue

        course = pick_from_list("course", courses, "name")

        display.show_status("Fetching topics...")
        topics = logic.list_topics(classroom, course["id"])

        files_to_download = []

        if not topics:
            display.show_warning("No topics found in this course.")
            display.show_status("Checking for announcement materials...")
            announcement_files = logic.get_announcement_materials(classroom, course["id"])
            if not announcement_files:
                display.show_error("No materials found at all in this course.")
                continue
            selected = pick_announcement_files(announcement_files)
            files_to_download.extend(selected)

        else:
            topic = pick_from_list("topic", topics, "name")

            display.show_status("Fetching materials...")
            materials = logic.get_course_materials(classroom, course["id"], topic["topicId"])
            if not materials:
                display.show_error("No materials found in this topic.")
                continue

            selected_materials = pick_materials(materials)
            for mat in selected_materials:
                files_to_download.extend(pick_files_from_material(mat))

            display.show_status("Checking for announcement materials...")
            announcement_files = logic.get_announcement_materials(classroom, course["id"])
            if announcement_files:
                selected = pick_announcement_files(announcement_files)
                files_to_download.extend(selected)

        if not files_to_download:
            display.show_error("No files selected.")
            continue

        default_dir  = os.path.join(os.path.expanduser("~"), "Downloads", "lectures")
        download_dir = prompt("Download folder path", default=default_dir)
        download_dir = os.path.expanduser(download_dir)

        confirm = input("  Proceed? (Y/n): ").strip().lower()
        if confirm == "n":
            display.show_error("Cancelled.")
            continue

        count = 0
        for file_id, name in files_to_download:
            ok, real_name, mime = logic.is_downloadable(drive, file_id)
            if ok:
                count += logic.download_file(drive, file_id, real_name, download_dir)
            else:
                display.show_warning(f"Skipping unsupported type: {real_name} ({mime})")

        display.show_success(
            f"Done! Downloaded {count} file(s) to:\n     {download_dir}\n"
        )

if __name__ == "__main__":
    main()
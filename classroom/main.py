import os
from googleapiclient.discovery import build

import display
import logic
from utils import prompt, pick_from_list, pick_materials, pick_files_from_material


def main():
    display.MainMenu()
    choice = input("  Your choice: ").strip()

    if choice == "0":
        return

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

    pdf_count = 0
    for file_id, name in files_to_download:
        ok, real_name = logic.is_pdf(drive, file_id)
        if ok:
            pdf_count += logic.download_pdf(drive, file_id, real_name, download_dir)
        else:
            display.show_warning(f"Skipping non-PDF: {real_name}")

    display.show_success(f"Done! Downloaded {pdf_count} new PDF(s) to:\n     {download_dir}\n")


if __name__ == "__main__":
    main()
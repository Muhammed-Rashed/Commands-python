from .logic import is_authenticated
from .colors import G, B, Y, C, R, RD, DM, W, P

def MainMenu(user_email=None, save_path=None, authenticated=False):
    authenticated = is_authenticated()
    status = f"{G}[authenticated]{R}" if authenticated else f"{RD}[x] Not signed in{R}"
    print(f"""
{G}+------------------------------------------+{R}
{G}|{R}  {B}Google Classroom PDF Downloader{R}  {P}v1.2{R}  {G}|{R}
{G}+------------------------------------------+{R}

{C}  User   :{R} {W}{user_email or 'Not signed in'}{R}
{C}  Save to:{R} {W}{save_path or '~/Downloads/lectures'}{R}
{C}  Status :{R} {status}

{DM}  ------------------------------------------{R}
  {Y}[1]{R} Download   {Y}[2]{R} Pick Course
  {Y}[3]{R} Settings        {RD}[0]{R} Exit
{DM}  ------------------------------------------{R}
""")

def show_summary(course, topic, selected_materials, download_dir):
    print(f"""
{DM}  ------------------------------------------{R}
{C}  Course :{R} {W}{course['name']}{R}
{C}  Topic  :{R} {W}{topic['name']}{R}
{C}  Files  :{R} {W}{len(selected_materials)} selected{R}
{C}  Save to:{R} {W}{download_dir}{R}
{DM}  ------------------------------------------{R}
""")

def show_status(msg):  print(f"  {B}[*]{R} {msg}")
def show_success(msg): print(f"  {G}[+]{R} {msg}")
def show_warning(msg): print(f"  {Y}[!]{R} {msg}")
def show_error(msg):   print(f"  {RD}[!]{R} {msg}")
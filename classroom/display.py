R  = "\033[0m"
G  = "\033[38;5;114m"
B  = "\033[38;5;111m"
Y  = "\033[38;5;179m"
C  = "\033[38;5;117m"
P  = "\033[38;5;141m"
RD = "\033[38;5;203m"
DM = "\033[38;5;241m"
W  = "\033[97m"

def MainMenu(user_email=None, save_path=None, authenticated=False):
    status = f"{G}[ok]{R}" if authenticated else f"{RD}[x] Not signed in{R}"
    print(f"""
{G}+------------------------------------------+{R}
{G}|{R}  {B}Google Classroom PDF Downloader{R}  {P}v1.1{R}  {G}|{R}
{G}+------------------------------------------+{R}

{C}  User   :{R} {W}{user_email or 'Not signed in'}{R}
{C}  Save to:{R} {W}{save_path or '~/Downloads/lectures'}{R}
{C}  Status :{R} {status}

{DM}  ------------------------------------------{R}
  {Y}[1]{R} Download PDFs   {Y}[2]{R} Pick Course
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
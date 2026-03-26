from .colors import G, B, Y, C, R, RD, DM, W, P
from .logic import get_credentials, logout

def settings():
    print(f"\n  {DM}Available settings:{R}")
    print(f"    {Y}{1}){R} {W}Authenticate{R}")
    print(f"    {Y}{2}){R} {W}Log out{R}")
    print(f"    {Y}{3}){R} {W}Colors{R}")
    while True:
        choice = input(f"\n  {C}>{R} Enter a number to choose: ").strip()
        if choice.isdigit():
            if choice == "1":
                get_credentials()
            elif choice == "2":
                logout()
            else:
                print(f"  {RD}[!]{R} Invalid number, try again.")
        else:
            print(f"  {RD}[!]{R} No match for '{choice}', try again.")
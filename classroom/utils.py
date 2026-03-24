from .display import G, B, Y, C, R, RD, DM, W, P

def prompt(question, default=None):
    if default:
        answer = input(f"  {C}>{R} {question} {DM}[{default}]{R}: ").strip()
        return answer if answer else default
    else:
        while True:
            answer = input(f"  {C}>{R} {question}: ").strip()
            if answer:
                return answer
            print(f"  {RD}[!]{R} This field is required, please enter a value.")

def pick_from_list(label, items, name_key):
    print(f"\n  {DM}Available {label}s:{R}")
    for i, item in enumerate(items, 1):
        print(f"    {Y}{i}){R} {W}{item[name_key]}{R}")
    while True:
        choice = input(f"\n  {C}>{R} Enter the number of your {label} (or type part of the name): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            print(f"  {RD}[!]{R} Invalid number, try again.")
        else:
            matches = [i for i in items if choice.lower() in i[name_key].lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"  {Y}[?]{R} Multiple matches, please be more specific:")
                for m in matches:
                    print(f"      {DM}-{R} {m[name_key]}")
            else:
                print(f"  {RD}[!]{R} No match for '{choice}', try again.")

def pick_files_from_material(material):
    all_files = []
    for mat in material.get("materials", []):
        df = mat.get("driveFile", {}).get("driveFile", {})
        if df.get("id"):
            all_files.append((df["id"], df.get("title", "unknown")))

    if not all_files:
        print(f"  {RD}[!]{R} No files found in '{material.get('title', 'Untitled')}'")
        return []

    print(f"\n  {B}[*]{R} {W}{material.get('title', 'Untitled')}{R} {DM}({len(all_files)} file(s)){R}")
    for i, (fid, name) in enumerate(all_files, 1):
        print(f"    {Y}{i}){R} {name}")

    print(f"\n  {G}A){R} Download ALL files")
    print(f"  {RD}S){R} Skip this material")
    print(f"  {DM}Or enter numbers separated by commas (e.g. 1,3){R}")

    while True:
        choice = input(f"\n  {C}>{R} Your choice: ").strip().lower()
        if choice == "a":
            return all_files
        elif choice == "s":
            print(f"  {Y}[~]{R} Skipped.")
            return []
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                for idx in indices:
                    if idx < 0 or idx >= len(all_files):
                        print(f"  {RD}[!]{R} Number {idx + 1} is out of range, try again.")
                        break
                else:
                    return [all_files[i] for i in indices]
            except ValueError:
                print(f"  {RD}[!]{R} Please enter 'A' for all, 'S' to skip, or numbers like 1,2,3")

def pick_materials(material):
    print(f"\n  {DM}Available materials ({len(material)} found):{R}")
    for i, mat in enumerate(material, 1):
        pdf_count = sum(
            1 for m in mat.get("materials", [])
            if m.get("driveFile", {}).get("driveFile", {}).get("id")
        )
        print(f"    {Y}{i}){R} {W}{mat.get('title', 'Untitled')}{R}  {DM}({pdf_count} file(s)){R}")

    print(f"\n  {G}A){R} Download ALL materials")
    print(f"  {DM}Or enter numbers separated by commas (e.g. 1,3,5){R}")

    while True:
        choice = input(f"\n  {C}>{R} Your choice: ").strip().lower()
        if choice == "a":
            return material
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected = []
                valid = True
                for idx in indices:
                    if 0 <= idx < len(material):
                        selected.append(material[idx])
                    else:
                        print(f"  {RD}[!]{R} Number {idx + 1} is out of range, try again.")
                        valid = False
                        break
                if valid and selected:
                    return selected
            except ValueError:
                print(f"  {RD}[!]{R} Please enter 'A' for all, or numbers like 1,2,3")
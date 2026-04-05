#!/usr/bin/env python3
"""
File Organizer - GUI Application (macOS Native)
Organizes files into categories with meaningful names.
Uses native macOS dialogs for the GUI.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import re
import subprocess
import sys


# Category definitions with file extensions
CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".numbers"],
    "Presentations": [".ppt", ".pptx", ".key"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic", ".webp", ".svg", ".ico", ".tiff"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a", ".wma", ".ogg"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".yaml", ".yml"],
    "Installers": [".dmg", ".pkg", ".exe", ".msi", ".deb", ".rpm", ".app"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
    "Ebooks": [".epub", ".mobi", ".azw3"],
}

# Keywords for smart subcategorization
SMART_KEYWORDS = {
    "House_Property": ["lease", "mortgage", "deed", "property", "home", "rent", "apartment",
                       "tenant", "landlord", "hoa", "maintenance", "closing", "escrow",
                       "appraisal", "inspection", "realtor", "housing", "house", "flat",
                       "agreement", "rental", "move", "furniture", "appliance"],
    "Bills_Utilities": ["bill", "utility", "electric", "electricity", "water", "gas",
                        "internet", "wifi", "broadband", "phone", "mobile", "cable",
                        "subscription", "payment", "due", "invoice", "receipt"],
    "IDs_Identity": ["aadhaar", "aadhar", "pan", "passport", "visa", "license", "licence",
                     "driving", "voter", "id card", "identity", "ssn", "social security",
                     "birth certificate", "citizenship", "immigration", "greencard",
                     "oci", "permit", "registration"],
    "Financial_Banking": ["bank", "statement", "account", "tax", "itr", "salary", "payroll",
                          "payslip", "income", "investment", "mutual fund", "stock", "trading",
                          "loan", "emi", "credit", "debit", "transaction", "budget", "savings",
                          "fd", "fixed deposit", "insurance", "policy", "premium", "claim"],
    "Medical_Health": ["medical", "health", "hospital", "doctor", "prescription", "lab",
                       "test", "report", "diagnosis", "treatment", "vaccine", "vaccination",
                       "covid", "medicine", "pharmacy", "clinic", "dental", "xray", "scan",
                       "mri", "blood", "checkup"],
    "Travel": ["ticket", "flight", "boarding", "hotel", "itinerary", "travel", "booking",
               "reservation", "emirates", "airline", "trip", "tour", "cruise", "railway",
               "train", "bus", "cab", "uber", "ola"],
    "Work_Employment": ["offer letter", "joining", "employment", "salary", "appraisal",
                        "promotion", "resignation", "experience", "relieving", "company",
                        "office", "hr", "employee", "contract", "nda", "project", "client"],
    "Education_Certificates": ["degree", "diploma", "certificate", "marksheet", "transcript",
                               "school", "college", "university", "course", "exam", "result",
                               "graduation", "semester", "education", "academic", "admission"],
    "Personal_Family": ["marriage", "wedding", "birth", "death", "family", "will", "nomination",
                        "affidavit", "notary", "legal", "court", "petition", "personal",
                        "photo", "invitation", "letter"],
    "Screenshots": ["screenshot", "screen shot", "capture", "snip", "screen grab"],
}

NAME_MAPPINGS = {
    "aadhaar": "Aadhaar_Card", "aadhar": "Aadhaar_Card", "pan": "PAN_Card",
    "passport": "Passport", "driving": "Driving_License", "voter": "Voter_ID",
    "license": "License", "bank statement": "Bank_Statement", "salary slip": "Salary_Slip",
    "payslip": "Salary_Slip", "payroll": "Payroll_Document", "tax": "Tax_Document",
    "itr": "Income_Tax_Return", "invoice": "Invoice", "receipt": "Receipt",
    "lease": "Lease_Agreement", "rental agreement": "Rental_Agreement",
    "mortgage": "Mortgage_Document", "property": "Property_Document",
    "deed": "Property_Deed", "electricity": "Electricity_Bill",
    "electric bill": "Electricity_Bill", "water bill": "Water_Bill",
    "gas bill": "Gas_Bill", "phone bill": "Phone_Bill", "internet bill": "Internet_Bill",
    "prescription": "Medical_Prescription", "lab report": "Lab_Report",
    "medical report": "Medical_Report", "vaccine": "Vaccination_Certificate",
    "marksheet": "Marksheet", "degree": "Degree_Certificate",
    "transcript": "Academic_Transcript", "insurance": "Insurance_Policy",
    "policy": "Insurance_Policy", "claim": "Insurance_Claim",
}

SKIP_ITEMS = {".DS_Store", ".localized", "Thumbs.db", "desktop.ini"}


# ============== macOS Native GUI Functions ==============

def show_alert(title: str, message: str):
    """Show a macOS alert dialog."""
    script = f'''
    display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"
    '''
    subprocess.run(['osascript', '-e', script], capture_output=True)


def show_notification(title: str, message: str):
    """Show a macOS notification."""
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script], capture_output=True)


def ask_yes_no(title: str, message: str) -> bool:
    """Show a yes/no dialog and return the result."""
    script = f'''
    display dialog "{message}" with title "{title}" buttons {{"No", "Yes"}} default button "Yes"
    set the button_pressed to the button returned of the result
    if the button_pressed is "Yes" then
        return "yes"
    else
        return "no"
    end if
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip() == "yes"


def select_folders() -> list[Path]:
    """Open macOS native folder picker with multi-select, starting from home directory."""
    script = '''
    set homeFolder to path to home folder
    set folderList to choose folder with prompt "Select folder(s) to organize (Cmd+Click for multiple):" default location homeFolder with multiple selections allowed
    set posixPaths to ""
    repeat with aFolder in folderList
        set posixPaths to posixPaths & POSIX path of aFolder & linefeed
    end repeat
    return posixPaths
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        paths = [Path(p.strip()) for p in result.stdout.strip().split('\n') if p.strip()]
        return paths
    return []


def show_preview_dialog(preview_text: str, file_count: int) -> bool:
    """Show preview in a dialog with scrollable text."""
    # Escape quotes for AppleScript
    preview_text = preview_text.replace('"', '\\"').replace("'", "\\'")

    script = f'''
    set previewText to "{preview_text}"
    display dialog "Found {file_count} files to organize.

Preview of changes (first 20 shown):
----------------------------------------
" & previewText & "
----------------------------------------

Do you want to proceed?" with title "File Organizer - Preview" buttons {{"Cancel", "Organize"}} default button "Organize"
    set the button_pressed to the button returned of the result
    if the button_pressed is "Organize" then
        return "yes"
    else
        return "no"
    end if
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip() == "yes"


def show_progress(message: str):
    """Print progress to terminal."""
    print(message)


# ============== File Organization Logic ==============

def get_smart_subcategory(filename: str) -> str:
    name_lower = filename.lower()
    for subcategory, keywords in SMART_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return subcategory
    return "General"


def get_category(file_path: Path) -> tuple[str, str]:
    ext = file_path.suffix.lower()
    name = file_path.stem.lower()

    main_category = "Other"
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            main_category = category
            break

    subcategory = get_smart_subcategory(name)
    return main_category, subcategory


def extract_date_from_name(name: str) -> str:
    match = re.search(r'(\d{4})[-_](\d{2})[-_](\d{2})', name)
    if match:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}"
    match = re.search(r'(\d{2})[-_](\d{2})[-_](\d{4})', name)
    if match:
        return f"{match.group(3)}{match.group(2)}{match.group(1)}"
    match = re.search(r'(\d{8})', name)
    if match:
        return match.group(1)
    return ""


def generate_meaningful_name(original_name: str, subcategory: str) -> str:
    name = original_name
    name_lower = name.lower()

    for keyword, meaningful_name in NAME_MAPPINGS.items():
        if keyword in name_lower:
            date_suffix = extract_date_from_name(name)
            if date_suffix:
                return f"{meaningful_name}_{date_suffix}"
            return meaningful_name

    if "whatsapp" in name_lower and "image" in name_lower:
        date_part = extract_date_from_name(name)
        if date_part:
            return f"WhatsApp_Photo_{date_part}"
        return f"WhatsApp_Photo_{datetime.now().strftime('%Y%m%d')}"

    if "screenshot" in name_lower or "screen shot" in name_lower:
        date_part = extract_date_from_name(name)
        if date_part:
            return f"Screenshot_{date_part}"
        return f"Screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if len(name) > 50 and any(c in name for c in "=-_"):
        words = name.replace("-", " ").replace("_", " ").split()
        meaningful_words = [w for w in words if len(w) > 3 and not w.isdigit()
                          and not all(c in "0123456789abcdef" for c in w.lower())]
        if meaningful_words:
            return "_".join(meaningful_words[:4]).title()
        return f"{subcategory}_{datetime.now().strftime('%Y%m%d')}"

    clean_name = name.replace(" ", "_").replace("-", "_")
    if not clean_name.strip("_"):
        return f"{subcategory}_Document"

    while "__" in clean_name:
        clean_name = clean_name.replace("__", "_")
    clean_name = clean_name.strip("_")

    parts = clean_name.split("_")
    clean_name = "_".join(word.capitalize() if word.islower() else word for word in parts)

    return clean_name


def analyze_folder(source_dir: Path) -> list:
    """Analyze folder and return list of operations (recursively)."""
    organized_dir = source_dir / "Organized_Files"
    operations = []

    def process_directory(current_dir: Path):
        """Recursively process a directory and its subdirectories."""
        for item in current_dir.iterdir():
            if item.name.startswith(".") or item.name in SKIP_ITEMS:
                continue
            if item.name == "Organized_Files":
                continue

            if item.is_dir():
                # Recursively process subdirectories
                process_directory(item)
                continue

            category, subcategory = get_category(item)
            original_stem = item.stem
            extension = item.suffix
            new_name = generate_meaningful_name(original_stem, subcategory)

            target_dir = organized_dir / category / subcategory
            target_path = target_dir / f"{new_name}{extension}"

            counter = 1
            base_name = new_name
            while target_path.exists() or any(op["target"] == target_path for op in operations):
                new_name = f"{base_name}_{counter}"
                target_path = target_dir / f"{new_name}{extension}"
                counter += 1

            operations.append({
                "source": item,
                "target": target_path,
                "category": category,
                "subcategory": subcategory,
                "original_name": item.name,
                "relative_path": str(item.relative_to(source_dir)),
                "new_name": f"{new_name}{extension}",
                "renamed": new_name != original_stem
            })

    process_directory(source_dir)
    return operations


def organize_files(operations: list, source_dir: Path):
    """Perform the actual file organization."""
    organized_dir = source_dir / "Organized_Files"

    for i, op in enumerate(operations):
        op["target"].parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(op["source"]), str(op["target"]))
        source_path = op.get("relative_path", op["original_name"])
        show_progress(f"[{i+1}/{len(operations)}] Moved: {source_path}")

    return organized_dir


def generate_preview_text(operations: list) -> str:
    """Generate preview text for dialog."""
    lines = []
    for op in operations[:20]:  # Show first 20
        source_path = op.get("relative_path", op["original_name"])
        if op["renamed"]:
            lines.append(f"{source_path} -> {op['new_name']}")
        else:
            lines.append(f"{source_path} (no rename)")

    if len(operations) > 20:
        lines.append(f"... and {len(operations) - 20} more files")

    return "\\n".join(lines)


# ============== Main Application ==============

def main():
    print("\n" + "=" * 50)
    print("      FILE ORGANIZER")
    print("=" * 50)

    # Step 1: Select folders (multi-select)
    print("\nStep 1: Select folder(s) to organize...")
    folders = select_folders()

    if not folders:
        show_alert("Cancelled", "No folder selected. Exiting.")
        print("No folder selected. Exiting.")
        return

    print(f"Selected {len(folders)} folder(s):")
    for folder in folders:
        print(f"  - {folder}")

    # Step 2: Analyze all folders
    print("\nStep 2: Analyzing files...")
    all_operations = []
    for folder in folders:
        operations = analyze_folder(folder)
        for op in operations:
            op["source_folder"] = folder
        all_operations.extend(operations)

    if not all_operations:
        show_alert("No Files", "No files found to organize in the selected folder(s).")
        print("No files to organize.")
        return

    print(f"Found {len(all_operations)} files to organize across {len(folders)} folder(s).")

    # Step 3: Show preview and confirm
    print("\nStep 3: Showing preview...")
    preview_text = generate_preview_text(all_operations)

    if not show_preview_dialog(preview_text, len(all_operations)):
        show_alert("Cancelled", "Operation cancelled. No files were moved.")
        print("Operation cancelled.")
        return

    # Step 4: Organize files
    print("\nStep 4: Organizing files...")
    organized_dirs = set()
    for folder in folders:
        folder_ops = [op for op in all_operations if op["source_folder"] == folder]
        if folder_ops:
            organized_dir = organize_files(folder_ops, folder)
            organized_dirs.add(organized_dir)

    # Step 5: Show completion
    show_alert("Complete!", f"Successfully organized {len(all_operations)} files!\\n\\nOrganized into {len(organized_dirs)} location(s).")
    show_notification("File Organizer", f"Organized {len(all_operations)} files!")

    print(f"\nDone! Files organized into {len(organized_dirs)} location(s).")

    # Open the organized folders in Finder
    for organized_dir in organized_dirs:
        subprocess.run(['open', str(organized_dir)])


if __name__ == "__main__":
    main()

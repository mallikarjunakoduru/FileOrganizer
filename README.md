# File Organizer

A macOS native GUI application that automatically organizes files into categorized folders with smart naming.

## Features

- **Recursive Processing** - Scans all nested folders, no matter how deep
- **Multi-Folder Selection** - Select multiple folders at once (Cmd+Click)
- **Smart Categorization** - Organizes files into categories like Documents, Images, Videos, Code, etc.
- **Intelligent Subcategories** - Detects keywords to create subcategories (Financial, Medical, Travel, etc.)
- **Meaningful Renaming** - Cleans up messy filenames while preserving important info
- **Native macOS Dialogs** - Uses native folder picker and notifications

## Categories

| Category | Extensions |
|----------|------------|
| Documents | .pdf, .doc, .docx, .txt, .rtf, .odt, .pages |
| Spreadsheets | .xls, .xlsx, .csv, .numbers |
| Presentations | .ppt, .pptx, .key |
| Images | .jpg, .jpeg, .png, .gif, .bmp, .heic, .webp, .svg |
| Videos | .mp4, .mov, .avi, .mkv, .wmv, .flv, .webm |
| Audio | .mp3, .wav, .aac, .flac, .m4a, .wma, .ogg |
| Archives | .zip, .rar, .7z, .tar, .gz, .bz2 |
| Code | .py, .js, .ts, .html, .css, .java, .cpp, .json |
| Installers | .dmg, .pkg, .exe, .msi, .app |
| Fonts | .ttf, .otf, .woff, .woff2 |
| Ebooks | .epub, .mobi, .azw3 |

## Smart Subcategories

Files are automatically sorted into subcategories based on keywords:

- **House_Property** - lease, mortgage, rental agreements
- **Bills_Utilities** - electricity, water, internet bills
- **IDs_Identity** - passport, license, Aadhaar, PAN
- **Financial_Banking** - bank statements, tax documents, investments
- **Medical_Health** - prescriptions, lab reports, medical records
- **Travel** - tickets, boarding passes, hotel bookings
- **Work_Employment** - offer letters, contracts, payslips
- **Education_Certificates** - degrees, transcripts, marksheets

## Usage

1. Run the application:
   ```bash
   python3 organize_files.py
   ```

2. Select one or more folders in the native macOS dialog (Cmd+Click for multiple)

3. Review the preview of changes

4. Click "Organize" to proceed

5. Files are moved to `Organized_Files/` within each selected folder

## Requirements

- macOS (uses native AppleScript dialogs)
- Python 3.x

## License

MIT License

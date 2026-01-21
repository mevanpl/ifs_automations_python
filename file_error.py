import os
import sys
import shutil
from datetime import datetime

# Define where to create the folders
BASE_FOLDER = r"E:\RPA\TraceToolCertificate"

def move_to_done(file_path):
    # Today's date
    today = datetime.now()
    year  = str(today.year)                 # 2025
    month = today.strftime("%B")            # December
    day   = f"{today.day:02d}"              # 02

    if not os.path.exists(file_path):
        print(f" File not found: {file_path}")
        return

    # DONE folder under BASE_FOLDER
    done_root = os.path.join(BASE_FOLDER, "NotArchivedInIFS")

    #  New folder structure: BASE_FOLDER\NotArchivedInIFS\YYYY\MonthName\DD
    year_path  = os.path.join(done_root, year)
    month_path = os.path.join(year_path, month)
    day_path   = os.path.join(month_path, day)

    os.makedirs(day_path, exist_ok=True)

    # Destination path
    filename = os.path.basename(file_path)
    destination = os.path.join(day_path, filename)

    # Move file
    shutil.move(file_path, destination)
    print(f" [DONE] moved file → {destination}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(' Usage: python file_done.py "file_full_path"')
        sys.exit(1)

    move_to_done(sys.argv[1])

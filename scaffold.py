import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def parse_and_build(md_file_path):
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Track the directory path at each level (Level 0 is current working directory)
        current_path_at_level = {0: Path(".")}
        
        # Track the current active folder level when using Header (#) syntax
        current_header_level = 0
        
        # Keep track of counts for the final message box
        folders_created = 0
        files_created = 0

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue  # Skip blank lines

            # -----------------------------------------------------------------
            # CASE 1: Markdown Headers (# folder_name, ## subfolder_name)
            # -----------------------------------------------------------------
            if stripped_line.startswith('#'):
                # Count the number of hashes to determine level (e.g., "##" = level 2)
                header_match = re.match(r'^(#+)\s*(.*)', stripped_line)
                if header_match:
                    hashes, folder_name = header_match.groups()
                    level = len(hashes)
                    
                    # Target path is relative to the parent level
                    parent_path = current_path_at_level.get(level - 1, Path("."))
                    target_path = parent_path / folder_name.strip()
                    
                    target_path.mkdir(parents=True, exist_ok=True)
                    print(f"📁 Created Folder (Header): {target_path}")
                    folders_created += 1
                    
                    # Update our active levels
                    current_path_at_level[level] = target_path
                    current_header_level = level
                continue

            # -----------------------------------------------------------------
            # CASE 2: Bullet Lists (- file) or ASCII Trees (├── file)
            # -----------------------------------------------------------------
            # Find where the actual name starts by stripping symbols/spaces
            raw_line = line.rstrip()
            match = re.search(r'([a-zA-Z0-9_\-\.\_\_]+)', raw_line)
            if not match:
                continue
            
            name = match.group(1)
            start_index = match.start()

            # Check if this item belongs to a Header structure or an Indented/Tree structure
            # If the line starts with tree symbols or significant spacing, it's tree/indented
            has_indentation = raw_line.startswith(' ') or any(c in raw_line[:start_index] for c in ['│', '├', '└'])

            if has_indentation:
                # Group items by spacing depth (approx 4 spaces per level)
                level = (start_index // 4) + 1
                is_folder = raw_line.strip().endswith('/') or ('.' not in name and '__' not in name)
                
                parent_path = current_path_at_level.get(level - 1, Path("."))
                target_path = parent_path / name
                
                if is_folder:
                    target_path.mkdir(parents=True, exist_ok=True)
                    print(f"📁 Created Folder (Tree): {target_path}")
                    folders_created += 1
                    current_path_at_level[level] = target_path
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.touch(exist_ok=True)
                    print(f"📄 Created File (Tree):   {target_path}")
                    files_created += 1
            else:
                # It belongs under the currently active markdown header folder
                parent_path = current_path_at_level.get(current_header_level, Path("."))
                target_path = parent_path / name
                
                # Check if it's explicitly a folder or file
                if raw_line.strip().endswith('/') or ('.' not in name and '__' not in name):
                    target_path.mkdir(parents=True, exist_ok=True)
                    print(f"📁 Created Folder (Under Header): {target_path}")
                    folders_created += 1
                    # Temporarily push down the level context for sub-items if it's a folder
                    current_path_at_level[current_header_level + 1] = target_path
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.touch(exist_ok=True)
                    print(f"📄 Created File (Under Header):   {target_path}")
                    files_created += 1

        messagebox.showinfo("Success", f"🎉 Scaffold generated successfully!\n\n📁 Folders created: {folders_created}\n📄 Files created: {files_created}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the project:\n{str(e)}")

def select_file():
    # Hide the main root window temporarily so only the file dialog shows up clean
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select Your Structure Markdown File",
        filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    
    if file_path:
        parse_and_build(file_path)
    else:
        print("❌ Action cancelled: No file selected.")

if __name__ == "__main__":
    select_file()

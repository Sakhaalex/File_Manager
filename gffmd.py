import os
import re
from pathlib import Path

def create_structure_from_md(md_file_path):
    if not os.path.exists(md_file_path):
        print(f"Error: The file '{md_file_path}' does not exist.")
        return

    # Track the current directory path hierarchy based on heading levels
    # e.g., {1: 'project_root', 2: 'project_root/src'}
    current_dirs = {}
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Match Markdown headings (Folders)
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                folder_name = heading_match.group(2).strip()
                
                # If it's the root folder (Level 1)
                if level == 1:
                    current_path = Path(folder_name)
                else:
                    # Find the parent folder from the previous levels
                    parent_path = current_dirs.get(level - 1)
                    if not parent_path:
                        # Fallback if headings skip a level
                        parent_path = current_dirs[max(current_dirs.keys())]
                    current_path = parent_path / folder_name
                
                # Store current level path and remove deeper stale paths
                current_dirs[level] = current_path
                current_dirs = {k: v for k, v in current_dirs.items() if k <= level}
                
                # Create the directory
                current_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created folder: {current_path}")
                continue

            # Match Markdown bullet points (Files)
            file_match = re.match(r'^[\-\*]\s+(.+)$', line.strip())
            if file_match:
                file_name = file_match.group(1).strip()
                
                # Determine where to place the file
                if current_dirs:
                    # Get the deepest active folder level
                    deepest_level = max(current_dirs.keys())
                    file_path = current_dirs[deepest_level] / file_name
                else:
                    # Fallback to current working directory if no folder heading exists yet
                    file_path = Path(file_name)
                
                # Create empty file
                file_path.touch()
                print(f"📄 Created file:   {file_path}")

if __name__ == "__main__":
    # Change 'config.md' to whatever your markdown file is named
    config_file = "test.md"
    print(f"Starting structure generation from '{config_file}'...\n")
    create_structure_from_md(config_file)
    print("\nStructure generation complete!")

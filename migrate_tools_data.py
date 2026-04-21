import json
import os
import shutil
from datetime import datetime

# Configuration
TOOLS_DIR = "/Users/kgt/Desktop/Projects/articleGen/CommandCenter/data/tools"
BACKUP_DIR = f"/Users/kgt/Desktop/Projects/articleGen/CommandCenter/data/tools_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def migrate_file(file_path, backup_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    new_commands = []
    
    # If the file has the old 'sections' structure
    if "sections" in data:
        for section in data["sections"]:
            for item in section.get("items", []):
                # Transform old item to new command structure
                command_obj = {
                    "command": item.get("command", ""),
                    "description": item.get("intent", ""), # Using intent as description/scenario
                    "scenario": item.get("intent", ""),   # Also using intent as scenario for now
                    "language": item.get("language", "bash"),
                    "tags": item.get("tags", []),
                    "is_curated": True,                   # Default existing items to curated
                    "man_page": ""                        # Placeholder
                }
                new_commands.append(command_obj)
        
        # Update the main data object
        data["commands"] = new_commands
        # Remove the old sections key to clean up
        del data["sections"]
    
    # If the file is already in the new format (or doesn't have sections), 
    # we ensure 'commands' exists even if empty
    elif "commands" not in data:
        data["commands"] = []

    # Write the updated data to the file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully migrated: {os.path.basename(file_path)}")

def main():
    if not os.path.exists(TOOLS_DIR):
        print(f"Error: Directory {TOOLS_DIR} does not exist.")
        return

    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"Created backup directory: {BACKUP_DIR}")

    files = [f for f in os.listdir(TOOLS_DIR) if f.endswith('.json')]
    
    if not files:
        print("No JSON files found in the tools directory.")
        return

    print(f"Found {len(files)} files. Starting migration...")

    for filename in files:
        file_path = os.path.join(TOOLS_DIR, filename)
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        # Copy to backup first
        shutil.copy2(file_path, backup_path)
        
        try:
            migrate_file(file_path, backup_path)
        except Exception as e:
            print(f"Failed to migrate {filename}: {e}")

    print("\nMigration complete!")
    print(f"Original files are backed up in: {BACKUP_DIR}")

if __name__ == "__main__":
    main()

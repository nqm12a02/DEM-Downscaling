#!/usr/bin/env python
"""Update metadata.txt with GitHub repository URLs"""
import os
import sys

def update_metadata_urls(github_username):
    """Update metadata.txt with GitHub repository URLs"""
    metadata_file = os.path.join(os.path.dirname(__file__), 'metadata.txt')
    
    if not os.path.exists(metadata_file):
        print(f"Error: {metadata_file} not found!")
        return False
    
    # Read current metadata
    with open(metadata_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace repository and tracker URLs
    new_repo_url = f"https://github.com/{github_username}/DEM_Downscaling"
    new_tracker_url = f"https://github.com/{github_username}/DEM_Downscaling/issues"
    
    # Find and replace
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('repository='):
            new_lines.append(f'repository={new_repo_url}')
        elif line.startswith('tracker='):
            new_lines.append(f'tracker={new_tracker_url}')
        else:
            new_lines.append(line)
    
    # Write back
    new_content = '\n'.join(new_lines)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated metadata.txt:")
    print(f"   Repository: {new_repo_url}")
    print(f"   Tracker: {new_tracker_url}")
    print()
    print("Next steps:")
    print("1. Run: python package_for_repository.py")
    print("2. Upload the new ZIP file to QGIS repository")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_metadata_urls.py <github_username>")
        print()
        print("Example:")
        print("  python update_metadata_urls.py nguyenquangminh")
        sys.exit(1)
    
    github_username = sys.argv[1]
    if update_metadata_urls(github_username):
        print("\n✅ Metadata updated successfully!")
    else:
        print("\n❌ Failed to update metadata")
        sys.exit(1)

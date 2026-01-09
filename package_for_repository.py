"""
Script to package the QGIS plugin for repository submission
Creates a ZIP file following QGIS plugin repository requirements
"""
import os
import zipfile
import shutil
from datetime import datetime

def package_for_repository(output_filename=None):
    """
    Package the plugin into a ZIP file ready for QGIS repository submission
    
    Parameters:
    -----------
    output_filename : str, optional
        Output ZIP filename. If None, generates name from metadata
    """
    # Get plugin directory (parent of this script)
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files and directories to exclude (repository submission should be clean)
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.git',
        '.gitignore',
        '*.zip',
        'create_icon.py',
        'create_dem_icon.py',
        'preview_ui.py',
        'view_ui_in_qgis.py',
        'open_ui_designer.bat',
        'package_plugin.py',
        'package_plugin.bat',
        'package_for_repository.py',
        'downscalingGeoRegister2021.py',  # Original script, not needed
        'QUICK_START.md',
        'VIEW_UI.md',
        'INSTALL.md',
        'PACKAGING.md',
        'DEM_SIZE_EVALUATION.md',  # Optional documentation
        'NODATA_SUPPORT.md',  # Optional documentation
        'PERFORMANCE.md',  # Optional documentation
        'GPU_SUPPORT.md',  # Optional documentation
        # Note: INSTALLATION_GUIDE.md, CUDA_TOOLKIT_INSTALL.md, INSTALL_CUPY_WINDOWS.md 
        # should be included - they're user documentation
        'test_gpu.py',  # Test script
        '*.tif',  # Exclude test DEM files
        '*.tiff',  # Exclude test DEM files
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '*.bak',
        '.DS_Store',
        'Thumbs.db',
    ]
    
    # Read plugin name from metadata
    metadata_file = os.path.join(plugin_dir, 'metadata.txt')
    plugin_name = 'DEM_Downscaling'
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('name='):
                    plugin_name = line.split('=', 1)[1].strip()
                    # Replace spaces with underscores for directory name
                    plugin_name = plugin_name.replace(' ', '_')
                    break
    
    # Generate output filename if not provided
    if output_filename is None:
        output_filename = f'{plugin_name}.zip'
    
    # Output in a subdirectory called "ready_to_install"
    output_dir = os.path.join(plugin_dir, '..', 'ready_to_install')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, output_filename)
    
    # Remove existing ZIP if it exists
    if os.path.exists(output_path):
        os.remove(output_path)
    
    print(f"Packaging plugin for QGIS repository: {plugin_name}")
    print(f"Output file: {output_path}")
    print()
    
    # Files to include (required files for QGIS plugin)
    required_files = [
        'metadata.txt',
        '__init__.py',
        'LICENSE',
    ]
    
    files_included = []
    
    # Create ZIP file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through plugin directory
        for root, dirs, files in os.walk(plugin_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(
                d.startswith(pattern.replace('*', '')) or 
                pattern.replace('*', '') in d
                for pattern in exclude_patterns
            )]
            
            # Skip the ready_to_install directory itself
            if 'ready_to_install' in root:
                continue
            
            # Process files
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, plugin_dir)
                
                # Skip files in ready_to_install
                if 'ready_to_install' in relative_path:
                    continue
                
                # Check if file should be excluded
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern.startswith('*'):
                        if file.endswith(pattern[1:]):
                            should_exclude = True
                            break
                    elif pattern in file or pattern in relative_path:
                        should_exclude = True
                        break
                
                # Always include documentation files (even if excluded pattern matches)
                doc_files = ['INSTALLATION_GUIDE.md', 'CUDA_TOOLKIT_INSTALL.md', 'INSTALL_CUPY_WINDOWS.md', 
                           'GPU_TROUBLESHOOTING.md', 'README.md']
                if file in doc_files:
                    should_exclude = False
                
                if should_exclude:
                    continue
                
                # Add file to ZIP (with plugin name as root directory)
                arcname = os.path.join(plugin_name, relative_path).replace('\\', '/')
                zipf.write(file_path, arcname)
                files_included.append(relative_path)
                print(f"Added: {relative_path}")
    
    # Verify required files are included
    missing_files = [f for f in required_files if f not in files_included]
    if missing_files:
        print(f"\nWARNING: Missing required files: {missing_files}")
    
    print()
    print("=" * 60)
    print("Plugin packaged successfully for QGIS repository!")
    print("=" * 60)
    print(f"File: {output_path}")
    print(f"Size: {os.path.getsize(output_path) / 1024:.2f} KB")
    print(f"Files included: {len(files_included)}")
    print()
    print("Next steps for repository submission:")
    print("1. Test the ZIP file by installing it in QGIS")
    print("2. Go to https://plugins.qgis.org/")
    print("3. Create an account if you don't have one")
    print("4. Go to 'Upload Plugin' section")
    print(f"5. Upload: {os.path.basename(output_path)}")
    print("6. Fill in the required information")
    print("7. Submit for review")
    print()
    print("Repository requirements checklist:")
    print("- [x] metadata.txt present")
    print("- [x] __init__.py present")
    print("- [x] No .pyc files")
    print("- [x] No development files")
    print("- [x] Proper directory structure")
    print("- [ ] Tested in QGIS (you need to verify)")
    print("- [ ] Icon present (verify icon.png exists)")
    
    return output_path

if __name__ == '__main__':
    import sys
    
    output_file = None
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    try:
        package_for_repository(output_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


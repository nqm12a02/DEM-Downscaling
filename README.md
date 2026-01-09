# DEM Downscaling Plugin for QGIS

QGIS plugin to increase DEM (Digital Elevation Model) resolution using the Hopfield Neural Network method with spatial dependence maximization and elevation constraints.

## Description

This plugin implements the DEM downscaling algorithm based on the research paper:

**"Downscaling Gridded DEMs Using the Hopfield Neural Network"**  
by Nguyen Quang Minh et al.  
IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing  
Volume 12, Issue 11, pp. 4426-4437, 2019  
DOI: [10.1109/IGARSS.2019.8932562](https://ieeexplore.ieee.org/document/8932562)

The plugin allows you to increase the resolution of DEM files by:
- Using spatial dependence maximization algorithm
- Applying elevation constraints based on Hopfield Neural Network approach
- Supporting resolution enhancement from 2x to 10x

## Features

- Select input DEM file (supports GeoTIFF, IMG, BIL formats)
- **NoData value support**: Automatically preserves NoData values from input raster
- **GPU acceleration**: Automatic GPU detection and acceleration using CuPy (8x faster for large DEMs)
- **Vectorized processing**: Uses NumPy tensor operations and SciPy convolution for 10-100x speed improvement (automatic if SciPy installed)
- Set resolution increase factor (zoom factor: 2-10)
- Adjust RSME parameter
- Real-time progress bar with percentage display
- Dialog stays open during processing with live updates
- Memory usage estimation and warnings
- Automatically load result into QGIS

## Installation

### Installation for Development

1. **Locate your QGIS plugins directory:**
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

2. **Copy the plugin folder** to the plugins directory above
   - Rename the folder to `dem_downscaling` (optional)

3. **Compile resources** (if needed):
   ```bash
   pyrcc5 -o resources.py resources.qrc
   ```

4. **Restart QGIS** or use Plugin Reloader

5. **Enable the plugin** in QGIS:
   - Go to `Plugins` > `Manage and Install Plugins...`
   - Click the `Installed` tab
   - Find "DEM Downscaling" and check the box

## Usage

1. Open QGIS
2. Go to menu **Plugins** > **DEM Downscaling**
3. In the dialog:
   - **Input DEM file**: Select the DEM file to enhance
   - **Output DEM file**: Choose the location to save the result file
   - **Zoom factor**: Select the resolution increase factor (2-10, default: 4)
   - **RSME parameter**: Adjust the RSME parameter (default: 4.0)
4. Click **Process**
5. Wait for processing to complete
6. The result file will be automatically loaded into QGIS

## Algorithm

The plugin implements the DEM downscaling algorithm based on the Hopfield Neural Network method described in the referenced paper. The algorithm consists of:

1. **Spatial Dependence Maximization**: Maximizes spatial dependence between neighboring pixels using a 3x3 window approach
2. **Elevation Constraints**: Ensures that the average elevation value of sub-pixels equals the original pixel value, maintaining elevation consistency
3. **Iterative Optimization**: Uses an iterative optimization loop (similar to Hopfield Neural Network energy minimization) until convergence threshold is reached

For detailed information about the algorithm, please refer to the original paper:
- Nguyen Quang Minh et al., "Downscaling Gridded DEMs Using the Hopfield Neural Network," IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, Volume 12, Issue 11, pp. 4426-4437, 2019, DOI: 10.1109/IGARSS.2019.8932562

## Requirements

- QGIS 3.0 or higher
- Python 3
- GDAL/OGR (included with QGIS)
- NumPy (included with QGIS)

## Project Structure

```
dem_downscaling/
├── metadata.txt                    # Plugin metadata
├── __init__.py                    # Plugin initialization
├── my_qgis_plugin.py              # Main plugin class
├── my_qgis_plugin_dialog.py       # Dialog UI handler
├── my_qgis_plugin_dialog_base.ui  # UI file (Qt Designer)
├── dem_downscaling_algorithm.py   # Downscaling algorithm
├── resources.qrc                  # Resource file
├── resources.py                   # Compiled resources
├── icon.png                       # Plugin icon
└── README.md                      # This file
```

## Development

### Customization

1. Edit `metadata.txt` with your information
2. Modify UI in `my_qgis_plugin_dialog_base.ui` (using Qt Designer)
3. Adjust algorithm in `dem_downscaling_algorithm.py`
4. Customize processing in `my_qgis_plugin_dialog.py`

### Compiling Resources

When modifying `resources.qrc`, recompile:

```bash
pyrcc5 -o resources.py resources.qrc
```

Or on Windows:

```powershell
pyrcc5.bat -o resources.py resources.qrc
```

## Citation

If you use this plugin in your research, please cite the original paper:

```
Nguyen Quang Minh, et al., "Downscaling Gridded DEMs Using the Hopfield Neural Network," 
IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 
Volume 12, Issue 11, pp. 4426-4437, 2019, 
doi: 10.1109/IGARSS.2019.8932562.
```

## Author

[Enter author name]

## License

[Enter license information]

## References

- **Original Algorithm**: Nguyen Quang Minh et al., "Downscaling Gridded DEMs Using the Hopfield Neural Network," IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, Volume 12, Issue 11, pp. 4426-4437, 2019. [IEEE Xplore](https://ieeexplore.ieee.org/document/8932562)
- [PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [QGIS Plugin Development Guide](https://docs.qgis.org/latest/en/docs/user_manual/plugins/plugins.html)
- GDAL/OGR Python API Documentation

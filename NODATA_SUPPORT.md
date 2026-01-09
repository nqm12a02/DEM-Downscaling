# NoData Value Support

## Overview

The DEM Downscaling plugin now fully supports raster files with NoData values. NoData pixels are preserved throughout the downscaling process and correctly maintained in the output file.

## How It Works

### 1. **Reading NoData Values**
- The plugin automatically detects NoData values from the input raster
- NoData values are read from the raster band metadata
- Supports any NoData value (e.g., -9999, -32768, NaN, etc.)

### 2. **Processing NoData Pixels**
- **Spatial Dependence**: NoData pixels are excluded from neighborhood calculations
- Only valid (non-NoData) pixels in the 3x3 window are used for calculations
- NoData pixels maintain their NoData value throughout iterations

### 3. **Elevation Constraints**
- Original pixels with NoData values result in all corresponding sub-pixels being set to NoData
- When calculating elevation constraints, only valid pixels are included in averages
- NoData areas are preserved in their original extent (scaled by zoom factor)

### 4. **Output Preservation**
- The original NoData value is preserved in the output raster
- NoData pixels in the output match the expanded NoData mask from the input
- The output raster band has the same NoData value set as the input

## Example Use Cases

### SRTM DEM with NoData
- SRTM DEMs often have NoData values for water bodies or areas outside coverage
- These NoData areas will be preserved in the downscaled output
- The downscaling algorithm only processes valid elevation data

### Cropped DEMs
- DEMs that have been clipped or cropped often have NoData around edges
- The plugin correctly handles these edge NoData values
- NoData boundaries are maintained in the output

### Multi-tile DEMs
- When combining DEM tiles, NoData may exist in gaps
- All NoData regions are correctly preserved during downscaling

## Technical Details

### NoData Detection
```python
# Automatically reads NoData from raster band
nodata_value = raster_band.GetNoDataValue()

# Creates mask for NoData pixels
nodata_mask = (data == nodata_value) | np.isnan(data)
```

### Processing Behavior
- NoData pixels are **not** included in:
  - Spatial dependence calculations
  - Elevation constraint averages
  - Energy minimization iterations

- NoData pixels are **preserved** as:
  - Original NoData value in output
  - Expanded mask covering all sub-pixels from original NoData pixel

### Output Handling
- Output raster uses the same NoData value as input
- If input has no NoData, output uses -9999 as default
- NoData mask is expanded by zoom factor (e.g., 4x zoom = 4x4 = 16 sub-pixels per original NoData pixel)

## Verification

You can verify NoData handling by:
1. Checking the input raster's NoData value in QGIS (Layer Properties > Information)
2. Processing the DEM with the plugin
3. Comparing NoData areas in input and output
4. Verifying output raster has the same NoData value set

## Limitations

- NoData values are preserved exactly as-is (no interpolation or estimation)
- If an entire 3x3 neighborhood is NoData, the center pixel remains NoData
- NoData areas cannot be "filled" or estimated by the algorithm




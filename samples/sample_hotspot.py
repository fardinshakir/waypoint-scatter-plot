"""
Generate sample hotspot maps with dummy waypoint data.
Uses sample_waypoint_data.json for testing without real data paths.
"""
import matplotlib.pyplot as plt
import contextily as ctx
import geopandas as gpd
from pyproj import Transformer
from matplotlib import rcParams
import json
import math
import time

def calculate_zoom_level(buffer_meters):
    max_zoom_level = 22  # Maximum zoom level supported by Mapbox
    min_zoom_level = 12  # Minimum zoom level for clear map overview
    zoom_scale_factor = 4000  # Scale factor for zoom calculation
    zoom_level = max(min_zoom_level,
        min(max_zoom_level, int(math.log(buffer_meters / zoom_scale_factor) * -1 + max_zoom_level)))
    return zoom_level

def sample_plotter(system):
    """Generate hotspot map for a single system using sample data."""
    # Load sample data
    with open('sample_waypoint_data.json', 'r') as f:
        monthly_data = json.load(f)

    if system not in monthly_data:
        print(f"System {system} not found in sample data")
        return

    sysinfo = monthly_data[system]
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)  # WGS84 (lat/lon) → Web Mercator (x/y meters)
    coordinates = [[value[1], value[2]] for value in sysinfo.values()]  # [count, lat, lon] → extract [lat, lon]
    sizes = [value[0] * 100 for value in sysinfo.values()]  # Scale count by 100 for marker size

    coordinates_mercator = [transformer.transform(coord[1], coord[0]) for coord in coordinates]
    x = [coord[0] for coord in coordinates_mercator]
    y = [coord[1] for coord in coordinates_mercator]

    gdf = gpd.GeoDataFrame(
        sysinfo.keys(),
        geometry=gpd.points_from_xy(x, y),
        crs="EPSG:3857"
    )

    x_diff = max(x) - min(x)
    y_diff = max(y) - min(y)
    buffer_meters = (max(x_diff, y_diff) - min(x_diff, y_diff))

    if buffer_meters <= 30:
        buffer_meters = 70  # Minimum map viewport buffer in meters

    center_x = sum(x) / len(x)
    center_y = sum(y) / len(y)

    x_min = center_x - buffer_meters
    x_max = center_x + buffer_meters
    y_min = center_y - buffer_meters
    y_max = center_y + buffer_meters

    x_min -= buffer_meters
    x_max += buffer_meters
    y_min -= buffer_meters
    y_max += buffer_meters

    aspect_ratio = 4 / 3  # Standard 4:3 display aspect ratio
    width = x_max - x_min
    height = y_max - y_min

    if width / height > aspect_ratio:
        extra_height = (width / aspect_ratio) - height
        y_min -= extra_height / 2
        y_max += extra_height / 2
    else:
        extra_width = (height * aspect_ratio) - width
        x_min -= extra_width / 2
        x_max += extra_width / 2

    rcParams['font.family'] = 'DejaVu Sans'
    rcParams['font.size'] = 12

    fig, ax = plt.subplots(figsize=(10, 7.5))
    gdf.plot(ax=ax, color='royalblue', markersize=sizes, edgecolor=None, alpha=0.8)

    sign = '+'
    for i, key in enumerate(sysinfo.keys()):
        if sign == '+':
            label_offset_y = (buffer_meters/4) + (buffer_meters/8)
            label_offset_x = (buffer_meters/4) + (buffer_meters/8)
            sign = '-'
        else:
            label_offset_y = (buffer_meters/4) - (buffer_meters/8)
            label_offset_x = (buffer_meters/4) - (buffer_meters/8)
            sign = '+'
        label_x = x[i] + label_offset_x
        label_y = y[i] + label_offset_y
        ax.plot([x[i], label_x], [y[i], label_y], color='white', linestyle='--', linewidth=2, alpha=0.9)
        ax.text(label_x, label_y, f"{key} ({sysinfo[key][0]})", fontsize=10, ha='left', va='bottom', color='black', style='italic', weight='light')

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.tick_params(
        axis='x',
        labelsize=8,
        labelcolor='white',
        pad=10,
        direction='out',
        length=5,
    )

    ax.tick_params(
        axis='y',
        labelsize=8,
        labelcolor='white',
        pad=10,
        direction='out',
        length=5,
    )

    # Add dummy map background (grid pattern as placeholder)
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#0f0f1e')

    # Add subtle grid as map reference
    ax.grid(True, color='#2a4a6a', linestyle=':', linewidth=0.5, alpha=0.3)

    ax.set_title(f'{system} - Hotspots (Sample Data)', fontsize=14, pad=15, loc='center', color='white', weight='bold')
    ax.grid(color='lightgray', linestyle='--', linewidth=0.5, alpha=0.6)

    plt.tight_layout()
    output_file = f"sample_{system}_hotspot.png"
    plt.savefig(output_file, dpi=150, facecolor='#1f1f1f')
    print(f"Saved {output_file}")
    plt.close(fig)


if __name__ == "__main__":
    try:
        start_time = time.time()
        sample_plotter("SYSTEM01")
        end_time = time.time()
        print(f"SYSTEM01 done in {round(end_time - start_time)}s")
    except Exception as e:
        print(f"Error: {e}")

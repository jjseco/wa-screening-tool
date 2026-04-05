import geopandas as gpd
import os
from config import ANALYSIS_CRS
from scripts.registry import LAYER_REGISTRY, get_layers_for_themes
from scripts.data_manager import get_layer_path


def load_layer(layer_key):
    """Load a single processed layer by its registry key."""

    if layer_key not in LAYER_REGISTRY:
        print(f"Layer '{layer_key}' not found in registry.")
        return None

    layer_def = LAYER_REGISTRY[layer_key]
    file_path = get_layer_path(layer_def["file"])

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    gdf = gpd.read_file(file_path)

    # Ensure correct CRS
    if gdf.crs is None or gdf.crs.to_epsg() != int(ANALYSIS_CRS.split(":")[1]):
        gdf = gdf.to_crs(ANALYSIS_CRS)

    print(f"Layer '{layer_key}' loaded. ({len(gdf)} features)")
    return gdf


def load_layers_for_themes(selected_themes):
    """Load all layers associated with the selected themes."""

    layer_keys = get_layers_for_themes(selected_themes)
    layers = {}

    for key in layer_keys:
        gdf = load_layer(key)
        if gdf is not None:
            layers[key] = gdf

    return layers


def load_all_layers():
    """Load all layers defined in the registry."""

    layers = {}
    for key in LAYER_REGISTRY:
        gdf = load_layer(key)
        if gdf is not None:
            layers[key] = gdf

    return layers
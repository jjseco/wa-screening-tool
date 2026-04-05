import geopandas as gpd
from scripts.registry import LAYER_REGISTRY


def get_nearby_names(layer_key, layer_gdf, buffer_union):
    """Get names or descriptions of features within a buffer zone."""

    layer_def = LAYER_REGISTRY.get(layer_key, {})
    nearby = layer_gdf[layer_gdf.geometry.intersects(buffer_union)]

    if len(nearby) == 0:
        return []

    names = []

    # Handle flag-based layers (e.g. ESA)
    if layer_def.get("name_flags"):
        found_flags = set()
        for _, row in nearby.iterrows():
            for col, label in layer_def["name_flags"].items():
                if col in row and row[col] == 1:
                    found_flags.add(label)
        names = list(found_flags) if found_flags else ["Environmentally Sensitive Area"]

    # Handle multiple combined fields (e.g. groundwater)
    elif layer_def.get("name_fields_combined"):
        seen = set()
        for _, row in nearby.iterrows():
            parts = []
            for col in layer_def["name_fields_combined"]:
                if col in row and str(row[col]).strip() not in ["", "nan", "None"]:
                    parts.append(str(row[col]).strip())
            combined = " | ".join(parts)
            if combined and combined not in seen:
                seen.add(combined)
                names.append(combined)

    # Handle single name field
    elif layer_def.get("name_field"):
        col = layer_def["name_field"]
        if col in nearby.columns:
            raw = nearby[col].dropna().unique().tolist()
            names = [str(n) for n in raw if str(n).strip() != ""]

    return names


def get_present(results, buffer_distances):
    """Determine if any features are present within the screening area."""
    if results["site_intersect"]:
        return True
    return any(results.get(f"within_{d}m", False) for d in buffer_distances)


def get_max_relevance(results, buffer_distances):
    """Determine the maximum relevance level based on query results."""
    if results["site_intersect"]:
        return "Site"
    for d in sorted(buffer_distances):
        if results.get(f"within_{d}m", False):
            return f"{d}m"
    return "None"


def get_primary_trigger(results, buffer_distances):
    """Determine the primary trigger description."""
    if results["site_intersect"]:
        return "Intersects site"
    for d in sorted(buffer_distances):
        if results.get(f"within_{d}m", False):
            return f"Within {d}m"
    max_d = max(buffer_distances)
    dist = results["nearest_distance_m"]
    if dist:
        return f"None within {max_d}m. Nearest at {dist}m"
    return f"None within {max_d}m"


def query_layer(layer_key, layer_gdf, site_gdf, buffers):
    """Run all spatial checks for a single layer against the site."""

    layer_def = LAYER_REGISTRY.get(layer_key, {})
    buffer_distances = sorted(buffers.keys())
    max_d = max(buffer_distances)

    results = {
        "layer_key": layer_key,
        "layer": layer_def.get("label", layer_key),
        "theme": layer_def.get("theme", ""),
        "site_intersect": False,
        "nearest_distance_m": None,
        "nearby_names": [],
        "present": False,
        "max_relevance": "None",
        "primary_trigger": f"None within {max_d}m",
        "comment": "",
    }

    # Initialise dynamic buffer keys
    for d in buffer_distances:
        results[f"within_{d}m"] = False
        results[f"count_{d}m"] = 0

    # Check if layer intersects the site point directly
    site_union = site_gdf.geometry.union_all()
    intersecting = layer_gdf[layer_gdf.geometry.intersects(site_union)]
    if len(intersecting) > 0:
        results["site_intersect"] = True

    # Check buffer intersections and counts
    for distance in buffer_distances:
        buffer_union = buffers[distance].geometry.union_all()
        intersecting_buffer = layer_gdf[layer_gdf.geometry.intersects(buffer_union)]
        count = len(intersecting_buffer)
        results[f"count_{distance}m"] = count
        if count > 0:
            results[f"within_{distance}m"] = True

    # Collect names from smallest buffer that has results
    for distance in buffer_distances:
        buffer_union = buffers[distance].geometry.union_all()
        names = get_nearby_names(layer_key, layer_gdf, buffer_union)
        if names:
            results["nearby_names"] = names
            break

    # Calculate nearest distance
    if not results["site_intersect"]:
        site_point = site_gdf.geometry.iloc[0]
        try:
            distances = layer_gdf.geometry.distance(site_point)
            distances = distances.dropna()
            if len(distances) > 0:
                min_dist = distances.min()
                if min_dist > 0:
                    results["nearest_distance_m"] = round(float(min_dist), 1)
        except Exception as e:
            print(f"Distance calculation error for {layer_key}: {e}")

    # Calculate present, max relevance and primary trigger
    results["present"] = get_present(results, buffer_distances)
    results["max_relevance"] = get_max_relevance(results, buffer_distances)
    results["primary_trigger"] = get_primary_trigger(results, buffer_distances)

    # Generate comment
    results["comment"] = generate_comment(
        layer_def.get("label", layer_key), results, buffer_distances
    )

    return results


def generate_comment(label, results, buffer_distances):
    """Generate an automatic comment based on query results."""
    max_d = max(buffer_distances)

    if results["site_intersect"]:
        return f"{label} intersects the site directly."
    for d in sorted(buffer_distances):
        if results.get(f"within_{d}m", False):
            return f"{label} identified within {d}m of the site."
    dist = results["nearest_distance_m"]
    if dist:
        return f"No {label} within {max_d}m. Nearest feature at {dist}m."
    return f"No {label} within {max_d}m."


def run_all_queries(layers, site_gdf, buffers):
    """Run spatial queries for all loaded layers."""

    all_results = []
    for layer_key, layer_gdf in layers.items():
        print(f"Querying layer: {layer_key}...")
        result = query_layer(layer_key, layer_gdf, site_gdf, buffers)
        all_results.append(result)

    return all_results

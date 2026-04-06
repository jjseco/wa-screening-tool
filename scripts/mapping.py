import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import os
from config import OUTPUTS_MAPS

# Buffer ring fill/edge colors — light grey tones (innermost first: 100m, 250m, 500m)
BUFFER_FILL_COLORS = ["#e8e8e8", "#f0f0f0", "#f5f5f5"]
BUFFER_EDGE_COLORS = ["#555555", "#777777", "#999999"]
BUFFER_ALPHA_FILL = 0.25

# Cadastre parcel / residential count label colors by buffer distance
BUFFER_PARCEL_COLORS = {
    100: "#d4a574",   # warm tan
    250: "#e8c99a",   # light tan
    500: "#f5e6d0",   # very light beige
}

# Community facility type colors
FACILITY_TYPE_COLORS = {
    "hospital": "#e63946",
    "school": "#f77f00",
    "church": "#9b5de5",
    "chapel": "#9b5de5",
    "cathedral": "#9b5de5",
    "mosque": "#9b5de5",
    "temple": "#9b5de5",
    "synagogue": "#9b5de5",
    "place_of_worship": "#9b5de5",
    "community_centre": "#2ec4b6",
    "community_hall": "#2ec4b6",
    "community": "#2ec4b6",
    "nursing_home": "#ff6b6b",
    "retirement_home": "#ff6b6b",
    "childcare": "#ffd166",
    "kindergarten": "#ffd166",
    "social_facility": "#06d6a0",
    "social_club": "#06d6a0",
    "civic": "#118ab2",
    "public": "#118ab2",
    "public_building": "#118ab2",
    "parish_hall": "#9b5de5",
    "scout_hall": "#06d6a0",
}
DEFAULT_FACILITY_COLOR = "#aaaaaa"

def _buffer_parcel_color(dist):
    """Return the parcel/label color for the given buffer distance."""
    return BUFFER_PARCEL_COLORS.get(dist, "#d4a574")

# Residential type colors
RESIDENTIAL_TYPE_COLORS = {
    "house": "#ffb3c1",
    "housing cluster": "#c1121f",
}

# Base layer styles
MAP_LAYER_STYLES = {
    "roads": {
        "color": "#bbbbbb", "alpha": 0.7, "linewidth": 0.5,
        "label": "Roads", "zorder": 1, "show_labels": False,
        "marker": None
    },
    "esa": {
        "color": "#e63946", "alpha": 0.25, "linewidth": 0.5,
        "label": "ESA", "zorder": 2, "show_labels": False,
        "marker": None
    },
    "wetlands": {
        "color": "#1d7bbf", "alpha": 0.25, "linewidth": 0.5,
        "label": "Wetlands", "zorder": 2, "show_labels": False,
        "marker": None
    },
    "ass": {
        "color": "#f4a261", "alpha": 0.25, "linewidth": 0.5,
        "label": "Acid Sulfate Soils", "zorder": 2, "show_labels": False,
        "marker": None
    },
    "soil_landscape_best": {
        "color": "#8B4513", "alpha": 0.25, "linewidth": 0.5,
        "label": "Soil Landscape - Best Available", "zorder": 2, "show_labels": False,
        "marker": None
    },
    "soil_group": {
        "color": "#D2691E", "alpha": 0.25, "linewidth": 0.5,
        "label": "Soil Group - WA Classification", "zorder": 2, "show_labels": False,
        "marker": None
    },
    "aboriginal_heritage": {
        "color": "#8B4513", "alpha": 0.20, "linewidth": 0.5,
        "label": "Aboriginal Heritage", "zorder": 2, "show_labels": False,
        "marker": None
    },
    "cadastre": {
        "color": "#999999", "alpha": 0.15, "linewidth": 0.3,
        "label": "Cadastral Parcels", "zorder": 3, "show_labels": False,
        "marker": None
    },
    "residential": {
        "color": "#ffb3c1", "alpha": 0.30, "linewidth": 0.3,
        "label": "Residential (Buildings WA)", "zorder": 4, "show_labels": False,
        "marker": None
    },
    "residential_osm": {
        "color": "#fffacd", "alpha": 0.40, "linewidth": 0.3,
        "label": "Residential (OSM)", "zorder": 4, "show_labels": False,
        "marker": None
    },
    "contaminated_sites": {
        "color": "#222222", "alpha": 0.9, "markersize": 8,
        "label": "Contaminated Sites", "zorder": 6,
        "show_labels": True, "label_field": "classification",
        "marker": "X"
    },
    "hospitals": {
        "color": "#e63946", "alpha": 0.9, "markersize": 12,
        "label": "Hospitals", "zorder": 7,
        "show_labels": True, "label_field": "name",
        "marker": "P"
    },
    "schools": {
        "color": "#f77f00", "alpha": 0.9, "markersize": 12,
        "label": "Schools", "zorder": 7,
        "show_labels": True, "label_field": "name",
        "marker": "s"
    },
    "community_facilities": {
        "color": "#9b5de5", "alpha": 0.9, "markersize": 10,
        "label": "Community Facilities", "zorder": 7,
        "show_labels": True, "label_field": "name",
        "marker": "^"
    },
}

def _build_buffer_styles(buffer_distances):
    """Build a {distance: style_dict} mapping for the given buffer distances."""
    styles = {}
    for i, d in enumerate(sorted(buffer_distances)):
        styles[d] = {
            "color": BUFFER_FILL_COLORS[i % len(BUFFER_FILL_COLORS)],
            "alpha": BUFFER_ALPHA_FILL,
            "label": f"{d}m buffer",
            "edgecolor": BUFFER_EDGE_COLORS[i % len(BUFFER_EDGE_COLORS)],
        }
    return styles


def add_north_arrow(ax):
    """Add a north arrow to the lower-right corner of the map.

    Placed at bottom-right to avoid overlapping the legend (upper-right).
    Uses a filled arrowhead and a separate text label for reliable rendering.
    """
    # Arrow shaft pointing upward (south → north)
    ax.annotate(
        "", xy=(0.93, 0.13), xytext=(0.93, 0.05),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(
            arrowstyle="-|>", color="black", lw=1.5,
            mutation_scale=14
        )
    )
    # "N" label above the arrowhead
    ax.text(
        0.93, 0.145, "N",
        ha="center", va="bottom",
        fontsize=10, fontweight="bold", color="black",
        transform=ax.transAxes, zorder=15
    )


def add_scale_bar(ax, extent):
    """Add a 100m scale bar."""
    map_width = extent[2] - extent[0]
    bar_fraction = 100 / map_width
    x_start = 0.05
    y_pos = 0.04
    ax.annotate(
        "", xy=(x_start + bar_fraction, y_pos),
        xytext=(x_start, y_pos),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(arrowstyle="|-|", color="black", lw=2)
    )
    ax.text(
        x_start + bar_fraction / 2, y_pos + 0.015,
        "100m", ha="center", va="bottom",
        fontsize=7, color="black",
        transform=ax.transAxes
    )


def plot_cadastre_by_buffer(ax, cadastre_gdf, buffers, legend_handles):
    """Plot cadastral parcels colored by which buffer they fall in."""
    plotted_ids = set()

    for dist in sorted(buffers.keys()):
        color = _buffer_parcel_color(dist)
        buf_union = buffers[dist].geometry.union_all()
        nearby = cadastre_gdf[cadastre_gdf.geometry.intersects(buf_union)].copy()
        new = nearby[~nearby.index.isin(plotted_ids)]
        if len(new) > 0:
            new.plot(
                ax=ax, color=color, alpha=0.20,
                linewidth=0.4, edgecolor=color, zorder=3
            )
            plotted_ids.update(new.index.tolist())
            handle = mpatches.Patch(
                color=color, alpha=0.5,
                label=f"Parcels within {dist}m ({len(new)})"
            )
            legend_handles.append(handle)


def plot_residential_by_type(ax, residential_gdf, buffers, legend_handles):
    """Plot residential buildings colored by type with buffer counts."""

    # Plot by type
    added_types = set()
    for btype, color in RESIDENTIAL_TYPE_COLORS.items():
        subset = residential_gdf[residential_gdf["type"] == btype]
        if len(subset) > 0:
            subset.plot(
                ax=ax, color=color, alpha=0.5,
                linewidth=0.3, edgecolor=color, zorder=4
            )
            if btype not in added_types:
                added_types.add(btype)
                label = btype.replace("_", " ").title()
                handle = mpatches.Patch(
                    color=color, alpha=0.7,
                    label=f"Residential - {label}"
                )
                legend_handles.append(handle)

    # Show counts per buffer as text
    for dist in sorted(buffers.keys()):
        buf_union = buffers[dist].geometry.union_all()
        count = len(residential_gdf[residential_gdf.geometry.intersects(buf_union)])
        if count > 0:
            buf_centroid = buffers[dist].geometry.iloc[0].centroid
            color = _buffer_parcel_color(dist)
            offset = dist * 0.6
            ax.text(
                buf_centroid.x - offset,
                buf_centroid.y - offset,
                f"Residential\n{dist}m: {count}",
                ha="center", va="center",
                fontsize=6.5, color=color, fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.2", facecolor="white",
                    alpha=0.85, edgecolor=color, linewidth=0.8
                ),
                zorder=9
            )


def plot_residential_osm(ax, residential_gdf, legend_handles):
    """Plot OSM residential buildings."""
    if len(residential_gdf) > 0:
        residential_gdf.plot(
            ax=ax, color="#fffacd", alpha=0.40,
            linewidth=0.3, edgecolor="#cccc00", zorder=4
        )
        handle = mpatches.Patch(
            color="#fffacd", alpha=0.6,
            label=f"Residential OSM ({len(residential_gdf)})"
        )
        legend_handles.append(handle)


def plot_community_facilities(ax, facility_gdf, legend_handles):
    """Plot community facilities with color by type."""
    added_types = {}

    for _, row in facility_gdf.iterrows():
        ftype = str(row.get("type", "")).lower().strip()
        color = FACILITY_TYPE_COLORS.get(ftype, DEFAULT_FACILITY_COLOR)

        geom = row.geometry
        x = geom.centroid.x if hasattr(geom, 'centroid') else geom.x
        y = geom.centroid.y if hasattr(geom, 'centroid') else geom.y

        ax.plot(x, y, marker="^", color=color, markersize=9,
                alpha=0.9, zorder=7, markeredgecolor="white",
                markeredgewidth=0.5)

        name = str(row.get("name", "")) if row.get("name") else ""
        if name and name != "nan":
            ax.annotate(
                name, xy=(x, y), xytext=(6, 4),
                textcoords="offset points",
                fontsize=6, color="black", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=color,
                          alpha=0.6, edgecolor="none"),
                zorder=8
            )

        label = ftype.replace("_", " ").title() if ftype else "Community Facility"
        if color not in added_types:
            added_types[color] = label
            handle = plt.Line2D(
                [0], [0], marker="^", color="w",
                markerfacecolor=color, markersize=9,
                label=label, linestyle="None",
                markeredgecolor="gray", markeredgewidth=0.5
            )
            legend_handles.append(handle)


def generate_map(site_gdf, buffers, layers, site_name, map_suffix="",
                 parcel_counts=None, session_id=""):
    """Generate a PNG map showing the site, buffers, and selected nearby features."""

    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # Get extent from largest buffer
    b = buffers[max(buffers.keys())].total_bounds
    margin = 200
    extent = [float(b[0]) - margin, float(b[1]) - margin,
              float(b[2]) + margin, float(b[3]) + margin]

    import math
    if any(math.isnan(v) or math.isinf(v) for v in extent):
        site_bounds = site_gdf.total_bounds
        margin = 600
        extent = [float(site_bounds[0]) - margin, float(site_bounds[1]) - margin,
                  float(site_bounds[2]) + margin, float(site_bounds[3]) + margin]

    legend_handles = []

    # Plot base layers (skip cadastre, residential, residential_osm, community_facilities
    # as they are handled by special functions below)
    special_layers = {"cadastre", "residential", "residential_osm", "community_facilities"}

    for layer_key, style in MAP_LAYER_STYLES.items():
        if layer_key not in layers or layer_key in special_layers:
            continue

        layer_gdf = layers[layer_key]

        try:
            clipped = layer_gdf.cx[extent[0]:extent[2], extent[1]:extent[3]]
            if len(clipped) == 0:
                continue

            geom_types = clipped.geometry.geom_type.unique()
            is_point = any(g in ["Point", "MultiPoint"] for g in geom_types)
            is_line = any(g in ["LineString", "MultiLineString"] for g in geom_types)

            if is_point:
                marker = style.get("marker", "o")
                clipped.plot(
                    ax=ax, color=style["color"],
                    alpha=style["alpha"],
                    markersize=style.get("markersize", 6),
                    marker=marker, zorder=style.get("zorder", 3),
                    edgecolors="white", linewidths=0.5
                )

                if style.get("show_labels") and style.get("label_field"):
                    label_col = style["label_field"]
                    if label_col in clipped.columns:
                        for _, row in clipped.iterrows():
                            name = str(row[label_col]) if row[label_col] else ""
                            if name and name != "nan":
                                geom = row.geometry
                                x = geom.centroid.x if hasattr(geom, 'centroid') else geom.x
                                y = geom.centroid.y if hasattr(geom, 'centroid') else geom.y
                                ax.annotate(
                                    name, xy=(x, y), xytext=(6, 4),
                                    textcoords="offset points",
                                    fontsize=6, color="black", fontweight="bold",
                                    bbox=dict(boxstyle="round,pad=0.2",
                                              facecolor=style["color"],
                                              alpha=0.6, edgecolor="none"),
                                    zorder=style.get("zorder", 3) + 1
                                )

                handle = plt.Line2D(
                    [0], [0], marker=marker, color="w",
                    markerfacecolor=style["color"],
                    markersize=9, label=style["label"],
                    linestyle="None", markeredgecolor="gray",
                    markeredgewidth=0.5
                )

            elif is_line:
                clipped.plot(
                    ax=ax, color=style["color"],
                    alpha=style["alpha"],
                    linewidth=style.get("linewidth", 0.5),
                    zorder=style.get("zorder", 1)
                )
                handle = mlines.Line2D(
                    [0], [0], color=style["color"],
                    alpha=0.8, linewidth=1.5, label=style["label"]
                )

            else:
                clipped.plot(
                    ax=ax, color=style["color"],
                    alpha=style["alpha"],
                    linewidth=style.get("linewidth", 0.5),
                    zorder=style.get("zorder", 2)
                )
                handle = mpatches.Patch(
                    color=style["color"], alpha=0.6, label=style["label"]
                )

            legend_handles.append(handle)

        except Exception as e:
            print(f"Map error for {layer_key}: {e}")

    # Plot cadastre by buffer
    if "cadastre" in layers:
        cadastre_clipped = layers["cadastre"].cx[
            extent[0]:extent[2], extent[1]:extent[3]
        ]
        if len(cadastre_clipped) > 0:
            plot_cadastre_by_buffer(ax, cadastre_clipped, buffers, legend_handles)

    # Plot residential (Buildings WA) by type
    if "residential" in layers:
        residential_clipped = layers["residential"].cx[
            extent[0]:extent[2], extent[1]:extent[3]
        ]
        if len(residential_clipped) > 0:
            plot_residential_by_type(ax, residential_clipped, buffers, legend_handles)

    # Plot residential (OSM)
    if "residential_osm" in layers:
        residential_osm_clipped = layers["residential_osm"].cx[
            extent[0]:extent[2], extent[1]:extent[3]
        ]
        if len(residential_osm_clipped) > 0:
            plot_residential_osm(ax, residential_osm_clipped, legend_handles)

    # Plot community facilities by type
    if "community_facilities" in layers:
        cf_clipped = layers["community_facilities"].cx[
            extent[0]:extent[2], extent[1]:extent[3]
        ]
        if len(cf_clipped) > 0:
            plot_community_facilities(ax, cf_clipped, legend_handles)

    # Plot buffers from largest to smallest
    buffer_styles = _build_buffer_styles(buffers.keys())
    for distance in sorted(buffers.keys(), reverse=True):
        style = buffer_styles[distance]
        try:
            buffers[distance].plot(
                ax=ax, color=style["color"],
                alpha=style["alpha"],
                edgecolor=style["edgecolor"],
                linewidth=1.5, linestyle="--", zorder=8
            )

            if parcel_counts and distance in parcel_counts:
                buf_centroid = buffers[distance].geometry.iloc[0].centroid
                count = parcel_counts[distance]
                offset = distance * 0.85
                ax.text(
                    buf_centroid.x, buf_centroid.y + offset,
                    f"{distance}m: {count} parcels",
                    ha="center", va="center",
                    fontsize=7, color=style["edgecolor"], fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              alpha=0.85, edgecolor=style["edgecolor"],
                              linewidth=0.8),
                    zorder=9
                )

            handle = mpatches.Patch(
                facecolor=style["color"], edgecolor=style["edgecolor"],
                alpha=0.5, label=style["label"], linestyle="--"
            )
            legend_handles.append(handle)
        except Exception:
            pass

    # Site point
    site_x = site_gdf.geometry.iloc[0].x
    site_y = site_gdf.geometry.iloc[0].y
    ax.plot(site_x, site_y, marker="*", color="#e63946",
            markersize=15, zorder=11,
            markeredgecolor="black", markeredgewidth=0.8)

    site_wgs = site_gdf.to_crs("EPSG:4326")
    lat = round(site_wgs.geometry.iloc[0].y, 5)
    lon = round(site_wgs.geometry.iloc[0].x, 5)
    ax.annotate(
        f"SITE\n{lat}, {lon}",
        xy=(site_x, site_y), xytext=(10, 8),
        textcoords="offset points",
        fontsize=7, color="black", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  alpha=0.9, edgecolor="#e63946", linewidth=1),
        zorder=12
    )

    site_handle = plt.Line2D(
        [0], [0], marker="*", color="#e63946",
        markersize=12, label="Site", linestyle="None",
        markeredgecolor="black", markeredgewidth=0.5
    )
    legend_handles.append(site_handle)

    # Legend
    ax.legend(
        handles=legend_handles,
        loc="upper right", fontsize=7,
        facecolor="white", edgecolor="#cccccc",
        framealpha=0.95, title="Legend", title_fontsize=8
    )

    # North arrow and scale bar
    add_north_arrow(ax)
    add_scale_bar(ax, extent)

    # Extent and styling
    ax.set_xlim(extent[0], extent[2])
    ax.set_ylim(extent[1], extent[3])
    ax.set_title(
        f"Preliminary Environmental Screening — {site_name}",
        fontsize=13, color="black", pad=12, fontweight="bold"
    )
    ax.set_xlabel("Easting (m)", color="black", fontsize=9)
    ax.set_ylabel("Northing (m)", color="black", fontsize=9)
    ax.tick_params(colors="black", labelsize=8)
    ax.grid(True, alpha=0.3, linewidth=0.5, color="#cccccc")
    for spine in ax.spines.values():
        spine.set_edgecolor("#cccccc")

    # Save
    out_dir = "/tmp/wa_outputs/maps"
    os.makedirs(out_dir, exist_ok=True)
    prefix = f"{session_id}_" if session_id else ""
    suffix = f"_{map_suffix}" if map_suffix else ""
    file_name = f"{prefix}{site_name.replace(' ', '_')}_screening_map{suffix}.png"
    file_path = os.path.join(out_dir, file_name)
    plt.tight_layout()
    plt.savefig(file_path, dpi=150, facecolor=fig.get_facecolor(),
                bbox_inches="tight")
    plt.close()

    print(f"Map saved to: {file_path}")
    return file_path
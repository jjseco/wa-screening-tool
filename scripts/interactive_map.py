import folium
from folium import LayerControl, FeatureGroup

# ---------------------------------------------------------------------------
# Risk colour palette for popup headers
# ---------------------------------------------------------------------------
RISK_COLORS = {
    "HIGH": "#e63946",
    "MEDIUM": "#f4a261",
    "LOW": "#2a9d8f",
    "NONE": "#aaaaaa",
}

# Human-readable labels for ESA flag columns
_ESA_FLAG_LABELS = {
    "bushforev": "Bush Forever",
    "tec": "Threatened Ecological Community",
    "whp": "Wetland of High Protection",
    "ramsar_50m": "Ramsar Wetland nearby",
    "wst_epp": "Water Source Protection",
}

# ---------------------------------------------------------------------------
# Per-layer rendering configuration
#
# render_as:
#   "polygon"       – GeoJson filled polygon with GeoJsonPopup
#   "marker"        – DivIcon marker at feature centroid (point or polygon centroid)
#   "line"          – GeoJson line, no popup
#
# popup_type:
#   "fields"        – show named field values
#   "flags"         – interpret ESA boolean/integer flag columns
#   "contaminated"  – show classification + clickable report_url
#   "none"          – no popup
#
# inner_buffer_only – True: clip to smallest buffer instead of largest
# ---------------------------------------------------------------------------
LAYER_CONFIG = {
    "esa": {
        "label": "ESA",
        "color": "#e63946",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "flags",
        "popup_fields": list(_ESA_FLAG_LABELS.keys()),
    },
    "wetlands": {
        "label": "Wetlands",
        "color": "#1d7bbf",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["wgs_wetlandname"],
    },
    "native_vegetation": {
        "label": "Native Vegetation",
        "color": "#228B22",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "none",
        "popup_fields": [],
    },
    "vegetation_complexes": {
        "label": "Vegetation Complexes",
        "color": "#32CD32",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["vsc_vegetype", "vsc_landform"],
    },
    "ass": {
        "label": "Acid Sulfate Soils",
        "color": "#f4a261",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["risk_category"],
    },
    "ass_estuaries": {
        "label": "ASS - Estuaries",
        "color": "#e76f51",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["risk_category"],
    },
    "soil_landscape": {
        "label": "Soil Landscape",
        "color": "#8B4513",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["mu_name"],
    },
    "soil_landscape_best": {
        "label": "Soil Landscape - Best Available",
        "color": "#8B4513",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["mu_name"],
    },
    "soil_group": {
        "label": "Soil Group",
        "color": "#D2691E",
        "fill_opacity": 0.25,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["wasg_decode"],
    },
    "aboriginal_heritage": {
        "label": "Aboriginal Heritage",
        "color": "#8B4513",
        "fill_opacity": 0.20,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["name"],
    },
    "historic_heritage": {
        "label": "State Heritage Register",
        "color": "#DAA520",
        "fill_opacity": 0.9,
        "render_as": "marker",
        "marker_symbol": "H",
        "popup_type": "fields",
        "popup_fields": ["place_name"],
    },
    "groundwater_areas": {
        "label": "Groundwater Areas",
        "color": "#4682B4",
        "fill_opacity": 0.20,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["area_name", "aquifer", "status"],
    },
    "groundwater_salinity": {
        "label": "Groundwater Salinity",
        "color": "#ADD8E6",
        "fill_opacity": 0.20,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["tds_mg_l_"],
    },
    "bores": {
        "label": "Hydro Bores",
        "color": "#1E90FF",
        "fill_opacity": 0.9,
        "render_as": "marker",
        "marker_symbol": "●",
        "popup_type": "fields",
        "popup_fields": ["well_type", "well_function", "depth"],
    },
    "contaminated_sites": {
        "label": "Contaminated Sites",
        "color": "#222222",
        "fill_opacity": 0.9,
        "render_as": "marker",
        "marker_symbol": "✕",
        "popup_type": "contaminated",
        "popup_fields": ["classification", "classification_date", "report_url"],
    },
    "hospitals": {
        "label": "Hospitals",
        "color": "#e63946",
        "fill_opacity": 0.9,
        "render_as": "marker",
        "marker_symbol": "H",
        "popup_type": "fields",
        "popup_fields": ["name"],
    },
    "schools": {
        "label": "Schools",
        "color": "#f77f00",
        "fill_opacity": 0.9,
        "render_as": "marker",
        "marker_symbol": "S",
        "popup_type": "fields",
        "popup_fields": ["name"],
    },
    "community_facilities": {
        "label": "Community Facilities",
        "color": "#9b5de5",
        "fill_opacity": 0.9,
        "render_as": "marker",
        "marker_symbol": "▲",
        "popup_type": "fields",
        "popup_fields": ["name", "type"],
    },
    "roads": {
        "label": "Roads",
        "color": "#bbbbbb",
        "fill_opacity": 0.7,
        "render_as": "line",
        "popup_type": "none",
        "popup_fields": [],
    },
    "residential": {
        "label": "Residential Buildings",
        "color": "#ffb3c1",
        "fill_opacity": 0.30,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["type"],
        "inner_buffer_only": False,
    },
    "residential_osm": {
        "label": "Residential (OSM)",
        "color": "#fffacd",
        "fill_opacity": 0.40,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["type"],
        "inner_buffer_only": False,
    },
    "cadastre": {
        "label": "Cadastral Parcels",
        "color": "#d4a574",
        "fill_opacity": 0.15,
        "render_as": "polygon",
        "popup_type": "none",
        "popup_fields": [],
        "inner_buffer_only": False,
    },
    "local_government": {
        "label": "Local Government Areas",
        "color": "#cccccc",
        "fill_opacity": 0.15,
        "render_as": "polygon",
        "popup_type": "fields",
        "popup_fields": ["name"],
    },
}


# ---------------------------------------------------------------------------
# Popup helpers
# ---------------------------------------------------------------------------

def _safe_str(val):
    """Return str(val) or '' for None / nan / 'None'."""
    if val is None:
        return ""
    s = str(val)
    return "" if s in ("nan", "None", "NaN", "") else s


def _flag_body(row):
    """Return HTML listing active ESA flags, or fallback text."""
    active = []
    for col, label in _ESA_FLAG_LABELS.items():
        val = row.get(col)
        if val is None:
            continue
        # Treat 1 / "1" / True / "Yes" / "Y" as active
        try:
            if int(float(str(val))) != 0:
                active.append(label)
        except (ValueError, TypeError):
            s = str(val).strip().lower()
            if s in ("true", "yes", "y"):
                active.append(label)
    return "<br>".join(f"• {f}" for f in active) if active else "ESA Area"


def _build_popup_html(row, config, layer_label, risk_level=None):
    """Build an HTML string for a Folium Marker popup."""
    # Coloured header
    if risk_level and risk_level != "NONE":
        hcol = RISK_COLORS.get(risk_level, "#aaaaaa")
        header = (
            f'<div style="font-weight:bold;color:{hcol};'
            f'border-bottom:2px solid {hcol};padding-bottom:2px;margin-bottom:4px;">'
            f'{risk_level} — {layer_label}</div>'
        )
    else:
        header = (
            f'<div style="font-weight:bold;border-bottom:1px solid #ccc;'
            f'padding-bottom:2px;margin-bottom:4px;">{layer_label}</div>'
        )

    popup_type = config.get("popup_type", "fields")
    popup_fields = config.get("popup_fields", [])

    if popup_type == "flags":
        body = _flag_body(row)

    elif popup_type == "contaminated":
        parts = []
        for f in popup_fields:
            val = _safe_str(row.get(f))
            if not val:
                continue
            if f == "report_url":
                parts.append(f'<a href="{val}" target="_blank">View Report</a>')
            elif f == "classification_date":
                parts.append(f"Date: {val}")
            else:
                parts.append(val)
        body = "<br>".join(parts) if parts else "Contaminated Site"

    elif popup_type == "fields":
        parts = [_safe_str(row.get(f)) for f in popup_fields]
        body = "<br>".join(p for p in parts if p)

    else:
        body = ""

    return header + body


def _div_icon_html(symbol, bg_color, text_color="#ffffff", size=20):
    """Return HTML for a square DivIcon with a centred symbol."""
    return (
        f'<div style="background:{bg_color};color:{text_color};'
        f'font-size:11px;font-weight:bold;'
        f'width:{size}px;height:{size}px;'
        f'border-radius:3px;border:1px solid rgba(0,0,0,0.35);'
        f'text-align:center;line-height:{size}px;">'
        f'{symbol}</div>'
    )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def generate_interactive_map(
    site_gdf, buffers, layers, site_name, buffer_distances, scored_results=None
):
    """Generate a Folium interactive map for the screening results.

    Parameters
    ----------
    site_gdf : GeoDataFrame  – site point in EPSG:32750
    buffers  : dict          – {distance_m: GeoDataFrame} in EPSG:32750
    layers   : dict          – {layer_key: GeoDataFrame} in EPSG:32750
    site_name : str
    buffer_distances : list[int]
    scored_results : list[dict], optional
        Output of score_results(). Used to colour popup headers by risk level.

    Returns
    -------
    folium.Map
    """
    # --- Site centre in WGS84 ---
    site_wgs84 = site_gdf.to_crs("EPSG:4326")
    lat = float(site_wgs84.geometry.iloc[0].y)
    lon = float(site_wgs84.geometry.iloc[0].x)

    # --- Risk level lookup: layer_key → risk_level ---
    risk_lookup = {}
    if scored_results:
        for r in scored_results:
            risk_lookup[r["layer_key"]] = r.get("risk_level", "NONE")

    # --- Create map ---
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles="OpenStreetMap")

    # --- Buffer circles (largest first so smallest renders on top) ---
    buf_fg = FeatureGroup(name="Buffer Zones", show=True)
    for dist in sorted(buffer_distances, reverse=True):
        folium.Circle(
            location=[lat, lon],
            radius=dist,
            color="#555555",
            weight=2,
            fill=False,
            opacity=0.8,
            dash_array="10",
            tooltip=f"{dist}m buffer",
        ).add_to(buf_fg)
    buf_fg.add_to(m)

    # --- Clip extents ---
    sorted_dists = sorted(buffer_distances)
    max_buf_geom = buffers[sorted_dists[-1]].geometry.union_all()
    min_buf_geom = buffers[sorted_dists[0]].geometry.union_all()

    # --- Environmental layers ---
    for layer_key, config in LAYER_CONFIG.items():
        if layer_key not in layers:
            continue

        gdf = layers[layer_key]
        clip_geom = min_buf_geom if config.get("inner_buffer_only") else max_buf_geom

        try:
            clipped = gdf[gdf.geometry.intersects(clip_geom)].copy()
        except Exception:
            continue

        if len(clipped) == 0:
            continue

        try:
            clipped_wgs = clipped.to_crs("EPSG:4326")
        except Exception:
            continue

        layer_label = config["label"]
        risk_level = risk_lookup.get(layer_key, "NONE")
        color = config["color"]
        fill_opacity = config["fill_opacity"]
        render_as = config.get("render_as", "polygon")
        popup_type = config.get("popup_type", "none")
        popup_fields = config.get("popup_fields", [])

        # Append risk badge to the name shown in LayerControl
        risk_badge = f" [{risk_level}]" if risk_level and risk_level != "NONE" else ""
        fg = FeatureGroup(name=f"{layer_label}{risk_badge}", show=True)

        # --- Line layers ---
        if render_as == "line":
            folium.GeoJson(
                clipped_wgs,
                style_function=lambda x, c=color, fo=fill_opacity: {
                    "color": c,
                    "weight": 1.5,
                    "opacity": fo,
                },
            ).add_to(fg)

        # --- Polygon layers ---
        elif render_as == "polygon":
            # Only include popup_fields that actually exist in this dataset
            available_fields = [f for f in popup_fields if f in clipped_wgs.columns]

            if popup_type == "none" or not available_fields:
                popup = None
            elif popup_type == "flags":
                aliases = [_ESA_FLAG_LABELS.get(f, f) + ":" for f in available_fields]
                popup = folium.GeoJsonPopup(
                    fields=available_fields, aliases=aliases, labels=True
                )
            else:
                popup = folium.GeoJsonPopup(fields=available_fields, labels=False)

            folium.GeoJson(
                clipped_wgs,
                style_function=lambda x, c=color, fo=fill_opacity: {
                    "fillColor": c,
                    "color": c,
                    "weight": 0.5,
                    "fillOpacity": fo,
                },
                popup=popup,
            ).add_to(fg)

        # --- Marker layers ---
        elif render_as == "marker":
            symbol = config.get("marker_symbol", "•")
            for _, row in clipped_wgs.iterrows():
                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                # Use centroid when the geometry is not already a point
                if geom.geom_type in ("Point", "MultiPoint"):
                    pt_lat, pt_lon = geom.y, geom.x
                else:
                    c = geom.centroid
                    pt_lat, pt_lon = c.y, c.x

                popup_html = _build_popup_html(row, config, layer_label, risk_level)
                icon = folium.DivIcon(
                    html=_div_icon_html(symbol, color),
                    icon_size=(20, 20),
                    icon_anchor=(10, 10),
                )
                folium.Marker(
                    location=[pt_lat, pt_lon],
                    icon=icon,
                    popup=folium.Popup(popup_html, max_width=320),
                ).add_to(fg)

        fg.add_to(m)

    # --- Site marker ---
    site_fg = FeatureGroup(name="Site", show=True)
    site_popup_html = (
        f'<div style="font-weight:bold;font-size:13px;margin-bottom:4px;">'
        f'{site_name}</div>'
        f'<div>Lat: {lat:.6f}</div>'
        f'<div>Lon: {lon:.6f}</div>'
    )
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(site_popup_html, max_width=250),
        tooltip=site_name,
        icon=folium.DivIcon(
            html=(
                '<div style="font-size:28px;color:#e63946;'
                'text-shadow:0 0 4px #000;line-height:1;">'
                '★</div>'
            ),
            icon_size=(30, 30),
            icon_anchor=(15, 15),
        ),
    ).add_to(site_fg)
    site_fg.add_to(m)

    # --- Layer control ---
    LayerControl(collapsed=True).add_to(m)

    return m

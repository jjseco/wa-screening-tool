import streamlit as st
from scripts.load_layers import load_layers_for_themes, load_layer
from scripts.geometry import create_site_point, create_buffers, create_bbox
from scripts.spatial_query import run_all_queries
from scripts.export import export_to_excel
from scripts.risk_scoring import score_results
from scripts.report_writer import generate_word_report
from scripts.mapping import generate_map, MAP_LAYER_STYLES
try:
    from scripts.interactive_map import generate_interactive_map, LAYER_CONFIG as _IMAP_CONFIG
    from streamlit_folium import st_folium
    _FOLIUM_AVAILABLE = True
except ImportError:
    _FOLIUM_AVAILABLE = False
from scripts.registry import get_available_themes, LAYER_REGISTRY, get_layers_for_themes
from scripts.export import _get_citation, _get_provider
from scripts.project_types import PROJECT_TYPES
from scripts.data_manager import is_cloud_mode
from config import BUFFER_PRESETS
import pandas as pd
import os
import uuid

# Page config
st.set_page_config(
    page_title="WA Environmental Screening Tool",
    layout="centered"
)

st.title("WA Preliminary Environmental Screening Tool")

# ----------------------------------------------------------------
# DISCLAIMER
# ----------------------------------------------------------------
st.warning(
    "PRELIMINARY SCREENING TOOL — This tool is intended for desktop screening purposes only. "
    "Results are based on publicly available spatial datasets and do not constitute a formal "
    "environmental assessment, environmental impact statement, or specialist technical report. "
    "Always verify results against current authoritative sources and consult a qualified "
    "environmental professional before making project decisions."
)
_acknowledged = st.checkbox(
    "I understand this is a preliminary screening tool only",
    key="disclaimer_acknowledged",
)
if not _acknowledged:
    st.stop()

# ----------------------------------------------------------------
# TUTORIAL
# ----------------------------------------------------------------
with st.expander("How to use this tool", expanded=False):
    st.markdown("""
    This tool performs a **preliminary desktop environmental screening** for sites in Western Australia.
    It is designed for early-stage consulting review only and does not replace a formal environmental assessment.

    **How to use:**
    1. Select your project type (optional — pre-selects recommended settings)
    2. Enter a site name and coordinates
    3. Choose buffer distances and screening themes
    4. Click **Run Screening**
    5. Review results and generate one or more maps as needed
    6. Download the Excel table and any maps for your records

    **Note:** Coordinates in decimal degrees. Find them by right-clicking in Google Maps.
    """)

# ----------------------------------------------------------------
# LAYER DEFINITIONS
# ----------------------------------------------------------------
with st.expander("Layer definitions and what to expect", expanded=False):
    st.markdown("""
    ### Environmentally Sensitive Areas (ESA) — DWER-046
    Areas protected under WA clearing regulations. Includes Bush Forever, Threatened Ecological Communities, Wetlands of High Protection, Ramsar wetlands, and Water Source Protection zones.

    ### Wetlands — Swan Coastal Plain — DBCA-019
    Geomorphic wetlands mapped across the Swan Coastal Plain. Reports wetland name where available.

    ### Acid Sulfate Soils — DWER-055
    ASS risk mapping for the Swan Coastal Plain. Reports risk category.

    ### Aboriginal Cultural Heritage — DPLH
    Registered Aboriginal heritage places. Reports place name and type.

    ### State Heritage Register — DPLH
    Places listed on the WA State Heritage Register. Reports place name.

    ### Groundwater Areas — DWER
    Proclaimed groundwater areas and protection zones. Reports aquifer name.

    ### Contaminated Sites — DWER-059
    Sites listed on the WA Contaminated Sites database. Reports classification.

    ### Local Government Areas — LGATE
    Identifies which Local Government Area the site falls within.

    ### Roads / Hospitals / Schools — OSM / Geofabrik
    Road network, hospitals and schools for site context and sensitive receptor assessment.

    ### Residential / Cadastral Parcels / Community Facilities
    Residential buildings from OSM, all cadastral parcels from Landgate, and community facilities from OSM.
    """)

# ----------------------------------------------------------------
# PROJECT TYPE SELECTION
# ----------------------------------------------------------------
st.subheader("Project Type")

project_type_options = list(PROJECT_TYPES.keys()) + ["Custom"]
project_type = st.selectbox(
    "Select project type",
    project_type_options,
    index=len(project_type_options) - 1,  # Default: Custom (last)
    key="project_type_select"
)

custom_project_description = ""
if project_type == "Custom":
    custom_project_description = st.text_input(
        "Describe your project",
        placeholder="e.g. Industrial warehouse development on greenfield site"
    )

# Derive recommended buffers and relevant themes from project type
if project_type != "Custom":
    pt_def = PROJECT_TYPES[project_type]
    rec_preset = pt_def["recommended_buffers"]
    relevant_themes = pt_def["relevant_themes"]
    st.info(
        f"**Recommended buffers:** {rec_preset} "
        f"({', '.join(str(d) + 'm' for d in rec_preset)})"
    )
else:
    rec_preset = "Standard"
    relevant_themes = []

# ----------------------------------------------------------------
# INPUT FORM
# ----------------------------------------------------------------
st.subheader("Site Details")
site_name = st.text_input("Site Name", placeholder="e.g. Test Site 01")

input_mode = st.radio(
    "Coordinate input method",
    ["Enter Coordinates", "Enter Address"],
    horizontal=True,
    key="input_mode",
)

if input_mode == "Enter Coordinates":
    latitude = st.number_input("Latitude", value=-31.9505, format="%.6f")
    longitude = st.number_input("Longitude", value=115.8605, format="%.6f")
else:
    address_query = st.text_input(
        "Address",
        placeholder="e.g. 200 St Georges Terrace, Perth WA",
        key="address_input",
    )
    if st.button("Geocode Address", key="btn_geocode"):
        if address_query.strip():
            try:
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="wa_screening_tool")
                location = geolocator.geocode(address_query.strip(), country_codes="au")
                if location:
                    st.session_state["geocoded_lat"] = location.latitude
                    st.session_state["geocoded_lon"] = location.longitude
                    st.session_state["geocoded_address"] = location.address
                else:
                    st.session_state["geocoded_lat"] = None
                    st.session_state["geocoded_lon"] = None
                    st.session_state["geocoded_address"] = None
                    st.error("Address not found. Try a more specific address including suburb and state.")
            except Exception as _e:
                st.session_state["geocoded_lat"] = None
                st.session_state["geocoded_lon"] = None
                st.session_state["geocoded_address"] = None
                st.error(f"Geocoding failed: {_e}")
        else:
            st.warning("Please enter an address.")

    _geocoded_lat = st.session_state.get("geocoded_lat")
    _geocoded_lon = st.session_state.get("geocoded_lon")
    if _geocoded_lat and _geocoded_lon:
        st.success(f"Resolved: {st.session_state.get('geocoded_address', '')}")
        st.caption(f"Coordinates: {_geocoded_lat:.6f}, {_geocoded_lon:.6f}")
        latitude = _geocoded_lat
        longitude = _geocoded_lon
    else:
        st.info("Enter an address and click **Geocode Address** to resolve coordinates.")
        latitude = -31.9505
        longitude = 115.8605

# Validate coordinates are within Western Australia
_WA_LAT_MIN, _WA_LAT_MAX = -35.5, -13.5
_WA_LON_MIN, _WA_LON_MAX = 112.5, 129.5
coords_in_wa = (
    _WA_LAT_MIN <= latitude <= _WA_LAT_MAX
    and _WA_LON_MIN <= longitude <= _WA_LON_MAX
)
if not coords_in_wa:
    st.error(
        "Coordinates appear to be outside Western Australia. "
        "Please check your coordinates and try again."
    )

# ----------------------------------------------------------------
# BUFFER CONFIGURATION
# ----------------------------------------------------------------
st.subheader("Buffer Distances")

preset_options = list(BUFFER_PRESETS.keys()) + ["Custom"]
default_preset_idx = preset_options.index(rec_preset) if rec_preset in preset_options else 0
buffer_preset = st.selectbox(
    "Buffer preset",
    preset_options,
    index=default_preset_idx,
    key="buffer_preset_select"
)

if buffer_preset == "Custom":
    col1, col2, col3 = st.columns(3)
    b1 = col1.number_input("Buffer 1 (m)", min_value=1, value=100, step=1)
    b2 = col2.number_input("Buffer 2 (m)", min_value=1, value=250, step=1)
    b3 = col3.number_input("Buffer 3 (m)", min_value=1, value=500, step=1)
    raw = [int(b1), int(b2), int(b3)]
    # Validate: must be 3 distinct positive integers
    if len(set(raw)) < 3:
        st.error("All three buffer distances must be different positive integers.")
        selected_buffer_distances = sorted(set(raw)) if len(set(raw)) >= 1 else [100, 250, 500]
    else:
        selected_buffer_distances = sorted(raw)
else:
    selected_buffer_distances = BUFFER_PRESETS[buffer_preset]
    st.caption(
        f"Buffers: {selected_buffer_distances[0]}m / "
        f"{selected_buffer_distances[1]}m / "
        f"{selected_buffer_distances[2]}m"
    )

# ----------------------------------------------------------------
# THEME SELECTION
# ----------------------------------------------------------------
st.subheader("Screening Themes")
if relevant_themes:
    st.markdown(
        f"Themes marked **\*** are most relevant for **{project_type}** projects. "
        "All themes are selected by default."
    )
else:
    st.markdown("Select the themes you want to include in this screening:")

available_themes = get_available_themes()
selected_themes = []
cols = st.columns(2)
for i, theme in enumerate(available_themes):
    col = cols[i % 2]
    label = f"* {theme}" if theme in relevant_themes else theme
    if col.checkbox(label, value=True, key=f"theme_{theme}"):
        selected_themes.append(theme)

# ----------------------------------------------------------------
# RUN SCREENING
# ----------------------------------------------------------------
st.divider()
if st.button("Run Screening", type="primary"):
    if not site_name:
        st.error("Please enter a site name.")
    elif input_mode == "Enter Address" and not st.session_state.get("geocoded_lat"):
        st.error("Please geocode an address before running the screening.")
    elif not coords_in_wa:
        st.error(
            "Coordinates appear to be outside Western Australia. "
            "Please check your coordinates and try again."
        )
    elif not selected_themes:
        st.error("Please select at least one screening theme.")
    else:
        if is_cloud_mode():
            st.info(
                "Cloud mode: spatial data layers will be downloaded from "
                "Hugging Face on first use and cached for this session. "
                "This may take a moment."
            )
        session_id = str(uuid.uuid4())[:8]
        st.session_state["session_id"] = session_id

        _progress = st.progress(0)
        with st.status("Running screening...", expanded=True) as _status:

            # Step 1/5 — Site geometry
            st.write("Step 1/5: Creating site geometry...")
            site_gdf = create_site_point(latitude, longitude)
            buffers = create_buffers(site_gdf, buffer_distances=selected_buffer_distances)
            bbox = create_bbox(latitude, longitude, margin_km=2.0)
            _progress.progress(20)

            # Step 2/5 — Load layers individually so each name is visible
            st.write("Step 2/5: Loading spatial layers...")
            _layer_keys = get_layers_for_themes(selected_themes)
            layers = {}
            for _lk in _layer_keys:
                st.write(f"  Loading: {_lk}")
                _gdf = load_layer(_lk, bbox=bbox)
                if _gdf is not None:
                    layers[_lk] = _gdf
            _progress.progress(40)

            if not layers:
                st.error("No processed layers found. Please run preprocessing first.")
                _status.update(label="Screening failed", state="error")
            else:
                # Step 3/5 — Spatial queries
                st.write("Step 3/5: Running spatial queries...")
                results = run_all_queries(layers, site_gdf, buffers)
                _progress.progress(60)

                # Step 4/5 — Score results
                st.write("Step 4/5: Scoring results...")
                scored_results, theme_summary = score_results(
                    results, project_type, selected_buffer_distances
                )
                _progress.progress(80)

                # Step 5/5 — Generate outputs
                st.write("Step 5/5: Generating outputs...")
                output_path = export_to_excel(
                    scored_results, site_name,
                    site_gdf=site_gdf,
                    layers=layers,
                    buffers=buffers,
                    theme_summary=theme_summary,
                    session_id=session_id,
                )

                st.session_state["results"] = scored_results
                st.session_state["layers"] = layers
                st.session_state["site_gdf"] = site_gdf
                st.session_state["buffers"] = buffers
                st.session_state["site_name"] = site_name
                st.session_state["selected_themes"] = selected_themes
                st.session_state["output_path"] = output_path
                st.session_state["project_type"] = project_type
                st.session_state["buffer_distances"] = selected_buffer_distances
                st.session_state["theme_summary"] = theme_summary
                st.session_state["latitude"] = latitude
                st.session_state["longitude"] = longitude

                word_path = generate_word_report(
                    scored_results, site_name,
                    latitude=latitude,
                    longitude=longitude,
                    project_type=project_type,
                    buffer_distances=selected_buffer_distances,
                    theme_summary=theme_summary,
                    layers=layers,
                    buffers=buffers,
                    selected_themes=selected_themes,
                    session_id=session_id,
                )
                st.session_state["word_report_path"] = word_path

                _progress.progress(100)
                _status.update(label="Screening complete", state="complete", expanded=False)

# ----------------------------------------------------------------
# RESULTS
# ----------------------------------------------------------------
if "results" in st.session_state:
    results = st.session_state["results"]
    layers = st.session_state["layers"]
    site_gdf = st.session_state["site_gdf"]
    buffers = st.session_state["buffers"]
    site_name_saved = st.session_state["site_name"]
    selected_themes_saved = st.session_state["selected_themes"]
    output_path = st.session_state["output_path"]
    buffer_distances = st.session_state.get("buffer_distances", sorted(buffers.keys()))
    theme_summary = st.session_state.get("theme_summary", {})

    st.success(
        f"Screening complete. {len(layers)} layers queried across "
        f"{len(selected_themes_saved)} themes."
    )

    # Short tab label for each full theme name
    _THEME_SHORT = {
        "Ecology": "Ecology",
        "ASS / Soils / Geology": "Soils",
        "Heritage": "Heritage",
        "Groundwater / Hydrology": "Groundwater",
        "Contaminated Land": "Contamination",
        "Planning / Local Government": "Planning",
        "Sensitive Receptors": "Receptors",
    }
    _RECEPTORS_THEME = "Sensitive Receptors"

    _theme_tab_labels = [_THEME_SHORT.get(t, t[:14]) for t in selected_themes_saved]
    _all_tab_labels = ["Risk Summary"] + _theme_tab_labels + ["Reports", "Maps"]
    _tabs = st.tabs(_all_tab_labels)

    # ------------------------------------------------
    # TAB: Risk Summary
    # ------------------------------------------------
    with _tabs[0]:
        _rating_display = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW", "NONE": "NONE"}
        _risk_rows = []
        for _theme in selected_themes_saved:
            if _theme in theme_summary:
                _ts = theme_summary[_theme]
                _risk_rows.append({
                    "Theme": _theme,
                    "Risk Rating": _rating_display.get(_ts["rating"], _ts["rating"]),
                    "Score": _ts["score"],
                    "Key Finding": _ts["key_finding"],
                })
        if _risk_rows:
            st.dataframe(pd.DataFrame(_risk_rows), use_container_width=True)

        _high = [t for t, ts in theme_summary.items() if ts["rating"] == "HIGH"]
        _med  = [t for t, ts in theme_summary.items() if ts["rating"] == "MEDIUM"]
        _low  = [t for t, ts in theme_summary.items() if ts["rating"] == "LOW"]
        _summary_parts = []
        if _high:
            _summary_parts.append(f"HIGH risk identified for: {', '.join(_high)}.")
        if _med:
            _summary_parts.append(f"MEDIUM risk identified for: {', '.join(_med)}.")
        if _low:
            _summary_parts.append(f"LOW risk identified for {len(_low)} theme(s).")
        if not _summary_parts:
            _summary_parts.append("No significant environmental sensitivities identified.")
        st.markdown(" ".join(_summary_parts))

    # ------------------------------------------------
    # TABS: One per selected theme
    # ------------------------------------------------
    for _ti, _theme in enumerate(selected_themes_saved):
        with _tabs[_ti + 1]:
            _theme_results = [r for r in results if r["theme"] == _theme]

            if not _theme_results:
                st.info("No data for this theme.")
            else:
                # Results table
                _display_rows = []
                for r in _theme_results:
                    _nearest = r["nearest_distance_m"]
                    _nearest_str = "—" if r["site_intersect"] else (str(_nearest) if _nearest else "—")
                    _row = {
                        "Layer": r["layer"],
                        "Present": "Yes" if r["present"] else "—",
                        "Max Relevance": r["max_relevance"],
                        "Primary Trigger": r["primary_trigger"],
                    }
                    for d in buffer_distances:
                        _row[f"Within {d}m"] = r.get(f"within_{d}m")
                    for d in buffer_distances:
                        _row[f"Count {d}m"] = r.get(f"count_{d}m")
                    _row["Nearest (m)"] = _nearest_str
                    _row["Detected Features"] = (
                        ", ".join(r["nearby_names"]) if r["nearby_names"] else "—"
                    )
                    _row["Interpretation"] = r.get("interpretation", "")
                    _display_rows.append(_row)
                st.dataframe(pd.DataFrame(_display_rows), use_container_width=True)

                # Detected features for this theme
                _found_any = False
                for r in _theme_results:
                    if r["layer_key"] == "roads":
                        continue
                    if r["nearby_names"]:
                        if not _found_any:
                            st.markdown("**Detected Features**")
                            _found_any = True
                        st.markdown(f"*{r['layer']}:*")
                        for _name in r["nearby_names"]:
                            st.markdown(f"- {_name}")
                if not _found_any:
                    st.info("No named features detected in this theme.")

                # Receptors tab: parcel counts summary
                if _theme == _RECEPTORS_THEME and "cadastre" in layers:
                    st.markdown("**Cadastral Parcel Counts**")
                    _parcel_parts = []
                    for _d in buffer_distances:
                        if _d in buffers:
                            _buf_union = buffers[_d].geometry.union_all()
                            _cnt = len(
                                layers["cadastre"][
                                    layers["cadastre"].geometry.intersects(_buf_union)
                                ]
                            )
                            _parcel_parts.append(f"{_cnt} within {_d}m")
                    if _parcel_parts:
                        st.markdown(", ".join(_parcel_parts))

    # ------------------------------------------------
    # TAB: Reports (second-to-last tab)
    # ------------------------------------------------
    with _tabs[-2]:
        st.markdown("**Excel Table**")
        st.caption(
            "Full screening results with all layers, buffer counts, detected features, "
            "risk scores, and interpretations. Includes Risk Summary, per-theme sheets, "
            "parcel detail, receptor detail, and data sources reference sheet."
        )
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Excel Table",
                data=f,
                file_name=os.path.basename(output_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel",
            )

        st.divider()
        st.markdown("**Word Report**")
        st.caption(
            "Structured report with cover page, executive summary, risk summary table, "
            "per-theme results, sensitive receptors detail, data sources, and disclaimer."
        )
        word_report_path = st.session_state.get("word_report_path")
        if word_report_path and os.path.exists(word_report_path):
            with open(word_report_path, "rb") as f:
                st.download_button(
                    label="Download Word Report",
                    data=f,
                    file_name=os.path.basename(word_report_path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_word",
                )
        else:
            st.info("Word report not available.")

    # ------------------------------------------------
    # TAB: Maps (last tab)
    # ------------------------------------------------
    with _tabs[-1]:
        _map_type = st.radio(
            "Map Type",
            ["Interactive Map", "Static PNG"],
            horizontal=True,
            key="current_map_type",
        )

        mappable_keys = [k for k in layers.keys() if k in MAP_LAYER_STYLES]

        # Only roads pre-selected by default; site marker and buffers are always-on
        _IMAP_DEFAULTS = {"roads"}
        _STATIC_DEFAULTS = {"roads"}

        # ------------------------------------------------
        # Interactive Map
        # ------------------------------------------------
        if _map_type == "Interactive Map":
            if not _FOLIUM_AVAILABLE:
                st.warning(
                    "Interactive map requires `folium` and `streamlit-folium`. "
                    "Add them to requirements.txt and reinstall dependencies."
                )
            else:
                _imap_keys = [k for k in layers.keys() if k in _IMAP_CONFIG]
                if not _imap_keys:
                    st.info("No mappable layers available in current screening.")
                else:
                    # Callback: mark map as needing regeneration on any checkbox change
                    def _mark_imap_dirty():
                        st.session_state["imap_dirty"] = True

                    # Column layout: layer selection left, map right
                    _col_layers, _col_map = st.columns([1, 3])

                    with _col_layers:
                        st.caption("**Layers**")
                        for _lk in _imap_keys:
                            _lbl = LAYER_REGISTRY.get(_lk, {}).get("label", _lk)
                            _default = _lk in _IMAP_DEFAULTS
                            st.checkbox(
                                _lbl,
                                value=_default,
                                key=f"imap_{_lk}",
                                on_change=_mark_imap_dirty,
                            )

                    with _col_map:
                        st.caption(
                            "Click on any feature to see its details. "
                            "Use the layer panel (top right) to toggle layers on/off. "
                            "Scroll to zoom, drag to pan."
                        )

                        # Auto-regenerate when any checkbox changes, or on first load
                        _imap_dirty = st.session_state.get("imap_dirty", False)
                        _should_regen = (
                            _imap_dirty
                            or "interactive_map_obj" not in st.session_state
                        )

                        if _should_regen:
                            st.session_state["imap_dirty"] = False
                            _imap_selected = [
                                lk for lk in _imap_keys
                                if st.session_state.get(f"imap_{lk}", lk in _IMAP_DEFAULTS)
                            ]
                            with st.spinner("Updating map..."):
                                _imap_layers = {
                                    k: layers[k] for k in _imap_selected if k in layers
                                }
                                _imap = generate_interactive_map(
                                    site_gdf, buffers, _imap_layers,
                                    site_name_saved, buffer_distances,
                                    scored_results=results,
                                )
                            st.session_state["interactive_map_obj"] = _imap

                        if "interactive_map_obj" in st.session_state:
                            st_folium(
                                st.session_state["interactive_map_obj"],
                                width=None,
                                height=600,
                                key="interactive_map",
                                returned_objects=[],
                            )

            # --- PNG always available regardless of display mode ---
            st.divider()
            st.markdown("**Download as Static PNG**")
            if not mappable_keys:
                st.info("No mappable layers available for PNG export.")
            else:
                # Display stored PNG first
                if (
                    st.session_state.get("static_map_path")
                    and os.path.exists(st.session_state["static_map_path"])
                ):
                    _dl_path = st.session_state["static_map_path"]
                    st.image(_dl_path)
                    with open(_dl_path, "rb") as _f:
                        st.download_button(
                            label="Download PNG",
                            data=_f,
                            file_name=os.path.basename(_dl_path),
                            mime="image/png",
                            key="download_png_imap_mode",
                        )

                # Layer selection + generate button (flat, 2-column checkboxes)
                _png_cols = st.columns(2)
                _png_selected = []
                for _pi, _lk in enumerate(mappable_keys):
                    _col = _png_cols[_pi % 2]
                    _lbl = LAYER_REGISTRY.get(_lk, {}).get("label", _lk)
                    _default = _lk in _STATIC_DEFAULTS
                    if _col.checkbox(_lbl, value=_default, key=f"png_{_lk}"):
                        _png_selected.append(_lk)

                if st.button("Generate PNG", key="btn_png_imap_mode"):
                    if not _png_selected:
                        st.warning("Please select at least one layer.")
                    else:
                        _png_layers = {k: layers[k] for k in _png_selected}
                        _png_parcel_counts = {}
                        if "cadastre" in layers and "cadastre" in _png_selected:
                            for _d in buffer_distances:
                                _bu = buffers[_d].geometry.union_all()
                                _png_parcel_counts[_d] = len(
                                    layers["cadastre"][
                                        layers["cadastre"].geometry.intersects(_bu)
                                    ]
                                )
                        with st.spinner("Generating PNG..."):
                            _png_path = generate_map(
                                site_gdf, buffers, _png_layers,
                                site_name_saved,
                                map_suffix="png",
                                parcel_counts=_png_parcel_counts or None,
                                session_id=st.session_state.get("session_id", ""),
                            )
                        st.session_state["static_map_path"] = _png_path
                        st.rerun()

        # ------------------------------------------------
        # Static PNG
        # ------------------------------------------------
        else:
            if not mappable_keys:
                st.info("No mappable layers available in current screening.")
            else:
                # Column layout: layer selection + button left, map right
                _col_layers, _col_map = st.columns([1, 3])

                with _col_layers:
                    st.caption("**Layers**")
                    _static_selected = []
                    for _lk in mappable_keys:
                        _lbl = LAYER_REGISTRY.get(_lk, {}).get("label", _lk)
                        _default = _lk in _STATIC_DEFAULTS
                        if st.checkbox(_lbl, value=_default, key=f"static_{_lk}"):
                            _static_selected.append(_lk)

                    st.divider()
                    if st.button("Generate Map", key="btn_static_map"):
                        if not _static_selected:
                            st.warning("Please select at least one layer.")
                        else:
                            _static_layers = {k: layers[k] for k in _static_selected}
                            _static_parcel_counts = {}
                            if "cadastre" in layers and "cadastre" in _static_selected:
                                for dist in buffer_distances:
                                    buf_union = buffers[dist].geometry.union_all()
                                    count = len(layers["cadastre"][
                                        layers["cadastre"].geometry.intersects(buf_union)
                                    ])
                                    _static_parcel_counts[dist] = count
                            with st.spinner("Generating map..."):
                                _static_map_path = generate_map(
                                    site_gdf, buffers, _static_layers,
                                    site_name_saved,
                                    map_suffix="static",
                                    parcel_counts=_static_parcel_counts or None,
                                    session_id=st.session_state.get("session_id", ""),
                                )
                            st.session_state["static_map_path"] = _static_map_path
                            st.rerun()

                with _col_map:
                    st.caption(
                        "Select layers on the left and click Generate Map. "
                        "The map will update with your selection."
                    )
                    if (
                        st.session_state.get("static_map_path")
                        and os.path.exists(st.session_state["static_map_path"])
                    ):
                        _dl_path = st.session_state["static_map_path"]
                        st.image(_dl_path, use_container_width=True)
                        with open(_dl_path, "rb") as _f:
                            st.download_button(
                                label="Download Map",
                                data=_f,
                                file_name=os.path.basename(_dl_path),
                                mime="image/png",
                                key="download_static_map",
                            )

# ----------------------------------------------------------------
# DATA SOURCES
# ----------------------------------------------------------------
st.divider()
st.markdown("### Data Sources")

_ds_rows = []
_ds_seen = set()
for _lk, _entry in LAYER_REGISTRY.items():
    if _lk in _ds_seen:
        continue
    _ds_seen.add(_lk)
    _label = _entry.get("label", _lk)
    _code = _entry.get("dataset_code", "")
    _source = _entry.get("source", "")
    _provider = _get_provider(_source) if _source else ""
    _citation = _get_citation(_lk, _entry)
    _ds_rows.append({
        "Theme": _entry.get("theme", ""),
        "Layer": _label,
        "Dataset Code": _code,
        "Provider": _provider,
        "Citation": _citation,
    })

_ds_df = pd.DataFrame(_ds_rows).sort_values(["Theme", "Layer"]).reset_index(drop=True)
st.dataframe(_ds_df, use_container_width=True)

st.markdown("""
<small>This tool is intended for preliminary desktop screening purposes only.
Results should be verified against current authoritative sources before use in formal environmental assessments.
Always consult a qualified environmental professional for project-specific advice.</small>
""", unsafe_allow_html=True)

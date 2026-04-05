import streamlit as st
from scripts.load_layers import load_layers_for_themes
from scripts.geometry import create_site_point, create_buffers, create_bbox
from scripts.spatial_query import run_all_queries
from scripts.export import export_to_excel
from scripts.risk_scoring import score_results
from scripts.report_writer import generate_word_report
from scripts.mapping import generate_map, MAP_LAYER_STYLES
from scripts.registry import get_available_themes, LAYER_REGISTRY
from scripts.export import _get_citation, _get_provider
from scripts.project_types import PROJECT_TYPES
from scripts.data_manager import is_cloud_mode
from config import BUFFER_PRESETS
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="WA Environmental Screening Tool",
    layout="centered"
)

st.title("WA Preliminary Environmental Screening Tool")

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
    elif not selected_themes:
        st.error("Please select at least one screening theme.")
    else:
        if is_cloud_mode():
            st.info(
                "Cloud mode: spatial data layers will be downloaded from "
                "Hugging Face on first use and cached for this session. "
                "This may take a moment."
            )
        with st.spinner("Running screening..."):
            site_gdf = create_site_point(latitude, longitude)
            buffers = create_buffers(site_gdf, buffer_distances=selected_buffer_distances)
            bbox = create_bbox(latitude, longitude, margin_km=2.0)
            layers = load_layers_for_themes(selected_themes, bbox=bbox)

            if not layers:
                st.error("No processed layers found. Please run preprocessing first.")
            else:
                results = run_all_queries(layers, site_gdf, buffers)
                scored_results, theme_summary = score_results(
                    results, project_type, selected_buffer_distances
                )
                output_path = export_to_excel(
                    scored_results, site_name,
                    site_gdf=site_gdf,
                    layers=layers,
                    buffers=buffers,
                    theme_summary=theme_summary,
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
                )
                st.session_state["word_report_path"] = word_path

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

    st.success(f"Screening complete. {len(layers)} layers queried across {len(selected_themes_saved)} themes.")

    # ------------------------------------------------
    # RISK SUMMARY TABLE
    # ------------------------------------------------
    _rating_display = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW", "NONE": "NONE"}
    st.subheader("Risk Summary")
    risk_summary_rows = []
    for theme in selected_themes_saved:
        if theme in theme_summary:
            ts = theme_summary[theme]
            risk_summary_rows.append({
                "Theme": theme,
                "Risk Rating": _rating_display.get(ts["rating"], ts["rating"]),
                "Score": ts["score"],
                "Key Finding": ts["key_finding"],
            })
    if risk_summary_rows:
        st.dataframe(pd.DataFrame(risk_summary_rows), use_container_width=True)

    # ------------------------------------------------
    # RESULTS BY THEME
    # ------------------------------------------------
    st.subheader("Screening Results")
    for theme in selected_themes_saved:
        theme_results = [r for r in results if r["theme"] == theme]
        if not theme_results:
            continue
        st.markdown(f"#### {theme}")
        display_rows = []
        for r in theme_results:
            nearest = r["nearest_distance_m"]
            nearest_str = "—" if r["site_intersect"] else (str(nearest) if nearest else "—")
            row = {
                "Layer": r["layer"],
                "Present": "Yes" if r["present"] else "—",
                "Max Relevance": r["max_relevance"],
                "Primary Trigger": r["primary_trigger"],
            }
            for d in buffer_distances:
                row[f"Within {d}m"] = r.get(f"within_{d}m")
            for d in buffer_distances:
                row[f"Count {d}m"] = r.get(f"count_{d}m")
            row["Nearest (m)"] = nearest_str
            row["Detected Features"] = ", ".join(r["nearby_names"]) if r["nearby_names"] else "—"
            row["Interpretation"] = r.get("interpretation", "")
            display_rows.append(row)
        df = pd.DataFrame(display_rows)
        st.dataframe(df, use_container_width=True)

    # ------------------------------------------------
    # DETECTED FEATURES
    # ------------------------------------------------
    st.subheader("Detected Features")
    found_any = False
    for theme in selected_themes_saved:
        theme_results = [r for r in results if r["theme"] == theme]
        theme_found = False
        for r in theme_results:
            if r["layer_key"] == "roads":
                continue
            if r["nearby_names"]:
                if not theme_found:
                    st.markdown(f"**{theme}**")
                    theme_found = True
                    found_any = True
                st.markdown(f"*{r['layer']}:*")
                for name in r["nearby_names"]:
                    st.markdown(f"- {name}")
    if not found_any:
        st.info("No named features identified within the screening buffers.")

    # ------------------------------------------------
    # DOWNLOAD RESULTS
    # ------------------------------------------------
    st.subheader("Download Results")
    with open(output_path, "rb") as f:
        st.download_button(
            label="Download Excel Table",
            data=f,
            file_name=os.path.basename(output_path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel",
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

    # ------------------------------------------------
    # MAP GENERATION
    # ------------------------------------------------
    st.divider()
    st.subheader("Generate Maps")
    st.markdown("Generate one or more maps. Each map can include different layers.")

    mappable_keys = [k for k in layers.keys() if k in MAP_LAYER_STYLES]

    if not mappable_keys:
        st.info("No mappable layers available in current screening.")
    else:
        num_maps = st.number_input(
            "How many maps do you want to generate?",
            min_value=1, max_value=5, value=1, step=1
        )

        for map_idx in range(int(num_maps)):
            st.markdown("---")
            st.markdown(f"**Map {map_idx + 1}**")

            map_cols = st.columns(2)
            map_selected_keys = []
            for i, layer_key in enumerate(mappable_keys):
                col = map_cols[i % 2]
                label = LAYER_REGISTRY.get(layer_key, {}).get("label", layer_key)
                if col.checkbox(label, value=True, key=f"map_{map_idx}_{layer_key}"):
                    map_selected_keys.append(layer_key)

            if st.button(f"Generate Map {map_idx + 1}", key=f"btn_map_{map_idx}"):
                if not map_selected_keys:
                    st.warning("Please select at least one layer.")
                else:
                    selected_layers = {k: layers[k] for k in map_selected_keys}

                    # Calculate parcel counts for map labels
                    parcel_counts = {}
                    if "cadastre" in layers and "cadastre" in map_selected_keys:
                        for dist in buffer_distances:
                            buf_union = buffers[dist].geometry.union_all()
                            count = len(layers["cadastre"][
                                layers["cadastre"].geometry.intersects(buf_union)
                            ])
                            parcel_counts[dist] = count

                    with st.spinner(f"Generating Map {map_idx + 1}..."):
                        map_path = generate_map(
                            site_gdf, buffers, selected_layers,
                            site_name_saved,
                            map_suffix=f"map{map_idx + 1}",
                            parcel_counts=parcel_counts if parcel_counts else None
                        )
                    st.image(map_path)
                    with open(map_path, "rb") as f:
                        st.download_button(
                            label=f"Download Map {map_idx + 1}",
                            data=f,
                            file_name=os.path.basename(map_path),
                            mime="image/png",
                            key=f"download_map_{map_idx}"
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

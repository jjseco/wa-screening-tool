# WA Screening Tool — Project Context

## What this project is
A local Python GIS tool for preliminary environmental screening in Western Australia.
The tool accepts site coordinates or a street address, queries spatial layers grouped by screening theme,
scores results by project type, and exports a structured Excel file, Word report, and custom PNG maps
via a Streamlit web interface.

## Current status
All core phases complete and working:
- 22+ layers across 7 themes, modular registry system
- Project type selection with contextual risk scoring
- Configurable buffer distances (presets + custom)
- Risk Summary with 🔴🟡🟢⚪ ratings in Streamlit and Excel
- Interpretation sentences per layer, context-specific per project type
- Geocoding (geopy Nominatim) for address input mode
- Word report (python-docx) fully implemented in scripts/report_writer.py
- Reverse geocoding for parcel addresses in Excel (inner buffer only)
- References sheet in Excel (last sheet)
- Data Sources section in Streamlit rebuilt dynamically from LAYER_REGISTRY
- Citation format standardised across Excel References sheet, Word report, and Streamlit Data Sources

## Machine setup
- macOS
- Python 3.12.4
- Virtual environment: venv
- Activate with: source venv/bin/activate
- All commands must be run from: ~/Desktop/wa_screening_tool

## How to run
### Activate environment first (every time)
```
cd ~/Desktop/wa_screening_tool
source venv/bin/activate
```

### Run Streamlit interface (main way to use the tool)
```
streamlit run app.py
```

### Run preprocessing only (when new data is added)
```
python3 -m scripts.preprocess_layers
```

## Installed libraries
- geopandas
- pandas
- openpyxl
- shapely
- pyproj
- matplotlib
- streamlit
- geopy  (Nominatim geocoding + reverse geocoding)
- python-docx  (Word report generation)

## File structure
```
wa_screening_tool/
├── data/
│   ├── raw/
│   │   ├── esa.gpkg
│   │   ├── wetlands.gpkg
│   │   ├── ass_scp.gpkg
│   │   ├── ass_estuaries.gpkg
│   │   ├── soil_landscape.gpkg
│   │   ├── aboriginal_heritage.gpkg
│   │   ├── historic_heritage.gpkg
│   │   ├── groundwater_areas.gpkg
│   │   ├── groundwater_salinity.gpkg
│   │   ├── bores.gpkg
│   │   ├── contaminated_sites.gpkg
│   │   ├── local_government.gpkg
│   │   ├── cadastre.gpkg
│   │   ├── native_vegetation.gpkg
│   │   ├── vegetation_complexes.gpkg
│   │   ├── buildings_wa.gpkg
│   │   ├── gis_osm_roads_free_1.shp    (+ .cpg .dbf .prj .shx)
│   │   ├── gis_osm_pois_free_1.shp     (+ .cpg .dbf .prj .shx)
│   │   └── gis_osm_buildings_a_free_1.shp  (+ .cpg .dbf .prj .shx)
│   └── processed/
│       ├── esa_clean.gpkg
│       ├── wetlands_clean.gpkg
│       ├── native_vegetation_clean.gpkg
│       ├── vegetation_complexes_clean.gpkg
│       ├── ass_clean.gpkg
│       ├── ass_estuaries_clean.gpkg
│       ├── soil_landscape_clean.gpkg
│       ├── aboriginal_heritage_clean.gpkg
│       ├── historic_heritage_clean.gpkg
│       ├── groundwater_areas_clean.gpkg
│       ├── groundwater_salinity_clean.gpkg
│       ├── bores_clean.gpkg
│       ├── contaminated_sites_clean.gpkg
│       ├── local_government_clean.gpkg
│       ├── cadastre_clean.gpkg
│       ├── roads_clean.gpkg
│       ├── hospitals_clean.gpkg
│       ├── schools_clean.gpkg
│       ├── residential_clean.gpkg         # Buildings WA (DPIRD-084) — primary source
│       ├── residential_osm_clean.gpkg     # OSM buildings filtered — secondary source
│       └── community_facilities_clean.gpkg
├── outputs/
│   ├── tables/      # Excel exports go here
│   ├── maps/        # PNG map exports go here
│   └── summaries/   # Word report exports go here
├── scripts/
│   ├── registry.py          # LAYER_REGISTRY and THEME_REGISTRY — single source of truth
│   ├── project_types.py     # PROJECT_TYPES with 7 types + Custom
│   ├── risk_scoring.py      # Post-processing: trigger, score, risk_level, interpretation
│   ├── preprocess_layers.py # One-time preprocessing of raw → processed layers
│   ├── load_layers.py       # Loads processed layers for selected themes
│   ├── geometry.py          # create_site_point, create_buffers
│   ├── spatial_query.py     # run_all_queries — per-layer spatial intersection logic
│   ├── mapping.py           # generate_map, MAP_LAYER_STYLES
│   ├── export.py            # export_to_excel — Excel with all sheets
│   └── report_writer.py     # generate_word_report — Word .docx
├── venv/
├── config.py
├── main.py
├── app.py
└── PROJECT_CONTEXT.md
```

## CRS
- Input CRS: EPSG:4326 (lat/lon entered by user or resolved by geocoder)
- Analysis CRS: EPSG:32750 (metric, used for all buffers and distance calculations)

## Buffer distances
- Configured via dropdown: Standard (100/250/500), Noise/Dust (50/100/200), Regional (100/500/1000), Custom
- Stored in st.session_state["buffer_distances"] after a run
- All spatial query, mapping, export, and report functions accept buffer_distances as a dynamic parameter
- Column names (Within Xm, Count Xm) are generated at runtime from the actual buffer values

## config.py
Defines BASE_DIR, DATA_RAW, DATA_PROCESSED, OUTPUTS_*, INPUT_CRS, ANALYSIS_CRS, BUFFERS (default), BUFFER_PRESETS dict, and a legacy LAYERS dict (superseded by registry.py).

## registry.py — LAYER_REGISTRY
Single source of truth for all layer definitions. Each entry contains:
- theme, label, source, dataset_code, geometry, file, query
- name_field and/or name_fields_combined and/or name_flags
- color (for mapping)
- description (shown in Data Sources)
- dataset_year (year of dataset publication/currency)
- accessed_year (year data was downloaded — currently 2026 for all)

### Citation format
Used in both export.py (_get_citation) and report_writer.py (_get_citation):
- WA government layers: `Provider (dataset_year). Label [Code]. Accessed March accessed_year from data.wa.gov.au`
- OSM layers: `OpenStreetMap contributors (dataset_year). Label. Geofabrik Australia extract. Accessed March accessed_year from download.geofabrik.de`

The same `_get_citation` and `_get_provider` helper functions are duplicated in export.py and report_writer.py (and imported into app.py from export.py).

### Active layers by theme

#### Ecology
| Key | Label | Code | File | Name logic |
|-----|-------|------|------|-----------|
| esa | Environmentally Sensitive Areas | DWER-046 | esa_clean.gpkg | name_flags: bushforev/tec/whp/ramsar_50m/wst_epp |
| wetlands | Wetlands - Swan Coastal Plain | DBCA-019 | wetlands_clean.gpkg | name_field: wgs_wetlandname |
| native_vegetation | Native Vegetation Extent | DPIRD-005 | native_vegetation_clean.gpkg | presence/absence only |
| vegetation_complexes | Vegetation Complexes - SCP | DBCA-046 | vegetation_complexes_clean.gpkg | name_fields_combined: vsc_vegetype, vsc_landform, vsc_structure |

Note: `threatened_flora` and `zoning` are defined in LAYER_REGISTRY but their processed files do not exist yet — they will silently fail to load.

#### ASS / Soils / Geology
| Key | Label | Code | File | Name logic |
|-----|-------|------|------|-----------|
| ass | ASS Risk - Swan Coastal Plain | DWER-055 | ass_clean.gpkg | name_fields_combined: risk_category |
| ass_estuaries | ASS Risk - Estuaries | DWER-050 | ass_estuaries_clean.gpkg | name_fields_combined: risk_category |
| soil_landscape | Soil Landscape | DPIRD-017 | soil_landscape_clean.gpkg | name_fields_combined: mu_name, mu_sum_des |

#### Heritage
| Key | Label | Code | File | Name logic |
|-----|-------|------|------|-----------|
| aboriginal_heritage | Aboriginal Cultural Heritage | DPLH-099 | aboriginal_heritage_clean.gpkg | name_field: name |
| historic_heritage | State Heritage Register | DPLH-006 | historic_heritage_clean.gpkg | name_field: place_name |

#### Groundwater / Hydrology
| Key | Label | Code | File | Name logic |
|-----|-------|------|------|-----------|
| groundwater_areas | Groundwater Areas | DWER-084 | groundwater_areas_clean.gpkg | name_fields_combined: area_name, aquifer, status |
| groundwater_salinity | Groundwater Salinity | DWER-026 | groundwater_salinity_clean.gpkg | name_fields_combined: tds_mg_l_ |
| bores | Hydro Bores | WCORP-073 | bores_clean.gpkg | name_fields_combined: well_type, well_function, depth |

#### Sensitive Receptors
| Key | Label | Code | File | Notes |
|-----|-------|------|------|-------|
| residential | Residential Buildings (Buildings WA) | DPIRD-084 | residential_clean.gpkg | Primary source. 493,037 features. Imagery 2018-2019 |
| residential_osm | Residential Buildings (OSM) | OSM/Geofabrik | residential_osm_clean.gpkg | Secondary. Coverage incomplete in some suburbs |
| cadastre | Cadastral Parcels | LGATE-001 | cadastre_clean.gpkg | All land use types — proxy for density |
| hospitals | Hospitals | OSM/Geofabrik | hospitals_clean.gpkg | name_field: name |
| schools | Schools | OSM/Geofabrik | schools_clean.gpkg | name_field: name |
| community_facilities | Community Facilities | OSM/Geofabrik | community_facilities_clean.gpkg | name_field: name |
| roads | Roads | OSM/Geofabrik | roads_clean.gpkg | Context and access only |

#### Contaminated Land
| Key | Label | Code | File | Name logic |
|-----|-------|------|------|-----------|
| contaminated_sites | Contaminated Sites | DWER-059 | contaminated_sites_clean.gpkg | name_fields_combined: classification, classification_date, report_url |

#### Planning / Local Government
| Key | Label | Code | File | Name logic |
|-----|-------|------|------|-----------|
| local_government | Local Government Areas | LGATE-233 | local_government_clean.gpkg | name_field: name |

## project_types.py — PROJECT_TYPES
Seven named project types plus Custom. Each defines:
- `recommended_buffers`: list of 3 distances
- `relevant_themes`: themes starred (⭐) in the UI
- `layer_weights`: dict of layer_key → weight (0 = not relevant, 1–4 = low to critical)
- `interpretation_rules`: dict of layer_key → trigger → (risk_level, text with {b1}/{b2}/{b3} placeholders)
- `not_relevant_layers`: convenience list of layers with weight=0

### Types and their focus
| Type | Recommended Buffers | Focus |
|------|--------------------|----|
| Noise Management | 50/100/200 | Sensitive receptors (residential, schools, hospitals, community facilities) |
| Dust Management | 50/100/200 | Sensitive receptors + ecology (wetlands, ESA, soil type) |
| Clearing / Vegetation Removal | 100/250/500 | Ecology (ESA, wetlands, native veg, veg complexes) + heritage + groundwater |
| Contamination Assessment | 100/250/500 | Contaminated sites + ASS + groundwater + soil |
| Groundwater Impact | 100/250/500 | Groundwater areas + bores + wetlands + ASS + contaminated sites |
| Heritage Assessment | 100/250/500 | Aboriginal heritage + historic heritage + ecology context |
| General Environmental Assessment | 100/250/500 | All themes, equal weighting |
| Custom | 100/250/500 | All themes, precautionary weights, generic interpretations |

### Fallback
`GENERIC_INTERPRETATIONS` and `GENERIC_RISK_BY_TRIGGER` in project_types.py are used when a layer/trigger combination has no specific rule defined.

## risk_scoring.py
Post-processes raw spatial query results. Called immediately after `run_all_queries`.

### Functions
- `get_trigger_key(result, buffer_distances)` → "Site" / "b1" / "b2" / "b3" / "None"
- `get_layer_interpretation(layer_key, trigger_key, project_type_name, buffer_distances)` → (risk_level, text) — formats {b1}/{b2}/{b3} with actual distances
- `get_layer_risk_score(layer_key, trigger_key, project_type_name)` → weight × relevance (Site=4, b1=3, b2=2, b3=1, None=0)
- `score_results(results, project_type_name, buffer_distances)` → (scored_results, theme_summary)

### Fields added to each result
trigger_key, layer_score, risk_level, interpretation

### Theme summary structure
`{theme: {rating, score, key_finding, interpretation}}`

### Risk rating logic
- HIGH 🔴: any layer risk_level == HIGH, or theme_score ≥ 20
- MEDIUM 🟡: any layer risk_level == MEDIUM, or theme_score ≥ 10
- LOW 🟢: any features present
- NONE ⚪: no features found

## Spatial query result fields
Each result dict from run_all_queries contains:
- layer_key, layer, theme
- site_intersect, within_{b}m (dynamic — one per buffer distance)
- count_{b}m (dynamic — one per buffer distance)
- nearest_distance_m
- nearby_names
- present, max_relevance, primary_trigger, comment
- (added by risk_scoring) trigger_key, layer_score, risk_level, interpretation

## Geocoding (app.py)
Input mode radio: "Enter Coordinates" (default) or "Enter Address".

### Address mode
- User types a street address and clicks "Geocode Address"
- `geopy.geocoders.Nominatim(user_agent="wa_screening_tool")` calls `.geocode(address, country_codes="au")`
- Resolved lat/lon stored in st.session_state["geocoded_lat"] / ["geocoded_lon"] / ["geocoded_address"]
- Coordinates displayed below the input; used as latitude/longitude for the screening run
- If not yet geocoded, defaults to Perth CBD (-31.9505, 115.8605) as a placeholder (run is blocked by validation)
- Validation: "Run Screening" is blocked if input_mode == "Enter Address" and geocoded_lat is not set

## export.py — export_to_excel
Produces an Excel file at outputs/tables/{site_name}_screening_results.xlsx

### Sheet order
1. **Risk Summary** — Theme, Risk Rating (emoji), Score, Key Finding, Interpretation
2. **Summary** — all layers with blank row between themes
3. **Ecology**
4. **ASS - Soils**
5. **Heritage**
6. **Groundwater**
7. **Contaminated Land**
8. **Planning**
9. **Sensitive Receptors**
10. **Parcels Detail** — one row per cadastral parcel within buffers, with reverse-geocoded address for inner buffer only
11. **Receptors Detail** — hospitals/schools/community facilities with name, distance, within-Xm flags, lat/lon
12. **References** (last sheet) — Theme, Layer, Dataset Code, Provider, Citation — built from LAYER_REGISTRY

### Reverse geocoding in Parcels Detail
For parcels in the innermost buffer only, `geopy.geocoders.Nominatim` reverse-geocodes the parcel centroid to get a street address. Uses `time.sleep(1)` between requests to respect Nominatim rate limits. Falls back silently if geopy is unavailable or geocoding fails.

### Excel formatting
- Blue header row (2F5496), white bold text, centre-aligned
- Freeze panes at D2 (header row + first 3 columns A-C)
- Auto column width (capped at 40 chars)
- Wrap text for Detected Features, Comment, Primary Trigger, Interpretation columns (width=35)
- Row height 30 for header

## report_writer.py — generate_word_report
Produces a Word .docx at outputs/summaries/{site_name}_screening_report.docx

### Document structure
1. **Cover** — title (centred heading), site name, coordinates, date, project type, buffer distances
2. **Executive Summary** — risk summary table (Theme / Risk Rating / Score / Key Finding) + auto-generated narrative paragraph
3. **Screening Results by Theme** — one heading per theme, one Table Grid table per theme with columns: Layer, Source, Present, Max Relevance, Primary Trigger, Nearest (m), Detected Features, Interpretation. Layers with weight=0 for the selected project type are omitted.
4. **Sensitive Receptors Detail** — cadastral parcel counts per buffer distance, then name/distance tables for hospitals, schools, community facilities
5. **Data Sources** — table: Theme, Layer, Dataset Code, Provider, Citation — built from LAYER_REGISTRY for all queried layers
6. **Disclaimer** — standard preliminary screening disclaimer

### Executive summary narrative
`_summary_paragraph` auto-generates a paragraph listing how many themes are HIGH/MEDIUM/LOW. Format: intro + counts + closing with advice to verify and consult.

### Default font
Calibri 11pt set on Normal style.

## mapping.py — map system
- White background PNG maps
- MAP_LAYER_STYLES defines which layers are mappable and their style options
- Special plot functions: plot_cadastre_by_buffer, plot_residential_by_type, plot_residential_osm, plot_community_facilities
- Residential colored by type: house=pink, housing cluster=dark red
- Cadastre colored by buffer zone: 100m=red, 250m=orange, 500m=teal
- Community facilities colored by type
- North arrow, scale bar, site coordinates label
- Parcel counts annotated on buffer rings
- 1–5 custom maps per session, each with independently selected layers

## Streamlit app (app.py) — section order
1. Title + Tutorial expander
2. Layer definitions expander
3. **Project Type** selector (7 types + Custom) — shows recommended buffer preset, marks relevant themes with ⭐, Custom shows free-text description field
4. **Site Details** — site name + coordinate/address input with geocoding
5. **Buffer Distances** — preset dropdown (Standard/Noise/Dust/Regional/Custom), custom shows 3 number inputs
6. **Screening Themes** — checkboxes (2 columns), all selected by default
7. **Run Screening** button — validates then runs full pipeline
8. **Results** (from session_state):
   - Risk Summary table (🔴🟡🟢⚪)
   - Per-theme result tables with Interpretation column
   - Detected Features section (named features only, roads excluded)
   - Download Excel button
   - Download Word Report button
   - Map generation (1–5 maps, per-map layer selection)
9. **Data Sources** table — rebuilt dynamically from LAYER_REGISTRY using _get_citation/_get_provider from export.py

## Data flow (single run)
```
app.py
  → create_site_point(lat, lon)         # geometry.py
  → create_buffers(site_gdf, distances)  # geometry.py
  → load_layers_for_themes(themes)       # load_layers.py → registry.py
  → run_all_queries(layers, site, bufs)  # spatial_query.py
  → score_results(results, proj, dists)  # risk_scoring.py → project_types.py
  → export_to_excel(...)                 # export.py
  → generate_word_report(...)            # report_writer.py
  → [on map button] generate_map(...)    # mapping.py
```

All intermediate objects stored in st.session_state to survive Streamlit reruns.

## Known issues / registry quirks
- `native_vegetation` is defined twice in LAYER_REGISTRY (duplicate key — second definition silently overwrites first). The second definition (lines 76–91) is the active one.
- `threatened_flora` and `zoning` are defined in LAYER_REGISTRY but their processed .gpkg files do not exist — they will fail to load silently.
- OSM residential coverage is incomplete in some Perth suburbs → Buildings WA (DPIRD-084) is the primary residential source.
- Cadastre includes all land use types, not only residential.
- ASS coverage limited to Swan Coastal Plain (DWER-055) and Estuaries (DWER-050).
- Geology (.gdb) not yet integrated.
- Threatened fauna/vegetation datasets not freely available.
- Buildings WA imagery is from 2018–2019.

## Test sites used
- Test Site 01: Perth CBD — lat=-31.9505, lon=115.8605
- Test Site 04: Yanchep — lat=-31.7470, lon=115.7290 (Bush Forever ESA)
- Test Site 05: Subiaco — lat=-31.9553, lon=115.8384 (ESA intersect)
- Test Site 06: Nedlands — lat=-31.9676, lon=115.8153 (hospital nearby)
- Test Site 07: Gallipoli St — lat=-31.965051, lon=115.904295 (residential area)

## Pending work

### Near-term
- Fix duplicate `native_vegetation` entry in registry.py (remove first, keep second)
- Add processed files for `threatened_flora` and `zoning`, or remove from registry

### Phase 5d
- Site polygon upload (replace point with shapefile boundary)

### Phase 5f
- Deploy to Streamlit Cloud
- Basic authentication

### Phase 5g
- Multiple sites comparison
- Database integration

## Completed phases
- Phase 1–4: Full spatial query, preprocessing, Streamlit, maps, Excel
- Phase 4b: Modular registry (registry.py) — 22+ layers, 7 themes
- Phase 4c: Project types + configurable buffers — 7 types + Custom, 4 buffer presets
- Phase 4d: Risk scoring — risk_scoring.py, Risk Summary in Streamlit and Excel
- Phase 4e: New datasets — Buildings WA, soil_landscape, ass_estuaries, bores, groundwater_salinity, native_vegetation, vegetation_complexes, residential_osm, cadastre, community_facilities
- Phase 5a: Geocoding — geopy Nominatim address input in app.py
- Phase 5b: Word report — report_writer.py with full structure (cover, executive summary, themes, receptors detail, data sources, disclaimer)
- Phase 5c: References sheet in Excel, reverse geocoding for inner-buffer parcels, Data Sources rebuilt dynamically from LAYER_REGISTRY

## Key technical decisions
- GeoPackage (.gpkg) is the internal standard for all spatial data
- Preprocessing and runtime are fully separated (preprocess_layers.py run once; load_layers.py at runtime)
- registry.py is the single source of truth for layer definitions — do not hardcode layer metadata elsewhere
- risk_scoring.py is separate from spatial_query.py — scoring is pure post-processing
- Buffer distances are never hardcoded after config.py — they flow as a parameter through every function
- Buildings WA (DPIRD-084) is primary residential source; residential_osm is secondary/supplementary
- st.session_state preserves all results and paths across Streamlit interactions
- Excel formatted with openpyxl (freeze panes, blue headers, auto width, wrap text)
- Word report uses python-docx with Table Grid tables and Calibri 11pt base font
- Citation format is standardised in `_get_citation()` helper — used in export.py, report_writer.py, and app.py (imported from export.py)

# WA Preliminary Environmental Screening Tool

A local Python GIS tool for preliminary desktop environmental screening in Western Australia.
The tool accepts a site location (coordinates or street address), queries 21 spatial layers
across 7 environmental themes, scores results by project type, and exports a structured
Excel table, Word report, and custom PNG maps.

Built with [Streamlit](https://streamlit.io), [GeoPandas](https://geopandas.org), and
publicly available WA government datasets.

## Features

- **21 spatial layers** across 7 themes: Ecology, ASS / Soils, Heritage, Groundwater,
  Contaminated Land, Sensitive Receptors, Planning
- **7 project types** with contextual risk scoring and buffer recommendations
  (Noise, Dust, Clearing, Contamination, Groundwater, Heritage, General)
- **Configurable buffer distances**: Standard (100/250/500m), Noise/Dust (50/100/200m),
  Regional (100/500/1000m), or custom
- **Geocoding**: enter a street address to resolve coordinates automatically
- **Excel export**: Risk Summary, per-theme sheets, Parcels Detail, Receptors Detail,
  References — with reverse-geocoded parcel addresses for the inner buffer
- **Word report**: cover page, executive summary, per-theme tables, data sources, disclaimer
- **PNG maps**: up to 5 configurable maps per run with per-map layer selection
- **Cloud mode**: spatial data is downloaded lazily from Hugging Face when
  `data/processed/` is not present

## Data sources

| Theme | Key datasets |
|-------|-------------|
| Ecology | ESA (DWER-046), Wetlands (DBCA-019), Native Vegetation (DPIRD-005), Vegetation Complexes (DBCA-046) |
| ASS / Soils | ASS Swan Coastal Plain (DWER-055), ASS Estuaries (DWER-050), Soil Landscape (DPIRD-017) |
| Heritage | Aboriginal Cultural Heritage (DPLH-099), State Heritage Register (DPLH-006) |
| Groundwater | Groundwater Areas (DWER-084), Groundwater Salinity (DWER-026), Hydro Bores (WCORP-073) |
| Contaminated Land | Contaminated Sites (DWER-059) |
| Sensitive Receptors | Buildings WA (DPIRD-084), OSM roads/schools/hospitals/community facilities, Cadastre (LGATE-001) |
| Planning | Local Government Areas (LGATE-233) |

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/jseco5555/wa-screening-tool.git
cd wa-screening-tool
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add processed data

Place the 21 processed `.gpkg` files in `data/processed/`.
See `scripts/preprocess_layers.py` to generate them from raw source data.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Streamlit Cloud deployment

Set the environment variable `STREAMLIT_CLOUD=true` in the app secrets or environment settings.
When this is set (or when `data/processed/` is absent), the app automatically downloads
spatial layers from the Hugging Face dataset
[jseco5555/wa-screening-tool-data](https://huggingface.co/datasets/jseco5555/wa-screening-tool-data)
on first use and caches them for the session.

## Project structure

```
wa_screening_tool/
├── app.py                      # Streamlit UI
├── config.py                   # Paths, CRS, buffer presets
├── main.py                     # CLI entry point (alternative to Streamlit)
├── requirements.txt
├── scripts/
│   ├── registry.py             # Layer definitions (single source of truth)
│   ├── project_types.py        # 7 project types with risk rules
│   ├── risk_scoring.py         # Scoring and interpretation
│   ├── data_manager.py         # Local/cloud path resolution + HF download
│   ├── preprocess_layers.py    # Raw → processed (run once)
│   ├── load_layers.py          # Load processed layers at runtime
│   ├── geometry.py             # Site point and buffer creation
│   ├── spatial_query.py        # Per-layer spatial queries
│   ├── mapping.py              # PNG map generation
│   ├── export.py               # Excel export
│   └── report_writer.py        # Word report generation
└── data/
    ├── raw/                    # Source data (not in git)
    └── processed/              # Preprocessed .gpkg files (not in git)
```

## Disclaimer

This tool is intended for preliminary desktop screening purposes only.
Results should be verified against current authoritative sources before use
in formal environmental assessments. Always consult a qualified environmental
professional for project-specific advice.

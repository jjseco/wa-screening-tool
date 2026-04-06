# Registry of all screening themes and their associated layers.
# Each theme contains one or more layers.
# Each layer defines its source, geometry type, processed file,
# query logic, name field, and display color for mapping.

LAYER_REGISTRY = {

    # ----------------------------------------------------------------
    # ECOLOGY
    # ----------------------------------------------------------------
    "esa": {
        "theme": "Ecology",
        "label": "Environmentally Sensitive Areas",
        "source": "Official WA - DWER-046",
        "dataset_code": "DWER-046",
        "geometry": "polygon",
        "file": "esa_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_flags": {
            "bushforev": "Bush Forever",
            "tec": "Threatened Ecological Community",
            "whp": "Wetland of High Protection",
            "ramsar_50m": "Ramsar Wetland nearby",
            "wst_epp": "Water Source Protection",
        },
        "color": "red",
        "description": "Areas protected under WA clearing regulations.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },
    "wetlands": {
        "theme": "Ecology",
        "label": "Wetlands - Swan Coastal Plain",
        "source": "Official WA - DBCA-019",
        "dataset_code": "DBCA-019",
        "geometry": "polygon",
        "file": "wetlands_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": "wgs_wetlandname",
        "name_flags": None,
        "color": "blue",
        "description": "Geomorphic wetlands mapped across the Swan Coastal Plain.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },
    "native_vegetation": {
        "theme": "Ecology",
        "label": "Native Vegetation Extent",
        "source": "Official WA - DPIRD-005",
        "dataset_code": "DPIRD-005",
        "geometry": "polygon",
        "file": "native_vegetation_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": None,
        "name_flags": None,
        "color": "forestgreen",
        "description": "Native vegetation extent derived from satellite imagery. Reports presence within screening buffers.",
        "dataset_year": 2023,
        "accessed_year": 2026,
    },
    "vegetation_complexes": {
        "theme": "Ecology",
        "label": "Vegetation Complexes - Swan Coastal Plain",
        "source": "Official WA - DBCA-046",
        "dataset_code": "DBCA-046",
        "geometry": "polygon",
        "file": "vegetation_complexes_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["vsc_vegetype", "vsc_landform", "vsc_structure"],
        "name_flags": None,
        "color": "limegreen",
        "description": "Vegetation complexes. Reports vegetation type, landform and structure.",
        "dataset_year": 2016,
        "accessed_year": 2026,
    },
    # ----------------------------------------------------------------
    # ASS / SOILS / GEOLOGY
    # ----------------------------------------------------------------
    "ass": {
        "theme": "ASS / Soils / Geology",
        "label": "Acid Sulfate Soils Risk - Swan Coastal Plain",
        "source": "Official WA - DWER-055",
        "dataset_code": "DWER-055",
        "geometry": "polygon",
        "file": "ass_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["risk_category"],
        "name_flags": None,
        "color": "orange",
        "description": "Acid sulfate soils risk mapping for the Swan Coastal Plain.",
        "dataset_year": 2006,
        "accessed_year": 2026,
    },
    "ass_estuaries": {
        "theme": "ASS / Soils / Geology",
        "label": "Acid Sulfate Soils Risk - Estuaries",
        "source": "Official WA - DWER-050",
        "dataset_code": "DWER-050",
        "geometry": "polygon",
        "file": "ass_estuaries_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["risk_category"],
        "name_flags": None,
        "color": "darkorange",
        "description": "Acid sulfate soils risk mapping for estuaries.",
        "dataset_year": 2006,
        "accessed_year": 2026,
    },
    "soil_landscape": {
        "theme": "ASS / Soils / Geology",
        "label": "Soil Landscape",
        "source": "Official WA - DPIRD-017",
        "dataset_code": "DPIRD-017",
        "geometry": "polygon",
        "file": "soil_landscape_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["mu_name", "mu_sum_des"],
        "name_flags": None,
        "color": "sienna",
        "description": "Soil landscape mapping. Reports soil unit name and description.",
        "dataset_year": 2025,
        "accessed_year": 2026,
    },
    "soil_landscape_best": {
        "theme": "ASS / Soils / Geology",
        "label": "Soil Landscape - Best Available",
        "source": "Official WA - DPIRD-027",
        "dataset_code": "DPIRD-027",
        "dataset_year": 2025,
        "accessed_year": 2026,
        "geometry": "polygon",
        "file": "soil_landscape_best_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["mu_name", "mu_sum_des"],
        "name_flags": None,
        "color": "peru",
        "description": "Best available soil landscape mapping for WA. Reports soil unit name and description.",
    },
    "soil_group": {
        "theme": "ASS / Soils / Geology",
        "label": "Soil Group - WA Classification",
        "source": "Official WA - DPIRD-076",
        "dataset_code": "DPIRD-076",
        "dataset_year": 2019,
        "accessed_year": 2026,
        "geometry": "polygon",
        "file": "soil_group_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["wasg_decode", "muwasgs_s1"],
        "name_flags": None,
        "color": "chocolate",
        "description": "WA Soil Group classification. Reports dominant soil group name and code.",
    },

    # ----------------------------------------------------------------
    # HERITAGE
    # ----------------------------------------------------------------
    "aboriginal_heritage": {
        "theme": "Heritage",
        "label": "Aboriginal Cultural Heritage",
        "source": "Official WA - DPLH (SLIP)",
        "dataset_code": "DPLH-099",
        "geometry": "polygon",
        "file": "aboriginal_heritage_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": "name",
        "name_flags": None,
        "color": "saddlebrown",
        "description": "Registered Aboriginal heritage places and surveyed areas.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },
    "historic_heritage": {
        "theme": "Heritage",
        "label": "State Heritage Register",
        "source": "Official WA - DPLH",
        "dataset_code": "DPLH-006",
        "geometry": "point",
        "file": "historic_heritage_clean.gpkg",
        "query": "buffer_distance",
        "name_field": "place_name",
        "name_flags": None,
        "color": "goldenrod",
        "description": "Places listed on the WA State Heritage Register.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },
    # ----------------------------------------------------------------
    # GROUNDWATER / HYDROLOGY
    # ----------------------------------------------------------------
    "groundwater_areas": {
        "theme": "Groundwater / Hydrology",
        "label": "Groundwater Areas",
        "source": "Official WA - DWER",
        "dataset_code": "DWER-084",
        "geometry": "polygon",
        "file": "groundwater_areas_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["area_name", "aquifer", "status"],
        "name_flags": None,
        "color": "steelblue",
        "description": "Proclaimed groundwater areas. Reports area name, aquifer and status.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },
    "groundwater_salinity": {
        "theme": "Groundwater / Hydrology",
        "label": "Groundwater Salinity",
        "source": "Official WA - DWER",
        "dataset_code": "DWER-026",
        "geometry": "polygon",
        "file": "groundwater_salinity_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["tds_mg_l_"],
        "name_flags": None,
        "color": "lightblue",
        "description": "Groundwater salinity mapping. Reports TDS classification in mg/L.",
        "dataset_year": 2019,
        "accessed_year": 2026,
    },
    "bores": {
        "theme": "Groundwater / Hydrology",
        "label": "Hydro Bores",
        "source": "Official WA - DWER",
        "dataset_code": "WCORP-073",
        "geometry": "point",
        "file": "bores_clean.gpkg",
        "query": "buffer_distance",
        "name_field": None,
        "name_fields_combined": ["well_type", "well_function", "depth"],
        "name_flags": None,
        "color": "dodgerblue",
        "description": "Hydro bores. Reports well type, function and depth.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },

    # ----------------------------------------------------------------
    # SENSITIVE RECEPTORS
    # ----------------------------------------------------------------
    "hospitals": {
        "theme": "Sensitive Receptors",
        "label": "Hospitals",
        "source": "OSM / Geofabrik",
        "dataset_code": "OSM / Geofabrik",
        "geometry": "point",
        "file": "hospitals_clean.gpkg",
        "query": "buffer_distance",
        "name_field": "name",
        "name_flags": None,
        "color": "purple",
        "description": "Hospitals and major medical facilities.",
        "dataset_year": 2026,
        "accessed_year": 2026,
    },
    "schools": {
        "theme": "Sensitive Receptors",
        "label": "Schools",
        "source": "OSM / Geofabrik",
        "dataset_code": "OSM / Geofabrik",
        "geometry": "point",
        "file": "schools_clean.gpkg",
        "query": "buffer_distance",
        "name_field": "name",
        "name_flags": None,
        "color": "orange",
        "description": "Primary and secondary schools.",
        "dataset_year": 2026,
        "accessed_year": 2026,
    },
    "residential": {
        "theme": "Sensitive Receptors",
        "label": "Residential Buildings (Buildings WA)",
        "source": "Official WA - DPIRD-084",
        "dataset_code": "DPIRD-084",
        "geometry": "polygon",
        "file": "residential_clean.gpkg",
        "query": "buffer_distance",
        "name_field": "type",
        "name_flags": None,
        "color": "pink",
        "description": "Residential buildings derived from satellite imagery. Includes houses and housing clusters.",
        "dataset_year": 2019,
        "accessed_year": 2026,
    },
    "residential_osm": {
        "theme": "Sensitive Receptors",
        "label": "Residential Buildings (OSM)",
        "source": "OSM / Geofabrik",
        "dataset_code": "OSM / Geofabrik",
        "geometry": "polygon",
        "file": "residential_osm_clean.gpkg",
        "query": "buffer_distance",
        "name_field": "type",
        "name_flags": None,
        "color": "lightyellow",
        "description": "Residential buildings from OpenStreetMap. Coverage incomplete in some Perth suburbs.",
        "dataset_year": 2026,
        "accessed_year": 2026,
    },
    "cadastre": {
        "theme": "Sensitive Receptors",
        "label": "Cadastral Parcels",
        "source": "Official WA - LGATE",
        "dataset_code": "LGATE-001",
        "geometry": "polygon",
        "file": "cadastre_clean.gpkg",
        "query": "buffer_distance",
        "name_field": None,
        "name_fields_combined": None,
        "name_flags": None,
        "color": "lightyellow",
        "description": "All cadastral parcels within screening buffers. Used as proxy for residential density. Includes all land use types.",
        "dataset_year": 2026,
        "accessed_year": 2026,
    },
    "community_facilities": {
        "theme": "Sensitive Receptors",
        "label": "Community Facilities",
        "source": "OSM / Geofabrik",
        "dataset_code": "OSM / Geofabrik",
        "geometry": "polygon",
        "file": "community_facilities_clean.gpkg",
        "query": "buffer_distance",
        "name_field": "name",
        "name_flags": None,
        "color": "mediumpurple",
        "description": "Community facilities including churches, community centres, nursing homes, childcare, and places of worship.",
        "dataset_year": 2026,
        "accessed_year": 2026,
    },
    "roads": {
        "theme": "Sensitive Receptors",
        "label": "Roads",
        "source": "OSM / Geofabrik",
        "dataset_code": "OSM / Geofabrik",
        "geometry": "line",
        "file": "roads_clean.gpkg",
        "query": "buffer_distance",
        "name_field": None,
        "name_flags": None,
        "color": "gray",
        "description": "Road network for site context and access.",
        "dataset_year": 2026,
        "accessed_year": 2026,
    },

    # ----------------------------------------------------------------
    # CONTAMINATED LAND
    # ----------------------------------------------------------------
    "contaminated_sites": {
        "theme": "Contaminated Land",
        "label": "Contaminated Sites",
        "source": "Official WA - DWER-059",
        "dataset_code": "DWER-059",
        "geometry": "polygon",
        "file": "contaminated_sites_clean.gpkg",
        "query": "intersect_buffer_distance",
        "name_field": None,
        "name_fields_combined": ["classification", "classification_date", "report_url"],
        "name_flags": None,
        "color": "black",
        "description": "Sites listed on the WA Contaminated Sites database.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },

    # ----------------------------------------------------------------
    # PLANNING / LOCAL GOVERNMENT
    # ----------------------------------------------------------------
    "local_government": {
        "theme": "Planning / Local Government",
        "label": "Local Government Areas",
        "source": "Official WA - LGATE",
        "dataset_code": "LGATE-233",
        "geometry": "polygon",
        "file": "local_government_clean.gpkg",
        "query": "intersect_name",
        "name_field": "name",
        "name_flags": None,
        "color": "lightgray",
        "description": "Local Government Area boundaries across WA.",
        "dataset_year": 2024,
        "accessed_year": 2026,
    },
}


# ----------------------------------------------------------------
# THEME REGISTRY
# Groups layers by theme for UI selection and selective execution.
# ----------------------------------------------------------------
THEME_REGISTRY = {}
for layer_key, layer_def in LAYER_REGISTRY.items():
    theme = layer_def["theme"]
    if theme not in THEME_REGISTRY:
        THEME_REGISTRY[theme] = []
    THEME_REGISTRY[theme].append(layer_key)


def get_layers_for_themes(selected_themes):
    """Return list of layer keys for the selected themes."""
    layers = []
    for theme in selected_themes:
        if theme in THEME_REGISTRY:
            layers.extend(THEME_REGISTRY[theme])
    return layers


def get_available_themes():
    """Return list of all theme names."""
    return list(THEME_REGISTRY.keys())


def get_layer_def(layer_key):
    """Return the definition dict for a single layer."""
    return LAYER_REGISTRY.get(layer_key, None)
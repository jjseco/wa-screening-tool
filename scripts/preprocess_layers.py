import geopandas as gpd
import os
from config import DATA_RAW, DATA_PROCESSED, ANALYSIS_CRS


def preprocess_layer(input_file, output_file, keep_columns=None, geometry_type=None, filter_column=None, filter_value=None):
    """Load a raw layer, reproject it, and save it as a clean GeoPackage."""

    input_path = os.path.join(DATA_RAW, input_file)
    output_path = os.path.join(DATA_PROCESSED, output_file)

    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    print(f"Loading {input_file}...")
    gdf = gpd.read_file(input_path)

    # Apply filter if specified
    if filter_column and filter_value:
        gdf = gdf[gdf[filter_column] == filter_value]
        print(f"Filtered to {filter_value}: {len(gdf)} features")

    # Reproject to analysis CRS
    print(f"Reprojecting to {ANALYSIS_CRS}...")
    gdf = gdf.to_crs(ANALYSIS_CRS)

    # Keep only selected columns plus geometry
    if keep_columns:
        available = [c for c in keep_columns if c in gdf.columns]
        gdf = gdf[available + ["geometry"]]

    # Fix invalid geometries only for polygons
    if geometry_type == "polygon":
        gdf["geometry"] = gdf.geometry.buffer(0)

    # Remove empty geometries
    gdf = gdf[~gdf.geometry.is_empty]
    gdf = gdf[gdf.geometry.notna()]

    # Save clean file
    gdf.to_file(output_path, driver="GPKG")
    print(f"Saved clean layer to: {output_path}")
    print(f"Total features: {len(gdf)}\n")


def run_preprocessing():
    """Run preprocessing for all available raw layers."""

    print("=" * 50)
    print("Starting preprocessing...")
    print("=" * 50 + "\n")

    # --- ECOLOGY ---
    preprocess_layer(
        input_file="esa.gpkg",
        output_file="esa_clean.gpkg",
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="wetlands.gpkg",
        output_file="wetlands_clean.gpkg",
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="native_vegetation.gpkg",
        output_file="native_vegetation_clean.gpkg",
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="vegetation_complexes.gpkg",
        output_file="vegetation_complexes_clean.gpkg",
        keep_columns=["vsc_vegetype", "vsc_landform", "vsc_structure", "vsc_system"],
        geometry_type="polygon"
    )

    # --- ASS / SOILS ---
    preprocess_layer(
        input_file="ass_scp.gpkg",
        output_file="ass_clean.gpkg",
        keep_columns=["risk_class", "risk_category"],
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="ass_estuaries.gpkg",
        output_file="ass_estuaries_clean.gpkg",
        keep_columns=["risk_class", "risk_category"],
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="soil_landscape.gpkg",
        output_file="soil_landscape_clean.gpkg",
        keep_columns=["mu_name", "mu_sum_des", "mu_system", "lq_sa_ris_", "lq_salin_m", "lq_su_aci_"],
        geometry_type="polygon"
    )
    # NOTE: rename data/raw/Soil Landscape Mapping.gpkg → data/raw/soil_landscape_best.gpkg before running
    preprocess_layer(
        input_file="soil_landscape_best.gpkg",
        output_file="soil_landscape_best_clean.gpkg",
        keep_columns=["mu_name", "mu_sum_des", "mu_system", "lq_sa_ris_", "lq_salin_m", "lq_su_aci_"],
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="Soil_group_dpird_076.gpkg",
        output_file="soil_group_clean.gpkg",
        keep_columns=["wasg_decode", "muwasgs_s1", "muwasgs_p1", "mu_symbol"],
        geometry_type="polygon"
    )

    # --- HERITAGE ---
    preprocess_layer(
        input_file="aboriginal_heritage.gpkg",
        output_file="aboriginal_heritage_clean.gpkg",
        keep_columns=["name", "place_type", "place_status", "restricted_place"],
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="historic_heritage.gpkg",
        output_file="historic_heritage_clean.gpkg",
        keep_columns=["place_name", "location", "lga"],
        geometry_type="polygon"
    )

    # --- GROUNDWATER / HYDROLOGY ---
    preprocess_layer(
        input_file="groundwater_areas.gpkg",
        output_file="groundwater_areas_clean.gpkg",
        keep_columns=["name", "area_name", "aquifer", "resourcetype", "status"],
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="groundwater_salinity.gpkg",
        output_file="groundwater_salinity_clean.gpkg",
        keep_columns=["tds_mg_l_", "salinity_"],
        geometry_type="polygon"
    )
    preprocess_layer(
        input_file="bores.gpkg",
        output_file="bores_clean.gpkg",
        keep_columns=["well_type", "well_function", "depth", "works_name"],
        geometry_type="point"
    )

    # --- CONTAMINATED LAND ---
    preprocess_layer(
        input_file="contaminated_sites.gpkg",
        output_file="contaminated_sites_clean.gpkg",
        keep_columns=["classification", "classification_date", "report_url", "css_id"],
        geometry_type="polygon"
    )

    # --- PLANNING / LGA ---
    preprocess_layer(
        input_file="local_government.gpkg",
        output_file="local_government_clean.gpkg",
        keep_columns=["name", "type_description"],
        geometry_type="polygon"
    )

    # --- SENSITIVE RECEPTORS ---
    preprocess_layer(
        input_file="gis_osm_roads_free_1.shp",
        output_file="roads_clean.gpkg",
        geometry_type="line"
    )
    preprocess_layer(
        input_file="gis_osm_pois_free_1.shp",
        output_file="hospitals_clean.gpkg",
        geometry_type="point",
        filter_column="fclass",
        filter_value="hospital"
    )
    preprocess_layer(
        input_file="gis_osm_pois_free_1.shp",
        output_file="schools_clean.gpkg",
        geometry_type="point",
        filter_column="fclass",
        filter_value="school"
    )

        # --- RESIDENTIAL RECEPTORS (Buildings WA - DPIRD-084) ---
    residential_types_wa = ['house', 'housing cluster']

    print("Loading buildings_wa.gpkg...")
    buildings_wa_path = os.path.join(DATA_RAW, 'buildings_wa.gpkg')
    if os.path.exists(buildings_wa_path):
        buildings_wa = gpd.read_file(buildings_wa_path)
        residential_wa = buildings_wa[buildings_wa['type'].isin(residential_types_wa)].copy()
        print(f"Filtered to residential types: {len(residential_wa)} features")
        residential_wa = residential_wa.to_crs(ANALYSIS_CRS)
        residential_wa = residential_wa[~residential_wa.geometry.is_empty]
        residential_wa = residential_wa[residential_wa.geometry.notna()]
        residential_wa = residential_wa[['type', 'accuracy_m', 'geometry']]
        residential_wa.to_file(os.path.join(DATA_PROCESSED, 'residential_clean.gpkg'), driver='GPKG')
        print(f"Saved clean layer to: {DATA_PROCESSED}/residential_clean.gpkg")
        print(f"Total features: {len(residential_wa)}\n")
    else:
        print("File not found: buildings_wa.gpkg\n")

    # --- ALL BUILDINGS WA (for context) ---
    print("Loading buildings_wa.gpkg for all buildings...")
    if os.path.exists(buildings_wa_path):
        all_buildings = gpd.read_file(buildings_wa_path)
        all_buildings = all_buildings.to_crs(ANALYSIS_CRS)
        all_buildings = all_buildings[~all_buildings.geometry.is_empty]
        all_buildings = all_buildings[all_buildings.geometry.notna()]
        all_buildings = all_buildings[['type', 'accuracy_m', 'geometry']]
        all_buildings.to_file(os.path.join(DATA_PROCESSED, 'buildings_wa_clean.gpkg'), driver='GPKG')
        print(f"Saved all buildings: {len(all_buildings)} features\n")

    # --- RESIDENTIAL RECEPTORS (OSM) ---
    residential_types_osm = [
        'house', 'apartments', 'residential', 'detached',
        'semidetached_house', 'semi_detached', 'semi-detached',
        'terrace', 'terraces', 'townhouse', 'townhouses',
        'flat', 'flats', 'granny_flat', 'granny flat',
        'duplex', 'bungalow', 'villa', 'unit', 'units',
        'subdivided_house', 'farmhouse', 'cottage'
    ]

    print("Loading gis_osm_buildings_a_free_1.shp for OSM residential...")
    osm_buildings_path = os.path.join(DATA_RAW, 'gis_osm_buildings_a_free_1.shp')
    if os.path.exists(osm_buildings_path):
        osm_buildings = gpd.read_file(osm_buildings_path)
        residential_osm = osm_buildings[osm_buildings['type'].isin(residential_types_osm)].copy()
        print(f"Filtered to OSM residential types: {len(residential_osm)} features")
        residential_osm = residential_osm.to_crs(ANALYSIS_CRS)
        residential_osm = residential_osm[~residential_osm.geometry.is_empty]
        residential_osm = residential_osm[residential_osm.geometry.notna()]
        residential_osm = residential_osm[['type', 'geometry']]
        residential_osm.to_file(os.path.join(DATA_PROCESSED, 'residential_osm_clean.gpkg'), driver='GPKG')
        print(f"Saved OSM residential to: {DATA_PROCESSED}/residential_osm_clean.gpkg")
        print(f"Total features: {len(residential_osm)}\n")
    else:
        print("File not found: gis_osm_buildings_a_free_1.shp\n")

    # --- COMMUNITY FACILITIES ---
    community_types = [
        'church', 'community_centre', 'community_hall', 'nursing_home',
        'childcare', 'retirement_home', 'social_facility', 'social_club',
        'parish_hall', 'scout_hall', 'kindergarten', 'mosque', 'temple',
        'synagogue', 'chapel', 'cathedral', 'place_of_worship',
        'community', 'civic', 'public', 'public_building'
    ]

    print("Loading gis_osm_buildings_a_free_1.shp for community facilities...")
    if os.path.exists(buildings_path):
        community = buildings[buildings['type'].isin(community_types)].copy()
        print(f"Filtered to community types: {len(community)} features")
        community = community.to_crs(ANALYSIS_CRS)
        community = community[~community.geometry.is_empty]
        community = community[community.geometry.notna()]
        community = community[['type', 'name', 'geometry']]
        community.to_file(os.path.join(DATA_PROCESSED, 'community_facilities_clean.gpkg'), driver='GPKG')
        print(f"Saved clean layer to: {DATA_PROCESSED}/community_facilities_clean.gpkg")
        print(f"Total features: {len(community)}\n")
    else:
        print("File not found: gis_osm_buildings_a_free_1.shp\n")

    # --- CADASTRE ---
    preprocess_layer(
        input_file="cadastre.gpkg",
        output_file="cadastre_clean.gpkg",
        geometry_type="polygon"
    )
    print("=" * 50)
    print("Preprocessing complete.")
    print("=" * 50)


if __name__ == "__main__":
    run_preprocessing()
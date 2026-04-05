from scripts.load_layers import load_all_layers
from scripts.geometry import create_site_point, create_buffers
from scripts.spatial_query import run_all_queries
from scripts.export import export_to_excel
from scripts.mapping import generate_map


def run_screening(site_name, latitude, longitude):
    """Run the full environmental screening for a given site."""

    print("=" * 50)
    print(f"Starting screening for: {site_name}")
    print(f"Coordinates: lat={latitude}, lon={longitude}")
    print("=" * 50)

    # Step 1 - Create site geometry and buffers
    print("\n[1/5] Creating site geometry...")
    site_gdf = create_site_point(latitude, longitude)
    buffers = create_buffers(site_gdf)

    # Step 2 - Load processed layers
    print("\n[2/5] Loading layers...")
    layers = load_all_layers()

    if not layers:
        print("No layers found. Please run the preprocessing step first.")
        return

    # Step 3 - Run spatial queries
    print("\n[3/5] Running spatial queries...")
    results = run_all_queries(layers, site_gdf, buffers)

    # Step 4 - Export results table
    print("\n[4/5] Exporting results table...")
    output_path = export_to_excel(results, site_name)

    # Step 5 - Generate map
    print("\n[5/5] Generating map...")
    map_path = generate_map(site_gdf, buffers, layers, site_name)

    print("\n" + "=" * 50)
    print("Screening complete.")
    print(f"Table saved to: {output_path}")
    print(f"Map saved to:   {map_path}")
    print("=" * 50)


if __name__ == "__main__":
    run_screening(
        site_name="Test Site 01",
        latitude=-31.9505,
        longitude=115.8605
    )
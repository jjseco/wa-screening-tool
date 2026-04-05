import geopandas as gpd
from shapely.geometry import Point
from config import INPUT_CRS, ANALYSIS_CRS, BUFFERS


def create_site_point(latitude, longitude):
    """Create a site point from latitude and longitude in the analysis CRS."""

    # Create point in input CRS (EPSG:4326)
    point = Point(longitude, latitude)
    gdf = gpd.GeoDataFrame(geometry=[point], crs=INPUT_CRS)

    # Reproject to metric analysis CRS
    gdf = gdf.to_crs(ANALYSIS_CRS)

    print(f"Site point created at lat={latitude}, lon={longitude}")
    return gdf


def create_buffers(site_gdf, buffer_distances=None):
    """Create buffer zones around the site point.

    Args:
        site_gdf: GeoDataFrame with the site point in ANALYSIS_CRS.
        buffer_distances: list of distances in metres. Defaults to BUFFERS from config.

    Returns:
        dict mapping distance -> buffered GeoDataFrame.
    """
    if buffer_distances is None:
        buffer_distances = BUFFERS

    buffers = {}
    for distance in buffer_distances:
        buffered = site_gdf.copy()
        buffered["geometry"] = site_gdf.geometry.buffer(distance)
        buffers[distance] = buffered
        print(f"Buffer {distance}m created.")

    return buffers
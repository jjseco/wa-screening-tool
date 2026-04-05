import math
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


def create_bbox(latitude, longitude, margin_km=2.0):
    """Create a bounding box around a point with a margin in kilometres.

    Args:
        latitude: Site latitude in decimal degrees (EPSG:4326).
        longitude: Site longitude in decimal degrees (EPSG:4326).
        margin_km: Half-width of the bounding box in kilometres. Default 2 km
                   is sufficient to cover 500 m buffers with comfortable margin.

    Returns:
        Tuple (minx, miny, maxx, maxy) in EPSG:4326.
    """
    deg_per_km_lat = 1.0 / 111.32
    deg_per_km_lon = 1.0 / (111.32 * math.cos(math.radians(latitude)))

    delta_lat = margin_km * deg_per_km_lat
    delta_lon = margin_km * deg_per_km_lon

    minx = longitude - delta_lon
    maxx = longitude + delta_lon
    miny = latitude - delta_lat
    maxy = latitude + delta_lat

    return (minx, miny, maxx, maxy)


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
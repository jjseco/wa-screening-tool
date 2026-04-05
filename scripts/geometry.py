import geopandas as gpd
from pyproj import Transformer
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
    """Create a bounding box around a point in the analysis CRS (EPSG:32750).

    Projects the site coordinates from EPSG:4326 to EPSG:32750 and adds a
    symmetric margin in metres, so the returned bbox matches the CRS of all
    processed layer files and can be passed directly to gpd.read_file(bbox=...).

    Args:
        latitude: Site latitude in decimal degrees (EPSG:4326).
        longitude: Site longitude in decimal degrees (EPSG:4326).
        margin_km: Half-width of the bounding box in kilometres. Default 2.0 km
                   is sufficient to cover 500 m buffers with comfortable margin.

    Returns:
        Tuple (minx, miny, maxx, maxy) in EPSG:32750.
    """
    transformer = Transformer.from_crs(INPUT_CRS, ANALYSIS_CRS, always_xy=True)
    x, y = transformer.transform(longitude, latitude)
    margin_m = margin_km * 1000
    return (x - margin_m, y - margin_m, x + margin_m, y + margin_m)


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
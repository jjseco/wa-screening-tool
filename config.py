import os

# Carpetas principales
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_TABLES = os.path.join(BASE_DIR, "outputs", "tables")
OUTPUTS_MAPS = os.path.join(BASE_DIR, "outputs", "maps")
OUTPUTS_SUMMARIES = os.path.join(BASE_DIR, "outputs", "summaries")

# Sistema de coordenadas
INPUT_CRS = "EPSG:4326"       # Coordenadas que ingresa el usuario (lat/lon)
ANALYSIS_CRS = "EPSG:32750"   # Métrico para WA (distancias en metros)

# Distancias de buffer en metros (default)
BUFFERS = [100, 250, 500]

# Buffer presets available in the UI
BUFFER_PRESETS = {
    "Standard": [100, 250, 500],
    "Noise/Dust": [50, 100, 200],
    "Regional": [100, 500, 1000],
}

# Capas del proyecto
LAYERS = {
    "esa":       {"file": "esa_clean.gpkg",       "type": "polygon"},
    "wetlands":  {"file": "wetlands_clean.gpkg",  "type": "polygon"},
    "roads":     {"file": "roads_clean.gpkg",     "type": "line"},
    "hospitals": {"file": "hospitals_clean.gpkg", "type": "point"},
    "schools":   {"file": "schools_clean.gpkg",   "type": "point"},
}
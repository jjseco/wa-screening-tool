"""
data_manager.py — Resolves file paths for processed layers.

Two modes:
  LOCAL  — reads from data/processed/ on the local filesystem.
  CLOUD  — downloads .gpkg files from Hugging Face on demand and caches them
            for the lifetime of the process.

Cloud mode is active when:
  1. The environment variable STREAMLIT_CLOUD=true is set, OR
  2. data/processed/ does not exist or contains no .gpkg files.

Hugging Face dataset layout:
  jseco5555/wa-screening-tool-data
  └── processed/
      ├── esa_clean.gpkg
      ├── wetlands_clean.gpkg
      └── ... (all 21 processed layers)
"""

import os
import traceback

from config import DATA_PROCESSED

HF_REPO_ID = "jseco5555/wa-screening-tool-data"
HF_SUBFOLDER = "processed"

# Explicit path — /tmp is always writable on Streamlit Community Cloud.
# Falls back to a subfolder of the system temp dir on Windows.
_CACHE_DIR = "/tmp/wa_screening_cache" if os.name != "nt" else os.path.join(
    os.environ.get("TEMP", os.path.expanduser("~")), "wa_screening_cache"
)

# Track filenames already logged so reruns are quieter.
_logged_downloads: set[str] = set()


def is_cloud_mode() -> bool:
    """Return True when running in cloud / deployment mode."""
    if os.environ.get("STREAMLIT_CLOUD", "").lower() == "true":
        return True
    if not os.path.isdir(DATA_PROCESSED):
        return True
    gpkg_files = [f for f in os.listdir(DATA_PROCESSED) if f.endswith(".gpkg")]
    return len(gpkg_files) == 0


def get_layer_path(filename: str) -> str:
    """
    Return the local filesystem path for a processed layer file.

    LOCAL mode: returns data/processed/{filename} directly.
    CLOUD mode: downloads the file from Hugging Face if not already cached,
                then returns the cached path.

    Files are stored in the HF repo under processed/{filename}, so
    hf_hub_download is called with subfolder='processed'.
    """
    if not is_cloud_mode():
        return os.path.join(DATA_PROCESSED, filename)

    # --- Cloud mode ---
    os.makedirs(_CACHE_DIR, exist_ok=True)

    hf_path = f"{HF_SUBFOLDER}/{filename}"

    if filename not in _logged_downloads:
        print(
            f"[data_manager] Fetching '{hf_path}' from "
            f"Hugging Face repo '{HF_REPO_ID}' (repo_type='dataset') "
            f"→ cache_dir='{_CACHE_DIR}'"
        )
        _logged_downloads.add(filename)

    try:
        from huggingface_hub import hf_hub_download

        local_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=filename,
            subfolder=HF_SUBFOLDER,
            repo_type="dataset",
            cache_dir=_CACHE_DIR,
        )
        print(f"[data_manager] OK — '{filename}' resolved to: {local_path}")
        return local_path

    except Exception as exc:
        print(
            f"[data_manager] ERROR downloading '{hf_path}' from '{HF_REPO_ID}':\n"
            f"  {type(exc).__name__}: {exc}\n"
            f"{traceback.format_exc()}"
        )
        # Return the expected flat path so load_layer emits its own "file not
        # found" warning rather than crashing with an unhandled exception.
        return os.path.join(_CACHE_DIR, filename)

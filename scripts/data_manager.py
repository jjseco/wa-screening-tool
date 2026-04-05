"""
data_manager.py — Resolves file paths for processed layers.

Two modes:
  LOCAL  — reads from data/processed/ on the local filesystem.
  CLOUD  — downloads .gpkg files from Hugging Face on demand and caches them
            for the lifetime of the process.

Cloud mode is active when:
  1. The environment variable STREAMLIT_CLOUD=true is set, OR
  2. data/processed/ does not exist or contains no .gpkg files.
"""

import os
import tempfile

from config import DATA_PROCESSED

HF_REPO_ID = "jseco5555/wa-screening-tool-data"

# Cache directory used in cloud mode. Lives in the system temp dir so it is
# always writable (including on Streamlit Community Cloud).
_CACHE_DIR = os.path.join(tempfile.gettempdir(), "wa_screening_cache")

# Internal set tracking which files have already been logged as "downloading"
# so repeat calls (e.g. after a Streamlit rerun) are quieter.
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
    CLOUD mode: downloads the file from Hugging Face if it is not already
                cached, then returns the cached path.
    """
    if not is_cloud_mode():
        return os.path.join(DATA_PROCESSED, filename)

    # --- Cloud mode ---
    os.makedirs(_CACHE_DIR, exist_ok=True)

    # hf_hub_download is fast when the file is already cached; it only
    # hits the network when the blob is missing or stale.
    if filename not in _logged_downloads:
        print(f"[data_manager] Fetching '{filename}' from Hugging Face ({HF_REPO_ID})…")
        _logged_downloads.add(filename)

    try:
        from huggingface_hub import hf_hub_download

        local_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=filename,
            repo_type="dataset",
            cache_dir=_CACHE_DIR,
        )
        return local_path

    except Exception as exc:
        print(f"[data_manager] ERROR downloading '{filename}': {exc}")
        # Return the expected path so load_layer can emit its own "file not
        # found" warning rather than crashing with an unhandled exception.
        return os.path.join(_CACHE_DIR, filename)

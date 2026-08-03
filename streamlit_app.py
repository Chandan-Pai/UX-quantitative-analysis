"""Repo-root entrypoint (optional). Prefer dashboard/app.py on Streamlit Cloud."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / "dashboard" / "app.py"), run_name="__main__")

"""Optional Uvicorn import target for the companion teaching project."""

from __future__ import annotations

import os
from pathlib import Path

from rice_dsm.data_product import create_app

database_path = Path(os.environ.get("RICE_DSM_DATABASE_PATH", "measurement-demo.sqlite3"))
app = create_app(database_path)

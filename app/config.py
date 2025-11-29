from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent  # Root of project
DATA_DIR = BASE_DIR / "app" / "data" /"DATA"
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Ensure DATA folder exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


print(" Imports successful!")
print(f" DATA folder: {DATA_DIR.resolve()}")
print(f" Database will be created at: {DB_PATH.resolve()}")
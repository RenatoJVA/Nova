from fastapi import FastAPI
import polars as pl
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="ML Nova API")

# Build a robust path to the data file
try:
    # Path to the root of the monorepo (up 3 levels from this file)
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_FILE_PATH = ROOT_DIR / "packages" / "machine-learning" / "data" / "processed" / "merged_selected.csv"
except NameError:
    # Fallback for environments where __file__ is not defined
    DATA_FILE_PATH = "packages/machine-learning/data/processed/merged_selected.csv"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the ML Nova API"}

@app.get("/data")
def get_data_info():
    try:
        if not Path(DATA_FILE_PATH).exists():
            return {"error": f"Data file not found at {DATA_FILE_PATH}"}
        df = pl.read_csv(DATA_FILE_PATH)
        return {
            "rows": df.height,
            "columns": df.width,
            "schema": df.schema
        }
    except Exception as e:
        return {"error": str(e)}

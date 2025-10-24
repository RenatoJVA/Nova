from abc import ABC, abstractmethod
from dataclasses import dataclass
import polars as pl
from pathlib import Path
from typing import Protocol
import logging
import hashlib

class DataReader(Protocol):
    def read(self) -> pl.DataFrame:
        ... 
        
# class MergeData(Protocol):
#     def merge(self, input_paths: list[Path], output_path: Path) -> None:
#         ...
        
@dataclass
class MergeConfig:
    base_dir: Path
    output_dir: Path
    log_file: Path
    delimiter: str = ','
    smiles: str = 'SMILES'
    
class BaseMergeData(ABC):
    def __init__(self, config: MergeConfig):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        
    @abstractmethod
    def merge(self, input_paths: list[Path], output_path: Path) -> pl.DataFrame:
        pass
    
class MergeData(BaseMergeData):
    def merge(self, input_paths: list[Path], output_path: Path) -> pl.DataFrame:
        dataframes = []
        for path in input_paths:
            try:
                df = pl.read_csv(path, separator=self.config.delimiter)
                source_name = path.stem.replace('_preprocessed', '')
                # Renombrar la columna canonical_smiles si existe
                if 'canonical_smiles' in df.columns:
                    df = df.rename({'canonical_smiles': 'SMILES'})
                df = df.with_columns(pl.lit(source_name).alias("source"))
                dataframes.append(df)
                logging.info(f"Loaded {len(df)} rows from {path.name}")
            except Exception as e:
                logging.error(f"Error reading {path}: {e}")

        if not dataframes:
            logging.error("No valid datasets loaded.")
            raise ValueError("No datasets to merge.")

        # Concatenar y procesar los DataFrames
        merged = pl.concat(dataframes, how="diagonal_relaxed")
        merged = merged.unique(subset=["SMILES"])
        merged = merged.with_columns(
            pl.col("SMILES").map_elements(
                lambda s: hashlib.sha1(s.encode()).hexdigest(), return_dtype=pl.Utf8
            ).alias("uid")
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged.write_csv(output_path)
        logging.info(f"Merged dataset saved to {output_path} with {len(merged)} rows.")
        return merged

def main():
    config = MergeConfig(
        base_dir=Path('data/pre_processed'),
        output_dir=Path('data/merged/'),
        log_file=Path('data/logs/merge.log'),
        delimiter=','
    )
    
    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.log_file.parent.mkdir(parents=True, exist_ok=True)
    print("CleanData module is set up.")
    
    merger = MergeData(config)
    input_paths = list(config.base_dir.glob("*_processed.csv"))
    output_path = config.output_dir / "merged_raw.csv"

    merged_df = merger.merge(input_paths, output_path)
    print(f"Merged dataset created: {len(merged_df)} rows, saved at {output_path}")
if __name__ == "__main__":
    main()
from abc import ABC, abstractmethod
from dataclasses import dataclass
import polars as pl
from pathlib import Path
from typing import Protocol
import logging

class CleanData(Protocol):
    def clean(self, input_path: Path, output_path: Path) -> pl.DataFrame:
        ...

@dataclass
class CleanConfig:
    base_dir: Path
    output_dir: Path
    log_file: Path
    delimiter: str = ','
    
    
class BaseDataAnalysis(ABC):
    def __init__(self, config: CleanConfig):
        self.config = config
    
    @abstractmethod
    def analysis(self, input_path: Path, output_path: Path) -> pl.DataFrame:
        pass
    
def _ensure_log_path(log_path: Path) -> Path:
    if log_path.exists() and log_path.is_dir():
        log_file = log_path / "processing.log"
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # log_file = log_path / f"data_analysis_{timestamp}.log"
    else:   
        log_file = log_path
        log_file.parent.mkdir(parents=True, exist_ok=True)
    return log_file

def setup_logger(log_path: Path) -> logging.Logger:
    log_file = _ensure_log_path(log_path)
    logger = logging.getLogger("data_processing")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger

def _df_info_str(df: pl.DataFrame, title: str = "") -> str:
    lines = []
    if title:
        lines.append(title)
    # shape
    rows, cols = df.shape
    lines.append(f"shape: {rows} rows, {cols} cols")
    # schema / dtypes
    lines.append("schema (column: dtype):")
    for col, dtype in df.schema.items():
        lines.append(f"  - {col}: {dtype}")
    # non-null counts
    lines.append("non-null counts:")
    for col in df.columns:
        try:
            non_null = int((~df[col].is_null()).sum())
        except Exception:
            # fallback: compute from height minus nulls
            try:
                nulls = int(df[col].is_null().sum())
                non_null = rows - nulls
            except Exception:
                non_null = "?"
        lines.append(f"  - {col}: {non_null}")
    # small sample
    try:
        # convert to pandas for a reliable string representation
        sample = df.head(5).to_pandas().to_string()
        lines.append("sample (first 5 rows):")
        lines.append(sample)
    except Exception:
        # fallback: use a simple rows() representation if pandas conversion fails
        try:
            rows = df.head(5).rows()
            lines.append("sample (first 5 rows):")
            lines.append(str(rows))
        except Exception:
            pass
    return "\n".join(lines)
    
class DataCleaner(BaseDataAnalysis):
    def analysis(self, input_path: Path, output_path: Path) -> pl.DataFrame:
        logger = logging.getLogger("data_processing")
        df = pl.read_csv(input_path, separator=self.config.delimiter)
        logger.info(_df_info_str(df, title=f"Before cleaning: {input_path.name}"))
        # Example cleaning operation: drop nulls
        cleaned_df = df.drop_nulls()
        logger.info(_df_info_str(cleaned_df, title=f"After cleaning: {input_path.name}"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_df.write_csv(output_path)
        return cleaned_df

class Processor:
    def __init__(self, config: CleanConfig):
        self.config = config
        self.cleaners = []
        # setup logger and ensure output dir exists
        setup_logger(self.config.log_file)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
    
    def add_cleaner(self, cleaner: CleanData) -> None:
        self.cleaners.append(cleaner)
    
    def process_all(self) -> list[pl.DataFrame]:
        results = []
        for cleaner in self.cleaners:
            input_path = self.config.base_dir / f"{cleaner.__class__.__name__}_input.csv"
            output_path = self.config.output_dir / f"{cleaner.__class__.__name__}_cleaned.csv"
            result = cleaner.analysis(input_path, output_path)
            results.append(result)
        return results
def main():
    config = CleanConfig(
        base_dir=Path('data/pre_proccessed'),
        output_dir=Path('/path/to/output'),
        log_file=Path('data/logs/'),
        delimiter=','
    )
    
    processor = Processor(config)
    # processor.add_cleaner(DataCleaner(config))
    
    results = processor.process_all()
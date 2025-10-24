from abc import ABC, abstractmethod
from dataclasses import dataclass
import polars as pl
from pathlib import Path
from typing import Protocol, List
import logging

class DataCleaner(Protocol):
    def clean(self, df: pl.DataFrame) -> pl.DataFrame:
        ...


@dataclass
class CleanConfig:
    base_dir: Path
    output_dir: Path
    log_file: Path
    delimiter: str = ","
    encoding: str = "utf-8"


class BaseDataCleaner(ABC):
    def __init__(self, config: CleanConfig):
        self.config = config
        self._setup_logging()

    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
        )

    @abstractmethod
    def clean(self, df: pl.DataFrame) -> pl.DataFrame:
        pass


class ColumnSelectorCleaner(BaseDataCleaner):
    def __init__(self, config: CleanConfig, keep_columns: List[str]):
        super().__init__(config)
        self.keep_columns = keep_columns

    def clean(self, df: pl.DataFrame) -> pl.DataFrame:
        existing_cols = [col for col in self.keep_columns if col in df.columns]
        missing_cols = set(self.keep_columns) - set(existing_cols)
        if missing_cols:
            logging.warning(f"ColumnSelectorCleaner: missing columns {missing_cols}")
        df = df.select(existing_cols)
        logging.info(f"ColumnSelectorCleaner: selected colummns {existing_cols}")
        return df


def main():
    config = CleanConfig(
        base_dir=Path("data/merged"),
        output_dir=Path("data/processed"),
        log_file=Path("data/logs/cleaning.log"),
    )

    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.log_file.parent.mkdir(parents=True, exist_ok=True)

    cleaner = ColumnSelectorCleaner(config, ["uid", "SMILES", "source"])

    input_path = config.base_dir / "merged_raw.csv"
    output_path = config.output_dir / "merged_selected.csv"

    df = pl.read_csv(input_path)
    cleaned_df = cleaner.clean(df)
    cleaned_df.write_csv(output_path)


if __name__ == "__main__":
    main()

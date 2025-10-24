from abc import ABC, abstractmethod
import pandas as pd
from rdkit import Chem
from rdkit import RDLogger
import logging
from dataclasses import dataclass
from typing import Protocol, List
from pathlib import Path

class MoleculeReader(Protocol):
    def read_molecules(self) -> pd.DataFrame:
        ...

class MoleculeConverter(Protocol):
    def convert(self, input_path: Path, output_path: Path) -> None:
        ...

@dataclass
class DataConfig:
    base_dir: Path
    output_dir: Path
    log_file: Path
    columns: List[str]
    delimiter: str = '\t'

class BaseMoleculeReader(ABC):
    def __init__(self, config: DataConfig):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
    
    @abstractmethod
    def read_molecules(self) -> pd.DataFrame:
        pass


class LotusReader(BaseMoleculeReader):
    def read_molecules(self) -> pd.DataFrame:
        input_file = self.config.base_dir / 'LOTUS_DB.smi'
        return pd.read_csv(
            input_file,
            sep=self.config.delimiter,
            header=None,
            names=self.config.columns
        )

class TTDConverter(BaseMoleculeReader):
    def __init__(self, config: DataConfig):
        super().__init__(config)
        RDLogger.DisableLog('rdApp.*') # type: ignore
        
    def read_molecules(self) -> pd.DataFrame:
        input_file = self.config.base_dir / 'TTD_DB.sdf'
        # output_file = self.config.output_dir / 'TTD_DB.csv'
        
        molecules = []
        sppl = Chem.SDMolSupplier(str(input_file))
        
        for idx, mol in enumerate(sppl):
            try:
                if mol is not None:
                    smi = Chem.MolToSmiles(mol)
                    name = mol.GetProp("_Name")
                    molecules.append({'SMILES': smi, 'ID': name})
                else:
                    logging.error(f"Failed to process molecule at index {idx}")
            except Exception as e:
                logging.error(f"Error processing molecule at index {idx}: {str(e)}")
        
        return pd.DataFrame(molecules)

class MoveData(BaseMoleculeReader):
    def read_molecules(self) -> pd.DataFrame:
        input_file = self.config.base_dir / 'COCONUT_DB.csv'
        return pd.read_csv(
            input_file,
        )

class MoleculeProcessor:
    def __init__(self, config: DataConfig):
        self.config = config
        self.readers: List[BaseMoleculeReader] = []
        
    def add_reader(self, reader: BaseMoleculeReader) -> None:
        self.readers.append(reader)
    
    def process_all(self) -> List[pd.DataFrame]:
        return [reader.read_molecules() for reader in self.readers]
    
    def save_results(self, dataframes: List[pd.DataFrame], filenames: List[str]) -> None:
        for df, filename in zip(dataframes, filenames):
            output_path = self.config.output_dir / filename
            df.to_csv(output_path, index=False)

def main():
    # Configuración
    config = DataConfig(
        base_dir=Path('data/base'),
        output_dir=Path('data/pre_processed'),
        log_file=Path('data/logs/conversion_errors.log'),
        columns=['SMILES', 'ID']
    )
    
    # Crear directorios si no existen
    config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializar procesador
    processor = MoleculeProcessor(config)
    
    # Agregar lectores
    processor.add_reader(LotusReader(config))
    processor.add_reader(TTDConverter(config))
    processor.add_reader(MoveData(config))
    
    # Procesar y guardar resultados
    results = processor.process_all()
    processor.save_results(results, ['lotus_processed.csv', 'ttd_processed.csv', 'coconut_processed.csv'])

if __name__ == "__main__":
    main()
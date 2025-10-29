#!/usr/bin/env python3
"""
Script para combinar los resultados de RMSD, RMSF y MMPBSA en un solo resumen.
Autor: CIIM - Renato Valencia
"""

import os
import pandas as pd
from typing import Optional

# === Funciones auxiliares ===

def load_data(file_path: str) -> Optional[pd.DataFrame]:
    """Carga un archivo CSV y devuelve un DataFrame, o None si falla."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encuentra el archivo {file_path}")
        
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error al cargar {file_path}: {e}")
        return None


def clean_ligand_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza los nombres de la columna 'ligand' eliminando sufijos no deseados."""
    if "ligand" not in df.columns:
        return df

    df = df.copy()
    df["ligand"] = (
        df["ligand"]
        .str.replace("-rmsd", "", regex=False)
        .str.replace("-rmsf", "", regex=False)
        .str.replace("_RESULTS_MMPBSA", "", regex=False)
        .str.strip()
    )
    return df


def merge_data(rmsd_df: pd.DataFrame, rmsf_df: pd.DataFrame, mmpbsa_df: pd.DataFrame) -> pd.DataFrame:
    """Fusiona los tres DataFrames en uno solo usando la columna 'ligand'."""
    try:
        print("Columnas originales detectadas:")
        print(f"RMSD → {rmsd_df.columns.tolist()}")
        print(f"RMSF → {rmsf_df.columns.tolist()}")
        print(f"MMPBSA → {mmpbsa_df.columns.tolist()}")

        # Renombrar columnas según su origen
        rmsd_rename = {
            'Media RMSD (nm)': 'RMSD_mean',
            'Desv. Est. RMSD (nm)': 'RMSD_std',
            'Desv. Est. (nm)': 'RMSD_std'
        }
        rmsd_df = rmsd_df.rename(columns={k: v for k, v in rmsd_rename.items() if k in rmsd_df.columns})

        rmsf_rename = {
            'mean_rmsf': 'RMSF_mean',
            'std_rmsf': 'RMSF_std',
            'Media RMSF (nm)': 'RMSF_mean',
            'Desv. Est. RMSF (nm)': 'RMSF_std'
        }
        rmsf_df = rmsf_df.rename(columns={k: v for k, v in rmsf_rename.items() if k in rmsf_df.columns})

        # Fusionar por 'ligand'
        merged = pd.merge(rmsd_df, rmsf_df, on="ligand", how="outer")
        merged = pd.merge(merged, mmpbsa_df, on="ligand", how="outer")

        # Columnas requeridas
        required_columns = [
            'ligand',
            'RMSD_mean', 'RMSD_std',
            'RMSF_mean', 'RMSF_std',
            'VDWAALS_mean', 'VDWAALS_std',
            'EEL_mean', 'EEL_std',
            'EGB_mean', 'EGB_std',
            'ESURF_mean', 'ESURF_std',
            'TOTAL_mean', 'TOTAL_std'
        ]

        missing = [c for c in required_columns if c not in merged.columns]
        if missing:
            raise ValueError(f"Faltan columnas requeridas: {missing}")

        merged = merged[required_columns]
        merged = merged.sort_values(by="ligand").round(6)

        return merged

    except Exception as e:
        print(f"Error al combinar datos: {e}")
        print(f"Columnas RMSD: {rmsd_df.columns.tolist()}")
        print(f"Columnas RMSF: {rmsf_df.columns.tolist()}")
        print(f"Columnas MMPBSA: {mmpbsa_df.columns.tolist()}")
        return pd.DataFrame()


# === Función principal ===

def main():
    """Punto de entrada principal."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    rmsd_file = os.path.join(results_dir, "rmsd_summary.csv")
    rmsf_file = os.path.join(results_dir, "rmsf_summary.csv")
    mmpbsa_file = os.path.join(results_dir, "mmpbsa_summary.csv")
    output_file = os.path.join(results_dir, "data_summary.csv")

    print("Combinando archivos:")
    print(f"• RMSD → {rmsd_file}")
    print(f"• RMSF → {rmsf_file}")
    print(f"• MMPBSA → {mmpbsa_file}")
    print(f"• Salida → {output_file}")

    rmsd_df = load_data(rmsd_file)
    rmsf_df = load_data(rmsf_file)
    mmpbsa_df = load_data(mmpbsa_file)

    if any(df is None for df in [rmsd_df, rmsf_df, mmpbsa_df]):
        print("No se pudieron cargar todos los archivos requeridos.")
        return

    # Normalizar identificadores (ligand)
    for df in (rmsd_df, rmsf_df, mmpbsa_df):
        df = clean_ligand_names(df)

    # Asegurar consistencia
    rmsd_df = clean_ligand_names(rmsd_df)
    rmsf_df = clean_ligand_names(rmsf_df)
    mmpbsa_df = clean_ligand_names(mmpbsa_df)

    merged_df = merge_data(rmsd_df, rmsf_df, mmpbsa_df)

    if merged_df.empty:
        print("No se pudieron combinar los datos correctamente.")
        return

    merged_df.to_csv(output_file, index=False)
    print(f"\Resumen de datos combinados guardado en {output_file}\n")
    print(merged_df.head(10))


if __name__ == "__main__":
    main()


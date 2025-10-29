#!/usr/bin/env python3
"""
Script para calcular la media y desviación estándar de MMPBSA de trayectorias moleculares.
Agrupa los resultados por proteína y ligando.
"""

import os
import pandas as pd
import glob
from typing import Dict

def process_mmpbsa_file(file_path: str) -> Dict[str, float]:
    try:
        start_line = -1
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if "Delta Energy Terms" in line:
                    start_line = i + 1
                    break
        
        if start_line == -1:
            print(f"Advertencia: 'Delta Energy Terms' no encontrado en {file_path}. Se intentará leer desde el principio.")
            start_line = 0

        # Leer datos
        df = pd.read_csv(file_path, skiprows=start_line)
        df.columns = [col.strip().replace('#', '').strip() for col in df.columns]

        if df.empty:
            print(f"Advertencia: DataFrame vacío para {file_path}")
            return None

        # Nombre base del archivo
        filename = os.path.basename(file_path).replace('_RESULTS_MMPBSA.csv', '')

        # Extraer ligando y proteína
        try:
            ligand, protein = filename.split('-', 1)
        except ValueError:
            ligand, protein = filename, "unknown"

        return {
            "protein": protein,
            "ligand": ligand,
            'VDWAALS_mean': df['VDWAALS'].mean() if 'VDWAALS' in df.columns else pd.NA,
            'VDWAALS_std': df['VDWAALS'].std() if 'VDWAALS' in df.columns else pd.NA,
            'EEL_mean': df['EEL'].mean() if 'EEL' in df.columns else pd.NA,
            'EEL_std': df['EEL'].std() if 'EEL' in df.columns else pd.NA,
            'EGB_mean': df['EGB'].mean() if 'EGB' in df.columns else pd.NA,
            'EGB_std': df['EGB'].std() if 'EGB' in df.columns else pd.NA,
            'ESURF_mean': df['ESURF'].mean() if 'ESURF' in df.columns else pd.NA,
            'ESURF_std': df['ESURF'].std() if 'ESURF' in df.columns else pd.NA,
            'TOTAL_mean': df['TOTAL'].mean() if 'TOTAL' in df.columns else pd.NA,
            'TOTAL_std': df['TOTAL'].std() if 'TOTAL' in df.columns else pd.NA
        }

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        filename = os.path.basename(file_path).replace('_RESULTS_MMPBSA.csv', '')
        try:
            ligand, protein = filename.split('-', 1)
        except ValueError:
            ligand, protein = filename, "unknown"

        return {
            "protein": protein,
            "ligand": ligand,
            'VDWAALS_mean': pd.NA,
            'VDWAALS_std': pd.NA,
            'EEL_mean': pd.NA,
            'EEL_std': pd.NA,
            'EGB_mean': pd.NA,
            'EGB_std': pd.NA,
            'ESURF_mean': pd.NA,
            'ESURF_std': pd.NA,
            'TOTAL_mean': pd.NA,
            'TOTAL_std': pd.NA
        }

def main():
    """Función principal para procesar los archivos MMPBSA."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'mmpbsa_data')
    output_dir = os.path.join(base_dir, 'results')
    output_file = os.path.join(output_dir, 'mmpbsa_summary.csv')
    
    files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    if not files:
        print(f"No se encontraron archivos .csv en {data_dir}")
        return
        
    all_stats = []
    for file in sorted(files):
        stats = process_mmpbsa_file(file)
        if stats:
            all_stats.append(stats)
            print(f"Ligando: {stats['ligand']}, Proteína: {stats['protein']}, "
                  f"Energía total media: {stats['TOTAL_mean']:.4f} kcal/mol, Desv: {stats['TOTAL_std']:.4f}")

    if not all_stats:
        print("No se pudieron procesar las estadísticas de ningún archivo.")
        return

    # Crear resumen ordenado
    summary_df = pd.DataFrame(all_stats)
    summary_df = summary_df.sort_values(['protein', 'ligand'])
    summary_df = summary_df.round(4)

    os.makedirs(output_dir, exist_ok=True)
    
    summary_df.to_csv(output_file, index=False, float_format='%.4f')
    print(f"\nResumen de MMPBSA guardado en {output_file}")
    print(summary_df)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Script para calcular la media y desviación estándar de RMSF de trayectorias moleculares.
Lee archivos .xvg de GROMACS y genera un resumen estadístico agrupado por proteína y ligando.
"""

import os
import glob
import numpy as np
import pandas as pd
from typing import Dict

def process_rmsf_file(file_path: str) -> Dict[str, float]:
    """
    Procesa un archivo RMSF y calcula estadísticas.
    
    Args:
        file_path: Ruta al archivo .xvg
        
    Returns:
        Diccionario con nombre de proteína, ligando y estadísticas RMSF
    """
    try:
        # Cargar datos, ignorando líneas con # o @
        data = np.loadtxt(file_path, comments=('#', '@'))
        
        # Calcular estadísticas de la segunda columna
        mean_rmsf = np.mean(data[:, 1])
        std_rmsf = np.std(data[:, 1])
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        mean_rmsf, std_rmsf = np.nan, np.nan

    # Obtener nombre base sin extensión
    filename = os.path.basename(file_path).replace('.xvg', '')

    # Quitar sufijo '-rmsf' si está presente
    if filename.endswith('-rmsf'):
        filename = filename.replace('-rmsf', '')

    # Dividir nombre en ligando y proteína
    try:
        ligand, protein = filename.split('-', 1)
    except ValueError:
        ligand, protein = filename, "unknown"

    return {
        "protein": protein,
        "ligand": ligand,
        "mean_rmsf": float(mean_rmsf),
        "std_rmsf": float(std_rmsf)
    }

def main():
    """Función principal del script"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(base_dir, 'data', 'rmsf_data')
    files = glob.glob(os.path.join(folder_path, '*.xvg'))
    
    if not files:
        print(f"No se encontraron archivos .xvg en {folder_path}")
        return
    
    results = []
    for file in files:
        result = process_rmsf_file(file)
        results.append(result)
        try:
            print(f'Ligando: {result["ligand"]}, Proteína: {result["protein"]}, '
                  f'Media RMSF: {result["mean_rmsf"]:.4f} nm, Desv. Est.: {result["std_rmsf"]:.4f} nm')
        except:
            print(f'Ligando: {result["ligand"]}, Proteína: {result["protein"]}, '
                  f'Media RMSF: nan nm, Desv. Est.: nan nm')
    
    # Crear DataFrame
    summary_df = pd.DataFrame(results)
    
    # Ordenar por proteína y ligando
    summary_df = summary_df.sort_values(['protein', 'ligand'])
    
    print("\nResumen de resultados:")
    print(summary_df)
    
    # Crear directorio de resultados si no existe
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Guardar archivo CSV
    output_file = os.path.join(results_dir, 'rmsf_summary.csv')
    summary_df.to_csv(output_file, index=False)
    print(f"\nResumen guardado en {output_file}")

if __name__ == "__main__":
    main()


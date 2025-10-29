#!/usr/bin/env python3
"""
Script para calcular la media y desviación estándar de RMSD de trayectorias moleculares.
Lee archivos .xvg de GROMACS y genera un resumen estadístico.
"""

import os
import glob
import pandas as pd
import numpy as np
from typing import Dict

def process_rmsd_file(file_path: str) -> Dict[str, float]:
    try:
        # Cargar datos, ignorando líneas de comentarios
        data = np.loadtxt(file_path, comments=('#', '@'))
        
        # Calcular estadísticas directamente de la segunda columna
        rmsd_mean = float(np.mean(data[:, 1]))
        rmsd_std = float(np.std(data[:, 1]))
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        rmsd_mean, rmsd_std = np.nan, np.nan
    
    # Obtener nombre base sin extensión
    filename = os.path.basename(file_path).replace('-rmsd.xvg', '')
    
    # Dividir el nombre en ligando y proteína
    try:
        ligand, protein = filename.split('-', 1)
    except ValueError:
        ligand, protein = filename, "unknown"
    
    return {
        "protein": protein,
        "ligand": ligand,
        "RMSD_mean": rmsd_mean,
        "RMSD_std": rmsd_std
    }

def main():
    """Función principal del script"""
    # Obtener rutas absolutas
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(base_dir, 'data', 'rmsd_data')
    files = glob.glob(os.path.join(folder_path, '*.xvg'))
    
    if not files:
        print(f"No se encontraron archivos .xvg en {folder_path}")
        return
    
    # Procesar archivos
    results = []
    for file in files:
        result = process_rmsd_file(file)
        results.append(result)
        print(f'Ligando: {result["ligand"]}, Proteína: {result["protein"]}, '
              f'Media RMSD: {result["RMSD_mean"]:.4f} nm, Desv. Est.: {result["RMSD_std"]:.4f} nm')
    
    # Crear DataFrame y ordenar por proteína y ligando
    summary_df = pd.DataFrame(results)
    summary_df = summary_df.sort_values(['protein', 'ligand'])
    
    # Redondear valores numéricos
    summary_df = summary_df.round(4)
    
    # Crear directorio de resultados si no existe
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Guardar archivo en el directorio de resultados
    output_file = os.path.join(results_dir, 'rmsd_summary.csv')
    summary_df.to_csv(output_file, index=False)
    print(f"\nResumen guardado en {output_file}")

if __name__ == "__main__":
    main()


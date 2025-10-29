#!/usr/bin/env python3
"""
Punto de entrada principal para el análisis de datos de dinámica molecular.
"""

import os
import sys
from typing import Optional, Dict, Any
import pandas as pd

# Añadir el directorio de scripts al path
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = os.getcwd()
SCRIPT_DIR = os.path.join(BASE_DIR, 'script')
if os.path.isdir(SCRIPT_DIR) and SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

def check_directory_structure() -> bool:
    """
    Verifica que la estructura de directorios necesaria existe.
    
    Returns:
        bool: True si la estructura es correcta, False en caso contrario
    """
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')
    results_dir = os.path.join(base_dir, 'results')
    
    # Verificar directorios de datos
    required_dirs = {
        'rmsd_data': os.path.join(data_dir, 'rmsd_data'),
        'rmsf_data': os.path.join(data_dir, 'rmsf_data'),
        'mmpbsa_data': os.path.join(data_dir, 'mmpbsa_data')
    }
    
    # Verificar que existe el directorio de resultados
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"Creado directorio de resultados: {results_dir}")
    
    for dir_name, dir_path in required_dirs.items():
        if not os.path.isdir(dir_path):
            print(f"Error: No se encuentra el directorio {dir_path}")
            return False
            
        # Verificar archivos según el tipo de directorio
        if dir_name == 'mmpbsa_data':
            files_csv = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            if not files_csv:
                print(f"Error: No se encontraron archivos .csv en {dir_path}")
                return False
        else:
            # Para rmsd_data y rmsf_data verificar archivos .xvg
            files = [f for f in os.listdir(dir_path) if f.endswith('.xvg')]
            if not files:
                print(f"Error: No se encontraron archivos .xvg en {dir_path}")
                return False
    
    return True

def run_analysis_module(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Ejecuta un módulo de análisis específico.
    
    Args:
        module_name: Nombre del módulo a ejecutar
        
    Returns:
        Dict con resultados del análisis o None si hay error
    """
    base_dir = os.path.dirname(__file__)
    results_dir = os.path.join(base_dir, 'results')
    
    # Asegurar que el directorio de resultados existe
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        if module_name == "rmsd":
            import script.mean_std_rmsd as mean_std_rmsd
            mean_std_rmsd.main()
            output_file = os.path.join(results_dir, 'rmsd_summary.csv')
            return {"status": "success", "file": output_file}
            
        elif module_name == "rmsf":
            import script.mean_std_rmsf as mean_std_rmsf
            mean_std_rmsf.main()
            output_file = os.path.join(results_dir, 'rmsf_summary.csv')
            return {"status": "success", "file": output_file}
        
        elif module_name == "mmpbsa":
            import script.mean_std_mmpbsa as mean_std_mmpbsa
            mean_std_mmpbsa.main()
            output_file = os.path.join(results_dir, 'mmpbsa_summary.csv')
            return {"status": "success", "file": output_file}
            
        elif module_name == "merge":
            import script.data_merge as data_merge
            data_merge.main()
            output_file = os.path.join(results_dir, 'data_summary.csv')
            return {"status": "success", "file": output_file}
            
    except Exception as e:
        print(f"Error ejecutando módulo {module_name}: {e}")
        print(f"Detalles del error: {str(e)}")
        return None
    
    return None

def validate_results(results: Dict[str, Any]) -> bool:
    """
    Valida los resultados del análisis.
    
    Args:
        results: Diccionario con información de resultados
        
    Returns:
        bool: True si los resultados son válidos, False en caso contrario
    """
    if results is None:
        print("Error: No se obtuvieron resultados")
        return False
        
    output_file = results.get("file")
    if not output_file:
        print("Error: No se especificó archivo de salida")
        return False
        
    if not os.path.exists(output_file):
        print(f"Error: No se encontró el archivo de resultados: {output_file}")
        return False
        
    try:
        df = pd.read_csv(output_file)
        if df.empty:
            print(f"Error: El archivo {output_file} está vacío")
            return False
        return True
    except Exception as e:
        print(f"Error leyendo {output_file}: {e}")
        return False

def main():
    """Función principal que coordina todo el análisis"""
    print("Iniciando análisis de dinámica molecular...")
    
    # Verificar estructura de directorios
    if not check_directory_structure():
        print("Error: La estructura de directorios no es correcta")
        sys.exit(1)
    
    # Ejecutar análisis RMSD
    print("\n1. Calculando estadísticas RMSD...")
    rmsd_results = run_analysis_module("rmsd")
    if not validate_results(rmsd_results):
        print("Error: Falló el análisis RMSD")
        sys.exit(1)
    
    # Ejecutar análisis RMSF
    print("\n2. Calculando estadísticas RMSF...")
    rmsf_results = run_analysis_module("rmsf")
    if not validate_results(rmsf_results):
        print("Error: Falló el análisis RMSF")
        sys.exit(1)
        
    # Ejecutar análisis MMPBSA
    print("\n3. Calculando estadísticas MMPBSA...")
    mmpbsa_results = run_analysis_module("mmpbsa")
    if not validate_results(mmpbsa_results):
        print("Error: Falló el análisis MMPBSA")
        sys.exit(1)
    
    # Combinar resultados
    print("\n4. Combinando resultados...")
    merge_results = run_analysis_module("merge")
    if not validate_results(merge_results):
        print("Error: Falló la combinación de resultados")
        sys.exit(1)
    
    print("\nAnálisis completado exitosamente!")
    print("Los resultados se han guardado en:")
    print(f"- Estadísticas RMSD: {rmsd_results['file']}")
    print(f"- Estadísticas RMSF: {rmsf_results['file']}")
    print(f"- Estadísticas MMPBSA: {mmpbsa_results['file']}")
    print(f"- Resumen combinado: {merge_results['file']}")

if __name__ == "__main__":
    main()
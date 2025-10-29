#!/usr/bin/env python3
"""
Punto de entrada principal para el análisis de datos de dinámica molecular.
Controla la ejecución de los módulos RMSD, RMSF, MMPBSA y su combinación final.
"""

import os
import sys
import pandas as pd
from typing import Optional, Dict, Any


# === CONFIGURACIÓN DE RUTAS ===
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

SCRIPT_DIR = os.path.join(BASE_DIR, "script")
if os.path.isdir(SCRIPT_DIR) and SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)


# === FUNCIONES AUXILIARES ===

def check_directory_structure() -> bool:
    """
    Verifica que la estructura de directorios necesaria existe y contiene datos válidos.
    """
    data_dir = os.path.join(BASE_DIR, "data")
    results_dir = os.path.join(BASE_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    required_dirs = {
        "rmsd_data": os.path.join(data_dir, "rmsd_data"),
        "rmsf_data": os.path.join(data_dir, "rmsf_data"),
        "mmpbsa_data": os.path.join(data_dir, "mmpbsa_data")
    }

    for name, path in required_dirs.items():
        if not os.path.isdir(path):
            print(f"Error: No se encuentra el directorio requerido: {path}")
            return False

        if name == "mmpbsa_data":
            files = [f for f in os.listdir(path) if f.endswith(".csv")]
        else:
            files = [f for f in os.listdir(path) if f.endswith(".xvg")]

        if not files:
            print(f"Error: No se encontraron archivos válidos en {path}")
            return False

    print("Estructura de directorios verificada correctamente.")
    return True


def run_analysis_module(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Ejecuta un módulo de análisis específico según su nombre.
    """
    results_dir = os.path.join(BASE_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    try:
        if module_name == "rmsd":
            import script.mean_std_rmsd as mod
            output = os.path.join(results_dir, "rmsd_summary.csv")

        elif module_name == "rmsf":
            import script.mean_std_rmsf as mod
            output = os.path.join(results_dir, "rmsf_summary.csv")

        elif module_name == "mmpbsa":
            import script.mean_std_mmpbsa as mod
            output = os.path.join(results_dir, "mmpbsa_summary.csv")

        elif module_name == "merge":
            import script.data_merge as mod
            output = os.path.join(results_dir, "data_summary.csv")

        else:
            print(f"Módulo desconocido: {module_name}")
            return None

        print(f"Ejecutando módulo: {module_name}")
        mod.main()

        return {"status": "success", "file": output}

    except Exception as e:
        print(f"Error ejecutando módulo '{module_name}': {e}")
        return None


def validate_results(result: Optional[Dict[str, Any]]) -> bool:
    """
    Valida si el resultado de un módulo de análisis es correcto.
    """
    if not result:
        print("Error: No se devolvió información del módulo.")
        return False

    file_path = result.get("file")
    if not file_path or not os.path.exists(file_path):
        print(f"Error: No se encontró el archivo de salida esperado: {file_path}")
        return False

    try:
        df = pd.read_csv(file_path)
        if df.empty:
            print(f"El archivo {os.path.basename(file_path)} está vacío.")
            return False
        print(f"Resultados válidos: {os.path.basename(file_path)} ({len(df)} filas)")
        return True
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return False


# === EJECUCIÓN PRINCIPAL ===

def main():
    print("\nIniciando análisis de dinámica molecular...\n")

    # Verificar estructura
    if not check_directory_structure():
        print("Estructura de directorios incorrecta. Abortando.")
        sys.exit(1)

    # Secuencia de módulos
    modules = ["rmsd", "rmsf", "mmpbsa", "merge"]
    results: Dict[str, Dict[str, Any]] = {}

    for i, module_name in enumerate(modules, start=1):
        print(f"\n{i}. Ejecutando módulo '{module_name.upper()}'...")
        result = run_analysis_module(module_name)
        if not validate_results(result):
            print(f"Falló el módulo {module_name.upper()}. Abortando.")
            sys.exit(1)
        results[module_name] = result

    # Resumen final
    print("\nAnálisis completado exitosamente.\n")
    print("Archivos generados:")
    for key, value in results.items():
        print(f" - {key.upper():<8}: {value['file']}")

    print("\nTodos los resultados están listos en el directorio 'results'.")


if __name__ == "__main__":
    main()


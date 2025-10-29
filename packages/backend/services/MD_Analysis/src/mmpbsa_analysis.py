import os
import subprocess
import yaml
import re 

config_path = "../utils/mmpbsa_config.yaml"

# with open(config_path, 'r') as f:
#         for i in range(25):
#             line = f.readline()
#             if not line:
#                 break
#             print(line.strip())

with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)
    
NP = config.get("NP", 4)
BASEDIR = config.get("BASEDIR", ".")
INTERVAL = config.get("INTERVAL", 250)
GROUPS = config.get("GROUPS", [1, 13])
TPR_PREFIX = config.get("TPR_PREFIX", "sdm.tpr")
XTC_SUFFIX = config.get("XTC_SUFFIX", "-noPBC.xtc")
NOGUI = config.get("NOGUI", "-nogui")
CLEAN = config.get("CLEAN", "--clean")

# ================================
# Funciones auxiliares
# ================================

def run_command(cmd, cwd=None):
    """Ejecuta un comando en la terminal y maneja errores."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {cmd}")
        print(e.stderr)
        raise

def edit_mmpbsa_interval(filepath, new_interval):
    """Edita el archivo de entrada de MMPBSA para cambiar el intervalo de frames."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe.")
    with open(filepath, 'r') as file:
        lines = file.readlines()
    with open(filepath, 'w') as file:
        for line in lines:
            if line.strip().startswith("interval"):
                file.write(f"interval = {new_interval}\n")
            else:
                file.write(line)
    return True


def extract_summary(compact_file, output_file):
    if not os.path.isfile(compact_file):
        raise FileNotFoundError(f"El archivo {compact_file} no existe.")
    with open(compact_file, 'r') as f:
        lines = f.readlines()
    
    capture = False
    dash_count = 0
    with open(output_file, 'w') as out:
        for line in lines:
            if "Delta (Complex - Receptor - Ligand):" in line:
                capture = True
                out.write(line)
                continue
            if capture:
                out.write(line)
                if re.match(r"^-+$", line.strip()):
                    dash_count += 1
                else:
                    dash_count = 0
                if dash_count == 2:
                    break
    print(f"Resumen extraído a {output_file}")
    
# ================================
# Script principal
# ================================
for dir_name in os.listdir(BASEDIR):
    dir_path = os.path.join(BASEDIR, dir_name)
    if not os.path.isdir(dir_path):
        continue
    
    print(f"Procesando directorio: {dir_path}")
    tpr = f"sdm-{dir_name}{TPR_PREFIX}"
    xtc = f"sdm-{dir_name}{XTC_SUFFIX}"
    topfile = f"{dir_name}{TOP_SUFFIX}"
    out_dat = f"{dir_name}_RESULTS_MMPBSA.dat"
    out_CSV = f"{dir_name}_RESULTS_MMPBSA.csv"
    
# Crear el input del mmpbsa    
run_command("gmx_MMPBSA --create_inputh", cwd=dir_path)
mmpbsa_file = os.path.join(dir_path, "mmpbsa.in")
if not os.path.isfile(mmpbsa_file):
    print(f"No se encontró el archivo mmpbsa.in en {dir_path}, saltando...")

# Editar el intervalo en el archivo mmpbsa.in
edit_mmpbsa_interval(mmpbsa_file, INTERVAL)

cmd = f"mpirun -np {NP} gmx_MMPBSA {NOGUI} -O -i mmpbsa.in -cs {tpr} -ci index.ndx -cg {','.join(map(str, GROUPS))} -ct {xtc} -o {out_dat} -eo {dir_name}_ENERGY_MMPBSA.dat -pf {topfile} {CLEAN}"
run_command(cmd, cwd=dir_path)


# # Extraer resumen
# compact_file = os.path.join(dir_path, "COMPACT_MMXSA_RESULTS.mmxsa")
# output_txt = os.path.join(dir_path, f"{dir_name}_MMPBSA_SUMMARY.txt")
# extract_summary(compact_file, output_txt)

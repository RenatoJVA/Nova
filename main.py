import os
import sys

from nova.src import DataStructure
from nova.src import CleanData
# from nova.src import DataProcessing
# from nova.src import DataAnalysis
# from nova.src import ModelTraining


# === Path setup ===
try: 
    _base_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _base_dir = os.getcwd()

BASE_DIR = _base_dir

SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path and SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)
    
def directory_setup(BASE_DIR: str) -> bool:
    
    data_dir = os.path.join(BASE_DIR, 'data')
    
    required_subdirs = ['base', 'pre_processed','processed', 'results', 'models', 'logs']
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        for subdir in required_subdirs:
            subdir_path = os.path.join(data_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
        
        return True
    except Exception as e:
        print(f"Error creating directories: {str(e)}")
        return False

def main():
    if directory_setup(BASE_DIR):
        print("Directory structure set up successfully.")
    else:
        print("Failed to set up directory structure.")
        
    DataStructure.main()
    CleanData.main()

if __name__ == "__main__":
    main()

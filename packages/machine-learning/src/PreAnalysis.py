import polars as pl
import time

lotus_df = pl.read_csv('data/pre_processed/lotus_processed.csv')
ttd_df = pl.read_csv('data/pre_processed/ttd_processed.csv')
coconut_df = pl.read_csv('data/pre_processed/coconut_processed.csv')
merge_df = pl.read_csv('data/merged/merged_raw.csv')

# headers = coconut_df.columns
# print(headers)

if 'canonical_smiles' in coconut_df.columns:
    coconut_df = coconut_df.rename({'canonical_smiles': 'SMILES'})
    print("Columna 'canonical_smiles' renombrada a 'SMILES' en coconut_df.")
    
dfs = {
    'lotus': lotus_df,
    'ttd': ttd_df,
    'coconut': coconut_df,
}


dfs_cleaned = {}
smiles_sets = {}

print("Starting pre-analysis...")
print("\n------- Cleaning Data---------")

for name, df in dfs.items():
    start_time = time.time()
    print(f"\nProcessing {name} dataset...")
    
    
    dfs_cleaned_temp = df.drop_nulls(subset=['SMILES'])
    dfs_cleaned[name] = dfs_cleaned_temp
    smiles_sets[name] = set(dfs_cleaned_temp['SMILES'].to_list())
    end_time = time.time()
    print(f"Original size: {df.height}, Cleaned size: {dfs_cleaned_temp.height}")
    
lotus_df, ttd_df, coconut_df = dfs_cleaned['lotus'], dfs_cleaned['ttd'], dfs_cleaned['coconut']

for name, df in dfs.items():
    complete_df = df.drop_nulls()  # elimina filas con algún valor nulo en cualquier columna
    num_complete = complete_df.height
    total = df.height
    print(f"{name}: {num_complete}/{total} filas con información completa ({(num_complete/total)*100:.2f}%)")

#merge_df.glimpse()
print("\n------- Merged Data Info---------")
print(f"Merge DataFrame has {merge_df.height} rows and {merge_df.width} columns.")
print(merge_df.schema)
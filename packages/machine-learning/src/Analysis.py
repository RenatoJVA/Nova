import pandas as pd
import polars as pl


lotus_df = pd.read_csv('data/pre_processed/lotus_processed.csv')
ttd_df = pd.read_csv('data/pre_processed/ttd_processed.csv')
coconut_df = pd.read_csv('data/pre_processed/coconut_processed.csv')

print(lotus_df.info())
print(ttd_df.info())
print(coconut_df.info())
#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Ruta del archivo con las métricas
data_path = "../results/data_summary.csv"


# Columnas que quieres incluir en el PCA
features = ['RMSD_mean', 'RMSD_std', 'RMSF_mean', 'RMSF_std']

# Cargar datos
df = pd.read_csv(data_path)

# Seleccionar solo las columnas que existan en el CSV
features = [f for f in features if f in df.columns]

# Matriz de datos: rellenar NaN con la media
X = df[features].fillna(df[features].mean())

# Escalar datos (muy importante para PCA)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA con 2 componentes principales
pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

# Guardar resultados en el DataFrame
df["PC1"], df["PC2"] = pca_result[:, 0], pca_result[:, 1]

# Imprimir varianza y loadings
print("Explained variance ratio:", pca.explained_variance_ratio_)
loadings = pd.DataFrame(pca.components_.T, index=features, columns=["PC1","PC2"])
print(loadings)
def run_pca_clustering(df, features, n_clusters=3, results_dir="."):
    # Matriz de datos: rellenar NaN con la media
    X = df[features].fillna(df[features].mean())

    # Escalar datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA con 2 componentes principales
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)

    # Guardar resultados en el DataFrame
    df["PC1"], df["PC2"] = pca_result[:, 0], pca_result[:, 1]

    # Imprimir varianza y loadings
    print("Explained variance ratio:", pca.explained_variance_ratio_)
    loadings = pd.DataFrame(pca.components_.T, index=features, columns=["PC1","PC2"])
    print(loadings)

    # Clustering en el espacio PCA
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df["cluster"] = kmeans.fit_predict(df[["PC1","PC2"]])

    # Guardar resultados
    output_file = os.path.join(results_dir, "pca_results.csv")
    df.to_csv(output_file, index=False)

    # Graficar con colores por cluster
    plt.figure(figsize=(7,5))
    sc = plt.scatter(df["PC1"], df["PC2"], c=df["cluster"], cmap="tab10", alpha=0.8)
    plt.colorbar(sc, label="Cluster")
    if "dynamic" in df.columns:
        for i, name in enumerate(df["dynamic"]):
            plt.text(df["PC1"][i], df["PC2"][i], name, fontsize=7)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("PCA con Clustering K-means")
    plt.tight_layout()
    plot_file = os.path.join(results_dir, "pca_clusters.png")
    plt.savefig(plot_file, dpi=300)
    plt.show()


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'results', 'data_summary.csv')
    # files = glob.glob.join(data_path, '*.csv')
    if not os.path.exists(data_path):
        print(f"El archivo {data_path} no existe.")
        return
    

    # Crear directorio de resultados si no existe
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Guardar archivo en el directorio de resultados
    output_file = os.path.join(results_dir, 'pca_results.csv')
    print(f"\nResumen guardado en {output_file}")
    
    run_pca_clustering(df, features, n_clusters=2, results_dir=results_dir)

if __name__ == "__main__":
    main()
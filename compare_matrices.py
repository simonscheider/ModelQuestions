from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def flatten_upper_triangle(matrix: np.ndarray) -> np.ndarray:
    """Return the upper triangle of a square matrix, excluding the diagonal."""
    idx = np.triu_indices_from(matrix, k=1)
    return matrix[idx]


def compare_nearest_neighbors(df_a: pd.DataFrame, df_b: pd.DataFrame):
    """
    Compare nearest neighbor of each dataset in two distance matrices.
    Returns a dataframe showing whether both matrices pick the same nearest neighbor.
    """
    labels = list(df_a.index)
    rows = []

    for label in labels:
        row_a = df_a.loc[label].astype(float).copy()
        row_b = df_b.loc[label].astype(float).copy()

        row_a[label] = np.inf
        row_b[label] = np.inf

        nn_a = row_a.idxmin()
        nn_b = row_b.idxmin()

        rows.append({
            "dataset": label,
            "ted_nearest": nn_a,
            "meta_nearest": nn_b,
            "same_nearest": nn_a == nn_b,
            "ted_distance": float(row_a.min()),
            "meta_distance": float(row_b.min()),
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    ted_path = Path("results_ted/ted_matrix.csv")
    meta_path = Path("results_meta/metadata_matrix.csv")
    output_dir = Path("results_comparison")
    output_dir.mkdir(exist_ok=True)

    # Load matrices
    df_ted = pd.read_csv(ted_path, index_col=0)
    df_meta = pd.read_csv(meta_path, index_col=0)

    if list(df_ted.index) != list(df_meta.index):
        raise ValueError("Row labels/order do not match between TED and metadata matrices.")
    if list(df_ted.columns) != list(df_meta.columns):
        raise ValueError("Column labels/order do not match between TED and metadata matrices.")

    labels = list(df_ted.index)

    print("Datasets used in both matrices:")
    for i, label in enumerate(labels):
        print(f"{i}: {label}")

    D_ted = df_ted.values.astype(float)
    D_meta = df_meta.values.astype(float)

    ted_vals = flatten_upper_triangle(D_ted)
    meta_vals = flatten_upper_triangle(D_meta)

    # Spearman rank correlation
    corr, pval = spearmanr(ted_vals, meta_vals)

    print("\nMatrix comparison:")
    print(f"Spearman correlation: {corr:.4f}")
    print(f"p-value: {pval:.4f}")

    with open(output_dir / "matrix_correlation.txt", "w", encoding="utf-8") as f:
        f.write(f"Spearman correlation: {corr:.6f}\n")
        f.write(f"p-value: {pval:.6f}\n")

    # Scatter plot
    plt.figure(figsize=(7, 6))
    plt.scatter(ted_vals, meta_vals)
    plt.xlabel("Tree Edit Distance")
    plt.ylabel("Metadata Distance")
    plt.title("TED vs metadata distance")
    plt.tight_layout()
    plt.savefig(output_dir / "ted_vs_metadata_scatter.png", dpi=300, bbox_inches="tight")
    plt.show()

    # Nearest-neighbor comparison
    nn_df = compare_nearest_neighbors(df_ted, df_meta)
    nn_df.to_csv(output_dir / "nearest_neighbor_comparison.csv", index=False)

    print("\nNearest-neighbor comparison:")
    print(nn_df)

    agreement = nn_df["same_nearest"].mean()
    print(f"\nNearest-neighbor agreement: {agreement:.2%}")

    # Optional: print a few pairwise comparisons
    pair_df = pd.DataFrame({
        "ted_distance": ted_vals,
        "meta_distance": meta_vals,
    })
    pair_df.to_csv(output_dir / "pairwise_distances.csv", index=False)
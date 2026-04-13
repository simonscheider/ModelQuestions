# metadata_distance_demo.py

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from modelQuestionGrammar import survey_questions


def get_labels_from_survey(survey_items):
    """Use dataset_id as label for each correct question, in survey order."""
    return [q["dataset_id"] for q in survey_items if q.get("is_correct")]


def save_matrix_csv(D, labels, filename):
    df = pd.DataFrame(D, index=labels, columns=labels)
    df.to_csv(filename)
    return df


def plot_heatmap(D, labels, title, output_path=None):
    plt.figure(figsize=(10, 8))
    plt.imshow(D, interpolation="nearest")
    plt.colorbar(label="Metadata distance")
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.yticks(range(len(labels)), labels)
    plt.title(title)
    plt.tight_layout()

    if output_path is not None:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.show()


def summarize_pairs(D, labels, top_n=5):
    """Return closest and farthest dataset pairs."""
    pairs = []
    n = len(labels)

    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((labels[i], labels[j], float(D[i, j])))

    pairs_sorted = sorted(pairs, key=lambda x: x[2])
    closest = pairs_sorted[:top_n]
    farthest = pairs_sorted[-top_n:]

    return closest, farthest


def print_pair_summary(closest, farthest):
    print("\nClosest metadata pairs:")
    for a, b, d in closest:
        print(f"{a} <-> {b}: distance = {d:.4f}")

    print("\nMost distant metadata pairs:")
    for a, b, d in reversed(farthest):
        print(f"{a} <-> {b}: distance = {d:.4f}")


if __name__ == "__main__":
    # Use the same dataset labels/order as the TED script
    correct_items = [q for q in survey_questions if q.get("is_correct")]
    labels = get_labels_from_survey(correct_items)

    # Metadata text per dataset_id
    # IMPORTANT:
    # - keys must exactly match the dataset_id values in your survey_questions
    # - descriptions should stay minimal and metadata-like
    metadata_by_dataset = {
        labels[0]: "Dataset of NO2 concentration measured at sensor locations in Amsterdam from 2010 to 2025.",
        labels[1]: "Dataset of housing value in Amsterdam in 2024.",
        labels[2]: "Dataset of earthquake events with magnitude, occurrence and location in Groningen province over time.",
        labels[3]: "Dataset of metro and tram lines in Amsterdam.",
        labels[4]: "Dataset of noise in Amsterdam in 2021.",
        labels[5]: "Dataset of trees with species and height in Amsterdam.",
        labels[6]: "Dataset of postcode areas and postcode identifiers in Amsterdam.",
        labels[7]: "Dataset of population counts in the Netherlands.",
        labels[8]: "Dataset of spatial wheat yield estimates in a study area.",
        labels[9]: "Dataset of NO2 exposure changes in Amsterdam under a traffic scenario.",
        labels[10]: "Dataset of conservation measures in agricultural land with soil loss outcomes.",
    }

    # Build metadata texts in the exact same order as labels
    metadata_texts = [metadata_by_dataset[label] for label in labels]

    print("Datasets used for metadata comparison:")
    for idx, (label, text) in enumerate(zip(labels, metadata_texts)):
        print(f"{idx}: {label} -> {text}")

    # Load model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Encode metadata text to embeddings
    embeddings = model.encode(metadata_texts)

    # Cosine similarity and distance
    sim_matrix = cosine_similarity(embeddings)
    D_meta = 1 - sim_matrix

    print("\nMetadata distance matrix:")
    print(D_meta)

    # Save outputs
    output_dir = Path("results_meta")
    output_dir.mkdir(exist_ok=True)

    df_meta = save_matrix_csv(D_meta, labels, output_dir / "metadata_matrix.csv")
    print("\nLabeled metadata distance matrix:")
    print(df_meta)

    plot_heatmap(
        D_meta,
        labels,
        title="Metadata distance between datasets",
        output_path=output_dir / "metadata_heatmap.png"
    )

    closest, farthest = summarize_pairs(D_meta, labels, top_n=5)
    print_pair_summary(closest, farthest)
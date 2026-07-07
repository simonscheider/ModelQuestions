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

    temporal_ids = {
        "NO2_Projection",
        "WheatYield_Prediction",
        "ConservationMeasures_Retrojection"
    }

    non_temporal = [
        q for q in correct_items
        if q["dataset_id"] not in temporal_ids
    ]

    temporal = [
        q for q in correct_items
        if q["dataset_id"] in temporal_ids
    ]

    correct_items = non_temporal + temporal

    labels = [q["dataset_id"] for q in correct_items]

    # Metadata text per dataset_id
    metadata_by_dataset = {
        "NO2_Amsterdam_2025": "Dataset of NO2 concentrations measured at sensor locations in Amsterdam, including spatial sensor locations and temporal coverage up to 2025.",
        "HousingValue_Amsterdam_2024": "Dataset of housing values in Amsterdam in 2024, represented by spatial areas and housing price intervals.",
        "Earthquakes_Groningen_2025": "Dataset of earthquake events in Groningen province in 2025, including event locations and earthquake magnitudes.",
        "MetroLines_Amsterdam": "Dataset of tram and metro line geometries in Amsterdam, representing linear public transport infrastructure.",
        "Noise_Amsterdam_2021": "Dataset of environmental noise levels in Amsterdam in 2021, represented by spatial noise intervals measured in decibels.",
        "Trees_Amsterdam": "Dataset of individual trees in Amsterdam, including tree locations, species, and height attributes.",
        "PostcodeAreas_Amsterdam": "Dataset of postcode areas and postcode identifiers in Amsterdam, representing administrative postal zones and address references.",
        "PopulationDensity_Netherlands": "Dataset of population counts for grid cells in the Netherlands, representing population distribution over a regular spatial grid.",
        "RoadAccidents_NL": "Dataset containing registered road accidents in the Netherlands in 2024, including municipality, province, date, road characteristics, and accident severity information.",
        "GreenSpace_Amsterdam": "Dataset containing polygon features of parks and recreational green spaces in Amsterdam, including name, district, park classification, and surface area.",
        "Temperature_Sensors_NL": "Dataset containing minimum temperature observations for weather sensor locations in the Netherlands on April 27, 2024.",
        "Rainfall_Sensors_NL": "Dataset containing rainfall amount observations for weather sensor locations in the Netherlands on March 30, 2024.",
        "Hospitals_NL": "Dataset containing locations of emergency general practitioner posts or hospital-related emergency care locations in the Netherlands.",
        "Landcover_NL": "Raster dataset representing land cover and land use classes in the Netherlands at 5 meter spatial resolution, including agricultural, forest, water, nature, and urban classes.",
        "NO2_Projection": "Dataset of NO2 exposure changes in Amsterdam under a traffic restriction scenario, representing future air quality outcomes under a hypothetical intervention.",
        "WheatYield_Prediction": "Dataset of spatial wheat yield estimates in a study area, representing future yield outcomes based on weather and soil conditions.",
        "ConservationMeasures_Retrojection": "Dataset of conservation measures in agricultural land, representing spatial planning options related to future soil loss reduction."
    }

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
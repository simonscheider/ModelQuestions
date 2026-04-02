# metadata_distance_demo.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Example: one metadata description per dataset
metadata_texts = [
    "Title: NO2 annual averages at air quality sensor locations, Amsterdam. Description: This point dataset contains yearly average NO2 concentrations measured at fixed air quality monitoring stations in the municipality of Amsterdam. Each feature represents one sensor location with attributes for annual mean NO2 values (µg/m³) per year and basic station metadata such as station code and type. The dataset covers the urban area of Amsterdam and is updated yearly.",
    "Title: Road traffic noise zones by decibel class, Amsterdam. Description: This polygon dataset represents modeled road traffic noise exposure for the municipality of Amsterdam, grouped into standard decibel intervals (e.g. 50–55 dB, 55–60 dB, etc.). Each polygon feature covers an area with similar noise levels and includes attributes for the noise class, sound level (Lden), and basic classification codes. The dataset covers the current situation and is intended for environmental noise assessment and planning.",
    "Title: Earthquake events with magnitude and duration near Amsterdam. Description: This point dataset contains recorded earthquake events in and around the Amsterdam region. Each feature represents a single event with attributes for epicentre location, magnitude, event start time, and estimated duration. The dataset aggregates observations from national seismic monitoring services and covers all available records up to the present.",
]

# Load a small general-purpose model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode to embeddings
embeddings = model.encode(metadata_texts)

# Cosine similarity (n x n)
sim_matrix = cosine_similarity(embeddings)

# Convert similarity to distance
D_meta = 1 - sim_matrix

print("Metadata distance matrix:\n", D_meta)

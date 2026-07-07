from lark import Tree, Token
from zss import Node, simple_distance
from modelQuestionGrammar import l_questions, survey_questions
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def lark_to_zss(node, ignore_words=None):
    if ignore_words is None:
        ignore_words = {"?", ",", "the"}

    if isinstance(node, Token):
        text = str(node)
        if text in ignore_words:
            return None
        return Node(text)

    if isinstance(node, Tree):
        root = Node(node.data)
        for child in node.children:
            child_node = lark_to_zss(child, ignore_words)
            if child_node is not None:
                root.addkid(child_node)
        return root

    return None


def parse_question_to_zss(q: str) -> Node:
    ltree = l_questions.parse(q)
    return lark_to_zss(ltree)


def tree_edit_distance(q1: str, q2: str) -> int:
    t1 = parse_question_to_zss(q1)
    t2 = parse_question_to_zss(q2)
    return simple_distance(t1, t2)

def get_labels_from_survey(survey_items):
    """Use dataset_id as label for each correct question."""
    return [q["dataset_id"] for q in survey_items if q.get("is_correct")]


def save_matrix_csv(D, labels, filename):
    df = pd.DataFrame(D, index=labels, columns=labels)
    df.to_csv(filename)
    return df


def plot_heatmap(D, labels, title, output_path=None):
    plt.figure(figsize=(9, 7))
    plt.imshow(D, interpolation="nearest")
    plt.colorbar(label="Tree Edit Distance")
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
            pairs.append((labels[i], labels[j], D[i, j]))

    pairs_sorted = sorted(pairs, key=lambda x: x[2])
    closest = pairs_sorted[:top_n]
    farthest = pairs_sorted[-top_n:]

    return closest, farthest


def print_pair_summary(closest, farthest):
    print("\nClosest dataset pairs:")
    for a, b, d in closest:
        print(f"{a} <-> {b}: TED = {d}")

    print("\nMost distant dataset pairs:")
    for a, b, d in reversed(farthest):
        print(f"{a} <-> {b}: TED = {d}")

if __name__ == "__main__":
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
    questions = [q["parser_question"] for q in correct_items]
    labels = [q["dataset_id"] for q in correct_items]

    n = len(questions)
    D = np.zeros((n, n), dtype=int)

    for i in range(n):
        for j in range(n):
            if i == j:
                D[i, j] = 0
            elif j > i:
                d = tree_edit_distance(questions[i], questions[j])
                D[i, j] = d
                D[j, i] = d

    print("Questions used:")
    for idx, (label, q) in enumerate(zip(labels, questions)):
        print(f"{idx}: {label} -> {q}")

    print("\nTree Edit Distance matrix (TED):")
    print(D)

    output_dir = Path("results_ted")
    output_dir.mkdir(exist_ok=True)

    df_ted = save_matrix_csv(D, labels, output_dir / "ted_matrix.csv")
    print("\nLabeled TED matrix:")
    print(df_ted)

    plot_heatmap(
        D,
        labels,
        title="Tree Edit Distance between datasets",
        output_path=output_dir / "ted_heatmap.png"
    )

    closest, farthest = summarize_pairs(D, labels, top_n=5)
    print_pair_summary(closest, farthest)
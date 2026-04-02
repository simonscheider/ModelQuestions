from lark import Tree, Token
from zss import Node, simple_distance
from modelQuestionGrammar import l_questions, survey_questions
import numpy as np


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


if __name__ == "__main__":
    questions = [q["parser_question"] for q in survey_questions[:12]]

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
    for idx, q in enumerate(questions):
        print(f"{idx}: {q}")

    print("\nTree Edit Distance matrix (TED):")
    print(D)
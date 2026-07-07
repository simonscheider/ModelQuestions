from pathlib import Path

import pandas as pd
from scipy.stats import binomtest, mannwhitneyu, fisher_exact
from statsmodels.stats.proportion import proportion_confint
import matplotlib.pyplot as plt

# --------------------
# paths
# --------------------
input_file = Path("results_survey/ExperimentalOriginsSurvey.csv")
output_dir = Path("results_survey")
output_dir.mkdir(exist_ok=True)

# --------------------
# read CSV
# --------------------
df = pd.read_csv(input_file)

# remove Qualtrics metadata row
df = df[df["StartDate"].astype(str) != "Start Date"].copy()

# convert progress to number
df["Progress_num"] = pd.to_numeric(df["Progress"], errors="coerce")

# keep real respondents with consent and at least 80% progress
df = df[
    (df["DistributionChannel"].astype(str).str.lower() == "anonymous") &
    (df["Introduction"].astype(str) == "1") &
    (df["Progress_num"] >= 80)
].copy()

print(f"Number of included respondents: {len(df)}")

# --------------------
# GIS experience grouping
# --------------------
experience_col = "Q0_1"

df["GIS_experience_num"] = pd.to_numeric(
    df[experience_col],
    errors="coerce"
)

def classify_experience(value):

    if value in [1, 2]:
        return "Beginner"

    elif value in [3, 4]:
        return "Skilled"

    else:
        return None

df["GIS_experience_group"] = df[
    "GIS_experience_num"
].apply(classify_experience)

print("\nGIS experience groups:")
print(df["GIS_experience_group"].value_counts(dropna=False))

# --------------------
# questions and answer key
# --------------------
question_cols = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Q5",
    "Q6",
    "Q7",
    "Q8",
    "Q9_Projection",
    "Q10_Prediction",
    "Q11_Retrojection",
]

question_labels = {
    "Q1": "Q1_NO2",
    "Q2": "Q2_Housing",
    "Q3": "Q3_Earthquake",
    "Q4": "Q4_Metro",
    "Q5": "Q5_Noise",
    "Q6": "Q6_Trees",
    "Q7": "Q7_Postcode",
    "Q8": "Q8_Population",
    "Q9_Projection": "Q9_Projection",
    "Q10_Prediction": "Q10_Prediction",
    "Q11_Retrojection": "Q11_Retrojection",
}

correct_answers = {
    "Q1": 1,
    "Q2": 1,
    "Q3": 1,
    "Q4": 1,
    "Q5": 1,
    "Q6": 1,
    "Q7": 1,
    "Q8": 1,
    "Q9_Projection": 3,
    "Q10_Prediction": 1,
    "Q11_Retrojection": 1,
}

def format_p_value(p):

    if p is None:
        return ""

    if p < 0.001:
        return "<.001"

    return f"{p:.3f}".replace("0.", ".")

# --------------------
# per-question results
# --------------------
summary_rows = []

for col in question_cols:
    responses = pd.to_numeric(df[col], errors="coerce").dropna()

    n_valid = len(responses)
    n_correct = int((responses == correct_answers[col]).sum())
    accuracy = n_correct / n_valid if n_valid > 0 else None

    if n_valid > 0:

        test = binomtest(
            k=n_correct,
            n=n_valid,
            p=1 / 3,
            alternative="greater"
        )

        p_value = test.pvalue

        ci_low, ci_high = proportion_confint(
            n_correct,
            n_valid,
            alpha=0.05,
            method="wilson"
        )

    else:
        p_value = None
        ci_low = None
        ci_high = None

    summary_rows.append({
        "question": question_labels[col],
        "n_valid": n_valid,
        "n_correct": n_correct,
        "accuracy": accuracy,
        "accuracy_pct": round(accuracy * 100, 1) if accuracy is not None else None,
        "ci_low_pct": round(ci_low * 100, 1) if ci_low is not None else None,
        "ci_high_pct": round(ci_high * 100, 1) if ci_high is not None else None,
        "chance_level": 1/3,
        "binomial_p_value": p_value,
        "significant_at_0_05": p_value < 0.05 if p_value is not None else None,
    })

summary_df = pd.DataFrame(summary_rows)

print("\nPer-question summary:")
print(summary_df)

plt.figure(figsize=(10, 6))
plt.bar(summary_df["question"], summary_df["accuracy_pct"])
plt.axhline(
    y=100/3,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label="Random guessing (33.3%)"
)
plt.ylabel("Percentage correct")
plt.xlabel("Question")
plt.title("Correct responses per survey question")
plt.ylim(0, 100)
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(output_dir / "question_accuracy_plot.png", dpi=300)
plt.show()

# --------------------
# overall result
# --------------------
all_results = []

for col in question_cols:
    responses = pd.to_numeric(df[col], errors="coerce").dropna()

    for response in responses:
        all_results.append(response == correct_answers[col])

overall_n = len(all_results)
overall_correct = int(sum(all_results))
overall_accuracy = overall_correct / overall_n

overall_test = binomtest(
    k=overall_correct,
    n=overall_n,
    p=1/3,
    alternative="greater"
)

overall_df = pd.DataFrame([{
    "overall_n_answered_items": overall_n,
    "overall_correct": overall_correct,
    "overall_accuracy": overall_accuracy,
    "overall_accuracy_pct": round(overall_accuracy * 100, 1),
    "chance_level": 1/3,
    "binomial_p_value": overall_test.pvalue,
    "significant_at_0_05": overall_test.pvalue < 0.05,
}])

print("\nOverall summary:")
print(overall_df)

# --------------------
# participant-level accuracy by GIS experience
# --------------------
participant_rows = []

for idx, row in df.iterrows():

    n_answered = 0
    n_correct = 0

    for col in question_cols:

        response = pd.to_numeric(
            row[col],
            errors="coerce"
        )

        if pd.notna(response):

            n_answered += 1

            if response == correct_answers[col]:
                n_correct += 1

    accuracy = (
        n_correct / n_answered
        if n_answered > 0
        else None
    )

    participant_rows.append({
        "GIS_experience_group": row["GIS_experience_group"],
        "n_answered": n_answered,
        "n_correct": n_correct,
        "accuracy": accuracy,
        "accuracy_pct": round(accuracy * 100, 1)
        if accuracy is not None
        else None,
    })

participant_df = pd.DataFrame(participant_rows)

experience_summary = (
    participant_df
    .dropna(subset=["GIS_experience_group"])
    .groupby("GIS_experience_group")
    .agg(
        n_participants=("accuracy", "count"),
        mean_accuracy=("accuracy", "mean"),
        median_accuracy=("accuracy", "median")
    )
    .reset_index()
)

experience_summary["mean_accuracy_pct"] = (
    experience_summary["mean_accuracy"] * 100
).round(1)

experience_summary["median_accuracy_pct"] = (
    experience_summary["median_accuracy"] * 100
).round(1)

print("\nExperience summary:")
print(experience_summary)

# Mann–Whitney U test
low_scores = participant_df.loc[
    participant_df["GIS_experience_group"] == "Beginner",
    "accuracy"
].dropna()

high_scores = participant_df.loc[
    participant_df["GIS_experience_group"] == "Skilled",
    "accuracy"
].dropna()

if len(low_scores) > 0 and len(high_scores) > 0:

    experience_test = mannwhitneyu(
        low_scores,
        high_scores,
        alternative="two-sided"
    )

    experience_test_df = pd.DataFrame([{
        "beginner_n": len(low_scores),
        "skilled_n": len(high_scores),
        "beginner_mean_accuracy_pct": round(low_scores.mean() * 100, 1),
        "skilled_mean_accuracy_pct": round(high_scores.mean() * 100, 1),
        "mann_whitney_u": experience_test.statistic,
        "p_value": experience_test.pvalue,
    }])

else:

    experience_test_df = pd.DataFrame()

print("\nExperience test:")
print(experience_test_df)

# --------------------
# per-question results by GIS experience group
# --------------------
group_table_rows = []

groups = ["Beginner", "Skilled"]

for col in question_cols:

    row_result = {
        "question": question_labels[col]
    }

    for group in groups:

        group_df = df[df["GIS_experience_group"] == group]

        responses = pd.to_numeric(
            group_df[col],
            errors="coerce"
        ).dropna()

        n_valid = len(responses)

        n_correct = int(
            (responses == correct_answers[col]).sum()
        )

        n_incorrect = n_valid - n_correct
        row_result[f"{group}_incorrect"] = n_incorrect

        if n_valid > 0:

            test = binomtest(
                k=n_correct,
                n=n_valid,
                p=1 / 3,
                alternative="greater"
            )

            p_value = test.pvalue

            row_result[f"{group}_n"] = n_valid
            row_result[f"{group}_correct"] = n_correct
            row_result[f"{group}_p_value"] = p_value
            row_result[f"{group}_cell"] = (
                f"{n_correct} ({format_p_value(p_value)})"
            )

        else:

            row_result[f"{group}_n"] = 0
            row_result[f"{group}_correct"] = None
            row_result[f"{group}_p_value"] = None
            row_result[f"{group}_cell"] = ""

    responses_total = pd.to_numeric(
        df[col],
        errors="coerce"
    ).dropna()

    n_total = len(responses_total)

    correct_total = int(
        (responses_total == correct_answers[col]).sum()
    )

    if n_total > 0:

        test_total = binomtest(
            k=correct_total,
            n=n_total,
            p=1 / 3,
            alternative="greater"
        )

        p_total = test_total.pvalue

        row_result["Total_n"] = n_total
        row_result["Total_correct"] = correct_total
        row_result["Total_p_value"] = p_total
        row_result["Total_cell"] = (
            f"{correct_total} ({format_p_value(p_total)})"
        )

    else:

        row_result["Total_n"] = 0
        row_result["Total_correct"] = None
        row_result["Total_p_value"] = None
        row_result["Total_cell"] = ""

    # Fisher exact test between groups
    if (
            row_result["Beginner_n"] > 0
            and row_result["Skilled_n"] > 0
    ):

        contingency = [
            [
                row_result["Beginner_correct"],
                row_result["Beginner_incorrect"]
            ],
            [
                row_result["Skilled_correct"],
                row_result["Skilled_incorrect"]
            ]
        ]

        _, fisher_p = fisher_exact(contingency)

        row_result["fisher_p"] = fisher_p

    else:
        row_result["fisher_p"] = None

    group_table_rows.append(row_result)

group_question_df = pd.DataFrame(group_table_rows)

print("\nQuestion results by GIS experience:")
print(group_question_df[
    [
        "question",
        "Beginner_cell",
        "Skilled_cell",
        "Total_cell"
    ]
])

# --------------------
# response distributions
# --------------------
distribution_rows = []

for col in question_cols:
    responses = pd.to_numeric(df[col], errors="coerce").dropna()

    counts = responses.value_counts().sort_index()

    for option, count in counts.items():
        distribution_rows.append({
            "question": question_labels[col],
            "option": int(option),
            "count": int(count),
            "is_correct": int(option) == correct_answers[col],
        })

distribution_df = pd.DataFrame(distribution_rows)

print("\nResponse distributions:")
print(distribution_df)




# --------------------
# save outputs
# --------------------
summary_df.to_csv(output_dir / "question_summary.csv", index=False)
overall_df.to_csv(output_dir / "overall_summary.csv", index=False)
distribution_df.to_csv(output_dir / "response_distributions.csv", index=False)
participant_df.to_csv(output_dir / "participant_scores.csv", index=False)
experience_summary.to_csv(output_dir / "experience_summary.csv", index=False)
experience_test_df.to_csv(output_dir / "experience_test.csv", index=False)
group_question_df.to_csv(
    output_dir / "question_summary_by_experience.csv",
    index=False
)

print(f"\nSaved outputs to: {output_dir}")
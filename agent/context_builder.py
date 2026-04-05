'''
What this does is turn the input dataframe into a structure text, 
which is then turned into system prompt as input to the LLM.
'''

import pandas as pd


def build_schema_summary(df: pd.DataFrame, n_samples: int = 3) -> str:
    lines = [] #lines is an object to record the information about the data which is later put to the LLM.
    lines.append(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns") #number of columns and rows of the dataframe
    lines.append("")

    lines.append("Columns and dtypes:") #the data types of the columns
    for col in df.columns:
        lines.append(f"  - {col!r}: {df[col].dtype}")
    lines.append("")

    lines.append(f"Sample rows ({n_samples}):") #sample a couple of rows for LLM to refer to
    lines.append(df.head(n_samples).to_string(index=False))
    lines.append("")

    # Numeric column ranges
    num_cols = df.select_dtypes(include="number").columns.tolist() #select the columns that contain numeric values
    if num_cols:
        lines.append("Numeric column ranges:")
        for col in num_cols:
            lines.append(
                f"  - {col!r}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                f"mean={df[col].mean():.2f}"
            )
        lines.append("")

    # Categorical columns
    cat_cols = df.select_dtypes(include=["object", "str"]).columns.tolist() #select columns that contain categorical values
    if cat_cols:
        lines.append("Categorical columns:")
        for col in cat_cols:
            n_unique = df[col].nunique()
            if n_unique <= 20:
                vals = df[col].dropna().unique().tolist()
                lines.append(f"  - {col!r}: {n_unique} unique values: {vals}")
            else:
                sample_vals = df[col].dropna().unique()[:5].tolist()
                lines.append(
                    f"  - {col!r}: {n_unique} unique values "
                    f"(sample: {sample_vals} ...)"
                )

    return "\n".join(lines) 
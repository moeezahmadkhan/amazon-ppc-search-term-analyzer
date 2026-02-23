"""
MLend query parser:
- Uses OpenAI to convert natural-language filter requests into a strict JSON filter spec.
- Applies strict guardrails (column whitelist, operator whitelist, value validation).
- Applies the validated spec to pandas DataFrames without eval/exec.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

import pandas as pd
from openai import OpenAI

NumericOperator = Literal[">", ">=", "<", "<=", "==", "!=", "between"]
TextOperator = Literal["contains", "equals", "in", "not_in"]
Operator = NumericOperator | TextOperator
Mode = Literal["all", "any"]


ALLOWED_COLUMNS: Dict[str, str] = {
    "Customer Search Term": "text",
    "Campaign Name (Informational only)": "text",
    "Ad Group Name (Informational only)": "text",
    "Portfolio Name (Informational only)": "text",
    "Match Type": "text",
    "Impressions": "number",
    "Clicks": "number",
    "Spend": "number",
    "Sales": "number",
    "Orders": "number",
    "ACOS": "number",
    "Conversion Rate": "number",
    "CPC": "number",
    "ROAS": "number",
}

NUMERIC_OPS = {">", ">=", "<", "<=", "==", "!=", "between"}
TEXT_OPS = {"contains", "equals", "in", "not_in"}
MAX_CONDITIONS = 8
MAX_IN_LIST = 25
MAX_STRING_LEN = 200


@dataclass
class Condition:
    column: str
    operator: Operator
    value: Any


@dataclass
class FilterSpec:
    mode: Mode
    conditions: List[Condition]
    limit: int = 50


def _build_system_prompt() -> str:
    return (
        "You convert user requests into strict JSON filters for an Amazon PPC dataframe. "
        "Return JSON only with this schema: "
        "{\"mode\":\"all|any\",\"conditions\":[{\"column\":str,\"operator\":str,\"value\":any}],\"limit\":int}. "
        "Allowed columns: " + ", ".join(ALLOWED_COLUMNS.keys()) + ". "
        "Numeric operators: >, >=, <, <=, ==, !=, between (value must be [min,max]). "
        "Text operators: contains, equals, in, not_in. "
        "For percentages, values are decimals (0.1 means 10%). "
        "Never output code, pandas, SQL, markdown, explanations, or extra keys."
    )


def _coerce_spec(raw: Dict[str, Any]) -> FilterSpec:
    mode = raw.get("mode", "all")
    if mode not in ("all", "any"):
        mode = "all"

    raw_conditions = raw.get("conditions", [])
    if not isinstance(raw_conditions, list):
        raw_conditions = []

    if len(raw_conditions) > MAX_CONDITIONS:
        raise ValueError(f"Too many conditions. Max allowed is {MAX_CONDITIONS}.")

    conditions: List[Condition] = []
    for cond in raw_conditions:
        if not isinstance(cond, dict):
            raise ValueError("Each condition must be an object.")

        col = cond.get("column")
        op = cond.get("operator")
        value = cond.get("value")

        if col not in ALLOWED_COLUMNS:
            raise ValueError(f"Column not allowed: {col}")

        col_type = ALLOWED_COLUMNS[col]
        if col_type == "number" and op not in NUMERIC_OPS:
            raise ValueError(f"Operator '{op}' not allowed for numeric column '{col}'.")
        if col_type == "text" and op not in TEXT_OPS:
            raise ValueError(f"Operator '{op}' not allowed for text column '{col}'.")

        if op == "between":
            if not (isinstance(value, list) and len(value) == 2):
                raise ValueError("'between' operator requires a 2-item list value.")
            try:
                value = [float(value[0]), float(value[1])]
            except Exception as exc:
                raise ValueError("'between' values must be numeric.") from exc
        elif op in NUMERIC_OPS:
            try:
                value = float(value)
            except Exception as exc:
                raise ValueError(f"Numeric operator '{op}' requires a numeric value.") from exc
        elif op in {"contains", "equals"}:
            value = str(value)
            if len(value) > MAX_STRING_LEN:
                raise ValueError("Text value too long.")
        elif op in {"in", "not_in"}:
            if not isinstance(value, list):
                raise ValueError(f"Operator '{op}' requires a list value.")
            if len(value) > MAX_IN_LIST:
                raise ValueError(f"Too many values in list. Max {MAX_IN_LIST}.")
            value = [str(v)[:MAX_STRING_LEN] for v in value]

        conditions.append(Condition(column=col, operator=op, value=value))

    limit = raw.get("limit", 50)
    try:
        limit = int(limit)
    except Exception:
        limit = 50
    limit = max(1, min(limit, 200))

    return FilterSpec(mode=mode, conditions=conditions, limit=limit)


def parse_query_with_openai(
    prompt: str,
    *,
    api_key: str,
    model: str = "gpt-4.1-mini",
) -> FilterSpec:
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing.")
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is empty.")

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user", "content": prompt.strip()},
        ],
    )

    content = completion.choices[0].message.content or "{}"
    raw = json.loads(content)
    return _coerce_spec(raw)


def apply_filter_spec(df: pd.DataFrame, spec: FilterSpec) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    masks = []
    for cond in spec.conditions:
        col = cond.column
        op = cond.operator
        value = cond.value

        series = df[col]
        if ALLOWED_COLUMNS[col] == "text":
            text_series = series.fillna("").astype(str)
            if op == "contains":
                mask = text_series.str.contains(str(value), case=False, na=False)
            elif op == "equals":
                mask = text_series.str.lower() == str(value).lower()
            elif op == "in":
                value_set = {str(v).lower() for v in value}
                mask = text_series.str.lower().isin(value_set)
            elif op == "not_in":
                value_set = {str(v).lower() for v in value}
                mask = ~text_series.str.lower().isin(value_set)
            else:
                raise ValueError(f"Unsupported text operator: {op}")
        else:
            num = pd.to_numeric(series, errors="coerce").fillna(0)
            if op == ">":
                mask = num > value
            elif op == ">=":
                mask = num >= value
            elif op == "<":
                mask = num < value
            elif op == "<=":
                mask = num <= value
            elif op == "==":
                mask = num == value
            elif op == "!=":
                mask = num != value
            elif op == "between":
                lo, hi = value
                mask = (num >= lo) & (num <= hi)
            else:
                raise ValueError(f"Unsupported numeric operator: {op}")

        masks.append(mask)

    if not masks:
        return df.head(spec.limit).copy()

    final_mask = masks[0]
    if spec.mode == "all":
        for m in masks[1:]:
            final_mask = final_mask & m
    else:
        for m in masks[1:]:
            final_mask = final_mask | m

    return df.loc[final_mask].head(spec.limit).copy()


def filter_spec_to_dict(spec: FilterSpec) -> Dict[str, Any]:
    return {
        "mode": spec.mode,
        "limit": spec.limit,
        "conditions": [
            {
                "column": c.column,
                "operator": c.operator,
                "value": c.value,
            }
            for c in spec.conditions
        ],
    }

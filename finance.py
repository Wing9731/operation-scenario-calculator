"""財務試算公式與情境資料整理。"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def calculate_financials(
    enrollment: int,
    tuition: float,
    fixed_cost: float,
    variable_cost_per_student: float,
    extra_cost: float,
) -> dict[str, int | float | None]:
    """以輸入的營運假設計算單一情境財務結果。"""
    revenue = enrollment * tuition
    variable_cost = enrollment * variable_cost_per_student
    total_cost = fixed_cost + variable_cost + extra_cost
    profit = revenue - total_cost
    contribution = tuition - variable_cost_per_student
    fixed_outlay = fixed_cost + extra_cost
    break_even = math.ceil(fixed_outlay / contribution) if contribution > 0 else None

    return {
        "招生人數": enrollment,
        "每人課程價格": tuition,
        "營收": revenue,
        "固定成本": fixed_cost,
        "每人變動成本": variable_cost_per_student,
        "變動成本": variable_cost,
        "其他額外成本": extra_cost,
        "總成本": total_cost,
        "營運利潤": profit,
        "利潤率": profit / revenue * 100 if revenue else None,
        "損益兩平招生人數": break_even,
    }


def build_profit_curve(
    scenarios: list[dict[str, Any]],
    fixed_cost: float,
    variable_cost_per_student: float,
    extra_cost: float,
    max_enrollment: int,
    points: int = 80,
) -> pd.DataFrame:
    """建立三情境的招生人數與利潤曲線資料。"""
    max_enrollment = max(1, int(max_enrollment))
    enrollments = sorted(set(round(i * max_enrollment / points) for i in range(points + 1)))
    rows: list[dict[str, int | float | str]] = []
    for scenario in scenarios:
        for count in enrollments:
            profit = count * (scenario["每人課程價格"] - variable_cost_per_student) - fixed_cost - extra_cost
            rows.append({"情境": scenario["情境"], "招生人數": count, "營運利潤": profit})
    return pd.DataFrame(rows)

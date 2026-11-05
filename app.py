from __future__ import annotations

import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from finance import build_profit_curve, calculate_financials


TEXT_DEFAULTS = {
    "page_title": "營運情境試算工具",
    "eyebrow": "",
    "page_subtitle": "調整招生與成本假設，快速掌握課程營運的收入、成本及損益兩平點。",
    "currency_prefix": "NT$",
    "base_section": "基本營運假設",
    "base_caption": "輸入一般情境的基準數值；金額以新台幣計。",
    "base_enrollment": "一般情境招生人數",
    "base_tuition": "每位學生課程價格",
    "fixed_cost": "固定成本",
    "variable_cost": "每位學生變動成本",
    "extra_cost": "其他額外成本",
    "margin_note": "利潤率在營收為零時顯示為「不適用」。",
    "scenario_section": "情境設定",
    "scenario_caption": "保守、一般、樂觀情境可各自調整招生人數與課程價格；各情境共用左側成本假設。",
    "scenario_conservative": "保守",
    "scenario_general": "一般",
    "scenario_optimistic": "樂觀",
    "scenario_suffix": "情境",
    "scenario_enrollment": "招生人數",
    "scenario_tuition": "每位學生課程價格",
    "summary_section": "一般情境財務摘要",
    "price_warning": "一般情境的課程價格必須高於每人變動成本，才會產生正的單位貢獻；目前無法達到損益兩平。",
    "kpi_revenue": "總營收",
    "kpi_cost": "總成本",
    "kpi_profit": "營運利潤",
    "kpi_margin": "利潤率",
    "kpi_breakeven": "損益兩平招生人數",
    "not_applicable": "不適用",
    "unattainable": "無法達成",
    "people_suffix": "人",
    "comparison_section": "三種情境財務比較",
    "table_scenario": "情境",
    "table_enrollment": "招生人數",
    "table_tuition": "每人課程價格",
    "table_revenue": "營收",
    "table_fixed": "固定成本",
    "table_variable": "變動成本",
    "table_extra": "其他額外成本",
    "table_total_cost": "總成本",
    "table_profit": "營運利潤",
    "table_margin": "利潤率",
    "table_breakeven": "損益兩平招生人數",
    "chart_section": "圖表分析",
    "tab_revenue": "營收與成本",
    "tab_profit": "招生與利潤",
    "tab_breakeven": "損益兩平分析",
    "revenue_caption": "比較各情境的總營收、總成本與營運利潤。",
    "profit_caption": "依各情境課程價格與共用成本假設，觀察招生人數改變時的利潤走勢。",
    "breakeven_selector": "損益兩平分析情境",
    "revenue_series": "總營收",
    "cost_series": "總成本",
    "profit_series": "營運利潤",
    "current_revenue_series": "目前招生營收",
    "current_enrollment_suffix": "目前招生",
    "break_even_line": "損益兩平線",
    "breakeven_annotation": "損益兩平",
    "axis_scenario": "情境",
    "axis_item": "項目",
    "axis_money": "金額（NT$）",
    "axis_enrollment": "招生人數（人）",
    "axis_profit": "營運利潤（NT$）",
    "breakeven_warning": "此情境每位學生的課程價格未高於變動成本，營收線不會與總成本線交會。",
    "formula_note": "計算公式：營收 = 招生人數 × 課程價格；總成本 = 固定成本 + 招生人數 × 每人變動成本 + 其他額外成本。損益兩平人數以（固定成本 + 其他額外成本）÷（課程價格 − 每人變動成本）計算並向上取整。",
    "disclaimer": "試算僅供營運規劃參考，未包含稅金、折舊、融資費用或未輸入的其他項目。",
}

EDIT_GROUPS = {
    "標題與輸入": [
        ("頁面標題", "page_title"), ("英文眉標", "eyebrow"), ("頁面說明", "page_subtitle"),
        ("金額前綴", "currency_prefix"), ("基本輸入區標題", "base_section"), ("基本輸入說明", "base_caption"),
        ("基準招生欄位", "base_enrollment"), ("課程價格欄位", "base_tuition"), ("固定成本欄位", "fixed_cost"),
        ("變動成本欄位", "variable_cost"), ("額外成本欄位", "extra_cost"), ("利潤率提示", "margin_note"),
    ],
    "情境與摘要": [
        ("情境區標題", "scenario_section"), ("情境區說明", "scenario_caption"),
        ("保守情境名稱", "scenario_conservative"), ("一般情境名稱", "scenario_general"),
        ("樂觀情境名稱", "scenario_optimistic"), ("情境名稱後綴", "scenario_suffix"), ("情境招生欄位", "scenario_enrollment"),
        ("情境課程價格欄位", "scenario_tuition"), ("摘要標題", "summary_section"),
        ("價格提示", "price_warning"), ("營收指標", "kpi_revenue"), ("成本指標", "kpi_cost"),
        ("利潤指標", "kpi_profit"), ("利潤率指標", "kpi_margin"), ("損益兩平指標", "kpi_breakeven"),
        ("不適用文字", "not_applicable"), ("無法達成文字", "unattainable"), ("人數單位", "people_suffix"),
    ],
    "表格與圖表": [
        ("比較表標題", "comparison_section"), ("表格情境欄", "table_scenario"),
        ("表格招生欄", "table_enrollment"), ("表格價格欄", "table_tuition"),
        ("表格營收欄", "table_revenue"), ("表格固定成本欄", "table_fixed"),
        ("表格變動成本欄", "table_variable"), ("表格額外成本欄", "table_extra"),
        ("表格總成本欄", "table_total_cost"), ("表格利潤欄", "table_profit"),
        ("表格利潤率欄", "table_margin"), ("表格損益兩平欄", "table_breakeven"),
        ("圖表區標題", "chart_section"), ("營收圖籤", "tab_revenue"), ("利潤圖籤", "tab_profit"),
        ("損益兩平圖籤", "tab_breakeven"), ("營收圖說明", "revenue_caption"),
        ("利潤圖說明", "profit_caption"), ("損益兩平選擇欄", "breakeven_selector"),
        ("營收圖例", "revenue_series"), ("成本圖例", "cost_series"), ("利潤圖例", "profit_series"),
        ("目前營收圖例", "current_revenue_series"), ("目前招生圖例文字", "current_enrollment_suffix"),
        ("損益兩平線文字", "break_even_line"), ("損益兩平標記", "breakeven_annotation"),
        ("情境座標軸", "axis_scenario"), ("項目座標軸", "axis_item"), ("金額座標軸", "axis_money"),
        ("招生座標軸", "axis_enrollment"), ("利潤座標軸", "axis_profit"),
        ("無法損益兩平提示", "breakeven_warning"),
    ],
    "說明文字": [("計算公式說明", "formula_note"), ("頁尾提醒", "disclaimer")],
}
MULTILINE_TEXT = {
    "page_subtitle", "base_caption", "margin_note", "scenario_caption", "price_warning",
    "revenue_caption", "profit_caption", "breakeven_warning", "formula_note", "disclaimer",
}

if "ui_texts" not in st.session_state:
    st.session_state["ui_texts"] = TEXT_DEFAULTS.copy()
TEXT = st.session_state["ui_texts"]

st.set_page_config(page_title=TEXT["page_title"], page_icon="📊", layout="wide")
if st.session_state.pop("reset_custom_texts_requested", False):
    TEXT.clear()
    TEXT.update(TEXT_DEFAULTS)
    for fields in EDIT_GROUPS.values():
        for _, text_key in fields:
            st.session_state[f"edit_text_{text_key}"] = TEXT_DEFAULTS[text_key]
for fields in EDIT_GROUPS.values():
    for _, text_key in fields:
        TEXT[text_key] = st.session_state.get(f"edit_text_{text_key}", TEXT[text_key])

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.7rem; padding-bottom: 2.5rem; max-width: 1480px;}
    [data-testid="stMetric"] {background: #f6f8fb; border: 1px solid #e8edf3;
        padding: 10px 12px; border-radius: 14px; min-height: 82px;}
    [data-testid="stMetricLabel"] {color: #637083; font-size: 0.72rem !important; line-height: 1.15;}
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] span {color: #13253a; font-size: 0.92rem !important;
        line-height: 1.15 !important; font-weight: 700; white-space: nowrap;}
    .eyebrow {color:#167d8d; font-size:.78rem; letter-spacing:.12em; font-weight:700;}
    .subtitle {color:#64748b; margin-top:-.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def ntd(value: float) -> str:
    return f"{TEXT['currency_prefix']} {value:,.0f}"


if TEXT["eyebrow"].strip():
    st.caption(TEXT["eyebrow"])
st.title(TEXT["page_title"])
st.write(TEXT["page_subtitle"])

with st.sidebar:
    st.header(TEXT["base_section"])
    st.caption(TEXT["base_caption"])
    base_enrollment = st.number_input(TEXT["base_enrollment"], min_value=0, max_value=1_000_000, value=30, step=1, key="base_enrollment_value")
    base_tuition = st.number_input(f"{TEXT['base_tuition']}（{TEXT['currency_prefix']}）", min_value=0.0, value=12000.0, step=500.0, key="base_tuition_value")
    fixed_cost = st.number_input(f"{TEXT['fixed_cost']}（{TEXT['currency_prefix']}）", min_value=0.0, value=180000.0, step=5000.0, key="fixed_cost_value")
    variable_cost = st.number_input(f"{TEXT['variable_cost']}（{TEXT['currency_prefix']}）", min_value=0.0, value=2500.0, step=100.0, key="variable_cost_value")
    extra_cost = st.number_input(f"{TEXT['extra_cost']}（{TEXT['currency_prefix']}）", min_value=0.0, value=0.0, step=1000.0, key="extra_cost_value")
    st.divider()
    st.caption(TEXT["margin_note"])

    with st.expander("編輯介面文字", expanded=False):
        selected_group = st.selectbox("文字分類", options=list(EDIT_GROUPS), key="text_editor_group")
        for field_label, text_key in EDIT_GROUPS[selected_group]:
            widget_key = f"edit_text_{text_key}"
            if text_key in MULTILINE_TEXT:
                st.text_area(field_label, value=TEXT[text_key], key=widget_key, height=80)
            else:
                st.text_input(field_label, value=TEXT[text_key], key=widget_key)
        for fields in EDIT_GROUPS.values():
            for _, text_key in fields:
                TEXT[text_key] = st.session_state.get(f"edit_text_{text_key}", TEXT[text_key])
        save_col, reset_col = st.columns(2)
        if save_col.button("儲存文字設定", use_container_width=True):
            st.session_state["ui_texts"] = TEXT.copy()
            st.success("文字設定已套用至目前工作階段。")
        if reset_col.button("還原預設文字", use_container_width=True):
            st.session_state["reset_custom_texts_requested"] = True
            st.rerun()

st.subheader(TEXT["scenario_section"])
st.caption(TEXT["scenario_caption"])
scenario_names = [TEXT["scenario_conservative"], TEXT["scenario_general"], TEXT["scenario_optimistic"]]
defaults = [
    (max(0, round(base_enrollment * 0.8)), base_tuition * 0.95),
    (int(base_enrollment), float(base_tuition)),
    (round(base_enrollment * 1.2), base_tuition * 1.05),
]
scenario_columns = st.columns(3)
scenarios: list[dict[str, int | float | str]] = []
for index, (name, (default_count, default_price), column) in enumerate(zip(scenario_names, defaults, scenario_columns)):
    with column:
        st.markdown(f"**{name}{TEXT['scenario_suffix']}**")
        count = st.number_input(
            TEXT["scenario_enrollment"], min_value=0, max_value=1_000_000, value=int(default_count), step=1,
            key=f"scenario_count_{index}_{base_enrollment}_{base_tuition:.2f}",
        )
        tuition = st.number_input(
            f"{TEXT['scenario_tuition']}（{TEXT['currency_prefix']}）", min_value=0.0, value=float(default_price), step=100.0,
            key=f"scenario_price_{index}_{base_enrollment}_{base_tuition:.2f}",
        )
    scenarios.append({"情境": name, "招生人數": int(count), "每人課程價格": float(tuition)})

results = [
    {
        "情境": scenario["情境"],
        **calculate_financials(
            int(scenario["招生人數"]),
            float(scenario["每人課程價格"]),
            float(fixed_cost),
            float(variable_cost),
            float(extra_cost),
        ),
    }
    for scenario in scenarios
]
results_df = pd.DataFrame(results)
st.divider()
general = results[1]

st.subheader(TEXT["summary_section"])
if float(general["每人課程價格"]) <= float(general["每人變動成本"]):
    st.warning(TEXT["price_warning"])

kpis = st.columns(5)
kpis[0].metric(TEXT["kpi_revenue"], ntd(float(general["營收"])))
kpis[1].metric(TEXT["kpi_cost"], ntd(float(general["總成本"])))
kpis[2].metric(TEXT["kpi_profit"], ntd(float(general["營運利潤"])))
kpis[3].metric(TEXT["kpi_margin"], f"{float(general['利潤率']):.1f}%" if general["利潤率"] is not None else TEXT["not_applicable"])
break_even_value = general["損益兩平招生人數"]
kpis[4].metric(TEXT["kpi_breakeven"], f"{break_even_value:,} {TEXT['people_suffix']}" if break_even_value is not None else TEXT["unattainable"])

st.divider()
st.subheader(TEXT["comparison_section"])
display_df = results_df[["情境", "招生人數", "每人課程價格", "營收", "固定成本", "變動成本", "其他額外成本", "總成本", "營運利潤", "利潤率", "損益兩平招生人數"]].copy()
display_df["每人課程價格"] = display_df["每人課程價格"].map(ntd)
for column in ["營收", "固定成本", "變動成本", "其他額外成本", "總成本", "營運利潤"]:
    display_df[column] = display_df[column].map(lambda amount: ntd(float(amount)))
display_df["招生人數"] = display_df["招生人數"].map(lambda count: f"{int(count):,} {TEXT['people_suffix']}")
display_df["利潤率"] = display_df["利潤率"].map(lambda value: f"{float(value):.1f}%" if pd.notna(value) else TEXT["not_applicable"])
display_df["損益兩平招生人數"] = display_df["損益兩平招生人數"].map(
    lambda count: f"{int(count):,} {TEXT['people_suffix']}" if pd.notna(count) else TEXT["unattainable"]
)
display_df.columns = [
    TEXT[key]
    for key in ["table_scenario", "table_enrollment", "table_tuition", "table_revenue", "table_fixed", "table_variable", "table_extra", "table_total_cost", "table_profit", "table_margin", "table_breakeven"]
]
st.dataframe(display_df, hide_index=True, use_container_width=True)

st.divider()
st.subheader(TEXT["chart_section"])
revenue_tab, profit_tab, breakeven_tab = st.tabs([TEXT["tab_revenue"], TEXT["tab_profit"], TEXT["tab_breakeven"]])

with revenue_tab:
    st.caption(TEXT["revenue_caption"])
    bar_df = results_df.melt(id_vars="情境", value_vars=["營收", "總成本", "營運利潤"], var_name="項目", value_name="金額")
    bar_df["項目"] = bar_df["項目"].map({"營收": TEXT["revenue_series"], "總成本": TEXT["cost_series"], "營運利潤": TEXT["profit_series"]})
    bar_fig = px.bar(
        bar_df, x="情境", y="金額", color="項目", barmode="group", text_auto=".2s",
        labels={"情境": TEXT["axis_scenario"], "項目": TEXT["axis_item"], "金額": TEXT["axis_money"]},
    )
    bar_fig.update_layout(legend_title_text="", xaxis_title="", hovermode="x unified")
    bar_fig.update_yaxes(tickprefix=f"{TEXT['currency_prefix']} ", separatethousands=True, zeroline=True)
    st.plotly_chart(bar_fig, use_container_width=True)

with profit_tab:
    st.caption(TEXT["profit_caption"])
    highest_count = max(int(scenario["招生人數"]) for scenario in scenarios)
    highest_be = max((int(row["損益兩平招生人數"]) for row in results if row["損益兩平招生人數"] is not None), default=0)
    curve_end = min(1_000_000, max(50, round(max(highest_count, highest_be) * 1.5)))
    profit_df = build_profit_curve(scenarios, float(fixed_cost), float(variable_cost), float(extra_cost), curve_end)
    profit_fig = px.line(profit_df, x="招生人數", y="營運利潤", color="情境", markers=False)
    profit_fig.add_hline(y=0, line_dash="dash", line_color="#7c8798", annotation_text=TEXT["break_even_line"])
    for row in results:
        profit_fig.add_scatter(
            x=[int(row["招生人數"])], y=[float(row["營運利潤"])], mode="markers",
            marker={"size": 10, "line": {"width": 2, "color": "white"}},
            name=f"{row['情境']}{TEXT['current_enrollment_suffix']}", showlegend=False,
        )
    profit_fig.update_layout(xaxis_title=TEXT["axis_enrollment"], yaxis_title=TEXT["axis_profit"], hovermode="x unified")
    profit_fig.update_yaxes(tickprefix=f"{TEXT['currency_prefix']} ", separatethousands=True, zeroline=True)
    st.plotly_chart(profit_fig, use_container_width=True)

with breakeven_tab:
    selected_index = st.selectbox(
        TEXT["breakeven_selector"], options=range(len(results)), index=1,
        format_func=lambda index: results[index]["情境"],
    )
    selected_row = results[selected_index]
    selected_price = float(selected_row["每人課程價格"])
    selected_break_even = selected_row["損益兩平招生人數"]
    max_x = max(50, int(selected_row["招生人數"] * 1.5), int(selected_break_even * 1.5) if selected_break_even is not None else 0)
    max_x = min(max_x, 1_000_000)
    enrollment_axis = list(range(0, max_x + 1, max(1, max_x // 80)))
    if enrollment_axis[-1] != max_x:
        enrollment_axis.append(max_x)
    revenue_values = [count * selected_price for count in enrollment_axis]
    cost_values = [float(fixed_cost) + float(extra_cost) + count * float(variable_cost) for count in enrollment_axis]
    be_fig = go.Figure()
    be_fig.add_trace(go.Scatter(x=enrollment_axis, y=revenue_values, mode="lines", name=TEXT["revenue_series"], line={"color": "#168c8c", "width": 3}))
    be_fig.add_trace(go.Scatter(x=enrollment_axis, y=cost_values, mode="lines", name=TEXT["cost_series"], line={"color": "#e28a45", "width": 3}))
    be_fig.add_trace(go.Scatter(
        x=[int(selected_row["招生人數"])], y=[float(selected_row["營收"])], mode="markers",
        name=TEXT["current_revenue_series"], marker={"size": 11, "color": "#234f87"},
    ))
    if selected_break_even is not None:
        be_fig.add_vline(
            x=int(selected_break_even), line_dash="dash", line_color="#7c8798",
            annotation_text=f"{TEXT['breakeven_annotation']} {selected_break_even:,} {TEXT['people_suffix']}",
        )
    else:
        st.warning(TEXT["breakeven_warning"])
    be_fig.update_layout(xaxis_title=TEXT["axis_enrollment"], yaxis_title=TEXT["axis_money"], hovermode="x unified")
    be_fig.update_yaxes(tickprefix=f"{TEXT['currency_prefix']} ", separatethousands=True)
    st.plotly_chart(be_fig, use_container_width=True)

st.caption(TEXT["formula_note"])
st.caption(TEXT["disclaimer"])

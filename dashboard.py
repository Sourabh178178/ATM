
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

TX_PATH = DATA / "atm_transactions.csv"
FORECAST_PATH = DATA / "forecast_results.csv"
METRICS_PATH = DATA / "model_metrics.csv"

st.set_page_config(
    page_title="ATM Intelligence | Cash Forecasting",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG = "#0B1120"
PANEL = "#111B2E"
BORDER = "#25344D"
CYAN = "#54D6FF"
GREEN = "#48D6A3"
MUTED = "#91A2BB"
WHITE = "#F1F5FC"
AMBER = "#F6BD60"
RED = "#FF7185"

# ---------------------------------------------------------
# PREMIUM DARK THEME
# ---------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {{
        --bg: {BG};
        --panel: {PANEL};
        --border: {BORDER};
        --cyan: {CYAN};
        --green: {GREEN};
        --muted: {MUTED};
        --white: {WHITE};
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 85% 0%, #142844 0%, transparent 38%),
            var(--bg);
        color: var(--white);
        font-family: 'DM Sans', sans-serif;
    }}

    [data-testid="stHeader"] {{
        background: rgba(11,17,32,.85);
    }}

    [data-testid="stSidebar"] {{
        background: #0D1627;
        border-right: 1px solid var(--border);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.3rem;
    }}

    h1, h2, h3 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--white) !important;
        letter-spacing: -0.5px;
    }}

    p, label, span, div {{
        font-family: 'DM Sans', sans-serif;
    }}

    .brand {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        font-weight: 700;
        color: var(--white);
        letter-spacing: -1px;
    }}

    .brand span {{
        color: var(--cyan);
    }}

    .eyebrow {{
        color: var(--cyan);
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 9px;
    }}

    .page-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(28px, 3vw, 39px);
        line-height: 1.15;
        font-weight: 700;
        color: var(--white);
        letter-spacing: -1.2px;
        margin: 0 0 10px 0;
    }}

    .subtext {{
        color: var(--muted);
        font-size: 14px;
        line-height: 1.65;
    }}

    .metric-card {{
        background: linear-gradient(145deg, #16243A, #101A2B);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px 20px 18px;
        min-height: 145px;
        box-shadow: 0 10px 28px rgba(0,0,0,.10);
        transition: border-color .2s, transform .2s;
    }}

    .metric-card:hover {{
        border-color: #47708F;
        transform: translateY(-2px);
    }}

    .metric-label {{
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: .5px;
        text-transform: uppercase;
    }}

    .metric-value {{
        font-family: 'Space Grotesk', sans-serif;
        color: var(--white);
        font-size: clamp(22px, 2vw, 30px);
        font-weight: 700;
        margin: 14px 0 7px;
        letter-spacing: -1px;
        overflow-wrap: anywhere;
    }}

    .metric-foot {{
        color: var(--green);
        font-size: 12px;
    }}

    .section-head {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: var(--white);
        margin: 12px 0 5px;
    }}

    .section-note {{
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 14px;
    }}

    .status-pill {{
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        background: rgba(72,214,163,.10);
        color: #67E8B7;
        border: 1px solid rgba(72,214,163,.25);
    }}

    .info-strip {{
        border: 1px solid #304663;
        background: rgba(84,214,255,.055);
        border-radius: 12px;
        padding: 14px 16px;
        color: #C2D3E7;
        font-size: 13px;
        line-height: 1.65;
    }}

    .footer {{
        color: #70839D;
        font-size: 11px;
        border-top: 1px solid var(--border);
        padding-top: 17px;
        margin-top: 35px;
    }}

    div[data-testid="stPlotlyChart"] {{
        border: 1px solid var(--border);
        border-radius: 14px;
        background: rgba(17,27,46,.65);
        padding: 8px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }}

    div.stButton > button, div.stDownloadButton > button {{
        border: 1px solid #35516C;
        background: #162840;
        color: var(--white);
        border-radius: 9px;
        font-weight: 600;
        transition: .2s;
    }}

    div.stButton > button:hover, div.stDownloadButton > button:hover {{
        border-color: var(--cyan);
        color: var(--cyan);
    }}

    [data-testid="stMetric"] {{
        background: var(--panel);
        padding: 14px;
        border-radius: 12px;
        border: 1px solid var(--border);
    }}

    hr {{
        border-color: var(--border);
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    tx = pd.read_csv(TX_PATH, parse_dates=["timestamp"])
    forecasts = pd.read_csv(FORECAST_PATH)
    forecasts["forecast_date"] = pd.to_datetime(
        forecasts["forecast_date"]
    )
    metrics = (
        pd.read_csv(METRICS_PATH)
        if METRICS_PATH.exists()
        else pd.DataFrame()
    )

    tx["date"] = tx["timestamp"].dt.normalize()

    daily = (
        tx.groupby(["atm_id", "date"], as_index=False)
        ["withdrawal_amount"]
        .sum()
        .rename(columns={"withdrawal_amount": "demand"})
    )

    return tx, daily, forecasts, metrics


if not all(p.exists() for p in [TX_PATH, FORECAST_PATH]):
    st.error(
        "Required files are missing. Run the data generator and "
        "forecasting model first."
    )
    st.stop()

tx, daily, forecasts, metrics = load_data()

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def money(value, decimals=0):
    return f"₹{value:,.{decimals}f}"


def chart_layout(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=MUTED, size=11),
        margin=dict(l=12, r=12, t=35, b=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=1.12,
            x=0,
        ),
        hoverlabel=dict(
            bgcolor="#15253A",
            font_color=WHITE,
            bordercolor=BORDER,
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
    )
    fig.update_yaxes(
        gridcolor="#223047",
        zeroline=False,
        tickfont=dict(color=MUTED),
    )
    return fig


def metric_card(label, value, foot, accent=CYAN):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot" style="color:{accent}">
                {foot}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title, note=None):
    st.markdown(
        f'<div class="section-head">{title}</div>',
        unsafe_allow_html=True,
    )
    if note:
        st.markdown(
            f'<div class="section-note">{note}</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand">ATM<span>.</span>INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Cash demand & operations platform</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown('<div class="eyebrow">WORKSPACE</div>',
                unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Forecast Analytics",
            "ATM Operations",
            "Data Explorer",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<div class="eyebrow">DATA STATUS</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<span class="status-pill">● Forecast files loaded</span>',
        unsafe_allow_html=True,
    )

    st.caption(f"{tx['atm_id'].nunique()} ATMs · {len(tx):,} transactions")
    st.caption(
        f"History: {tx['timestamp'].min():%d %b %Y} — "
        f"{tx['timestamp'].max():%d %b %Y}"
    )

    st.markdown("---")
    st.markdown(
        '<div class="subtext">ATM Intelligence v1.0<br>'
        'Academic demonstration · Synthetic data</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# COMMON CALCULATIONS
# ---------------------------------------------------------
total_predicted = forecasts["predicted_demand"].sum()
total_recommended = forecasts["recommended_cash"].sum()
buffer_total = total_recommended - total_predicted

mae = (
    float(metrics.iloc[0]["mae_rupees"])
    if not metrics.empty and "mae_rupees" in metrics.columns
    else np.nan
)
wape = (
    float(metrics.iloc[0]["wape_percent"])
    if not metrics.empty and "wape_percent" in metrics.columns
    else np.nan
)

next_date = forecasts["forecast_date"].min()
top_atm = forecasts.loc[
    forecasts["predicted_demand"].idxmax()
]
low_atm = forecasts.loc[
    forecasts["predicted_demand"].idxmin()
]

# ---------------------------------------------------------
# PAGE: OVERVIEW
# ---------------------------------------------------------
if page == "Overview":
    st.markdown('<div class="eyebrow">OPERATIONS CENTER / 01</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="page-title">Cash intelligence, at a glance.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">A consolidated view of ATM demand, '
        'forecast performance and next-day cash planning.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown(
        f'<span class="status-pill">FORECAST DATE · '
        f'{next_date:%d %b %Y}</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Predicted cash demand",
            money(total_predicted),
            "Across all monitored ATMs",
            CYAN,
        )
    with c2:
        metric_card(
            "Recommended cash",
            money(total_recommended),
            "Includes 10% planning buffer",
            GREEN,
        )
    with c3:
        metric_card(
            "Forecast MAE",
            money(mae) if pd.notna(mae) else "N/A",
            "Held-out historical test period",
            AMBER,
        )
    with c4:
        metric_card(
            "ATMs monitored",
            str(len(forecasts)),
            "With a next-day forecast",
            CYAN,
        )

    st.write("")
    left, right = st.columns([1.65, 1])

    with left:
        section(
            "Demand by ATM",
            "Predicted next-day withdrawal amount, ranked by demand",
        )
        ordered = forecasts.sort_values(
            "predicted_demand", ascending=True
        )
        fig = px.bar(
            ordered,
            x="predicted_demand",
            y="atm_id",
            orientation="h",
            text="predicted_demand",
            color="predicted_demand",
            color_continuous_scale=["#1C496A", CYAN],
            labels={
                "predicted_demand": "Predicted demand (₹)",
                "atm_id": "ATM",
            },
        )
        fig.update_traces(
            texttemplate="₹%{x:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig.update_layout(coloraxis_showscale=False)
        fig = chart_layout(fig, 360)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        section(
            "Cash allocation",
            "Share of recommended cash by ATM",
        )
        fig = px.pie(
            forecasts,
            values="recommended_cash",
            names="atm_id",
            hole=0.72,
            color_discrete_sequence=[
                CYAN, GREEN, "#8C9EFF", AMBER,
                "#A78BFA", "#5EEAD4", "#FB8BBA", "#72A7FF",
            ],
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(line=dict(color=BG, width=3)),
        )
        fig.add_annotation(
            text=f"<b>{money(total_recommended)}</b><br>"
                 "<span style='font-size:11px'>Total plan</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=WHITE, size=17),
        )
        fig = chart_layout(fig, 360)
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    st.write("")
    section("Tomorrow's replenishment plan",
            "Highest-demand ATMs are listed first.")

    table = forecasts.sort_values(
        "predicted_demand", ascending=False
    ).copy()
    table["Predicted demand"] = table["predicted_demand"].map(
        lambda x: money(x, 2)
    )
    table["Recommended cash"] = table["recommended_cash"].map(
        money
    )
    table["Planning buffer"] = (
        table["recommended_cash"] - table["predicted_demand"]
    ).map(money)
    table["Forecast date"] = table["forecast_date"].dt.strftime(
        "%d %b %Y"
    )

    st.dataframe(
        table[[
            "atm_id", "Forecast date", "Predicted demand",
            "Recommended cash", "Planning buffer",
        ]].rename(columns={"atm_id": "ATM ID"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        '<div class="info-strip">Planning note: recommendations '
        'are forecasts with a configurable planning buffer. They '
        'do not represent live ATM cash balances or verified cash '
        'shortages.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# PAGE: FORECAST ANALYTICS
# ---------------------------------------------------------
elif page == "Forecast Analytics":
    st.markdown('<div class="eyebrow">PREDICTIVE INTELLIGENCE / 02</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="page-title">Understand tomorrow\'s demand.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Explore historical withdrawals and '
        'the next-day forecast for individual ATMs.</div>',
        unsafe_allow_html=True,
    )

    atm_ids = sorted(forecasts["atm_id"].unique())
    selected_atm = st.selectbox("Select ATM", atm_ids)

    hist = daily[daily["atm_id"] == selected_atm].sort_values("date")
    forecast_row = forecasts[
        forecasts["atm_id"] == selected_atm
    ].iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Next-day forecast",
                    money(forecast_row["predicted_demand"]),
                    selected_atm, CYAN)
    with c2:
        metric_card("Suggested cash",
                    money(forecast_row["recommended_cash"]),
                    "Includes planning buffer", GREEN)
    with c3:
        metric_card("Planning buffer",
                    money(forecast_row["recommended_cash"]
                          - forecast_row["predicted_demand"]),
                    "Above predicted demand", AMBER)

    st.write("")
    section("Historical demand trend",
            "Daily withdrawals with a seven-day moving average.")

    hist = hist.copy()
    hist["7-day average"] = hist["demand"].rolling(
        7, min_periods=1
    ).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist["date"], y=hist["demand"],
        name="Daily demand", mode="lines",
        line=dict(color=CYAN, width=1.5),
        fill="tozeroy", fillcolor="rgba(84,214,255,.07)",
    ))
    fig.add_trace(go.Scatter(
        x=hist["date"], y=hist["7-day average"],
        name="7-day average", mode="lines",
        line=dict(color=GREEN, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=[forecast_row["forecast_date"]],
        y=[forecast_row["predicted_demand"]],
        name="Next-day forecast", mode="markers",
        marker=dict(color=AMBER, size=13, symbol="diamond"),
    ))
    fig.update_layout(
        yaxis_title="Withdrawal demand (₹)",
        xaxis_title="Date",
    )
    fig = chart_layout(fig, 430)
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        section("Forecast evaluation",
                "Historical holdout metrics for the trained model.")
        if pd.notna(mae):
            st.metric("Mean Absolute Error (MAE)", money(mae, 2))
        if pd.notna(wape):
            st.metric("Weighted Absolute Percentage Error", f"{wape:.2f}%")
        st.caption(
            "Evaluation uses a later chronological test period. "
            "Metrics from simulated data do not establish real-world "
            "banking accuracy."
        )

    with right:
        section("Model configuration")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Forecasting algorithm</div>
                <div class="metric-value" style="font-size:22px">
                    Random Forest
                </div>
                <div class="subtext">
                    150 trees · Maximum depth 12<br>
                    Historical lags: 1, 2 and 7 days<br>
                    Rolling averages: 7 and 14 days<br>
                    Chronological 80/20 train-test split
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# PAGE: ATM OPERATIONS
# ---------------------------------------------------------
elif page == "ATM Operations":
    st.markdown('<div class="eyebrow">CASH OPERATIONS / 03</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="page-title">Replenishment control center.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Review, filter and export the '
        'next-day cash plan for each ATM.</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input("Search ATM ID", placeholder="e.g. ATM003")
    min_demand = st.slider(
        "Minimum predicted demand (₹)",
        min_value=0,
        max_value=int(
            max(1000, forecasts["predicted_demand"].max())
        ),
        value=0,
        step=1000,
    )

    view = forecasts.copy()
    view = view[
        view["predicted_demand"] >= min_demand
    ]
    if search.strip():
        view = view[
            view["atm_id"].str.contains(
                search.strip(), case=False, na=False
            )
        ]

    view = view.sort_values(
        "predicted_demand", ascending=False
    )

    st.write("")
    a, b, c = st.columns(3)
    with a:
        metric_card("Matching ATMs", str(len(view)),
                    "After current filters", CYAN)
    with b:
        metric_card("Demand in selection",
                    money(view["predicted_demand"].sum()),
                    "Predicted withdrawal amount", GREEN)
    with c:
        metric_card("Cash in selection",
                    money(view["recommended_cash"].sum()),
                    "Recommended amount", AMBER)

    st.write("")
    section("ATM replenishment register")

    display = view.rename(columns={
        "atm_id": "ATM ID",
        "forecast_date": "Forecast date",
        "predicted_demand": "Predicted demand (₹)",
        "recommended_cash": "Recommended cash (₹)",
    }).copy()

    display["Forecast date"] = display["Forecast date"].dt.strftime(
        "%d %b %Y"
    )
    display["Predicted demand (₹)"] = display[
        "Predicted demand (₹)"
    ].round(2)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Predicted demand (₹)": st.column_config.NumberColumn(
                format="₹%.2f"
            ),
            "Recommended cash (₹)": st.column_config.NumberColumn(
                format="₹%.0f"
            ),
        },
    )

    st.download_button(
        "Download filtered cash plan",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="atm_replenishment_plan.csv",
        mime="text/csv",
        use_container_width=False,
    )

    st.markdown(
        '<div class="info-strip">This register is a planning aid. '
        'Actual replenishment decisions should also consider live '
        'cash-on-hand, cassette denominations, refill logistics, '
        'and operational constraints, which are not included in '
        'this synthetic dataset.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# PAGE: DATA EXPLORER
# ---------------------------------------------------------
elif page == "Data Explorer":
    st.markdown('<div class="eyebrow">DATA & MODEL AUDIT / 04</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="page-title">Inspect the data behind the forecast.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Explore simulated transactions, '
        'daily aggregates, model metrics and exportable outputs.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs([
        "Transactions", "Daily demand", "Model metrics"
    ])

    with tab1:
        st.caption(f"{len(tx):,} transaction records")
        st.dataframe(
            tx.sort_values("timestamp", ascending=False).head(500),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download transaction dataset",
            data=tx.drop(columns=["date"]).to_csv(index=False).encode(),
            file_name="atm_transactions.csv",
            mime="text/csv",
        )

    with tab2:
        st.caption(f"{len(daily):,} ATM-day records")
        st.dataframe(
            daily.sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download daily demand",
            data=daily.to_csv(index=False).encode(),
            file_name="atm_daily_demand.csv",
            mime="text/csv",
        )

    with tab3:
        if metrics.empty:
            st.warning("Model metrics file was not found.")
        else:
            st.dataframe(metrics, use_container_width=True,
                         hide_index=True)
            st.download_button(
                "Download model metrics",
                data=metrics.to_csv(index=False).encode(),
                file_name="model_metrics.csv",
                mime="text/csv",
            )

        st.markdown(
            """
            <div class="info-strip">
            Data provenance: synthetic withdrawal events generated for
            academic demonstration. Forecast metrics are calculated on
            a chronological holdout. No live bank system is connected.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        ATM INTELLIGENCE · BIG DATA ANALYTICS MINI-PROJECT<br>
        Synthetic data · Forecasts are estimates, not live ATM balances
    </div>
    """,
    unsafe_allow_html=True,
)

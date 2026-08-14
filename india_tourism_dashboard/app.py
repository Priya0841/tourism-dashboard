
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Urban Pulse | India Tourism Intelligence",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. PROFESSIONAL THEME
# ============================================================
st.markdown(
    """
    <style>
        .stApp { background: #07111F; color: #EAF2FF; }
        .main { background: #07111F; }
        .block-container { padding-top: 1.35rem; padding-bottom: 2.8rem; max-width: 1550px; }
        section[data-testid="stSidebar"] { background: #0A1626 !important; border-right: 1px solid #1D3048; }
        section[data-testid="stSidebar"] * { color: #EAF2FF; }
        section[data-testid="stSidebar"] .stMarkdown h3 { color: #F8FAFC !important; font-size: 18px; margin-top: 8px; }
        .hero { background: linear-gradient(135deg, #0D1B2E 0%, #0A1728 100%); border: 1px solid #223A58; border-radius: 18px; padding: 25px 29px; margin-bottom: 20px; box-shadow: 0 10px 28px rgba(0,0,0,.22); }
        .hero-title { font-size: 30px; font-weight: 800; letter-spacing: .15px; margin: 0; color: #F8FAFC; }
        .hero-subtitle { color: #9FB3CC; font-size: 13px; margin-top: 7px; }
        .section-title { font-size: 20px; font-weight: 800; color: #F8FAFC; margin: 25px 0 5px 0; }
        .section-note { color: #8FA6C1; font-size: 12px; margin-top: -1px; margin-bottom: 12px; }
        div[data-testid="stMetric"] { background: #0D1A2C; border: 1px solid #213852; border-radius: 15px; padding: 15px 17px; min-height: 105px; box-shadow: 0 8px 22px rgba(0,0,0,.18); }
        div[data-testid="stMetricLabel"] label { color: #8FA6C1 !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: .4px; }
        div[data-testid="stMetricValue"] { color: #F8FAFC !important; font-weight: 800 !important; }
        .stSelectbox label, .stMultiSelect label { color: #B8C8DA !important; font-size: 11px !important; font-weight: 700 !important; }
        [data-baseweb="select"] > div { background: #0D1929; border-color: #29415E; border-radius: 9px; color: #F8FAFC; }
        [data-baseweb="select"] span { color: #F8FAFC !important; }
        div[data-baseweb="popover"] { background: #0D1929; }
        .stDataFrame { border: 1px solid #213852; border-radius: 12px; background: #0D1A2C; }
        .small-caption { color: #8198B2; font-size: 11px; }
        .section-header { margin-top: 28px; margin-bottom: 18px; }
        .section-header h2 { font-size: 24px; margin-bottom: 4px; }
        .section-header p { color: #94a3b8; font-size: 14px; margin-top: 0; }
        .insight-card { background: #0f1b2d; border: 1px solid #24344d; border-radius: 12px; padding: 18px 22px; margin-top: 12px; }
        .insight-title { font-size: 17px; font-weight: 700; margin-bottom: 14px; }
        .insight-row { display: flex; justify-content: space-between; align-items: center; padding: 9px 0; border-bottom: 1px solid #1e2b3e; }
        .insight-label { color: #cbd5e1; font-size: 14px; }
        .insight-value { color: #f8fafc; font-weight: 600; font-size: 14px; }
        .insight-value.positive { color: #34d399; }
        .insight-value.negative { color: #f87171; }
        .insight-note { color: #94a3b8; font-size: 12px; margin-top: 14px; line-height: 1.5; }
        hr { border-color: #20354E !important; }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. DATA PATH
# ============================================================
BASE_DIR = Path(__file__).resolve().parent


def csv_path(filename: str) -> Path:
    return BASE_DIR / filename


# ============================================================
# 4. LOAD ONLY THE SUPPLIED PROJECT DATA
# ============================================================
@st.cache_data
def load_data():
    required = [
        "dim_country_rows.csv",
        "dim_location_rows.csv",
        "dim_time_rows.csv",
        "dim_weather_rows.csv",
        "fact_attractions_rows.csv",
        "fact_country_arrivals_rows.csv",
        "fact_festivals_rows.csv",
        "fact_monthly_tourism_rows.csv",
        "view_galaxy_monthly_tourism_rows.csv",
        "view_weather_tourism_analysis_rows.csv",
    ]

    missing = [f for f in required if not csv_path(f).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing project CSV file(s): " + ", ".join(missing)
        )

    dim_country = pd.read_csv(csv_path("dim_country_rows.csv"))
    dim_location = pd.read_csv(csv_path("dim_location_rows.csv"))
    dim_time = pd.read_csv(csv_path("dim_time_rows.csv"))
    dim_weather = pd.read_csv(csv_path("dim_weather_rows.csv"))
    attractions = pd.read_csv(csv_path("fact_attractions_rows.csv"))
    country_arrivals = pd.read_csv(csv_path("fact_country_arrivals_rows.csv"))
    festivals = pd.read_csv(csv_path("fact_festivals_rows.csv"))
    monthly = pd.read_csv(csv_path("fact_monthly_tourism_rows.csv"))
    galaxy = pd.read_csv(csv_path("view_galaxy_monthly_tourism_rows.csv"))
    weather_tourism = pd.read_csv(
        csv_path("view_weather_tourism_analysis_rows.csv")
    )

    # Numeric cleanup
    for df, cols in [
        (dim_location, ["latitude", "longitude"]),
        (attractions, ["google_rating", "entry_fee"]),
        (country_arrivals, ["arrivals_in_numbers", "average_duration_of_stay_in_days"]),
        (festivals, ["amount_sanctioned", "amount_released"]),
        (monthly, ["tourism_revenue_crore_inr", "foreign_tourist_arrivals"]),
        (galaxy, ["tourism_revenue_crore_inr", "foreign_tourist_arrivals"]),
        (
            weather_tourism,
            [
                "tourism_revenue_crore_inr",
                "foreign_tourist_arrivals",
                "temp_c",
                "rainfall_mm",
                "humidity_pct",
            ],
        ),
        (
            dim_weather,
            ["temp_c", "rainfall_mm", "humidity_pct"],
        ),
    ]:
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    attractions = attractions[
        attractions["google_rating"].between(0, 5, inclusive="both")
    ].copy()

    # Join attraction + location.
    attr = attractions.merge(
        dim_location,
        on="location_id",
        how="left",
        suffixes=("", "_location"),
    )

    # Join country arrivals + country dimension.
    countries = country_arrivals.merge(
        dim_country,
        on="country_id",
        how="left",
    )

    # Time enrichment. The monthly CSV already contains year/month fields,
    # so merge only the missing time-dimension fields and coalesce safely.
    time = dim_time.copy()
    time["Season"] = time["month_name"].apply(
        lambda m: (
            "Peak Season"
            if m in [
                "October", "November", "December",
                "January", "February", "March",
            ]
            else "Off-Peak Season"
        )
    )

    time_lookup = time[[
        "time_id", "year", "month_name", "month_num", "quarter", "Season"
    ]].copy()

    monthly_enriched = monthly.merge(
        time_lookup,
        on="time_id",
        how="left",
        suffixes=("", "_time"),
    )

    for col in ["year", "month_name", "month_num", "quarter", "Season"]:
        dim_col = f"{col}_time"
        if col not in monthly_enriched.columns and dim_col in monthly_enriched.columns:
            monthly_enriched.rename(columns={dim_col: col}, inplace=True)
        elif col in monthly_enriched.columns and dim_col in monthly_enriched.columns:
            monthly_enriched[col] = monthly_enriched[col].combine_first(
                monthly_enriched[dim_col]
            )
            monthly_enriched.drop(columns=[dim_col], inplace=True)

    # Normalize year/month fields so filters never depend on pandas suffixes.
    if "year" in monthly_enriched.columns:
        monthly_enriched["year"] = pd.to_numeric(
            monthly_enriched["year"], errors="coerce"
        )

    galaxy_enriched = galaxy.copy()
    galaxy_enriched["Season"] = galaxy_enriched["month_name"].apply(
        lambda m: (
            "Peak Season"
            if m in [
                "October",
                "November",
                "December",
                "January",
                "February",
                "March",
            ]
            else "Off-Peak Season"
        )
    )

    # Weather-tourism view + location coordinates.
    weather_geo = weather_tourism.merge(
        dim_location[["city", "state", "latitude", "longitude"]],
        left_on="location_name",
        right_on="city",
        how="left",
    )

    return {
        "dim_country": dim_country,
        "dim_location": dim_location,
        "dim_time": time,
        "dim_weather": dim_weather,
        "attractions": attr,
        "countries": countries,
        "festivals": festivals,
        "monthly": monthly_enriched,
        "galaxy": galaxy_enriched,
        "weather": weather_geo,
    }


try:
    data = load_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()


attr = data["attractions"]
countries = data["countries"]
festivals = data["festivals"]
monthly = data["monthly"]
weather = data["weather"]
dim_time = data["dim_time"]


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================
COLORS = {
    "cyan": "#38BDF8", "blue": "#4F8CFF", "teal": "#22C7B8",
    "gold": "#F5B84B", "green": "#35D07F", "red": "#FF6B6B",
    "purple": "#9B7CFF", "orange": "#FFB84D", "text": "#EAF2FF",
    "muted": "#9FB3CC", "grid": "#29415E", "panel": "#0D1A2C",
    "bg": "#07111F",
}


def format_number(value):
    if pd.isna(value):
        return "—"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def month_sort(df, col="month_name"):
    out = df.copy()
    if col in out.columns:
        out[col] = pd.Categorical(out[col], categories=MONTH_ORDER, ordered=True)
        out = out.sort_values(col)
    return out


def chart_layout(fig, height=330, title=None):
    fig.update_layout(
        title=dict(text=title or "", x=0.02, xanchor="left", font=dict(size=15, color=COLORS["text"], family="Arial")),
        height=height, paper_bgcolor=COLORS["panel"], plot_bgcolor=COLORS["panel"],
        font=dict(color=COLORS["text"], size=11, family="Arial"),
        margin=dict(l=72, r=42, t=72 if title else 20, b=62),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["muted"], size=10)),
        hoverlabel=dict(bgcolor="#13243A", bordercolor="#35516F", font_color="#F8FAFC"),
        xaxis=dict(gridcolor=COLORS["grid"], zeroline=False, automargin=True, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]), linecolor="#29415E"),
        yaxis=dict(gridcolor=COLORS["grid"], zeroline=False, automargin=True, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]), linecolor="#29415E"),
    )
    return fig


def empty_chart(message="No data available for the selected filters."):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(color=COLORS["muted"], size=13),
    )
    chart_layout(fig, height=300)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# ============================================================
# 6. SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding:4px 0 12px 0;">
            <div style="font-size:20px;font-weight:800;color:#F8FAFC;">
                URBAN PULSE
            </div>
            <div style="font-size:11px;color:#9FB3CC;">
                Tourism Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Dashboard Filters")

    years = sorted(monthly["year"].dropna().unique().astype(int).tolist())
    selected_year = st.selectbox("Year", ["All"] + years)

    quarters = ["All", "Q1", "Q2", "Q3", "Q4"]
    selected_quarter = st.selectbox("Quarter", quarters)

    months = [
        "All",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    selected_month = st.selectbox("Month", months)

    selected_season = st.selectbox(
        "Season",
        ["All", "Peak Season", "Off-Peak Season"],
    )

    states = ["All"] + sorted(attr["state"].dropna().astype(str).unique())
    selected_state = st.selectbox("State", states)

    if selected_state != "All":
        city_values = sorted(
            attr.loc[attr["state"] == selected_state, "city"]
            .dropna()
            .astype(str)
            .unique()
        )
    else:
        city_values = sorted(attr["city"].dropna().astype(str).unique())

    selected_city = st.selectbox("City", ["All"] + city_values)

    categories = ["All"] + sorted(
        attr["category"].dropna().astype(str).unique()
    )
    selected_category = st.selectbox("Tourism Category", categories)

    country_values = ["All"] + sorted(
        countries.loc[
            ~countries["country_name"].astype(str).str.strip().isin(["Total", "Others"]),
            "country_name",
        ].dropna().astype(str).unique()
    )
    selected_country = st.selectbox("Origin Country", country_values)

    st.markdown("---")
    st.markdown(
        """
        <div class="small-caption">
        Source policy: dashboard uses only the supplied project CSV datasets.
        No external tourism data is added.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. APPLY FILTERS
# ============================================================
filtered_attr = attr.copy()

if selected_state != "All":
    filtered_attr = filtered_attr[filtered_attr["state"] == selected_state]

if selected_city != "All":
    filtered_attr = filtered_attr[filtered_attr["city"] == selected_city]

if selected_category != "All":
    filtered_attr = filtered_attr[filtered_attr["category"] == selected_category]


filtered_monthly = monthly.copy()

if selected_year != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["year"] == int(selected_year)
    ]

if selected_quarter != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["quarter"] == selected_quarter
    ]

if selected_month != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["month_name"] == selected_month
    ]

if selected_season != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["Season"] == selected_season
    ]


filtered_country = countries.copy()
# Remove aggregate rows from source-country ranking; they are not individual countries.
filtered_country = filtered_country[
    ~filtered_country["country_name"].astype(str).str.strip().isin(["Total", "Others"])
].copy()

if selected_country != "All":
    filtered_country = filtered_country[
        filtered_country["country_name"] == selected_country
    ]


filtered_festivals = festivals.copy()

if selected_state != "All":
    filtered_festivals = filtered_festivals[
        filtered_festivals["state"].astype(str).str.contains(
            selected_state, case=False, na=False
        )
    ]

if selected_year != "All":
    filtered_festivals = filtered_festivals[
        filtered_festivals["year"].astype(str).str.startswith(
            str(selected_year)
        )
    ]


filtered_weather = weather.copy()

if selected_year != "All":
    filtered_weather = filtered_weather[
        filtered_weather["year"] == int(selected_year)
    ]

if selected_month != "All":
    filtered_weather = filtered_weather[
        filtered_weather["month"] == selected_month
    ]

if selected_state != "All":
    filtered_weather = filtered_weather[
        filtered_weather["state"].astype(str).str.contains(
            selected_state, case=False, na=False
        )
    ]

if selected_city != "All":
    filtered_weather = filtered_weather[
        filtered_weather["city"].astype(str).str.contains(
            selected_city, case=False, na=False
        )
    ]


# ============================================================
# 8. HEADER
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🇮🇳 INCREDIBLE INDIA TOURISM INTELLIGENCE</div>
        <div class="hero-subtitle">
            Unified tourism, attraction, festival, foreign-arrival and weather analytics
            built exclusively from the supplied project datasets.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 9. KPI CARDS
# ============================================================
total_places = len(filtered_attr)
avg_rating = filtered_attr["google_rating"].mean() if not filtered_attr.empty else 0
avg_fee = filtered_attr["entry_fee"].mean() if not filtered_attr.empty else 0
foreign_arrivals = (
    filtered_monthly["foreign_tourist_arrivals"].sum()
    if not filtered_monthly.empty
    else 0
)
revenue = (
    filtered_monthly["tourism_revenue_crore_inr"].sum()
    if not filtered_monthly.empty
    else 0
)
festival_count = len(filtered_festivals)

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Tourist Places", format_number(total_places))
k2.metric("Average Rating", f"{avg_rating:.2f} / 5")
k3.metric("Average Entry Fee", f"₹{avg_fee:,.0f}")
k4.metric("Foreign Arrivals", format_number(foreign_arrivals))
k5.metric("Tourism Revenue", f"₹{revenue:,.0f} Cr")
k6.metric("Festival Records", format_number(festival_count))


# ============================================================
# 10. MAIN DEMAND & GEOGRAPHY
# ============================================================
st.markdown(
    '<div class="section-title">Demand & Geographic Intelligence</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Attraction density, location distribution and geographic drill-down.</div>',
    unsafe_allow_html=True,
)

map_col, cat_col = st.columns([1.55, 1])

with map_col:
    st.markdown("**Tourist Attraction Density Map**")

    map_df = filtered_attr.dropna(subset=["latitude", "longitude"]).copy()

    if not map_df.empty:
        m = folium.Map(
            location=[
                map_df["latitude"].mean(),
                map_df["longitude"].mean(),
            ],
            zoom_start=5,
            tiles="CartoDB positron",
        )

        # Density is based on the number of supplied attraction records at a location.
        location_density = (
            map_df.groupby(["latitude", "longitude"])
            .size()
            .reset_index(name="attraction_count")
        )

        heat_data = [
            [r.latitude, r.longitude, r.attraction_count]
            for r in location_density.itertuples()
        ]

        HeatMap(
            heat_data,
            radius=20,
            blur=18,
            min_opacity=0.35,
            max_zoom=8,
        ).add_to(m)

        for row in (
            map_df.groupby(
                ["location_id", "state", "city", "latitude", "longitude"]
            )
            .agg(
                attractions=("place_name", "count"),
                avg_rating=("google_rating", "mean"),
            )
            .reset_index()
            .itertuples()
        ):
            folium.CircleMarker(
                location=[row.latitude, row.longitude],
                radius=max(4, min(10, row.attractions)),
                tooltip=f"{row.city}, {row.state}",
                popup=(
                    f"<b>{row.city}</b><br>"
                    f"{row.state}<br>"
                    f"Attractions: {row.attractions}<br>"
                    f"Avg rating: {row.avg_rating:.2f}"
                ),
                color=COLORS["cyan"],
                fill=True,
                fill_opacity=0.75,
            ).add_to(m)

        st_folium(
            m,
            width=None,
            height=430,
            use_container_width=True,
        )

    else:
        st.info("No geographic attraction records match the selected filters.")


with cat_col:
    category_counts = (
        filtered_attr["category"]
        .value_counts()
        .rename_axis("Category")
        .reset_index(name="Places")
        .head(10)
        .sort_values("Places")
    )

    if not category_counts.empty:
        fig = px.bar(
            category_counts,
            x="Places",
            y="Category",
            orientation="h",
            text="Places",
        )
        fig.update_traces(
            marker_color=COLORS["teal"],
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False,
        )
        fig.update_xaxes(title="Number of Places", rangemode="tozero")
        fig.update_yaxes(title="", automargin=True)
        chart_layout(fig, height=430, title="Top Tourism Categories")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 11. TOP PLACES + VALUE ANALYSIS
# ============================================================
st.markdown(
    '<div class="section-title">Attraction Performance</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1])

with left:
    top_places = (
        filtered_attr.sort_values(
            ["google_rating", "place_name"],
            ascending=[False, True],
        )
        .head(10)
        .sort_values("google_rating")
    )

    if not top_places.empty:
        fig = px.bar(
            top_places,
            x="google_rating",
            y="place_name",
            orientation="h",
            text="google_rating",
            hover_data=["city", "state", "entry_fee"],
        )
        fig.update_traces(
            marker_color=COLORS["cyan"],
            texttemplate="%{text:.1f}",
            textposition="outside",
        )
        fig.update_xaxes(range=[0, 5.2], title="Google Rating")
        fig.update_yaxes(title="")
        chart_layout(fig, height=420, title="Top 10 Highest-Rated Tourist Places")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

with right:
    if not filtered_attr.empty:
        value_df = filtered_attr[
            [
                "place_name",
                "city",
                "state",
                "category",
                "entry_fee",
                "google_rating",
            ]
        ].copy()

        value_df["entry_fee"] = pd.to_numeric(value_df["entry_fee"], errors="coerce")
        value_df["google_rating"] = pd.to_numeric(value_df["google_rating"], errors="coerce")
        value_df = value_df.dropna(subset=["entry_fee", "google_rating"])
        value_df = value_df[
            (value_df["entry_fee"] >= 0)
            & (value_df["google_rating"] >= 0)
            & (value_df["google_rating"] <= 5)
        ]

        if not value_df.empty:
            fig_value = go.Figure()
            fee_plot = value_df["entry_fee"].where(value_df["entry_fee"] > 0, 1)

            fig_value.add_trace(
                go.Scatter(
                    x=fee_plot,
                    y=value_df["google_rating"],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color="#38BDF8",
                        opacity=0.75,
                        line=dict(width=0.8, color="#BFE7FF"),
                    ),
                    customdata=value_df[
                        [
                            "place_name",
                            "city",
                            "state",
                            "category",
                            "entry_fee",
                            "google_rating",
                        ]
                    ].values,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "City: %{customdata[1]}<br>"
                        "State: %{customdata[2]}<br>"
                        "Category: %{customdata[3]}<br>"
                        "Entry Fee: ₹%{customdata[4]:,.0f}<br>"
                        "Google Rating: %{customdata[5]:.1f}/5"
                        "<extra></extra>"
                    ),
                    name="Tourist Places",
                )
            )

            median_fee = value_df["entry_fee"].median()
            median_rating = value_df["google_rating"].median()

            fig_value.add_vline(
                x=median_fee if median_fee > 0 else 1,
                line_dash="dash",
                line_color="#94A3B8",
                line_width=1,
            )
            fig_value.add_hline(
                y=median_rating,
                line_dash="dash",
                line_color="#94A3B8",
                line_width=1,
            )

            fig_value.update_layout(
                height=520,
                margin=dict(l=65, r=30, t=35, b=65),
                title=dict(
                    text="Entry Fee vs Google Rating",
                    x=0.02,
                    xanchor="left",
                    font=dict(size=20),
                ),
                xaxis=dict(
                    title="Entry Fee (₹)",
                    type="log",
                    tickformat="~s",
                    showgrid=True,
                    zeroline=False,
                    fixedrange=False,
                ),
                yaxis=dict(
                    title="Google Rating (out of 5)",
                    range=[0, 5.2],
                    dtick=1,
                    showgrid=True,
                    zeroline=False,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                ),
                hovermode="closest",
                paper_bgcolor=COLORS["panel"],
                plot_bgcolor=COLORS["panel"],
                font=dict(color=COLORS["text"], size=11, family="Arial"),
            )

            st.plotly_chart(
                fig_value,
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )

            st.markdown(
                """
                <div class="insight-card">
                    <div class="insight-title">How to read this chart</div>
                    <div class="insight-row">
                        <span class="insight-label">Higher rating + lower fee</span>
                        <span class="insight-value positive">Better visitor value</span>
                    </div>
                    <div class="insight-row">
                        <span class="insight-label">Higher rating + higher fee</span>
                        <span class="insight-value">Premium experience</span>
                    </div>
                    <div class="insight-row">
                        <span class="insight-label">Lower rating + higher fee</span>
                        <span class="insight-value negative">Lower value</span>
                    </div>
                    <div class="insight-note">
                        Free attractions are shown separately near the left side of the
                        logarithmic scale so they do not distort paid-entry comparisons.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No valid tourist value data available for the selected filters.")
    else:
        st.info("No tourist attraction data available for the selected filters.")


# ============================================================
# 12. TOURISM ARRIVALS + REVENUE
# ============================================================
st.markdown(
    '<div class="section-title">Tourism Demand & Economic Trends</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Monthly national tourism indicators. When multiple years are selected, each year is shown separately to avoid misleading connections.</div>',
    unsafe_allow_html=True,
)

trend1, trend2 = st.columns(2)

trend_monthly = (
    filtered_monthly.groupby(["year", "month_name"], as_index=False)
    .agg(
        foreign_tourist_arrivals=("foreign_tourist_arrivals", "sum"),
        tourism_revenue_crore_inr=("tourism_revenue_crore_inr", "sum"),
    )
)
trend_monthly = month_sort(trend_monthly, "month_name")

with trend1:
    if not trend_monthly.empty:
        fig = px.line(
            trend_monthly,
            x="month_name",
            y="foreign_tourist_arrivals",
            color="year",
            markers=True,
            labels={
                "month_name": "Month",
                "foreign_tourist_arrivals": "Foreign Tourist Arrivals",
                "year": "Year",
            },
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
        fig.update_xaxes(categoryorder="array", categoryarray=MONTH_ORDER)
        fig.update_yaxes(rangemode="tozero")
        chart_layout(fig, height=350, title="Foreign Tourist Arrivals")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

with trend2:
    if not trend_monthly.empty:
        fig = px.line(
            trend_monthly,
            x="month_name",
            y="tourism_revenue_crore_inr",
            color="year",
            markers=True,
            labels={
                "month_name": "Month",
                "tourism_revenue_crore_inr": "Revenue (₹ Crore)",
                "year": "Year",
            },
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
        fig.update_xaxes(categoryorder="array", categoryarray=MONTH_ORDER)
        fig.update_yaxes(rangemode="tozero")
        chart_layout(fig, height=350, title="Tourism Revenue")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 13. COUNTRY-WISE FOREIGN TOURISM
# ============================================================
st.markdown(
    '<div class="section-title">International Tourist Profile</div>',
    unsafe_allow_html=True,
)

country_chart, country_table = st.columns([1.45, 1])

with country_chart:
    top_countries = (
        filtered_country.groupby("country_name", as_index=False)
        .agg(
            arrivals=("arrivals_in_numbers", "sum"),
            avg_stay=("average_duration_of_stay_in_days", "mean"),
        )
        .sort_values("arrivals", ascending=False)
        .head(12)
        .sort_values("arrivals")
    )

    if not top_countries.empty:
        fig = px.bar(
            top_countries,
            x="arrivals",
            y="country_name",
            orientation="h",
            text="arrivals",
            hover_data={"avg_stay": ":.1f"},
        )
        fig.update_traces(
            marker_color=COLORS["teal"],
            texttemplate="%{text:,.0f}",
            textposition="outside",
        )
        fig.update_xaxes(title="Arrivals")
        fig.update_yaxes(title="")
        chart_layout(
            fig,
            height=430,
            title="Top Source Countries by Foreign Arrivals",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

with country_table:
    st.markdown("**Country Profile**")

    profile = (
        filtered_country.groupby("country_name", as_index=False)
        .agg(
            Arrivals=("arrivals_in_numbers", "sum"),
            Avg_Stay_Days=("average_duration_of_stay_in_days", "mean"),
        )
        .sort_values("Arrivals", ascending=False)
        .head(12)
    )

    if not profile.empty:
        profile["Avg_Stay_Days"] = profile["Avg_Stay_Days"].round(1)
        st.dataframe(
            profile,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No country records match the selected filter.")


# ============================================================
# 14. FESTIVAL FUNDING ANALYSIS
# ============================================================
st.markdown(
    '<div class="section-title">Festival Funding & Cultural Activity</div>',
    unsafe_allow_html=True,
)

fest1, fest2 = st.columns([1.25, 1])

with fest1:
    fest_budget = (
        filtered_festivals.groupby("festival_name", as_index=False)
        .agg(
            sanctioned=("amount_sanctioned", "sum"),
            released=("amount_released", "sum"),
        )
        .sort_values("sanctioned", ascending=False)
        .head(10)
    )

    if not fest_budget.empty:
        long_fest = fest_budget.melt(
            id_vars="festival_name",
            value_vars=["sanctioned", "released"],
            var_name="Budget Type",
            value_name="Amount",
        )

        long_fest["Budget Type"] = long_fest["Budget Type"].map(
            {
                "sanctioned": "Sanctioned",
                "released": "Released",
            }
        )

        fig = px.bar(
            long_fest.sort_values("Amount"),
            x="Amount",
            y="festival_name",
            color="Budget Type",
            barmode="group",
            orientation="h",
            color_discrete_map={
                "Sanctioned": COLORS["blue"],
                "Released": COLORS["gold"],
            },
            labels={
                "festival_name": "Festival",
                "Amount": "Funding Amount",
            },
        )
        fig.update_yaxes(title="", automargin=True)
        fig.update_xaxes(title="Funding Amount")
        chart_layout(
            fig,
            height=450,
            title="Festival Sanctioned vs Released Funding",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

with fest2:
    release = (
        filtered_festivals.groupby("festival_name", as_index=False)
        .agg(
            sanctioned=("amount_sanctioned", "sum"),
            released=("amount_released", "sum"),
        )
    )

    if not release.empty:
        release["release_pct"] = (
            release["released"] / release["sanctioned"].replace(0, pd.NA) * 100
        )
        release = (
            release.sort_values("release_pct", ascending=False)
            .head(10)
            .sort_values("release_pct")
        )

        fig = px.bar(
            release,
            x="release_pct",
            y="festival_name",
            orientation="h",
            text="release_pct",
        )
        fig.update_traces(
            marker_color=COLORS["green"],
            texttemplate="%{text:.0f}%",
            textposition="outside",
        )
        fig.update_xaxes(title="Released / Sanctioned (%)")
        fig.update_yaxes(title="")
        chart_layout(
            fig,
            height=420,
            title="Festival Budget Release Efficiency",
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 15. GEOGRAPHIC DRILL-DOWN
# ============================================================
st.markdown(
    '<div class="section-title">Geographic Drill-Down</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">State → City → Tourist Place using the supplied location and attraction dimensions.</div>',
    unsafe_allow_html=True,
)

geo = filtered_attr.copy()

if not geo.empty:
    geo_summary = (
        geo.groupby(["state", "city", "place_name"], as_index=False)
        .agg(
            Rating=("google_rating", "mean"),
            Entry_Fee=("entry_fee", "mean"),
            Category=("category", "first"),
        )
        .sort_values(["state", "city", "Rating"], ascending=[True, True, False])
    )

    states_available = sorted(geo_summary["state"].unique())
    drill_state = st.selectbox(
        "Drill-down State",
        ["All"] + states_available,
        key="drill_state",
    )

    drill = geo_summary.copy()

    if drill_state != "All":
        drill = drill[drill["state"] == drill_state]

    cities_available = sorted(drill["city"].unique())
    drill_city = st.selectbox(
        "Drill-down City",
        ["All"] + cities_available,
        key="drill_city",
    )

    if drill_city != "All":
        drill = drill[drill["city"] == drill_city]

    st.dataframe(
        drill[
            ["state", "city", "place_name", "Category", "Rating", "Entry_Fee"]
        ].rename(
            columns={
                "state": "State",
                "city": "City",
                "place_name": "Tourist Place",
                "Category": "Category",
                "Rating": "Rating",
                "Entry_Fee": "Entry Fee (₹)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No geographic records match the selected filters.")


# ============================================================
# 16. WEATHER IMPACT
# ============================================================
st.markdown(
    '<div class="section-title">Weather Impact on Tourism</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Monthly foreign arrivals compared with temperature, rainfall and humidity from the supplied weather-tourism view.</div>',
    unsafe_allow_html=True,
)

if not filtered_weather.empty:
    weather_monthly = (
        filtered_weather.groupby("month", as_index=False)
        .agg(
            foreign_tourist_arrivals=("foreign_tourist_arrivals", "first"),
            temp_c=("temp_c", "mean"),
            rainfall_mm=("rainfall_mm", "mean"),
            humidity_pct=("humidity_pct", "mean"),
        )
    )

    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    weather_monthly["month"] = pd.Categorical(
        weather_monthly["month"],
        categories=month_order,
        ordered=True,
    )
    weather_monthly = weather_monthly.sort_values("month")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=weather_monthly["month"],
            y=weather_monthly["foreign_tourist_arrivals"],
            name="Foreign Arrivals",
            marker_color=COLORS["cyan"],
            yaxis="y",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=weather_monthly["month"],
            y=weather_monthly["temp_c"],
            name="Temperature (°C)",
            mode="lines+markers",
            line=dict(color=COLORS["gold"], width=2.5),
            yaxis="y2",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=weather_monthly["month"],
            y=weather_monthly["rainfall_mm"],
            name="Rainfall (mm)",
            mode="lines+markers",
            line=dict(color=COLORS["purple"], width=2.5),
            yaxis="y2",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=weather_monthly["month"],
            y=weather_monthly["humidity_pct"],
            name="Humidity (%)",
            mode="lines+markers",
            line=dict(color=COLORS["green"], width=2.5),
            yaxis="y2",
        )
    )

    fig.update_layout(
        height=450,
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font=dict(color=COLORS["text"], family="Arial", size=11),
        margin=dict(l=78, r=78, t=88, b=62),
        title=dict(
            text="Weather Conditions vs Foreign Tourist Arrivals",
            x=0.02,
            font=dict(size=15, color=COLORS["text"]),
        ),
        xaxis=dict(
            title="Month",
            gridcolor=COLORS["grid"],
            tickangle=0,
            automargin=True,
        ),
        yaxis=dict(
            title="Foreign Tourist Arrivals",
            gridcolor=COLORS["grid"],
            tickformat="~s",
            automargin=True,
        ),
        yaxis2=dict(
            title="Weather Metrics",
            overlaying="y",
            side="right",
            showgrid=False,
            automargin=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(size=10, color=COLORS["muted"]),
            bgcolor="rgba(255,255,255,0)",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 17. WEATHER MAP
# ============================================================
weather_map_col, weather_summary_col = st.columns([1.4, 1])

with weather_map_col:
    weather_geo = filtered_weather.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    if not weather_geo.empty:
        latest_weather = (
            weather_geo.sort_values("time_id")
            .groupby(["city", "state", "latitude", "longitude"], as_index=False)
            .tail(1)
        )

        fig = px.scatter_mapbox(
            latest_weather,
            lat="latitude",
            lon="longitude",
            color="temp_c",
            size="rainfall_mm",
            hover_name="city",
            hover_data=[
                "state",
                "temp_c",
                "rainfall_mm",
                "humidity_pct",
            ],
            color_continuous_scale="Turbo",
            center={"lat": 20.5937, "lon": 78.9629},
            zoom=3.8,
            mapbox_style="carto-positron",
        )

        fig.update_layout(
            height=430,
            paper_bgcolor=COLORS["panel"],
            plot_bgcolor=COLORS["panel"],
            margin=dict(l=0, r=0, t=48, b=0),
            title=dict(
                text="Weather Conditions Across Tourist Locations",
                x=0.02,
                font=dict(size=15, color=COLORS["text"]),
            ),
            font=dict(color=COLORS["text"], family="Arial"),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)

with weather_summary_col:
    if not filtered_weather.empty:
        avg_temp = filtered_weather["temp_c"].mean()
        avg_rain = filtered_weather["rainfall_mm"].mean()
        avg_humidity = filtered_weather["humidity_pct"].mean()

        a, b = st.columns(2)
        a.metric("Avg Temperature", f"{avg_temp:.1f} °C")
        b.metric("Avg Rainfall", f"{avg_rain:.1f} mm")

        st.metric("Avg Humidity", f"{avg_humidity:.1f}%")

        weather_corr = filtered_weather[
            [
                "foreign_tourist_arrivals",
                "temp_c",
                "rainfall_mm",
                "humidity_pct",
            ]
        ].corr()["foreign_tourist_arrivals"].drop(
            "foreign_tourist_arrivals"
        )

        corr_df = weather_corr.rename("Correlation").reset_index()
        corr_df.columns = ["Weather Metric", "Correlation"]

        fig = px.bar(
            corr_df,
            x="Correlation",
            y="Weather Metric",
            orientation="h",
            range_x=[-1, 1],
            text="Correlation",
        )
        fig.update_traces(marker_color=COLORS["purple"])
        chart_layout(
            fig,
            height=270,
            title="Weather / Foreign Arrival Correlation",
        )
        st.plotly_chart(fig, use_container_width=True)



# ============================================================
# 18. FOOTER
# ============================================================
st.markdown(
    """
    <div style="
        margin-top:26px;
        padding:16px 0 4px 0;
        border-top:1px solid #E1E7EF;
        color:#9FB3CC;
        font-size:11px;
        text-align:center;
    ">
        Urban Pulse • India Tourism Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)

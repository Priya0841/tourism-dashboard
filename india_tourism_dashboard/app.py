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
# 1. PAGE
# ============================================================
st.set_page_config(
    page_title="Urban Pulse | India Tourism Intelligence",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. LIGHT PROFESSIONAL THEME
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #060B12 0%, #0B1220 100%);
        color: #E5ECF6;
    }

    [data-testid="stSidebar"] {
        background: #0D141D !important;
        border-right: 1px solid #1B2635;
    }

    [data-testid="stSidebar"] * {
        color: #E5ECF6;
    }

    .block-container {
        max-width: 1550px;
        padding: 1.25rem 1.5rem 2.5rem 1.5rem;
    }

    .brand {
        padding: 4px 0 22px 0;
    }

    .brand-title {
        font-size: 23px;
        font-weight: 800;
        color: #D4AF37;
        letter-spacing: .3px;
    }

    .brand-subtitle {
        font-size: 12px;
        color: #9AA9BA;
        margin-top: 2px;
    }

    .hero {
        background: linear-gradient(135deg, #111827 0%, #0F172A 100%);
        border: 1px solid #243244;
        border-radius: 18px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
    }

    .hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
    }

    .hero-subtitle {
        font-size: 13px;
        color: #B4C1D3;
        margin-top: 6px;
    }

    .section-title {
        font-size: 19px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 22px 0 4px 0;
    }

    .section-note {
        font-size: 12px;
        color: #9AA9BA;
        margin-bottom: 10px;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #111827 0%, #0F172A 100%);
        border: 1px solid #243244;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
        min-height: 105px;
    }

    [data-testid="stMetricLabel"] label {
        color: #A8B4C7 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }

    .card {
        background: #0F172A;
        border: 1px solid #243244;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
    }

    .stSelectbox label,
    .stMultiSelect label {
        color: #D9E4F2 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }

    .stDataFrame {
        border: 1px solid #243244;
        border-radius: 12px;
        background: #0F172A;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. DATA LOCATION
# ============================================================
BASE_DIR = Path(__file__).resolve().parent


def csv_path(filename: str) -> Path:
    return BASE_DIR / filename


REQUIRED_FILES = [
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


# ============================================================
# 4. LOAD ONLY THE SUPPLIED CSV DATA
# ============================================================
@st.cache_data
def load_data():
    missing = [f for f in REQUIRED_FILES if not csv_path(f).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing CSV file(s): " + ", ".join(missing)
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

    numeric_columns = {
        "dim_location": ["latitude", "longitude"],
        "dim_weather": ["temp_c", "rainfall_mm", "humidity_pct"],
        "attractions": ["google_rating", "entry_fee"],
        "country_arrivals": [
            "arrivals_in_numbers",
            "average_duration_of_stay_in_days",
        ],
        "festivals": ["amount_sanctioned", "amount_released"],
        "monthly": ["tourism_revenue_crore_inr", "foreign_tourist_arrivals"],
        "galaxy": ["tourism_revenue_crore_inr", "foreign_tourist_arrivals"],
        "weather_tourism": [
            "tourism_revenue_crore_inr",
            "foreign_tourist_arrivals",
            "temp_c",
            "rainfall_mm",
            "humidity_pct",
        ],
    }

    frames = {
        "dim_location": dim_location,
        "dim_weather": dim_weather,
        "attractions": attractions,
        "country_arrivals": country_arrivals,
        "festivals": festivals,
        "monthly": monthly,
        "galaxy": galaxy,
        "weather_tourism": weather_tourism,
    }

    for name, cols in numeric_columns.items():
        for col in cols:
            if col in frames[name].columns:
                frames[name][col] = pd.to_numeric(
                    frames[name][col], errors="coerce"
                )

    attractions = attractions[
        attractions["google_rating"].between(0, 5, inclusive="both")
    ].copy()

    attr = attractions.merge(
        dim_location,
        on="location_id",
        how="left",
        suffixes=("", "_location"),
    )

    countries = country_arrivals.merge(
        dim_country,
        on="country_id",
        how="left",
    )

    time = dim_time.copy()
    time["Season"] = time["month_name"].map(
        lambda x: (
            "Peak Season"
            if x in [
                "October", "November", "December",
                "January", "February", "March"
            ]
            else "Off-Peak Season"
        )
    )

    # Enrich monthly tourism data with the time dimension.
    # Handles cases where year/quarter/month already exist in the monthly CSV.
    time_fields = [
        c for c in [
            "time_id",
            "year",
            "month_name",
            "month_num",
            "quarter",
            "Season",
        ]
        if c in time.columns
    ]
    monthly_enriched = monthly.merge(
        time[time_fields],
        on="time_id",
        how="left",
        suffixes=("", "_dimtime"),
    )
    for col in ["year", "month_name", "month_num", "quarter", "Season"]:
        dim_col = f"{col}_dimtime"
        if col not in monthly_enriched.columns and dim_col in monthly_enriched.columns:
            monthly_enriched.rename(
                columns={dim_col: col},
                inplace=True,
            )
        elif col in monthly_enriched.columns and dim_col in monthly_enriched.columns:
            monthly_enriched[col] = monthly_enriched[col].combine_first(
                monthly_enriched[dim_col]
            )
            monthly_enriched.drop(
                columns=[dim_col],
                inplace=True,
            )

    galaxy_enriched = galaxy.copy()
    if "month_name" in galaxy_enriched.columns:
        galaxy_enriched["Season"] = galaxy_enriched["month_name"].map(
            lambda x: (
                "Peak Season"
                if x in [
                    "October", "November", "December",
                    "January", "February", "March"
                ]
                else "Off-Peak Season"
            )
        )

    weather_geo = weather_tourism.merge(
        dim_location[
            ["city", "state", "latitude", "longitude"]
        ].drop_duplicates(),
        left_on="location_name",
        right_on="city",
        how="left",
    )

    return {
        "attr": attr,
        "countries": countries,
        "festivals": festivals,
        "monthly": monthly_enriched,
        "galaxy": galaxy_enriched,
        "weather": weather_geo,
        "dim_time": time,
    }


try:
    DATA = load_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()

attr = DATA["attr"]
countries = DATA["countries"]
festivals = DATA["festivals"]
monthly = DATA["monthly"]
weather = DATA["weather"]


# ============================================================
# 5. HELPERS
# ============================================================
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

COLORS = {
    "blue": "#4F8CFF",
    "cyan": "#38BDF8",
    "teal": "#14B8A6",
    "green": "#22C55E",
    "orange": "#F4B740",
    "purple": "#A78BFA",
    "red": "#FF5A5F",
    "navy": "#0B1220",
    "text": "#E5ECF6",
    "muted": "#9AA9BA",
    "grid": "#243244",
    "panel": "#0F172A",
}


def fmt_num(value):
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


def ordered_months(df, column="month_name"):
    out = df.copy()
    if column in out.columns:
        out[column] = pd.Categorical(
            out[column],
            categories=MONTH_ORDER,
            ordered=True,
        )
        out = out.sort_values(column)
    return out


def base_layout(fig, height=340, title=None):
    fig.update_layout(
        title=dict(
            text=title or "",
            x=0.02,
            xanchor="left",
            font=dict(size=16, color=COLORS["navy"]),
        ),
        height=height,
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font=dict(
            family="Arial",
            size=11,
            color=COLORS["text"],
        ),
        margin=dict(l=58, r=28, t=58, b=55),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(size=10, color=COLORS["muted"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_color=COLORS["text"],
        ),
        xaxis=dict(
            gridcolor=COLORS["grid"],
            zeroline=False,
            automargin=True,
        ),
        yaxis=dict(
            gridcolor=COLORS["grid"],
            zeroline=False,
            automargin=True,
        ),
    )
    return fig


def empty_chart(message="No data for the selected filters."):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=13, color=COLORS["muted"]),
    )
    fig.update_layout(
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# ============================================================
# 6. SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">URBAN PULSE</div>
            <div class="brand-subtitle">Tourism Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Dashboard Filters")

    years = sorted(
        monthly["year"].dropna().astype(int).unique().tolist()
    )
    selected_year = st.selectbox("Year", ["All"] + years)

    selected_quarter = st.selectbox(
        "Quarter",
        ["All", "Q1", "Q2", "Q3", "Q4"],
    )

    selected_month = st.selectbox(
        "Month",
        ["All"] + MONTH_ORDER,
    )

    selected_season = st.selectbox(
        "Season",
        ["All", "Peak Season", "Off-Peak Season"],
    )

    states = ["All"] + sorted(
        attr["state"].dropna().astype(str).unique().tolist()
    )
    selected_state = st.selectbox("State", states)

    if selected_state != "All":
        city_values = sorted(
            attr.loc[
                attr["state"].astype(str) == selected_state,
                "city"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    else:
        city_values = sorted(
            attr["city"].dropna().astype(str).unique().tolist()
        )

    selected_city = st.selectbox(
        "City",
        ["All"] + city_values,
    )

    categories = ["All"] + sorted(
        attr["category"].dropna().astype(str).unique().tolist()
    )
    selected_category = st.selectbox(
        "Tourism Category",
        categories,
    )

    st.markdown("---")
    st.caption("Data source: supplied Urban Pulse project CSV files only.")


# ============================================================
# 7. FILTER DATA
# ============================================================
filtered_attr = attr.copy()

if selected_state != "All":
    filtered_attr = filtered_attr[
        filtered_attr["state"].astype(str) == selected_state
    ]

if selected_city != "All":
    filtered_attr = filtered_attr[
        filtered_attr["city"].astype(str) == selected_city
    ]

if selected_category != "All":
    filtered_attr = filtered_attr[
        filtered_attr["category"].astype(str) == selected_category
    ]


filtered_monthly = monthly.copy()

if selected_year != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["year"] == int(selected_year)
    ]

if selected_quarter != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["quarter"].astype(str) == selected_quarter
    ]

if selected_month != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["month_name"] == selected_month
    ]

if selected_season != "All":
    filtered_monthly = filtered_monthly[
        filtered_monthly["Season"] == selected_season
    ]


filtered_festivals = festivals.copy()

if selected_state != "All" and "state" in filtered_festivals.columns:
    filtered_festivals = filtered_festivals[
        filtered_festivals["state"].astype(str).str.contains(
            selected_state,
            case=False,
            na=False,
        )
    ]

if selected_year != "All" and "year" in filtered_festivals.columns:
    filtered_festivals = filtered_festivals[
        filtered_festivals["year"].astype(str).str.startswith(
            str(selected_year)
        )
    ]


filtered_weather = weather.copy()

if selected_year != "All" and "year" in filtered_weather.columns:
    filtered_weather = filtered_weather[
        filtered_weather["year"] == int(selected_year)
    ]

if selected_month != "All" and "month" in filtered_weather.columns:
    filtered_weather = filtered_weather[
        filtered_weather["month"] == selected_month
    ]

if selected_state != "All" and "state" in filtered_weather.columns:
    filtered_weather = filtered_weather[
        filtered_weather["state"].astype(str).str.contains(
            selected_state,
            case=False,
            na=False,
        )
    ]

if selected_city != "All" and "city" in filtered_weather.columns:
    filtered_weather = filtered_weather[
        filtered_weather["city"].astype(str).str.contains(
            selected_city,
            case=False,
            na=False,
        )
    ]


# ============================================================
# 8. HEADER
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">India Tourism Intelligence Dashboard</div>
        <div class="hero-subtitle">
            Tourism demand, attractions, international arrivals, festival funding,
            geographic intelligence and weather insights.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 9. KPI CARDS
# ============================================================
total_places = len(filtered_attr)

category_count = (
    filtered_attr["category"].nunique()
    if not filtered_attr.empty
    else 0
)

high_rated = (
    int((filtered_attr["google_rating"] >= 4).sum())
    if not filtered_attr.empty
    else 0
)

avg_rating = (
    filtered_attr["google_rating"].mean()
    if not filtered_attr.empty
    else 0
)

avg_fee = (
    filtered_attr["entry_fee"].mean()
    if not filtered_attr.empty
    else 0
)

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

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Tourist Places", fmt_num(total_places))
k2.metric("Tourism Categories", fmt_num(category_count))
k3.metric("Highly Rated Places", fmt_num(high_rated))
k4.metric("Average Rating", f"{avg_rating:.2f} / 5")
k5.metric("Average Entry Fee", f"₹{avg_fee:,.0f}")


# ============================================================
# 10. GEOGRAPHIC OVERVIEW
# ============================================================
st.markdown(
    '<div class="section-title">Demand & Geographic Intelligence</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Attraction density and tourism category distribution.</div>',
    unsafe_allow_html=True,
)

map_col, category_col = st.columns([1.35, 1])

with map_col:
    st.markdown("#### Tourist Attraction Density Map")

    map_df = filtered_attr.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    if not map_df.empty:
        center_lat = map_df["latitude"].mean()
        center_lon = map_df["longitude"].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles="CartoDB positron",
        )

        density = (
            map_df.groupby(["latitude", "longitude"])
            .size()
            .reset_index(name="count")
        )

        heat_data = [
            [row.latitude, row.longitude, row["count"]]
            for _, row in density.iterrows()
        ]

        HeatMap(
            heat_data,
            radius=18,
            blur=16,
            min_opacity=0.25,
            max_zoom=8,
        ).add_to(m)

        locations = (
            map_df.groupby(
                ["location_id", "state", "city", "latitude", "longitude"],
                as_index=False,
            )
            .agg(
                Attractions=("place_name", "count"),
                Avg_Rating=("google_rating", "mean"),
            )
        )

        for row in locations.itertuples():
            folium.CircleMarker(
                location=[row.latitude, row.longitude],
                radius=max(4, min(10, row.Attractions)),
                tooltip=f"{row.city}, {row.state}",
                popup=(
                    f"<b>{row.city}</b><br>"
                    f"{row.state}<br>"
                    f"Tourist places: {row.Attractions}<br>"
                    f"Average rating: {row.Avg_Rating:.2f}"
                ),
                color="#2563EB",
                fill=True,
                fill_opacity=0.65,
            ).add_to(m)

        st_folium(
            m,
            height=390,
            use_container_width=True,
        )
    else:
        st.plotly_chart(
            empty_chart(),
            use_container_width=True,
        )


with category_col:
    category_counts = (
        filtered_attr["category"]
        .value_counts()
        .reset_index()
    )
    category_counts.columns = ["Category", "Places"]
    category_counts = category_counts.head(10).sort_values("Places")

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
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_xaxes(title="Number of Places")
        fig.update_yaxes(
            title="",
            automargin=True,
        )

        base_layout(
            fig,
            height=390,
            title="Top 10 Tourism Categories",
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 11. ATTRACTION PERFORMANCE
# ============================================================
st.markdown(
    '<div class="section-title">Attraction Performance</div>',
    unsafe_allow_html=True,
)

left, right = st.columns(2)

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
            marker_color=COLORS["blue"],
            texttemplate="%{text:.1f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_xaxes(
            range=[0, 5.2],
            title="Google Rating",
        )
        fig.update_yaxes(title="", automargin=True)

        base_layout(
            fig,
            height=390,
            title="Top 10 Tourist Places by Rating",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


with right:
    if not filtered_attr.empty:
        scatter = filtered_attr.copy()

        # Limit visual clutter while preserving the underlying data.
        scatter = scatter.sort_values(
            "google_rating",
            ascending=False,
        ).head(500)

        fig = px.scatter(
            scatter,
            x="entry_fee",
            y="google_rating",
            color="category",
            hover_name="place_name",
            hover_data=["city", "state"],
            labels={
                "entry_fee": "Entry Fee (₹)",
                "google_rating": "Google Rating",
                "category": "Category",
            },
        )

        fig.update_traces(
            marker=dict(
                size=8,
                opacity=0.72,
            )
        )

        fig.update_xaxes(
            title="Entry Fee (₹)",
            rangemode="tozero",
        )
        fig.update_yaxes(
            title="Google Rating",
            range=[0, 5.2],
        )

        base_layout(
            fig,
            height=390,
            title="Rating vs Entry Fee",
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 12. TOURISM DEMAND & REVENUE
# ============================================================
st.markdown(
    '<div class="section-title">Tourism Demand & Economic Trends</div>',
    unsafe_allow_html=True,
)

trend_left, trend_right = st.columns(2)

with trend_left:
    trend = ordered_months(filtered_monthly)

    if not trend.empty:
        fig = px.line(
            trend,
            x="month_name",
            y="foreign_tourist_arrivals",
            markers=True,
            labels={
                "month_name": "Month",
                "foreign_tourist_arrivals": "Foreign Tourist Arrivals",
            },
        )

        fig.update_traces(
            line=dict(
                color=COLORS["blue"],
                width=3,
            ),
            marker=dict(size=7),
        )

        fig.update_xaxes(
            title="Month",
            tickangle=0,
        )
        fig.update_yaxes(
            title="Foreign Tourist Arrivals",
            tickformat="~s",
        )

        base_layout(
            fig,
            height=330,
            title="Foreign Tourist Arrivals Trend",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


with trend_right:
    trend = ordered_months(filtered_monthly)

    if not trend.empty:
        fig = px.line(
            trend,
            x="month_name",
            y="tourism_revenue_crore_inr",
            markers=True,
            labels={
                "month_name": "Month",
                "tourism_revenue_crore_inr": "Revenue (₹ Crore)",
            },
        )

        fig.update_traces(
            line=dict(
                color=COLORS["green"],
                width=3,
            ),
            marker=dict(size=7),
        )

        fig.update_xaxes(
            title="Month",
            tickangle=0,
        )
        fig.update_yaxes(
            title="Revenue (₹ Crore)",
        )

        base_layout(
            fig,
            height=330,
            title="Tourism Revenue Trend",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_chart(), use_container_width=True)


# ============================================================
# 13. INTERNATIONAL TOURIST PROFILE
# ============================================================
st.markdown(
    '<div class="section-title">International Tourist Profile</div>',
    unsafe_allow_html=True,
)

country_chart, country_table = st.columns([1.35, 1])

country_profile = (
    countries.groupby("country_name", as_index=False)
    .agg(
        Arrivals=("arrivals_in_numbers", "sum"),
        Avg_Stay=("average_duration_of_stay_in_days", "mean"),
    )
)

# Exclude aggregate rows from rankings.
aggregate_names = {
    "Total",
    "Others",
    "Other Countries",
    "All Countries",
}

country_profile = country_profile[
    ~country_profile["country_name"].isin(aggregate_names)
]

country_profile = country_profile.sort_values(
    "Arrivals",
    ascending=False,
)

with country_chart:
    top_countries = (
        country_profile.head(10)
        .sort_values("Arrivals")
    )

    if not top_countries.empty:
        fig = px.bar(
            top_countries,
            x="Arrivals",
            y="country_name",
            orientation="h",
            text="Arrivals",
        )

        fig.update_traces(
            marker_color=COLORS["teal"],
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_xaxes(
            title="Foreign Arrivals",
        )
        fig.update_yaxes(
            title="",
            automargin=True,
        )

        base_layout(
            fig,
            height=370,
            title="Top 10 Source Countries",
        )

        st.plotly_chart(fig, use_container_width=True)


with country_table:
    profile = country_profile.head(10).copy()
    profile["Avg_Stay"] = profile["Avg_Stay"].round(1)

    profile = profile.rename(
        columns={
            "country_name": "Country",
            "Arrivals": "Arrivals",
            "Avg_Stay": "Avg. Stay (Days)",
        }
    )

    st.dataframe(
        profile,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 14. FESTIVAL FUNDING
# ============================================================
st.markdown(
    '<div class="section-title">Festival Funding & Cultural Activity</div>',
    unsafe_allow_html=True,
)

fest_left, fest_right = st.columns(2)

fest_budget = (
    filtered_festivals.groupby("festival_name", as_index=False)
    .agg(
        Sanctioned=("amount_sanctioned", "sum"),
        Released=("amount_released", "sum"),
    )
    .sort_values("Sanctioned", ascending=False)
    .head(10)
)

with fest_left:
    if not fest_budget.empty:
        long_fest = fest_budget.melt(
            id_vars="festival_name",
            value_vars=["Sanctioned", "Released"],
            var_name="Budget Type",
            value_name="Amount",
        )

        fig = px.bar(
            long_fest,
            x="festival_name",
            y="Amount",
            color="Budget Type",
            barmode="group",
            color_discrete_map={
                "Sanctioned": COLORS["blue"],
                "Released": COLORS["green"],
            },
            labels={
                "festival_name": "Festival",
                "Amount": "Amount",
            },
        )

        fig.update_xaxes(
            tickangle=-25,
            automargin=True,
        )
        fig.update_yaxes(
            title="Funding Amount",
        )

        base_layout(
            fig,
            height=400,
            title="Festival Sanctioned vs Released Funding",
        )

        st.plotly_chart(fig, use_container_width=True)


with fest_right:
    if not fest_budget.empty:
        release = fest_budget.copy()
        release["Release %"] = (
            release["Released"]
            / release["Sanctioned"].replace(0, pd.NA)
            * 100
        )

        release = (
            release.dropna(subset=["Release %"])
            .sort_values("Release %")
            .head(10)
        )

        fig = px.bar(
            release,
            x="Release %",
            y="festival_name",
            orientation="h",
            text="Release %",
        )

        fig.update_traces(
            marker_color=COLORS["purple"],
            texttemplate="%{text:.0f}%",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_xaxes(
            title="Released / Sanctioned (%)",
            range=[0, max(105, float(release["Release %"].max()) + 8)]
            if not release.empty
            else [0, 100],
        )
        fig.update_yaxes(
            title="",
            automargin=True,
        )

        base_layout(
            fig,
            height=400,
            title="Festival Budget Release Efficiency",
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 15. GEOGRAPHIC DRILL-DOWN
# ============================================================
st.markdown(
    '<div class="section-title">Geographic Drill-Down</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">State → City → Tourist Place.</div>',
    unsafe_allow_html=True,
)

geo = filtered_attr.copy()

if not geo.empty:
    geo_summary = (
        geo.groupby(
            ["state", "city", "place_name"],
            as_index=False,
        )
        .agg(
            Category=("category", "first"),
            Rating=("google_rating", "mean"),
            Entry_Fee=("entry_fee", "mean"),
        )
    )

    drill_state = st.selectbox(
        "State",
        ["All"] + sorted(geo_summary["state"].dropna().unique()),
        key="geo_state",
    )

    drill = geo_summary.copy()

    if drill_state != "All":
        drill = drill[drill["state"] == drill_state]

    drill_city = st.selectbox(
        "City",
        ["All"] + sorted(drill["city"].dropna().unique()),
        key="geo_city",
    )

    if drill_city != "All":
        drill = drill[drill["city"] == drill_city]

    drill = drill.sort_values(
        ["state", "city", "Rating"],
        ascending=[True, True, False],
    )

    display_drill = drill.rename(
        columns={
            "state": "State",
            "city": "City",
            "place_name": "Tourist Place",
            "Category": "Category",
            "Rating": "Rating",
            "Entry_Fee": "Entry Fee (₹)",
        }
    )

    display_drill["Rating"] = display_drill["Rating"].round(1)
    display_drill["Entry Fee (₹)"] = display_drill["Entry Fee (₹)"].round(0)

    st.dataframe(
        display_drill,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 16. WEATHER IMPACT
# ============================================================
st.markdown(
    '<div class="section-title">Weather Impact on Tourism</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Monthly foreign arrivals compared with temperature, rainfall and humidity.</div>',
    unsafe_allow_html=True,
)

weather_chart, weather_metrics = st.columns([1.55, 1])

with weather_chart:
    if not filtered_weather.empty:
        weather_monthly = (
            filtered_weather.groupby("month", as_index=False)
            .agg(
                foreign_tourist_arrivals=(
                    "foreign_tourist_arrivals",
                    "first",
                ),
                temp_c=("temp_c", "mean"),
                rainfall_mm=("rainfall_mm", "mean"),
                humidity_pct=("humidity_pct", "mean"),
            )
        )

        weather_monthly["month"] = pd.Categorical(
            weather_monthly["month"],
            categories=MONTH_ORDER,
            ordered=True,
        )
        weather_monthly = weather_monthly.sort_values("month")

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=weather_monthly["month"],
                y=weather_monthly["foreign_tourist_arrivals"],
                name="Foreign Arrivals",
                marker_color=COLORS["blue"],
                opacity=0.85,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=weather_monthly["month"],
                y=weather_monthly["temp_c"],
                name="Temperature (°C)",
                mode="lines+markers",
                line=dict(
                    color=COLORS["orange"],
                    width=2.5,
                ),
                marker=dict(size=6),
                yaxis="y2",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=weather_monthly["month"],
                y=weather_monthly["rainfall_mm"],
                name="Rainfall (mm)",
                mode="lines+markers",
                line=dict(
                    color=COLORS["purple"],
                    width=2.5,
                ),
                marker=dict(size=6),
                yaxis="y2",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=weather_monthly["month"],
                y=weather_monthly["humidity_pct"],
                name="Humidity (%)",
                mode="lines+markers",
                line=dict(
                    color=COLORS["green"],
                    width=2.5,
                ),
                marker=dict(size=6),
                yaxis="y2",
            )
        )

        fig.update_layout(
            height=430,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                family="Arial",
                color=COLORS["text"],
                size=11,
            ),
            margin=dict(
                l=70,
                r=70,
                t=88,
                b=58,
            ),
            title=dict(
                text="Weather Conditions vs Foreign Tourist Arrivals",
                x=0.02,
                font=dict(
                    size=16,
                    color=COLORS["navy"],
                ),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0)",
            ),
            xaxis=dict(
                title="Month",
                tickangle=0,
                gridcolor=COLORS["grid"],
                automargin=True,
            ),
            yaxis=dict(
                title="Foreign Tourist Arrivals",
                gridcolor=COLORS["grid"],
                automargin=True,
            ),
            yaxis2=dict(
                title="Weather Metrics",
                overlaying="y",
                side="right",
                showgrid=False,
                automargin=True,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )
    else:
        st.plotly_chart(
            empty_chart(),
            use_container_width=True,
        )


with weather_metrics:
    if not filtered_weather.empty:
        avg_temp = filtered_weather["temp_c"].mean()
        avg_rain = filtered_weather["rainfall_mm"].mean()
        avg_humidity = filtered_weather["humidity_pct"].mean()

        m1, m2 = st.columns(2)
        m1.metric(
            "Avg Temperature",
            f"{avg_temp:.1f} °C",
        )
        m2.metric(
            "Avg Rainfall",
            f"{avg_rain:.1f} mm",
        )

        st.metric(
            "Avg Humidity",
            f"{avg_humidity:.1f}%",
        )

        corr = (
            filtered_weather[
                [
                    "foreign_tourist_arrivals",
                    "temp_c",
                    "rainfall_mm",
                    "humidity_pct",
                ]
            ]
            .corr()["foreign_tourist_arrivals"]
            .drop("foreign_tourist_arrivals")
            .dropna()
            .reset_index()
        )

        corr.columns = ["Metric", "Correlation"]

        if not corr.empty:
            fig = px.bar(
                corr,
                x="Correlation",
                y="Metric",
                orientation="h",
                text="Correlation",
                range_x=[-1, 1],
            )

            fig.update_traces(
                marker_color=COLORS["purple"],
                texttemplate="%{text:.2f}",
                textposition="outside",
                cliponaxis=False,
            )

            fig.update_xaxes(
                title="Correlation",
                automargin=True,
            )
            fig.update_yaxes(
                title="",
                automargin=True,
            )

            base_layout(
                fig,
                height=260,
                title="Weather / Arrival Correlation",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


# ============================================================
# 17. WEATHER MAP
# ============================================================
st.markdown(
    '<div class="section-title">Weather Conditions Across Tourist Locations</div>',
    unsafe_allow_html=True,
)

weather_geo = filtered_weather.dropna(
    subset=["latitude", "longitude"]
).copy()

if not weather_geo.empty:
    latest_weather = (
        weather_geo.sort_values("time_id")
        .groupby(
            ["city", "state", "latitude", "longitude"],
            as_index=False,
        )
        .tail(1)
    )

    fig = px.scatter_map(
        latest_weather,
        lat="latitude",
        lon="longitude",
        color="temp_c",
        size="rainfall_mm",
        hover_name="city",
        hover_data={
            "state": True,
            "temp_c": ":.1f",
            "rainfall_mm": ":.1f",
            "humidity_pct": ":.1f",
            "latitude": False,
            "longitude": False,
        },
        color_continuous_scale="Turbo",
        center={
            "lat": 20.5937,
            "lon": 78.9629,
        },
        zoom=3.6,
        height=420,
    )

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=0, r=0, t=20, b=0),
        font=dict(
            family="Arial",
            color=COLORS["text"],
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# 18. FOOTER
# ============================================================
st.markdown(
    """
    <div style="
        margin-top:24px;
        padding:14px 0;
        border-top:1px solid #E3E8F0;
        color:#667085;
        font-size:11px;
        text-align:center;
    ">
        Urban Pulse • India Tourism Intelligence • Dashboard built from the supplied project CSV datasets
    </div>
    """,
    unsafe_allow_html=True,
)

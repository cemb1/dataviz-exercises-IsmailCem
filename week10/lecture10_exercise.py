import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime

st.set_page_config(page_title="CO₂ Emissions Explorer", page_icon="🌍", layout="wide")

# ── Data loader with caching ────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌍 CO₂ Emissions Explorer")
st.caption("Source: Our World in Data | CO₂ Emissions 2000–2022")

# ── All filters grouped in the sidebar ──────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # 1. selectbox — chained filter: Region narrows Country list
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions)

    if selected_region == 'All':
        country_options = sorted(df['Country'].unique())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].unique())

    # 2. multiselect — country choice (chained to region)
    default_countries = country_options[:3]
    selected_countries = st.multiselect(
        "Countries",
        options=country_options,
        default=default_countries
    )

    # 3. date_input — calendar range picker
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2005, 1, 1), datetime.date(2020, 1, 1)),
        min_value=datetime.date(int(df['Year'].min()), 1, 1),
        max_value=datetime.date(int(df['Year'].max()), 1, 1),
        format="YYYY-MM-DD"
    )

    st.divider()

    # 4. radio — metric choice (2 exclusive options)
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    # 5. checkbox — optional toggle for showing raw data table
    show_table = st.checkbox("Show data table", value=False)

# ── Guards: stop early on incomplete input ──────────────────────────────────
if not selected_countries:
    st.warning("👆 Select at least one country.")
    st.stop()

if len(date_range) != 2:
    st.warning("Select a start AND end date.")
    st.stop()

# Convert dates to Timestamp before pandas comparison
start_ts, end_ts = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

# ── Filter the data ─────────────────────────────────────────────────────────
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) &
    (df['Date'] <= end_ts)
]

if filtered.empty:
    st.warning("No data in this date range for the selected countries.")
    st.stop()

# Pick the metric column
y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

# Filter summary caption (BBD: show count of matching records)
st.caption(
    f"Showing {len(selected_countries)} countries | {selected_region} | "
    f"{date_range[0].strftime('%d %b %Y')} – {date_range[1].strftime('%d %b %Y')} | "
    f"{metric} | {len(filtered)} data points"
)

# ── Charts ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{metric} over time")
    fig1 = px.line(
        filtered, x='Date', y=y_col, color='Country',
        labels={y_col: y_label, 'Date': ''}
    )
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial'),
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Latest year ranking")
    latest_year = filtered['Year'].max()
    latest = filtered[filtered['Year'] == latest_year].sort_values(y_col)
    fig2 = px.bar(
        latest, x=y_col, y='Country', orientation='h',
        color_discrete_sequence=['#2E75B6'],
        labels={y_col: y_label, 'Country': ''}
    )
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial'),
                       xaxis=dict(range=[0, latest[y_col].max() * 1.15]),
                       margin=dict(l=10, r=10, t=10, b=10))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

# ── Optional data table (checkbox toggle) ───────────────────────────────────
if show_table:
    st.divider()
    st.subheader("Filtered data")
    st.dataframe(filtered, use_container_width=True)

st.divider()
st.caption("Built with Streamlit + Plotly")

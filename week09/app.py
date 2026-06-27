import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="World Happiness", page_icon="🌍", layout="wide")

df = pd.read_csv('data/world_happiness_2023.csv')
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]

st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# Two-column layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rankings")
    top = filtered.nlargest(top_n, 'Score').sort_values('Score')
    fig1 = px.bar(top, x='Score', y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={'Score':'Score (0–10)','Country':''})
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       xaxis=dict(range=[0,8.5]), font=dict(family='Arial',size=12),
                       margin=dict(l=10,r=10,t=5,b=10))
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Score vs GDP")
    fig2 = px.scatter(filtered, x='GDP', y='Score', hover_name='Country',
                      color_discrete_sequence=['#E63946'])
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial',size=12),
                       margin=dict(l=10,r=10,t=5,b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── STEP 6: Third chart — diverging colour scale ──────────────────────────
st.subheader("Happiness vs Global Average — Diverging Scale")

# Compute deviation from global mean
global_mean = df['Score'].mean()
filtered2 = filtered.copy()
filtered2['deviation'] = filtered2['Score'] - global_mean
filtered2 = filtered2.sort_values('deviation')

fig3 = px.bar(
    filtered2,
    x='deviation',
    y='Country',
    orientation='h',
    color='deviation',
    color_continuous_scale='RdBu',
    color_continuous_midpoint=0,
    labels={'deviation': 'Deviation from global average', 'Country': ''}
)

# Annotate the midpoint
fig3.add_vline(
    x=0,
    line_dash='dash',
    line_color='#444444',
    line_width=1.5
)
fig3.add_annotation(
    x=0, y=1, yref='paper',
    text=f"Global avg: {global_mean:.2f}",
    showarrow=False,
    xanchor='left', xshift=6,
    font=dict(family='Arial', size=11, color='#444444')
)

fig3.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    coloraxis_showscale=False,
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption("Built with Streamlit + Plotly")

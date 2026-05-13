import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Dashboard Configuration - FORCING WIDE MODE
st.set_page_config(layout="wide", page_title="Ultimate Accident Analytics")

# Injecting Custom CSS for visibility and prevention of text clipping
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 98%; 
    }
    [data-testid="stMetricValue"] {
        font-size: 38px !important; /* Balanced size to fit names like New Delhi */
        font-weight: 700;
        color: #1f77b4;
    }
    [data-testid="stMetricLabel"] {
        font-size: 18px !important;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Data Management & Mapping
with st.sidebar:
    st.header("📂 Data Management")
    uploaded_file = st.file_uploader("Upload Accident CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("Analysis Ready!")
    else:
        st.info("Please upload a CSV file to begin.")
        st.stop()

    st.divider()
    st.header("🎯 KPI & Column Mapping")
    all_cols = df.columns.tolist()

    # Hybrid Auto-detection logic
    auto_name = next((c for c in all_cols if "type" in c.lower()), all_cols[0])
    auto_val = next((c for c in all_cols if "count" in c.lower()), all_cols[min(1, len(all_cols)-1)])
    auto_group = next((c for c in all_cols if "category" in c.lower()), all_cols[min(2, len(all_cols)-1)])

    name_col = st.selectbox("Label Column (Type)", all_cols, index=all_cols.index(auto_name))
    val_col = st.selectbox("Value Column (Count)", all_cols, index=all_cols.index(auto_val))
    group_col = st.selectbox("Grouping Column (Category)", all_cols, index=all_cols.index(auto_group))

    st.divider()
    st.header("Chart Settings")
    target_cats = ["Weather", "Time", "Location", "Road", "Severity", "Light"]
    available_options = [cat for cat in target_cats if cat in df[group_col].unique()]
    if not available_options: 
        available_options = df[group_col].unique().tolist()

    x_axis_filter = st.selectbox("Select Category Group", options=available_options)
    
    selected_graph = st.selectbox("Choose Graph to Display", 
        ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])

# 3. KPI Header - Safe/Unsafe Logic (Excluding "Unknown")
st.title("🚗 Accident Intelligence Dashboard")
m1, m2, m3, m4, m5 = st.columns(5)

def get_filtered_kpi(data, category_keyword, find_max=True):
    try:
        # Exclude 'Unknown' and 'Other' to show meaningful locations/times
        subset = data[(data[group_col].str.contains(category_keyword, case=False, na=False)) & 
                      (~data[name_col].astype(str).str.lower().isin(["unknown", "other"]))]
        
        if subset.empty: return "N/A"
        
        idx = subset[val_col].idxmax() if find_max else subset[val_col].idxmin()
        return subset.loc[idx][name_col]
    except: 
        return "N/A"

with m1:
    total_val = df[val_col].sum() if pd.api.types.is_numeric_dtype(df[val_col]) else len(df)
    st.metric("Total Incidents", f"{total_val:,}")
with m2: st.metric("Unsafe Time", str(get_filtered_kpi(df, "Time", True)))
with m3: st.metric("Safe Time", str(get_filtered_kpi(df, "Time", False)))
with m4: st.metric("Unsafe Location", str(get_filtered_kpi(df, "Location", True)))
with m5: st.metric("Safe Location", str(get_filtered_kpi(df, "Location", False)))

st.divider()

# 4. Performance-Optimized Visualization Display
CHART_HEIGHT = 700 
# Limit to top 15 results to prevent lag with large datasets like Locations
display_df = df[df[group_col] == x_axis_filter].sort_values(by=val_col, ascending=False).head(15)

st.subheader(f"📊 {selected_graph}: {x_axis_filter} (Top Results)")

if selected_graph == "Bar Chart":
    fig = px.bar(display_df, x=name_col, y=val_col, color=name_col, text=val_col, height=CHART_HEIGHT)
    fig.update_traces(textposition='inside', textfont=dict(size=16))
elif selected_graph == "Line Chart":
    fig = px.line(display_df, x=name_col, y=val_col, markers=True, text=val_col, height=CHART_HEIGHT)
    fig.update_traces(textposition="top center")
elif selected_graph == "Pie Chart":
    fig = px.pie(display_df, names=name_col, values=val_col, hole=0.4, height=CHART_HEIGHT)
    fig.update_traces(textinfo='percent+label')
else:
    fig = px.scatter(display_df, x=name_col, y=val_col, size=val_col, color=name_col, height=CHART_HEIGHT)


# Fixed layout property structure to avoid ValueErrors
fig.update_layout(
    font=dict(size=15),
    xaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14), tickangle=45),
    yaxis=dict(title=dict(font=dict(size=18)), tickfont=dict(size=14)),
    margin=dict(l=10, r=10, t=50, b=150)
)

st.plotly_chart(fig, use_container_width=True)

# 5. Data Explorer
with st.expander("🔍 View Raw Analysis Data"):
    st.dataframe(df, use_container_width=True)
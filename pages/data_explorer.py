import streamlit as st
import pandas as pd
import io
import os
import numpy as np

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("d:/Depi Project/style.css")

if 'filtered_df' not in st.session_state:
    st.warning("Please go to the Home page first to initialize data.")
    st.stop()

df = st.session_state['filtered_df']
is_filtered = st.session_state.get('is_filtered', False)

st.markdown("<h1 style='font-size: 2.2rem;'>Raw Data Explorer</h1>", unsafe_allow_html=True)
if is_filtered:
    st.markdown("<span style='color: #a855f7; font-weight: 600;'>⚠️ Filters Active (Data is filtered)</span>", unsafe_allow_html=True)
st.markdown("<div class='gradient-bar' style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

st.markdown("""
Use this explorer to inspect, search, and export the underlying campaign performance dataset. 
The columns displayed here correspond to the fact table merged with its dimension entities.
""")

# Column multiselect
all_columns = list(df.columns)
default_columns = [
    'Date', 'CampaignName', 'Channel', 'Region', 'TargetAudience', 
    'Impressions', 'Clicks', 'Leads', 'Enrollments', 'Cost', 'Revenue', 'ROAS'
]
# Make sure default columns exist in current dataframe
default_columns = [c for c in default_columns if c in all_columns]

selected_cols = st.multiselect("Select Columns to Display", all_columns, default=default_columns)

if not selected_cols:
    st.error("Please select at least one column to display.")
    st.stop()

# Search box
search_query = st.text_input("Search (filters rows containing matching text in any string column)", "")

explorer_df = df[selected_cols].copy()

if search_query:
    # Filter rows based on search query
    mask = pd.Series(False, index=explorer_df.index)
    for col in explorer_df.columns:
        # Check string columns for matches
        if explorer_df[col].dtype == 'object' or explorer_df[col].dtype == 'string' or isinstance(explorer_df[col].dtype, pd.ArrowDtype):
            mask = mask | explorer_df[col].astype(str).str.contains(search_query, case=False, na=False)
    explorer_df = explorer_df[mask]

# Limit preview size for performance, but show count
total_rows = len(explorer_df)
limit = st.slider("Display Limit (Rows)", 10, min(total_rows, 500) if total_rows > 10 else 10, min(total_rows, 100) if total_rows > 10 else 10)

st.write(f"Showing {min(total_rows, limit)} of {total_rows:,} matching records.")
st.dataframe(explorer_df.head(limit), width='stretch')

# Export buttons
col1, col2 = st.columns(2)

# CSV Download
csv_data = explorer_df.to_csv(index=False).encode('utf-8')
col1.download_button(
    label="Download Current View as CSV",
    data=csv_data,
    file_name="campaign_data_export.csv",
    mime='text/csv'
)

# Excel Download
try:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        explorer_df.to_excel(writer, index=False, sheet_name='ExportedData')
    excel_data = buffer.getvalue()
    col2.download_button(
        label="Download Current View as Excel",
        data=excel_data,
        file_name="campaign_data_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
except Exception as e:
    col2.error(f"Excel generation failed: {e}")

st.markdown("<br><hr style='border:0; height:1px; background:rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
st.subheader("Summary Statistics")

# Show basic descriptive statistics for numeric columns
num_cols = explorer_df.select_dtypes(include=[np.number]).columns
if len(num_cols) > 0:
    st.write(explorer_df[num_cols].describe().style.format("{:,.2f}"))
else:
    st.write("No numeric columns selected to calculate stats.")

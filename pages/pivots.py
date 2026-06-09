import streamlit as st
import pandas as pd
import numpy as np
import os

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

if 'filtered_df' not in st.session_state:
    st.warning("Please go to the Home page first to initialize data.")
    st.stop()

df = st.session_state['filtered_df']
is_filtered = st.session_state.get('is_filtered', False)

st.markdown("<h1 style='font-size: 2.2rem;'>Interactive Pivot Tables</h1>", unsafe_allow_html=True)
if is_filtered:
    st.markdown("<span style='color: #a855f7; font-weight: 600;'>⚠️ Filters Active (Data is filtered)</span>", unsafe_allow_html=True)
st.markdown("<div class='gradient-bar' style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Select pivot table
pivot_options = [
    "1. Cost & Revenue By Region",
    "2. Cost & Revenue By Platform/Channel",
    "3. Full Funnel Metrics By Platform/Channel",
    "4. Full Funnel Metrics By Campaign",
    "5. Financials & ROAS By Campaign",
    "6. Platform Spending Share (%)",
    "7. Performance Ratios By Campaign (CTR, CPC, CPL, CPE)",
    "8. Leads & Enrollments By Target Audience",
    "9. Clicks, Enrollments & Revenue By Creative Asset",
    "10. Enrollments & Revenue By Region",
    "11. Manager Budget, Cost & Revenue",
    "12. Monthly Performance Trends (Cost & Enrollments)",
    "13. Revenue & Enrollments By Region"
]

selected_pivot = st.selectbox("Select Pivot Table to Replicate", pivot_options)

st.markdown("<br>", unsafe_allow_html=True)

# Generate Pivot Tables based on selection
pt_df = None
format_dict = {}

if selected_pivot.startswith("1. "):
    # Region Cost & Revenue
    pt_df = df.groupby('Region')[['Cost', 'Revenue']].sum()
    # Add Grand Total
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Cost': '₹{:,.2f}', 'Revenue': '₹{:,.2f}'}
    
elif selected_pivot.startswith("2. "):
    # Platform Cost & Revenue
    pt_df = df.groupby('Channel')[['Cost', 'Revenue']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Cost': '₹{:,.2f}', 'Revenue': '₹{:,.2f}'}

elif selected_pivot.startswith("3. "):
    # Full Funnel Metrics By Platform
    pt_df = df.groupby('Channel')[['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {m: '{:,.0f}' for m in ['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments']}

elif selected_pivot.startswith("4. "):
    # Full Funnel Metrics By Campaign
    pt_df = df.groupby('CampaignName')[['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {m: '{:,.0f}' for m in ['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments']}

elif selected_pivot.startswith("5. "):
    # Campaign Budget, Cost, Revenue and ROAS
    pt_df = df.groupby('CampaignName')[['Cost', 'Revenue']].sum()
    # Excel calculates ROAS by summing row ROAS which is not standard but we'll show mathematical ROAS:
    pt_df['ROAS (Actual)'] = pt_df['Revenue'] / pt_df['Cost']
    # And Excel Sum of ROAS (for matching verification):
    excel_roas = df.groupby('CampaignName')['ROAS'].sum()
    pt_df['ROAS (Excel Sum)'] = excel_roas
    
    # Add Grand Total
    totals = pt_df.sum()
    # Overwrite actual ROAS grand total with correct calculation
    totals['ROAS (Actual)'] = totals['Revenue'] / totals['Cost'] if totals['Cost'] > 0 else 0
    pt_df.loc['Grand Total'] = totals
    
    format_dict = {'Cost': '₹{:,.2f}', 'Revenue': '₹{:,.2f}', 'ROAS (Actual)': '{:.2f}x', 'ROAS (Excel Sum)': '{:.2f}'}

elif selected_pivot.startswith("6. "):
    # Platform Spend Share
    pt_df = df.groupby('Channel')[['Cost']].sum()
    total_spend = pt_df['Cost'].sum()
    pt_df['Spending Share'] = pt_df['Cost'] / total_spend if total_spend > 0 else 0
    
    # Grand Total
    pt_df.loc['Grand Total'] = [total_spend, 1.0]
    format_dict = {'Cost': '₹{:,.2f}', 'Spending Share': '{:.2%}'}

elif selected_pivot.startswith("7. "):
    # Performance Ratios (Average)
    pt_df = df.groupby('CampaignName')[['CTR', 'CPC', 'CPL', 'Cost Per Enrollment']].mean()
    
    # Grand Total (which is average of averages in Excel)
    averages = pt_df.mean()
    pt_df.loc['Grand Total'] = averages
    
    # Rename columns to match
    pt_df = pt_df.rename(columns={
        'CTR': 'Average of CTR',
        'CPC': 'Average of CPC',
        'CPL': 'Average of CPL',
        'Cost Per Enrollment': 'Average of CPE'
    })
    
    format_dict = {
        'Average of CTR': '{:.4%}',
        'Average of CPC': '₹{:,.2f}',
        'Average of CPL': '₹{:,.2f}',
        'Average of CPE': '₹{:,.2f}'
    }

elif selected_pivot.startswith("8. "):
    # Audience vs Leads & Enrollments
    pt_df = df.groupby('TargetAudience')[['Leads', 'Enrollments']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Leads': '{:,.0f}', 'Enrollments': '{:,.0f}'}

elif selected_pivot.startswith("9. "):
    # Creative vs Clicks, Enrollments & Revenue
    pt_df = df.groupby('Creative Type')[['Clicks', 'Enrollments', 'Revenue']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Clicks': '{:,.0f}', 'Enrollments': '{:,.0f}', 'Revenue': '₹{:,.2f}'}

elif selected_pivot.startswith("10. "):
    # Region vs Enrollments & Revenue
    pt_df = df.groupby('Region')[['Enrollments', 'Revenue']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Enrollments': '{:,.0f}', 'Revenue': '₹{:,.2f}'}

elif selected_pivot.startswith("11. "):
    # Manager Budget, Cost & Revenue
    # Join manager details to calculate total budget
    pt_df = df.groupby('Manager').agg({
        'Budget': 'first', # Budget is static per manager/campaign
        'Cost': 'sum',
        'Revenue': 'sum'
    })
    
    # Grand Total
    totals = pd.Series({
        'Budget': pt_df['Budget'].sum(),
        'Cost': pt_df['Cost'].sum(),
        'Revenue': pt_df['Revenue'].sum()
    })
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Budget': '₹{:,.2f}', 'Cost': '₹{:,.2f}', 'Revenue': '₹{:,.2f}'}

elif selected_pivot.startswith("12. "):
    # Monthly performance trends
    # Sort option
    sort_option = st.radio("Month Sorting Option", ["Chronological (Recommended)", "Alphabetical (Excel Match)"], horizontal=True)
    
    if "Alphabetical" in sort_option:
        pt_df = df.groupby(['Date (Year)', 'Date (Month)'])[['Cost', 'Enrollments']].sum()
    else:
        # Group by year and month index, then map index back to month name for chronological sort
        grouped = df.groupby(['Date (Year)', 'Date (Month Index)', 'Date (Month)'])[['Cost', 'Enrollments']].sum().reset_index()
        grouped = grouped.sort_values(by=['Date (Year)', 'Date (Month Index)'])
        grouped = grouped.drop(columns='Date (Month Index)')
        pt_df = grouped.set_index(['Date (Year)', 'Date (Month)'])
        
    totals = pt_df.sum()
    pt_df.loc[('Grand Total', ''), :] = totals
    format_dict = {'Cost': '₹{:,.2f}', 'Enrollments': '{:,.0f}'}

elif selected_pivot.startswith("13. "):
    # Region vs Revenue & Enrollments
    pt_df = df.groupby('Region')[['Revenue', 'Enrollments']].sum()
    totals = pt_df.sum()
    pt_df.loc['Grand Total'] = totals
    format_dict = {'Revenue': '₹{:,.2f}', 'Enrollments': '{:,.0f}'}

# Display Table
if pt_df is not None:
    st.markdown(f"### {selected_pivot[3:]}")
    
    # Apply styling
    styled_df = pt_df.style.format(format_dict)
    
    # Render table
    st.dataframe(styled_df, width='stretch')
    
    # Export to CSV
    csv = pt_df.to_csv().encode('utf-8')
    st.download_button(
        label="Download Pivot Table as CSV",
        data=csv,
        file_name=f"{selected_pivot.lower().replace(' ', '_').replace('.', '')}.csv",
        mime='text/csv'
    )

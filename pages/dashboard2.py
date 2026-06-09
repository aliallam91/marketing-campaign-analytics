import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("d:/Depi Project/style.css")

# Retrieve raw merged dataset from session state
if 'all_data' not in st.session_state:
    st.warning("Please go to the Home page first to initialize data.")
    st.stop()

df_raw = st.session_state['all_data']['merged']

# Page Title
st.markdown("""
<div class="excel-header">
    <h1 class="excel-header-title">Regional & Asset Analytics</h1>
</div>
""", unsafe_allow_html=True)

# Main Multi-column layout (1 part Slicers, 4 parts Content)
col_slicers, col_content = st.columns([1, 4])

with col_slicers:
    st.markdown("<h3 style='color: #50164A; font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; margin-top: 0;'>Excel Slicers</h3>", unsafe_allow_html=True)
    
    # Render slicers inside a container mimicking Excel Sidebar Rounded Rectangle 5
    st.markdown('<div class="slicer-grid-panel">', unsafe_allow_html=True)
    
    # 1. Date Slicer
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">📅 Date Range</div><div class="slicer-box-body">', unsafe_allow_html=True)
    min_date = df_raw['Date'].min().date()
    max_date = df_raw['Date'].max().date()
    date_val = st.date_input("Date Filter", [min_date, max_date], min_value=min_date, max_value=max_date, label_visibility="collapsed", key="d2_date")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # 2. Region Slicer
    region_options = sorted(df_raw['Region'].dropna().unique())
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">🌍 Region</div><div class="slicer-box-body">', unsafe_allow_html=True)
    selected_regions = st.pills("Regions", region_options, selection_mode="multi", label_visibility="collapsed", key="d2_region")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # 3. Creative Asset Slicer
    asset_options = sorted(df_raw['Creative Type'].dropna().unique())
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">🎨 Creative Asset</div><div class="slicer-box-body">', unsafe_allow_html=True)
    selected_assets = st.pills("Assets", asset_options, selection_mode="multi", label_visibility="collapsed", key="d2_asset")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # 4. Manager Slicer
    manager_options = sorted(df_raw['Manager'].dropna().unique())
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">👤 Manager</div><div class="slicer-box-body">', unsafe_allow_html=True)
    selected_managers = st.pills("Managers", manager_options, selection_mode="multi", label_visibility="collapsed", key="d2_manager")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Apply filters locally on the page
df_filtered = df_raw.copy()

# Date filter
if isinstance(date_val, tuple) and len(date_val) == 2:
    start_date, end_date = date_val
    df_filtered = df_filtered[(df_filtered['Date'].dt.date >= start_date) & (df_filtered['Date'].dt.date <= end_date)]

# Slicer filters
if selected_regions:
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
if selected_assets:
    df_filtered = df_filtered[df_filtered['Creative Type'].isin(selected_assets)]
if selected_managers:
    df_filtered = df_filtered[df_filtered['Manager'].isin(selected_managers)]

# Propagate filtered dataframe to session state for pivots page to optionally read
st.session_state['filtered_df'] = df_filtered
st.session_state['is_filtered'] = (
    len(selected_regions) > 0 or 
    len(selected_assets) > 0 or 
    len(selected_managers) > 0 or
    (isinstance(date_val, tuple) and len(date_val) == 2 and (date_val[0] != min_date or date_val[1] != max_date))
)

with col_content:
    if st.session_state['is_filtered']:
        st.markdown("<div style='margin-bottom: 15px;'><span style='background-color: #FEE2E2; color: #DC2626; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; border: 1px solid #FCA5A5;'>⚠️ Slicers Active - Data is Filtered</span></div>", unsafe_allow_html=True)

    # Helper functions for number formatting
    def format_currency(val):
        if val >= 10_000_000:
            return f"₹{val/10_000_000:.2f} Cr"
        elif val >= 100_000:
            return f"₹{val/100_000:.2f} L"
        else:
            return f"₹{val:,.2f}"

    def format_count(val):
        if val >= 1_000_000:
            return f"{val/1_000_000:.2f} M"
        elif val >= 1_000:
            return f"{val/1_000:.1f} K"
        else:
            return str(val)

    # Calculations for KPI cards
    total_revenue = df_filtered['Revenue'].sum()
    total_cost = df_filtered['Cost'].sum()
    total_leads = df_filtered['Leads'].sum()
    total_enrollments = df_filtered['Enrollments'].sum()
    overall_roas = total_revenue / total_cost if total_cost > 0 else 0
    overall_cpl = total_cost / total_leads if total_leads > 0 else 0

    # Render KPI Cards in Ice-Blue panels
    kpi_cols = st.columns(5)

    with kpi_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{format_currency(total_revenue)}</div>
            <div class="metric-subtext">Exact: ₹{total_revenue:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Cost</div>
            <div class="metric-value">{format_currency(total_cost)}</div>
            <div class="metric-subtext">Exact: ₹{total_cost:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Leads</div>
            <div class="metric-value">{format_count(total_leads)}</div>
            <div class="metric-subtext">Exact: {total_leads:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Enrollments</div>
            <div class="metric-value">{format_count(total_enrollments)}</div>
            <div class="metric-subtext">Exact: {total_enrollments:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[4]:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #E2EAF4 !important; border-color: #9EC0E6 !important;">
            <div class="metric-label" style="color: #1E3A8A;">Overall ROAS</div>
            <div class="metric-value" style="color: #1E3A8A;">{overall_roas:.2f}x</div>
            <div class="metric-subtext" style="color: rgba(30, 58, 138, 0.7);">CPL: {format_currency(overall_cpl)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1 Charts (Creative Asset Performance + Revenue by Region)
    row1_cols = st.columns([3, 2])

    with row1_cols[0]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>🎨 Creative Asset Performance</div>", unsafe_allow_html=True)
        
        asset_toggle = st.radio(
            "Asset Metric View Option", 
            ["Revenue (₹)", "Engagement (Clicks & Enrollments)"], 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Group by Creative Type
        asset_df = df_filtered.groupby('Creative Type')[['Clicks', 'Enrollments', 'Revenue']].sum().reset_index()
        
        if "Revenue" in asset_toggle:
            fig1 = px.bar(
                asset_df,
                y='Creative Type',
                x='Revenue',
                orientation='h',
                color_discrete_sequence=['#388E3C'],
                labels={'Revenue': 'Revenue (₹)', 'Creative Type': 'Creative Asset'},
                height=240,
                template='plotly_white'
            )
            fig1.update_xaxes(gridcolor='#F1F5F9', title_text="Revenue (₹)")
        else:
            asset_df_melted = asset_df.melt(id_vars='Creative Type', value_vars=['Clicks', 'Enrollments'],
                                             var_name='Metric', value_name='Count')
            fig1 = px.bar(
                asset_df_melted,
                y='Creative Type',
                x='Count',
                color='Metric',
                barmode='group',
                orientation='h',
                color_discrete_map={'Clicks': '#3b82f6', 'Enrollments': '#fbbf24'},
                labels={'Count': 'Count', 'Creative Type': 'Creative Asset'},
                height=240,
                template='plotly_white'
            )
            fig1.update_xaxes(gridcolor='#F1F5F9', title_text="Count")
            
        fig1.update_layout(
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font_family='Plus Jakarta Sans',
            font_color='#2D3748',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=80, r=20, t=10, b=20),
            yaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig1, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_cols[1]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>🍩 Revenue Share By Region</div>", unsafe_allow_html=True)
        
        # Group by Region for Revenue
        region_df = df_filtered.groupby('Region')[['Cost', 'Revenue', 'Enrollments']].sum().reset_index()
        
        fig2 = px.pie(
            region_df,
            values='Revenue',
            names='Region',
            color_discrete_sequence=['#50164A', '#78206E', '#1C355E', '#3b82f6', '#fbbf24'],
            height=280,
            template='plotly_white'
        )
        fig2.update_layout(
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font_family='Plus Jakarta Sans',
            font_color='#2D3748',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=10, b=20)
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 2 Charts (Cost vs Revenue by Region + Enrollments Share by Region)
    row2_cols = st.columns([3, 2])

    with row2_cols[0]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>📊 Cost vs Revenue By Region</div>", unsafe_allow_html=True)
        
        region_df_melted = region_df.melt(id_vars='Region', value_vars=['Cost', 'Revenue'],
                                           var_name='Metric', value_name='Amount')
        
        fig3 = px.bar(
            region_df_melted,
            x='Region',
            y='Amount',
            color='Metric',
            barmode='group',
            color_discrete_map={'Cost': '#D32F2F', 'Revenue': '#388E3C'},
            labels={'Amount': 'Amount (₹)', 'Region': 'Region'},
            height=280,
            template='plotly_white'
        )
        fig3.update_layout(
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font_family='Plus Jakarta Sans',
            font_color='#2D3748',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=10, b=20),
            xaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='rgba(0,0,0,0)'),
            yaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='#F1F5F9')
        )
        st.plotly_chart(fig3, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_cols[1]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>🍩 Enrollment Share By Region</div>", unsafe_allow_html=True)
        
        fig4 = px.pie(
            region_df,
            values='Enrollments',
            names='Region',
            color_discrete_sequence=['#50164A', '#78206E', '#1C355E', '#3b82f6', '#fbbf24'],
            height=280,
            template='plotly_white'
        )
        fig4.update_layout(
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font_family='Plus Jakarta Sans',
            font_color='#2D3748',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=10, b=20)
        )
        fig4.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig4, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

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

local_css("style.css")

# Retrieve raw merged dataset from session state
if 'all_data' not in st.session_state:
    st.warning("Please go to the Home page first to initialize data.")
    st.stop()

df_raw = st.session_state['all_data']['merged']

# Page Title
st.markdown("""
<div class="excel-header">
    <h1 class="excel-header-title">Platform Performance Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# Main Multi-column layout (1 part Slicers, 4 parts Content)
col_slicers, col_content = st.columns([1, 4])

with col_slicers:
    st.markdown("<h3 style='color: #50164A; font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; margin-top: 0;'>Excel Slicers</h3>", unsafe_allow_html=True)
    
    # Render slicers inside a container mimicking Excel Sidebar Rounded Rectangle 2
    st.markdown('<div class="slicer-grid-panel">', unsafe_allow_html=True)
    
    # 1. Date Slicer
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">📅 Date Range</div><div class="slicer-box-body">', unsafe_allow_html=True)
    min_date = df_raw['Date'].min().date()
    max_date = df_raw['Date'].max().date()
    date_val = st.date_input("Date Filter", [min_date, max_date], min_value=min_date, max_value=max_date, label_visibility="collapsed", key="d1_date")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # 2. Campaign Slicer
    campaign_options = sorted(df_raw['CampaignName'].dropna().unique())
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">📁 Campaign Name</div><div class="slicer-box-body">', unsafe_allow_html=True)
    selected_campaigns = st.pills("Campaigns", campaign_options, selection_mode="multi", label_visibility="collapsed", key="d1_campaign")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # 3. Platform Slicer
    channel_options = sorted(df_raw['Channel'].dropna().unique())
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">🔌 Platform</div><div class="slicer-box-body">', unsafe_allow_html=True)
    selected_channels = st.pills("Platforms", channel_options, selection_mode="multi", label_visibility="collapsed", key="d1_channel")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # 4. Audience Slicer
    audience_options = sorted(df_raw['TargetAudience'].dropna().unique())
    st.markdown('<div class="slicer-box"><div class="slicer-box-header">👥 Target Audience</div><div class="slicer-box-body">', unsafe_allow_html=True)
    selected_audiences = st.pills("Audiences", audience_options, selection_mode="multi", label_visibility="collapsed", key="d1_audience")
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Apply filters locally on the page
df_filtered = df_raw.copy()

# Date filter
if isinstance(date_val, tuple) and len(date_val) == 2:
    start_date, end_date = date_val
    df_filtered = df_filtered[(df_filtered['Date'].dt.date >= start_date) & (df_filtered['Date'].dt.date <= end_date)]

# Slicer filters
if selected_campaigns:
    df_filtered = df_filtered[df_filtered['CampaignName'].isin(selected_campaigns)]
if selected_channels:
    df_filtered = df_filtered[df_filtered['Channel'].isin(selected_channels)]
if selected_audiences:
    df_filtered = df_filtered[df_filtered['TargetAudience'].isin(selected_audiences)]

# Propagate filtered dataframe to session state for pivots page to optionally read
st.session_state['filtered_df'] = df_filtered
st.session_state['is_filtered'] = (
    len(selected_campaigns) > 0 or 
    len(selected_channels) > 0 or 
    len(selected_audiences) > 0 or
    (isinstance(date_val, tuple) and len(date_val) == 2 and (date_val[0] != min_date or date_val[1] != max_date))
)

with col_content:
    if st.session_state['is_filtered']:
        st.markdown("<div style='margin-bottom: 15px;'><span style='background-color: #FEE2E2; color: #DC2626; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; border: 1px solid #FCA5A5;'>⚠️ Slicers Active - Data is Filtered</span></div>", unsafe_allow_html=True)

    # Helper function for currency formatting
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
    overall_ctr = df_filtered['Clicks'].sum() / df_filtered['Impressions'].sum() if df_filtered['Impressions'].sum() > 0 else 0

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
            <div class="metric-subtext" style="color: rgba(30, 58, 138, 0.7);">CTR: {overall_ctr:.2%}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1 Charts (Cost vs Revenue + Spend share)
    row1_cols = st.columns([3, 2])

    with row1_cols[0]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>📊 Cost vs Revenue By Platform</div>", unsafe_allow_html=True)
        
        # Aggregate data by platform (Channel)
        platform_df = df_filtered.groupby('Channel')[['Cost', 'Revenue']].sum().reset_index()
        platform_df_melted = platform_df.melt(id_vars='Channel', value_vars=['Cost', 'Revenue'], 
                                              var_name='Metric', value_name='Amount')
        
        fig1 = px.bar(
            platform_df_melted,
            x='Channel',
            y='Amount',
            color='Metric',
            barmode='group',
            color_discrete_map={'Cost': '#D32F2F', 'Revenue': '#388E3C'}, # Excel red/green
            labels={'Amount': 'Amount (₹)', 'Channel': 'Platform'},
            height=280,
            template='plotly_white'
        )
        fig1.update_layout(
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font_family='Plus Jakarta Sans',
            font_color='#2D3748',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=10, b=20),
            xaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='rgba(0,0,0,0)'),
            yaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='#F1F5F9')
        )
        st.plotly_chart(fig1, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_cols[1]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>🍩 Spending Share By Platform</div>", unsafe_allow_html=True)
        
        fig2 = px.pie(
            platform_df,
            values='Cost',
            names='Channel',
            hole=0.4,
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

    # Row 2 Charts (Funnel + Audience matrix)
    row2_cols = st.columns([3, 2])

    with row2_cols[0]:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-title'>📈 Cross-Channel Acquisition Funnel</div>", unsafe_allow_html=True)
        
        chart_type = st.radio("Funnel Visual Selector", ["Funnel Visual", "Trend Line Visual (Excel Exact)"], horizontal=True, label_visibility="collapsed")
        
        if "Funnel" in chart_type:
            funnel_metrics = {
                'Stage': ['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments'],
                'Count': [
                    df_filtered['Impressions'].sum(),
                    df_filtered['Clicks'].sum(),
                    df_filtered['Leads'].sum(),
                    df_filtered['Applications'].sum(),
                    df_filtered['Enrollments'].sum()
                ]
            }
            funnel_df = pd.DataFrame(funnel_metrics)
            
            fig3 = go.Figure(go.Funnel(
                y=funnel_df['Stage'],
                x=funnel_df['Count'],
                textinfo="value+percent initial",
                marker=dict(color=["#50164A", "#78206E", "#1C355E", "#3b82f6", "#10b981"])
            ))
            fig3.update_layout(
                height=280,
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FFFFFF',
                font_family='Plus Jakarta Sans',
                font_color='#2D3748',
                margin=dict(l=80, r=20, t=10, b=20)
            )
            st.plotly_chart(fig3, width='stretch')
        else:
            line_data = df_filtered.groupby('Channel')[['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments']].sum().reset_index()
            
            fig3 = go.Figure()
            metrics = ['Impressions', 'Clicks', 'Leads', 'Applications', 'Enrollments']
            colors = ["#50164A", "#78206E", "#1C355E", "#3b82f6", "#10b981"]
            
            for idx, metric in enumerate(metrics):
                fig3.add_trace(go.Scatter(
                    x=line_data['Channel'],
                    y=line_data[metric],
                    mode='lines+markers',
                    name=metric,
                    line=dict(color=colors[idx], width=2.5),
                    marker=dict(size=7)
                ))
                
            fig3.update_layout(
                height=280,
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
        st.markdown("<div class='chart-title'>👥 Audience Engagement Matrix</div>", unsafe_allow_html=True)
        
        # Group by Audience Age
        audience_df = df_filtered.groupby('TargetAudience')[['Leads', 'Enrollments']].sum().reset_index()
        audience_df_melted = audience_df.melt(id_vars='TargetAudience', value_vars=['Leads', 'Enrollments'],
                                               var_name='Metric', value_name='Count')
        
        fig4 = px.bar(
            audience_df_melted,
            x='TargetAudience',
            y='Count',
            color='Metric',
            barmode='group',
            color_discrete_map={'Leads': '#3b82f6', 'Enrollments': '#fbbf24'},
            labels={'Count': 'Count', 'TargetAudience': 'Age Groups'},
            height=280,
            template='plotly_white'
        )
        fig4.update_layout(
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font_family='Plus Jakarta Sans',
            font_color='#2D3748',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=10, b=20),
            xaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='rgba(0,0,0,0)'),
            yaxis=dict(showline=True, linecolor='#CBD5E1', gridcolor='#F1F5F9')
        )
        st.plotly_chart(fig4, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

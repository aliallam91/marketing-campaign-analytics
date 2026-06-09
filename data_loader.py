import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(file_path='d:/Depi Project/The Final Project.xlsx'):
    """
    Loads sheets from the Excel file, cleans columns, merges fact and dimension sheets,
    and returns both the merged dataset and the individual dataframes.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found at: {file_path}")
        
    xls = pd.ExcelFile(file_path)
    
    # Load raw dataframes
    fact = pd.read_excel(xls, 'FactCampaignPerformance')
    dim_campaign = pd.read_excel(xls, 'DimCampaignMeta')
    dim_channel = pd.read_excel(xls, 'DimChannelRates')
    dim_audience = pd.read_excel(xls, 'DimTargetAudience')
    dim_region = pd.read_excel(xls, 'DimRegion')
    dim_date = pd.read_excel(xls, 'DimDate')
    
    # Clean column names (strip whitespace)
    for df in [fact, dim_campaign, dim_channel, dim_audience, dim_region, dim_date]:
        df.columns = [str(c).strip() for c in df.columns]
        
    # Standardize Cost & Revenue column names across fact
    fact = fact.rename(columns={
        'Cost ()': 'Cost', 'Cost (\u20b9)': 'Cost', 'Cost (?)': 'Cost',
        'Revenue ()': 'Revenue', 'Revenue (\u20b9)': 'Revenue', 'Revenue (?)': 'Revenue'
    })
    
    # Standardize Budget column name in DimCampaignMeta
    dim_campaign = dim_campaign.rename(columns={
        'Budget ()': 'Budget', 'Budget (\u20b9)': 'Budget', 'Budget (?)': 'Budget'
    })
    
    # Clean dimension string contents for better UI display
    # Replace the weird character in audience age (e.g. '1721 Age') with a proper en-dash or hyphen
    dim_audience['TargetAudience'] = dim_audience['TargetAudience'].str.replace('\ufffd', '–', regex=False)
    dim_audience['TargetAudience'] = dim_audience['TargetAudience'].str.replace('?', '–', regex=False)
    
    # Do the same in case fact has any audience strings (it holds ID, so we join on ID)
    
    # Make sure IDs are string type for clean joins
    fact['CampaignID'] = fact['CampaignID'].astype(str)
    fact['ChannelID'] = fact['ChannelID'].astype(str)
    fact['RegionID'] = fact['RegionID'].astype(str)
    fact['TargetAudienceID'] = fact['TargetAudienceID'].astype(str)
    
    dim_campaign['CampaignID'] = dim_campaign['CampaignID'].astype(str)
    dim_channel['ChannelID'] = dim_channel['ChannelID'].astype(str)
    dim_region['RegionID'] = dim_region['RegionID'].astype(str)
    dim_audience['TargetAudienceID'] = dim_audience['TargetAudienceID'].astype(str)
    
    # Left join fact with dimensions
    merged = fact.merge(dim_campaign, on='CampaignID', how='left')
    merged = merged.merge(dim_channel, on='ChannelID', how='left')
    merged = merged.merge(dim_region, on='RegionID', how='left')
    merged = merged.merge(dim_audience, on='TargetAudienceID', how='left')
    
    # Parse dates
    merged['Date'] = pd.to_datetime(merged['Date'])
    
    # Ensure all calculated columns are correctly populated in row-level for exact Excel pivot replication
    merged['ROAS'] = merged['Revenue'] / merged['Cost']
    merged['CTR'] = merged['Clicks'] / merged['Impressions']
    merged['CPC'] = merged['Cost'] / merged['Clicks']
    merged['CPL'] = merged['Cost'] / merged['Leads']
    merged['Cost Per Enrollment'] = merged['Cost'] / merged['Enrollments']
    
    # In case there are NaNs or Infs from division by zero, clean them up
    for col in ['ROAS', 'CTR', 'CPC', 'CPL', 'Cost Per Enrollment']:
        merged[col] = merged[col].replace([float('inf'), float('-inf')], 0)
        merged[col] = merged[col].fillna(0)
        
    return {
        'merged': merged,
        'fact': fact,
        'dim_campaign': dim_campaign,
        'dim_channel': dim_channel,
        'dim_region': dim_region,
        'dim_audience': dim_audience,
        'dim_date': dim_date
    }

import pandas as pd
import json

def get_family(name):
    """Helper to group launch vehicles into families."""
    if not isinstance(name, str):
        return 'Other'
    name = name.upper()
    if 'PSLV' in name: return 'PSLV'
    if 'GSLV' in name or 'LVM3' in name: return 'GSLV/LVM3' # Grouping heavier lifters
    if 'SLV' in name: return 'SLV/ASLV'
    return 'Other'

def get_growth_trend(df):
    """
    Returns annual mission counts.
    Format suitable for line plot (Year on X, Count on Y).
    """
    if df.empty or 'Year' not in df.columns:
        return []
    trend = df.groupby('Year').size().reset_index(name='Mission_Count')
    return trend.to_dict(orient='records')

def get_success_rates(df):
    """
    Success rate for top 3 launch vehicle families.
    """
    if df.empty or 'launch_vehicle' not in df.columns or 'Success_Flag' not in df.columns:
        return []

    df['Family'] = df['launch_vehicle'].apply(get_family)
    
    stats = df.groupby('Family')['Success_Flag'].agg(['count', 'mean']).reset_index()
    stats.columns = ['Family', 'Total_Launches', 'Success_Rate']
    stats = stats.sort_values(by='Total_Launches', ascending=False).head(3)
    return stats.to_dict(orient='records')

def get_strategic_focus(df):
    """
    Distribution of missions by Application.
    """
    if df.empty or 'application' not in df.columns:
        return []
    focus = df['application'].value_counts().reset_index()
    focus.columns = ['Application', 'Count']
    return focus.to_dict(orient='records')

def get_orbit_complexity(df):
    """
    Returns data for Sankey Diagram: Source (Vehicle) -> Target (Orbit).
    """
    if df.empty or 'launch_vehicle' not in df.columns or 'orbit_type' not in df.columns:
        return []

    if 'Family' not in df.columns:
        df['Family'] = df['launch_vehicle'].apply(get_family)

    # Group by Family and Orbit to get counts (Link Value)
    links = df.groupby(['Family', 'orbit_type']).size().reset_index(name='value')
    links = links.rename(columns={'Family': 'source', 'orbit_type': 'target'})
    
    # Return list of dicts: [{'source': 'PSLV', 'target': 'SSPO', 'value': 20}, ...]
    return links.to_dict(orient='records')

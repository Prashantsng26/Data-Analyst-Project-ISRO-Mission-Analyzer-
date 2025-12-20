import pandas as pd
import json

def get_growth_trend(df):
    """
    Returns annual mission counts.
    Format suitable for line plot (Year on X, Count on Y).
    """
    trend = df.groupby('Year').size().reset_index(name='Mission_Count')
    return trend.to_dict(orient='records')

def get_success_rates(df):
    """
    Success rate for top 3 launch vehicle families.
    """
    # Simply grouping by exact vehicle name might be too granular (e.g. PSLV-C1, PSLV-C2).
    # We need to group by family.
    def get_family(name):
        name = name.upper()
        if 'PSLV' in name: return 'PSLV'
        if 'GSLV' in name or 'LVM3' in name: return 'GSLV/LVM3' # Grouping heavier lifters
        if 'SLV' in name: return 'SLV/ASLV'
        return 'Other'

    df['Family'] = df['launch_vehicle'].apply(get_family)
    
    stats = df.groupby('Family')['Success_Flag'].agg(['count', 'mean']).reset_index()
    stats.columns = ['Family', 'Total_Launches', 'Success_Rate']
    stats = stats.sort_values(by='Total_Launches', ascending=False).head(3)
    return stats.to_dict(orient='records')

def get_strategic_focus(df):
    """
    Distribution of missions by Application.
    """
    focus = df['application'].value_counts().reset_index()
    focus.columns = ['Application', 'Count']
    return focus.to_dict(orient='records')

def get_orbit_complexity(df):
    """
    Returns data for Sankey Diagram: Source (Vehicle) -> Target (Orbit).
    """
    if 'Family' not in df.columns:
        def get_family(name):
            name = name.upper()
            if 'PSLV' in name: return 'PSLV'
            if 'GSLV' in name or 'LVM3' in name: return 'GSLV/LVM3'
            if 'SLV' in name: return 'SLV/ASLV'
            return 'Other'
        df['Family'] = df['launch_vehicle'].apply(get_family)

    # Group by Family and Orbit to get counts (Link Value)
    links = df.groupby(['Family', 'orbit_type']).size().reset_index(name='value')
    links = links.rename(columns={'Family': 'source', 'orbit_type': 'target'})
    
    # Return list of dicts: [{'source': 'PSLV', 'target': 'SSPO', 'value': 20}, ...]
    return links.to_dict(orient='records')

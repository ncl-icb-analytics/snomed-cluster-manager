# =============================================================================
# SNOMED Cluster Manager - Chart Components
# =============================================================================

import pandas as pd
import altair as alt
import streamlit as st


def create_org_bar_chart(df, agg_level):
    """Create bar chart for organisation rates"""
    if df.empty:
        return None
    
    # Sort by rate for better visualization
    df_sorted = df.sort_values('RATE_PER_1000', ascending=True)
    
    # Create horizontal bar chart
    chart = alt.Chart(df_sorted).mark_bar().encode(
        x=alt.X('RATE_PER_1000:Q', 
                title='Rate per 1,000 population',
                scale=alt.Scale(domain=[0, df_sorted['RATE_PER_1000'].max() * 1.1])),
        y=alt.Y('UNIT_NAME:N', 
                title=agg_level,
                sort=None),  # Keep the sorted order from dataframe
        tooltip=[
            alt.Tooltip('UNIT_NAME:N', title=agg_level),
            alt.Tooltip('TOTAL_POPULATION:Q', format=',.0f', title='Population'),
            alt.Tooltip('PATIENTS_WITH_CODE:Q', format=',.0f', title='Patients'),
            alt.Tooltip('NEW_PATIENTS_30D:Q', format=',.0f', title='New (30d)'),
            alt.Tooltip('RATE_PER_1000:Q', format='.2f', title='Rate per 1,000')
        ]
    ).properties(
        height=max(300, len(df_sorted) * 25),  # Dynamic height based on number of units
        title=f'{agg_level} Rates'
    ).interactive()
    
    return chart


def create_practice_scatter(df):
    """Create scatter plot for practice-level data showing age vs rate"""
    if df.empty:
        return None
    
    # Calculate average rate for reference line
    avg_rate = df['RATE_PER_1000'].mean()
    
    # Create scatter plot
    scatter = alt.Chart(df).mark_circle().encode(
        x=alt.X('AVG_AGE:Q', 
                title='Average Age',
                scale=alt.Scale(domain=[df['AVG_AGE'].min() - 2, df['AVG_AGE'].max() + 2])),
        y=alt.Y('RATE_PER_1000:Q', 
                title='Rate per 1,000 population'),
        size=alt.Size('PATIENTS_WITH_CODE:Q',
                     title='Patients with Code',
                     scale=alt.Scale(range=[20, 400])),
        color=alt.Color('RATE_PER_1000:Q',
                       scale=alt.Scale(scheme='orangered'),
                       title='Rate'),
        tooltip=[
            alt.Tooltip('UNIT_NAME:N', title='Practice'),
            alt.Tooltip('AVG_AGE:Q', format='.1f', title='Avg Age'),
            alt.Tooltip('TOTAL_POPULATION:Q', format=',.0f', title='Population'),
            alt.Tooltip('PATIENTS_WITH_CODE:Q', format=',.0f', title='Patients with Code'),
            alt.Tooltip('RATE_PER_1000:Q', format='.2f', title='Rate per 1,000')
        ]
    ).properties(
        width=600,
        height=400,
        title='Practice Rates by Average Age'
    ).interactive()
    
    # Add average rate reference line
    rule = alt.Chart(pd.DataFrame({'y': [avg_rate]})).mark_rule(
        strokeDash=[5, 5],
        color='gray'
    ).encode(y='y:Q')
    
    # Add text label for average
    text = alt.Chart(pd.DataFrame({
        'y': [avg_rate],
        'x': [df['AVG_AGE'].max() - 1],
        'label': [f'Avg: {avg_rate:.1f}']
    })).mark_text(
        align='right',
        baseline='bottom',
        color='gray',
        fontSize=10
    ).encode(
        x='x:Q',
        y='y:Q',
        text='label:N'
    )
    
    return scatter + rule + text
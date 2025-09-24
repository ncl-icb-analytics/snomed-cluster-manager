# =============================================================================
# SNOMED Cluster Manager - Demographics Page
# =============================================================================

import streamlit as st
from database import rerun
from services.demographics_service import get_demographics_summary, get_demographics_by_care_team, get_care_team_summary, get_system_age_sex_distribution
from utils.charts import create_population_pyramid


def render_demographics():
    """Render the Demographics page"""
    
    # Header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = 'home'
            rerun()
    
    st.title("👥 Population Health Demographics")
    
    st.markdown("Overview of the population demographics across the system.")
    
    # Load system-wide demographics
    with st.spinner("Loading demographics data..."):
        demographics_summary = get_demographics_summary()
    
    if not demographics_summary.empty:
        summary = demographics_summary.iloc[0]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Active Patients", f"{summary['TOTAL_ACTIVE_PATIENTS']:,.0f}")
        with col2:
            st.metric("Total Practices", f"{summary['TOTAL_PRACTICES']:,.0f}")
        with col3:
            st.metric("Total PCNs", f"{summary['TOTAL_PCNS']:,.0f}")
        with col4:
            st.metric("Average Age", f"{summary['AVG_AGE']:.1f} years")
        
        # Age/Sex Distribution
        st.subheader("System-wide Age/Sex Distribution")
        age_sex_dist = get_system_age_sex_distribution()
        if not age_sex_dist.empty:
            create_population_pyramid(age_sex_dist)
        else:
            st.warning("No age/sex distribution data available")
        
        # Care Team Analysis
        st.subheader("Care Team Analysis")
        care_team_level = st.selectbox(
            "Select care team level:",
            options=["System", "PCN", "Practice"],
            index=0
        )
        
        if care_team_level != "System":
            care_team_data = get_care_team_summary(care_team_level)
            if not care_team_data.empty:
                st.dataframe(care_team_data, use_container_width=True)
                
                # Download button
                csv = care_team_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Care Team Data",
                    data=csv,
                    file_name=f"care_team_summary_{care_team_level.lower()}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No {care_team_level.lower()} level data available")
    else:
        st.error("Unable to load demographics data")
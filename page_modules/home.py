# =============================================================================
# SNOMED Cluster Manager - Home Page
# =============================================================================

import streamlit as st
import pandas as pd
from database import rerun
from services.cluster_service import get_all_clusters
from components.cluster_components import render_flash_message
from utils.helpers import get_status_emoji, format_time_ago
from config import CLUSTER_TYPE_DISPLAY, STALE_LABEL


def render_home():
    """Render the Home page with cluster list and search"""
    
    # Load cluster data with error handling
    try:
        clusters_df = get_all_clusters()
    except Exception as e:
        st.error(f"⚠️ Database connection error: {str(e)}")
        st.info("Please refresh the page or contact support if this persists.")
        clusters_df = pd.DataFrame()

    # Flash message component
    render_flash_message()

    if clusters_df.empty:
        st.info("🌟 **Welcome to SNOMED Cluster Manager!** No ECL clusters found yet.")
        st.markdown("Get started by creating your first cluster with the **✨ Add New** button above.")
    else:
        # KPI indicators
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_clusters = len(clusters_df)
            st.metric("Total Clusters", total_clusters)
        with col2:
            fresh_count = len(clusters_df[clusters_df['STATUS'] == 'Fresh'])
            st.metric("Fresh", fresh_count)
        with col3:
            stale_count = len(clusters_df[clusters_df['STATUS'] == STALE_LABEL])
            st.metric("Stale", stale_count)
        with col4:
            total_codes = clusters_df['RECORD_COUNT'].fillna(0).sum()
            st.metric("Total Codes", f"{int(total_codes):,}")
        
        st.markdown("---")
        
        # Search bar
        st.subheader("Search Clusters")
        search_term = st.text_input("", placeholder="Search by name or description...", label_visibility="collapsed")
        
        # Filter clusters based on search
        filtered_clusters = clusters_df
        if search_term:
            mask = (clusters_df['CLUSTER_ID'].str.contains(search_term, case=False, na=False) | 
                   clusters_df['DESCRIPTION'].str.contains(search_term, case=False, na=False))
            filtered_clusters = clusters_df[mask]
            if filtered_clusters.empty:
                st.info(f"No clusters match '{search_term}'")
            else:
                st.caption(f"Found {len(filtered_clusters)} cluster(s) matching '{search_term}'")
        
        # Cluster list
        if not filtered_clusters.empty:
            for idx, cluster in filtered_clusters.iterrows():
                # Status emoji
                status_emoji = get_status_emoji(cluster, STALE_LABEL)
                
                # Row layout
                col1, col2, col3, col4, col5 = st.columns([0.3, 3.5, 2.2, 1.4, 1])
                
                with col1:
                    st.markdown(f"<div style='text-align: center; line-height: 1.2;'>{status_emoji}</div>", 
                              unsafe_allow_html=True)
                
                with col2:
                    # Cluster type badge
                    cluster_type = cluster.get('CLUSTER_TYPE', 'OBSERVATION')
                    type_text = CLUSTER_TYPE_DISPLAY.get(cluster_type, '[observation]')
                    st.markdown(f"**{cluster['CLUSTER_ID']}** <small style='color: #999;'>{type_text}</small>", 
                              unsafe_allow_html=True)
                    if cluster['DESCRIPTION']:
                        st.caption(cluster['DESCRIPTION'])
                
                with col3:
                    # Code count
                    code_count = int(cluster['RECORD_COUNT']) if not pd.isna(cluster['RECORD_COUNT']) else 0
                    codes_text = f"{code_count:,}"
                    code_label = "code" if code_count == 1 else "codes"
                    st.text(f"{codes_text} {code_label}")
                    refresh_text = format_time_ago(cluster['LAST_SUCCESSFUL_REFRESH'])
                    st.caption(f"Refreshed {refresh_text}")
                
                with col4:
                    updated_by = cluster.get('UPDATED_BY', 'N/A')
                    if pd.isna(updated_by):
                        updated_by = 'N/A'
                    st.caption("Updated by")
                    st.text(str(updated_by))

                with col5:
                    # Action buttons
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("👁️ View", key=f"view_{cluster['CLUSTER_ID']}", help="View details"):
                            st.session_state.selected_cluster = cluster['CLUSTER_ID']
                            st.session_state.page = 'details'
                            rerun()
                    with btn_col2:
                        if st.button("✏️ Edit", key=f"edit_{cluster['CLUSTER_ID']}", help="Edit"):
                            st.session_state.selected_cluster = cluster['CLUSTER_ID']
                            st.session_state.page = 'edit'
                            rerun()
                
                # Spacing
                if idx < len(filtered_clusters) - 1:
                    st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
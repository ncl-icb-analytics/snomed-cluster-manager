# =============================================================================
# SNOMED Cluster Manager - Cluster UI Components
# =============================================================================

import streamlit as st
from services.cluster_service import get_cluster_change_history
from utils.helpers import format_time_ago
from config import CLUSTER_TYPE_DISPLAY


def render_change_history(cluster_id, cluster=None, limit=50):
    """Render change history for a cluster"""
    history_df = get_cluster_change_history(cluster_id, limit)
    
    st.subheader("📋 Change History")
    
    # Show cluster creation/modification info if available
    if cluster is not None and not cluster.empty:
        col1, col2 = st.columns(2)
        with col1:
            if cluster.get('CREATED_BY'):
                st.caption(f"**Created by:** {cluster.get('CREATED_BY')} • {format_time_ago(cluster.get('CREATED_AT'))}")
        with col2:
            if cluster.get('UPDATED_BY'):
                st.caption(f"**Last modified by:** {cluster.get('UPDATED_BY')} • {format_time_ago(cluster.get('UPDATED_AT'))}")
    
    if history_df.empty:
        st.info("No change history available for this cluster. Changes are only tracked when codes are added or removed during cache refreshes.")
        return
    
    # Group by refresh session for better display
    sessions = history_df['REFRESH_SESSION_ID'].unique()
    
    for session in sessions[:25]:  # Show last 25 refresh sessions
        session_data = history_df[history_df['REFRESH_SESSION_ID'] == session]
        
        if session_data.empty:
            continue
        
        # Get session info
        first_change = session_data.iloc[0]
        timestamp = first_change['CHANGE_TIMESTAMP']
        changed_by = first_change['CHANGED_BY'] or 'System'
        
        # Count changes
        added_count = len(session_data[session_data['CHANGE_TYPE'] == 'ADDED'])
        removed_count = len(session_data[session_data['CHANGE_TYPE'] == 'REMOVED'])
        
        # Display session summary
        with st.expander(f"🔄 {format_time_ago(timestamp)} by {changed_by} (+{added_count} -{removed_count})"):
            if added_count > 0:
                st.write("**Added codes:**")
                added_codes = session_data[session_data['CHANGE_TYPE'] == 'ADDED'][['CODE', 'DISPLAY']].head(50)
                st.dataframe(added_codes, use_container_width=True)
                if added_count > 50:
                    st.caption(f"... and {added_count - 50} more")
            
            if removed_count > 0:
                st.write("**Removed codes:**")
                removed_codes = session_data[session_data['CHANGE_TYPE'] == 'REMOVED'][['CODE', 'DISPLAY']].head(50)
                st.dataframe(removed_codes, use_container_width=True)
                if removed_count > 50:
                    st.caption(f"... and {removed_count - 50} more")


def render_cluster_metadata(cluster):
    """Render cluster metadata information"""
    st.subheader("ℹ️ Cluster Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cluster ID:**", cluster['CLUSTER_ID'])
        st.write("**Type:**", CLUSTER_TYPE_DISPLAY.get(cluster.get('CLUSTER_TYPE', 'OBSERVATION'), '[observation]'))
        st.write("**Created:**", format_time_ago(cluster.get('CREATED_AT')))
        if cluster.get('CREATED_BY'):
            st.write("**Created by:**", cluster['CREATED_BY'])
    
    with col2:
        st.write("**Last Updated:**", format_time_ago(cluster.get('UPDATED_AT')))
        if cluster.get('UPDATED_BY'):
            st.write("**Updated by:**", cluster['UPDATED_BY'])
        st.write("**Last Refresh:**", format_time_ago(cluster.get('LAST_SUCCESSFUL_REFRESH')))
        if cluster.get('LAST_REFRESHED_BY'):
            st.write("**Refreshed by:**", cluster['LAST_REFRESHED_BY'])


def render_flash_message():
    """Render flash messages from session state"""
    if "flash" in st.session_state:
        level, message = st.session_state["flash"]
        if level == "success":
            st.success(message)
        elif level == "info":
            st.info(message)
        elif level == "warning":
            st.warning(message)
        else:
            st.error(message)
        del st.session_state["flash"]
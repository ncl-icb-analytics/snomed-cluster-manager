# =============================================================================
# SNOMED Cluster Manager - Database Connection Management
# =============================================================================

import streamlit as st
from config import ROLE, WAREHOUSE


@st.cache_resource
def get_connection():
    """Get Snowflake session for Snowflake Streamlit environment"""
    from snowflake.snowpark.context import get_active_session
    return get_active_session()


def rerun():
    """Handle different Streamlit versions"""
    if hasattr(st, 'rerun'):
        st.rerun()
    else:
        st.experimental_rerun()
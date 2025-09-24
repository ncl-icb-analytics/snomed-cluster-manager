# =============================================================================
# SNOMED Cluster Manager - Create New Cluster Page
# =============================================================================

import streamlit as st
from database import rerun
from services.cluster_service import test_ecl_expression, create_new_cluster


def render_create():
    """Render the Create New Cluster page"""
    st.title("✨ Create New Cluster")
    
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = 'home'
            rerun()
    
    # Check for quick create from playground
    quick_create = st.session_state.get("quick_create")
    if quick_create:
        default_cluster_id = quick_create["cluster_id"]
        default_description = quick_create["description"]
        default_ecl = quick_create["ecl_expression"]
        default_cluster_type = quick_create.get("cluster_type", "OBSERVATION")
        del st.session_state["quick_create"]
    else:
        default_cluster_id = ""
        default_description = ""
        default_ecl = ""
        default_cluster_type = "OBSERVATION"
    
    # Form
    with st.form("create_cluster_form"):
        st.subheader("📝 Cluster Details")
        
        cluster_id = st.text_input(
            "Cluster ID *",
            value=default_cluster_id,
            placeholder="e.g., DIABETES_CONDITIONS",
            help="Unique identifier for this cluster (will be converted to uppercase)"
        ).strip().upper()
        
        description = st.text_input(
            "Description *",
            value=default_description,
            placeholder="Brief description of what this cluster contains"
        )
        
        cluster_type = st.selectbox(
            "Cluster Type",
            options=['OBSERVATION', 'MEDICATION'],
            index=['OBSERVATION', 'MEDICATION'].index(default_cluster_type),
            help="Type of clinical data this cluster represents"
        )
        
        ecl_expression = st.text_area(
            "ECL Expression *",
            value=default_ecl,
            height=150,
            placeholder="Enter SNOMED CT ECL expression, e.g., << 73211009 |Diabetes mellitus|",
            help="Expression Constraint Language query to define cluster contents"
        )
        
        # Warning about API limit
        st.caption("⚠️ Queries returning more than 50,000 codes will error due to API limits")
        
        # Form validation and submission
        col1, col2 = st.columns([3, 1])
        with col2:
            submit_clicked = st.form_submit_button("🚀 Create Cluster", type="primary", use_container_width=True)
        
        if submit_clicked:
            # Validation
            errors = []
            if not cluster_id:
                errors.append("Cluster ID is required")
            if not description:
                errors.append("Description is required")
            if not ecl_expression.strip():
                errors.append("ECL Expression is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Test ECL expression first
                st.info("🧪 Testing ECL expression...")
                test_result = test_ecl_expression(ecl_expression.strip())
                
                if test_result.empty:
                    st.error("❌ ECL expression is invalid or returns no results. Please test in the Playground first.")
                else:
                    st.success(f"✅ ECL expression is valid! Found {len(test_result):,} codes")
                    
                    # Create cluster
                    with st.spinner("Creating cluster..."):
                        if create_new_cluster(cluster_id, ecl_expression.strip(), description, cluster_type):
                            st.session_state["flash"] = ("success", f"✅ Cluster '{cluster_id}' created successfully!")
                            st.session_state.selected_cluster = cluster_id
                            st.session_state.page = 'details'
                            rerun()
    
    # Helper section
    st.markdown("---")
    st.subheader("💡 Tips")
    st.markdown("""
    - **Test your ECL first**: Use the 🧪 Playground to validate expressions before creating clusters
    - **Cluster IDs**: Use descriptive, uppercase names with underscores (e.g., `DIABETES_CONDITIONS`)
    - **Descriptions**: Keep them concise but informative for other users
    - **ECL Syntax**: Use standard SNOMED CT Expression Constraint Language syntax
    """)
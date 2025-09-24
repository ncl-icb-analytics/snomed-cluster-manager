# =============================================================================
# SNOMED Cluster Manager - ECL Expression Playground Page
# =============================================================================

import streamlit as st
from database import rerun
from services.cluster_service import test_ecl_expression


def render_playground():
    """Render the ECL Expression Playground page"""
    st.title("🧪 ECL Expression Playground")
    
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = 'home'
            rerun()
    
    st.markdown("Test SNOMED CT Expression Constraint Language (ECL) expressions before creating clusters.")
    
    # Always-visible ECL guidance
    st.markdown("### ℹ️ ECL Quick Reference")
    st.markdown("""
    Use `<< concept` for concept and all subtypes, `< concept` for subtypes only. 
    Add refinements with `: attribute = value`. Combine with `AND`, `OR`, `MINUS`.  
    
    **Examples:** `<< 73211009 |Diabetes mellitus|` returns all diabetes types.  
    `<< 373873005 |Pharmaceutical / biologic product| : 127489000 |Has active ingredient| = << 387517004 |Paracetamol|` returns paracetamol medications.
    
    *Note: Text between `|` pipes is optional - only for readability. The server ignores the text between pipes.*
    """)
    
    # Initialize session state for playground ECL and results
    if 'playground_ecl' not in st.session_state:
        st.session_state.playground_ecl = ""
    if 'playground_test_results' not in st.session_state:
        st.session_state.playground_test_results = None
    if 'playground_tested_ecl' not in st.session_state:
        st.session_state.playground_tested_ecl = None
    
    # Handle example selection
    if "selected_example_ecl" in st.session_state:
        st.session_state.playground_ecl = st.session_state["selected_example_ecl"]
        del st.session_state["selected_example_ecl"]
    
    # Handle navigation from details page
    if "ecl_test_expr" in st.session_state:
        st.session_state.playground_ecl = st.session_state["ecl_test_expr"]
        del st.session_state["ecl_test_expr"]
    
    # ECL input - use session state to persist value
    ecl_expression = st.text_area(
        "ECL Expression",
        value=st.session_state.playground_ecl,
        height=150,
        placeholder="Enter ECL expression, e.g., << 73211009 |Diabetes mellitus|",
        help="Enter a SNOMED CT ECL expression to test",
        key="ecl_input",
        on_change=lambda: st.session_state.update({"playground_ecl": st.session_state["ecl_input"]})
    )
    
    # Test button
    test_clicked = st.button("🔍 Test Expression", type="primary")
    
    # Warning about API limit
    st.caption("⚠️ Queries returning more than 50,000 codes will error due to API limits")
    
    # Get the current ECL expression value
    test_ecl = st.session_state.get("ecl_input", st.session_state.playground_ecl).strip()
    
    # Test button clicked - run test and store results
    if test_clicked and test_ecl:
        # Update session state with the current value to persist it
        st.session_state.playground_ecl = test_ecl
        with st.spinner("Testing ECL expression..."):
            result_df = test_ecl_expression(test_ecl)
        
        # Store test results in session state
        if not result_df.empty:
            st.session_state.playground_test_results = result_df
            st.session_state.playground_tested_ecl = test_ecl
        else:
            st.session_state.playground_test_results = None
            st.session_state.playground_tested_ecl = None
            st.error("❌ ECL expression returned no results or contains errors")
    
    elif test_clicked and not test_ecl:
        st.warning("Please enter an ECL expression to test")
    
    # Display stored test results if they exist and match current ECL
    if (st.session_state.playground_test_results is not None and 
        st.session_state.playground_tested_ecl == test_ecl):
        
        result_df = st.session_state.playground_test_results
        
        # Show appropriate limit message based on result count
        if len(result_df) == 50000:
            st.success(f"✅ ECL expression is valid! Found {len(result_df):,} codes (showing first 50,000)")
        elif len(result_df) == 10000:
            st.success(f"✅ ECL expression is valid! Found {len(result_df):,} codes (showing first 10,000)")
        else:
            st.success(f"✅ ECL expression is valid! Found {len(result_df):,} codes")
        
        # Search functionality
        search_term = st.text_input("🔍 Search results", placeholder="Search by code or description...", key="search_results_input")
        
        # Filter results
        filtered_df = result_df
        if search_term:
            mask = (result_df['CODE'].astype(str).str.contains(search_term, case=False, na=False) | 
                   result_df['DISPLAY'].str.contains(search_term, case=False, na=False))
            filtered_df = result_df[mask]
        
        # Display results
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
            
            if len(filtered_df) < len(result_df):
                st.caption(f"Showing {len(filtered_df)} of {len(result_df)} results")
            
            # Quick create cluster section
            st.markdown("---")
            st.subheader("Create Cluster from this ECL")
            
            col1, col2 = st.columns([2, 2])
            with col1:
                quick_cluster_id = st.text_input("Cluster ID", placeholder="Enter cluster ID...", key="quick_cluster_id_input")
            with col2:
                quick_description = st.text_input("Description", placeholder="Enter description...", key="quick_description_input")
            
            col3, col4 = st.columns([2, 2])
            with col3:
                quick_cluster_type = st.selectbox(
                    "Cluster Type",
                    options=['OBSERVATION', 'MEDICATION'],
                    key="quick_cluster_type_select",
                    help="Type of clinical data this cluster represents"
                )
            with col4:
                st.markdown("<br>", unsafe_allow_html=True)  # Add space to align button
                create_clicked = st.button("✨ Create Cluster", type="primary", use_container_width=True, key="quick_create_button")
            
            if create_clicked:
                if not quick_cluster_id.strip():
                    st.error("❌ Cluster ID is required")
                elif not quick_description.strip():
                    st.error("❌ Description is required")
                else:
                    st.session_state["quick_create"] = {
                        "cluster_id": quick_cluster_id.strip(),
                        "description": quick_description.strip(),
                        "ecl_expression": test_ecl,
                        "cluster_type": quick_cluster_type
                    }
                    st.session_state.page = 'create'
                    rerun()
        else:
            st.info(f"No results match '{search_term}'")
    
    # Examples section with diverse complexity levels
    st.markdown("---")
    st.subheader("📚 Example ECL Expressions")
    st.caption("Click any example to load it into the expression box above:")
    
    # Organize examples in columns for better layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🟢 Basic (Hierarchy)**")
        basic_examples = [
            ("Type 2 Diabetes", "<<44054006 |Type 2 diabetes mellitus|"),
            ("Hypertension", "<< 38341003 |Hypertensive disorder, systemic arterial|"),
            ("Learning disability", "<< 110359009 |Learning disability|"),
            ("HbA1c + history", "<<1003671000000109 |Hemoglobin A1c level| {{ +HISTORY-MAX }}")
        ]
        
        for name, expression in basic_examples:
            if st.button(f"📄 {name}", key=f"basic_{name}", use_container_width=True):
                st.session_state["selected_example_ecl"] = expression
                rerun()
    
    with col2:
        st.markdown("**🟡 Intermediate (Operators)**")
        refined_examples = [
            ("Diabetes excl. gestational", "<< 73211009 |Diabetes mellitus| MINUS << 11687002 |Gestational diabetes mellitus|"),
            ("Reference set members", "^ 999002381000000108 |Safeguarding issues simple reference set|"),
            ("Medications with ibuprofen", "* : 10362801000001104 |Has specific active ingredient| = 387207008 |Ibuprofen (substance)|"),
            ("Blood pressure codes", "<<271649006 |Systolic blood pressure| OR <<271650006 |Diastolic blood pressure|")
        ]
        
        for name, expression in refined_examples:
            if st.button(f"🔧 {name}", key=f"refined_{name}", use_container_width=True):
                st.session_state["selected_example_ecl"] = expression
                rerun()
    
    with col3:
        st.markdown("**🔴 Advanced (Complex)**")
        complex_examples = [
            ("Valproate (all forms)", "(* : 10362801000001104 |Has specific active ingredient| = 387481005 |Sodium valproate|) OR (* : 10362801000001104 |Has specific active ingredient| = 387080000 |Valproic acid|) OR (* : 10362801000001104 |Has specific active ingredient| = 5641004 |Valproate semisodium|)"),
            ("Viral infections", "<< 40733004 |Infectious disease| : 246075003 |Causative agent| = << 49872002 |Virus|"),
            ("Osteoporotic fractures", "<< 125605004 |Fracture of bone| : 363698007 |Finding site| = (<< 29627003 |Neck of femur structure| OR << 75129005 |Distal radius structure|)"),
            ("Secondary hypertension", "(<< 38341003 |Hypertensive disorder| : 42752001 |Due to| = *) OR <<31992008 |Secondary hypertension|")
        ]
        
        for name, expression in complex_examples:
            if st.button(f"⚡ {name}", key=f"complex_{name}", use_container_width=True):
                st.session_state["selected_example_ecl"] = expression
                rerun()
    
    st.caption("💡 **Tip:** Start with green examples (basic), then try yellow (intermediate), then red (advanced complex logic).")
    
    # Comprehensive documentation sections
    st.markdown("---")
    st.subheader("📖 ECL Documentation")
    
    with st.expander("💡 Resources & Tools", expanded=False):
        st.markdown("""
        **Interactive Tools:**
        - [NHS Term Browser](https://termbrowser.nhs.uk/) - Best for exploring concepts
        - [Shrimp ECL Builder](https://ontoserver.csiro.au/shrimp/launch.html?iss=https://ontology.onelondon.online/authoring/fhir) - Visual ECL expression builder
        - [ECL Guide](https://confluence.ihtsdotools.org/display/DOCECL/Expression+Constraint+Language+-+Specification+and+Guide) - Official ECL documentation
        
        **Key Operators Quick Reference:**
        - `<<` descendant or self, `<` descendant only
        - `^` member of reference set
        - `MINUS`, `AND`, `OR` for boolean logic
        - `{{ +HISTORY-MAX }}` includes inactive concepts
        """)
    
    with st.expander("🎯 Constraint Operators & Basic Syntax", expanded=False):
        st.markdown("""
        **Hierarchy Navigation:**
        - `<< concept` - concept and all subtypes (descendants-or-self)
        - `< concept` - subtypes only (descendants)  
        - `>> concept` - concept and all supertypes (ancestors-or-self)
        - `> concept` - supertypes only (ancestors)
        - `^ refset` - members of reference set
        
        **Basic Refinements:**
        ```go
        < 19829001 |Disorder of lung| : 
            116676008 |Associated morphology| = 79654002 |Edema|
        ```
        
        **Multiple Attributes (comma = AND):**
        ```go
        < 404684003 |Clinical finding| :
            363698007 |Finding site| = << 39057004 |Pulmonary valve|,
            116676008 |Associated morphology| = << 415582006 |Stenosis|
        ```
        """)
    
    with st.expander("🔗 Compound Expressions & Logic", expanded=False):
        st.markdown("""
        **Boolean Operations:**
        - `expr1 AND expr2` - intersection (both must be true)
        - `expr1 OR expr2` - union (either can be true)
        - `expr1 MINUS expr2` - exclusion (first but not second)
        - Use parentheses: `(expr1 OR expr2) AND expr3`
        
        **Example 1 - Intersection (finding overlap):**
        ```go
        << 64572001 |Disease| AND << 128139000 |Inflammatory disorder|
        ```
        
        **Example 2 - Complex expression with parentheses:**
        ```go
        (<< 19829001 |Disorder of lung| OR << 301867009 |Edema of trunk|) 
        MINUS << 195967001 |Asthma|
        ```
        """)
    
    with st.expander("🏗️ Attribute Groups & Cardinality", expanded=False):
        st.markdown("""
        **Attribute Groups (keeping related attributes together):**
        
        Curly braces `{}` group attributes that must co-occur within the same relationship group.
        This matches how SNOMED CT models complex concepts with multiple relationship groups.
        
        **Example: Finding a fracture with specific characteristics**
        ```go
        << 125605004 |Fracture of bone| :
            { 363698007 |Finding site| = << 299701004 |Bone of forearm|,
              116676008 |Associated morphology| = << 72704001 |Fracture| }
        ```
        This ensures the fracture morphology is specifically linked to the forearm bone site.
        
        **Multiple relationship groups:**
        ```go
        < 404684003 |Clinical finding| :
            { 363698007 |Finding site| = << 39057004 |Pulmonary valve|,
              116676008 |Associated morphology| = << 415582006 |Stenosis| },
            { 363698007 |Finding site| = << 53085002 |Right ventricle|,
              116676008 |Associated morphology| = << 56246009 |Hypertrophy| }
        ```
        This matches concepts that have BOTH relationship groups as modeled in SNOMED:
        - Group 1: Pulmonary valve with stenosis
        - Group 2: Right ventricle with hypertrophy
        
        Groups ensure you're matching the exact SNOMED model structure, not just the presence of attributes.
        
        **Cardinality (counting relationships):**
        - `[0..1]` = Zero or one
        - `[1..3]` = Must have between 1 and 3
        - `[1..*]` = One or more (default)
        - `[3..*]` = Three or more
        
        **Example:**
        ```go
        < 373873005 |Pharmaceutical product| : 
            [3..*] 127489000 |Has active ingredient| = < 105590001 |Substance|
        ```
        (Products with 3+ active ingredients)
        """)
    
    with st.expander("🔢 Concrete Values & Advanced Attributes", expanded=False):
        st.markdown("""
        **Concrete Values with Comparisons:**
        ```go
        < 763158003 |Medicinal product| :
            1142135004 |Presentation strength value| >= #250,
            1142135004 |Presentation strength value| <= #500,
            732945000 |Presentation strength unit| = 258684004 |milligram|
        ```
        
        **Comparison Operators:**
        - `= #value` - equals
        - `!= #value` - not equals
        - `>= #value` - greater than or equal
        - `<= #value` - less than or equal
        - `> #value` - greater than
        - `< #value` - less than
        
        **Reverse Attributes (find sources):**
        ```go
        < 91723000 |Anatomical structure| :
            R 363698007 |Finding site| = < 125605004 |Fracture of bone|
        ```
        
        **Dotted Attributes (chaining):**
        ```go
        < 125605004 |Fracture of bone| . 363698007 |Finding site|
        ```
        """)
    
    with st.expander("🔍 Filters & History Supplements", expanded=False):
        st.markdown("""
        **Description Filters (search by term):**
        ```go
        < 64572001 |Disease| {{ term = "heart" }}  // Contains word starting with "heart"
        < 64572001 |Disease| {{ term = "heart att" }}  // Contains both "heart" AND "att" (any order)
        < 64572001 |Disease| {{ term = ("heart" "card") }}  // Contains "heart" OR "card"
        ```
        
        **Wildcard Searches:**
        ```go
        < 64572001 |Disease| {{ term = wild:"*itis" }}  // Ends with "itis"
        < 64572001 |Disease| {{ term = wild:"cardi*" }}  // Starts with "cardi"
        < 64572001 |Disease| {{ term = wild:"*heart*" }}  // Contains "heart" anywhere
        ```
        
        **Description Type Filters:**
        ```go
        < 56265001 |Heart disease| {{ term = "heart", type = fsn }}  // Fully specified name
        < 56265001 |Heart disease| {{ term = "heart", type = syn }}  // Synonym only
        < 56265001 |Heart disease| {{ term = "heart", type = (syn fsn) }}  // Synonym OR FSN
        ```
        
        **Concept Filters:**
        ```go
        < 404684003 |Clinical finding| {{ C effectiveTime = "20230131" }}  // Concepts from specific release
        < 73211009 |Diabetes mellitus| {{ C effectiveTime > "20220101" }}  // Concepts added after date
        ```
        
        **Including Inactive Concepts:**
        ```go
        << 73211009 |Diabetes mellitus| {{ +HISTORY-MAX }}  // Includes historical/inactive diabetes concepts
        ^ 999002381000000108 |Safeguarding issues simple reference set| {{ C active = false }}  // Only inactive members
        ```
        
        **Member Filters (for reference sets):**
        ```go
        ^ 999002381000000108 |Safeguarding issues simple reference set| {{ M active = true }}
        ```
        
        **History Supplements (include inactive concepts):**
        ```go
        << 195967001 |Asthma| {{ +HISTORY-MIN }}    (same meaning only)
        << 195967001 |Asthma| {{ +HISTORY-MOD }}    (balanced precision/recall)
        << 195967001 |Asthma| {{ +HISTORY-MAX }}    (maximum recall)
        ```
        
        **Top/Bottom Operators:**
        ```go
        !!> << 404684003 |Clinical finding|    (most general concepts)
        !!< << 404684003 |Clinical finding|    (most specific concepts)
        ```
        """)
    
    with st.expander("🎭 Wildcards & Special Operators", expanded=False):
        st.markdown("""
        **Wildcard Usage:**
        - `*` - any concept
        - `* : 246075003 |Causative agent| = 387517004 |Paracetamol|` (any concept with paracetamol as causative agent)
        
        **Attribute Wildcards:**
        - `< 404684003 |Clinical finding| : * = 79654002 |Edema|` (any attribute with edema value)
        - `< 404684003 |Clinical finding| : 116676008 |Associated morphology| = *` (any morphology value)
        
        **Constraint Operators on Attributes:**
        - `<< attribute` - attribute or any subtype
        - `>> attribute` - attribute or any supertype
        
        **Example:**
        ```go
        << 404684003 |Clinical finding| :
            << 47429007 |Associated with| = << 267038008 |Edema|
        ```
        (Matches 'Associated with', 'Due to', 'After', 'Causative agent' etc.)
        """)
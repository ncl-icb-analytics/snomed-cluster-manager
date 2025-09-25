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
        st.markdown("**🟡 Intermediate (Operators & Refinements)**")
        refined_examples = [
            ("Diabetes excl. gestational", "<< 73211009 |Diabetes mellitus| MINUS << 11687002 |Gestational diabetes mellitus|"),
            ("Reference set members", "^ 999002381000000108 |Safeguarding issues simple reference set|"),
            ("Viral infections", "<< 40733004 |Infectious disease| : 246075003 |Causative agent| = << 49872002 |Virus|"),
            ("Osteoporotic fractures", "<< 125605004 |Fracture of bone| : 363698007 |Finding site| = (<< 29627003 |Neck of femur structure| OR << 75129005 |Distal radius structure|)")
        ]
        
        for name, expression in refined_examples:
            if st.button(f"🔧 {name}", key=f"refined_{name}", use_container_width=True):
                st.session_state["selected_example_ecl"] = expression
                rerun()
    
    with col3:
        st.markdown("**🔴 Advanced (Genuinely Complex)**")
        complex_examples = [
            ("Drug ingredients (chained)", "<< 373873005 |Pharmaceutical product| . 127489000 |Has active ingredient|"),
            ("Viral lung infections (grouped)", "<< 40733004 |Infectious disease| : { 246075003 |Causative agent| = << 49872002 |Virus|, 363698007 |Finding site| = << 39607008 |Lung| }"),
            ("Body parts that fracture (reverse)", "< 91723000 |Anatomical structure| : R 363698007 |Finding site| = << 125605004 |Fracture of bone|"),
            ("Anything causing edema (wildcard)", "* : << 47429007 |Associated with| = << 267038008 |Edema|")
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
    
    with st.expander("🏗️ Attribute Groups vs ANDs (When Groups Matter)", expanded=False):
        st.markdown("""
        **The Problem Without Groups:**
        SNOMED concepts can have multiple relationships. Without groups, ECL can't tell which attributes go together.

        **REAL Example - Viral Lung Infections:**
        You want: "Lung infections caused by viruses" - both attributes must be linked together.

        **Without Groups (Less Precise):**
        ```go
        << 40733004 |Infectious disease| :
            246075003 |Causative agent| = << 49872002 |Virus|,
            363698007 |Finding site| = << 39607008 |Lung|
        ```
        **Issue:** This could match infectious diseases that have:
        - A viral cause (from one infection type)
        - A lung location (from a different infection type)

        May include unintended matches like bacterial lung infections with viral components.

        **With Groups (More Precise):**
        ```go
        << 40733004 |Infectious disease| :
            { 246075003 |Causative agent| = << 49872002 |Virus|,
              363698007 |Finding site| = << 39607008 |Lung| }
        ```
        **Result:** This ensures the viral agent and lung location are linked together in the same relationship group.

        **Key Point:** Groups reflect how SNOMED models complex concepts with multiple related attributes.

        **Simple Rule:**
        - Comma `,` = AND (within same group)
        - Curly braces `{}` = "these attributes must be linked in SNOMED's model"

        **When to Use Groups:**
        - Multiple body sites with different problems
        - Medications with multiple active ingredients
        - Complex clinical conditions
        - Any time relationships need to stay paired

        **Cardinality (How Many):**
        ```go
        < 373873005 |Pharmaceutical product| :
            [2..5] 127489000 |Has active ingredient| = < 105590001 |Substance|
        ```
        *"Products with 2-5 active ingredients"*

        - `[0..1]` = Optional (zero or one)
        - `[1..3]` = Between 1 and 3
        - `[2..*]` = Two or more
        - `[1..*]` = One or more (default)
        """)
    
    with st.expander("🔢 Concrete Values (Numbers & Measurements)", expanded=False):
        st.markdown("""
        **What are Concrete Values?**
        Some SNOMED concepts have numerical data attached - like drug strengths, measurement ranges, or doses.
        ECL lets you filter by these numbers using comparison operators.

        **Common Use Cases:**

        **1. Drug Strengths (find medications by dose range):**
        ```go
        < 763158003 |Medicinal product| :
            1142135004 |Has presentation strength value| >= #250,
            1142135004 |Has presentation strength value| <= #500,
            732945000 |Has presentation strength unit| = 258684004 |milligram|
        ```
        *"Find medications between 250-500mg strength"*

        **2. Laboratory Reference Ranges:**
        ```go
        < 365845006 |Finding of laboratory test result| :
            1149367008 |Has normal range low value| <= #4.0,
            1149366004 |Has normal range high value| >= #11.0
        ```
        *"Find lab tests with normal ranges spanning 4.0 to 11.0"*

        **All Comparison Operators:**
        - `= #value` - exactly equals
        - `!= #value` - not equals
        - `>= #value` - greater than or equal
        - `<= #value` - less than or equal
        - `> #value` - strictly greater than
        - `< #value` - strictly less than

        **💡 Pro Tip:** Always combine with unit attributes to avoid mixing mg with mcg!
        """)

    with st.expander("⚙️ Reverse Attributes (R) - Find What Points TO Something", expanded=False):
        st.markdown("""
        **The Power of Reverse Queries:**
        Normal queries go FROM concept TO value. Reverse goes FROM value TO concept.

        **Example 1 - Find Fracture Sites:**
        Normal: "Find fractures of the femur"
        ```go
        << 125605004 |Fracture of bone| : 363698007 |Finding site| = << 71341001 |Femur|
        ```

        Reverse: "Find body parts that can fracture"
        ```go
        < 91723000 |Anatomical structure| : R 363698007 |Finding site| = << 125605004 |Fracture of bone|
        ```
        Returns: femur, radius, tibia, skull, etc. (all the bones)

        **Example 2 - Find Allergy Triggers:**
        ```go
        < 105590001 |Substance| : R 246075003 |Causative agent| = << 609328004 |Allergic disposition|
        ```
        *"What substances cause allergic reactions?"*

        **Example 3 - Find Disorder Sites:**
        ```go
        < 91723000 |Anatomical structure| : R 363698007 |Finding site| = << 64572001 |Disease|
        ```
        *"What body parts can have diseases?"*
        """)

    with st.expander("🔗 Dotted Attributes (.) - Follow The Chain", expanded=False):
        st.markdown("""
        **What Dotted Attributes Do:**
        Instead of returning the original concepts, dotted attributes follow the relationship and return the TARGET values.

        **Example 1 - Get All Drug Ingredients:**
        Without dots (normal): Returns the medications
        ```go
        << 373873005 |Pharmaceutical product| : 127489000 |Has active ingredient| = << 387517004 |Paracetamol|
        ```

        With dots (chained): Returns the ingredients themselves
        ```go
        << 373873005 |Pharmaceutical product| . 127489000 |Has active ingredient|
        ```
        Returns: paracetamol, ibuprofen, aspirin, etc. (the substances, not the meds)

        **Example 2 - All Body Sites That Can Have Findings:**
        ```go
        << 404684003 |Clinical finding| . 363698007 |Finding site|
        ```
        Returns: heart, lung, liver, etc. (anatomical structures)

        **Example 3 - Find Fracture Locations:**
        ```go
        << 125605004 |Fracture of bone| . 363698007 |Finding site|
        ```
        Returns: femur, radius, tibia, etc. (the anatomical sites where fractures occur)

        **When to Use Dots:**
        - "Show me the VALUES of this relationship, not the source concepts"
        - Building lists of targets (ingredients, locations, causes)
        - Data extraction and analysis queries
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
# SNOMED Cluster Manager

A Streamlit application for managing and analyzing SNOMED ECL (Expression Constraint Language) clusters with comprehensive demographics and health equity insights.

## Overview

The SNOMED Cluster Manager provides healthcare analysts and researchers with tools to:

- **Create and manage ECL clusters** - Define groups of SNOMED codes using ECL expressions
- **Analyze usage patterns** - View code usage across patient populations and time periods
- **Demographic insights** - Age/sex distributions and population pyramids
- **Health equity analysis** - Examine disparities across ethnicity, deprivation, language, and geography
- **Organizational analysis** - Practice, PCN, and borough-level breakdowns with rates per 1,000 population
- **Export capabilities** - Download data and generate SQL queries for further analysis

## Features

### ECL Cluster Management
- Test ECL expressions with live validation
- Create, edit, and rename clusters with full audit trail
- Automatic refresh with change tracking
- Support for both observation and medication cluster types

### Analytics Dashboard
- **Usage Summary**: Patient counts, observation/medication totals, trends over time
- **Code Analysis**: Ranking by usage frequency, unused code identification
- **Demographics**: Age/sex breakdowns with population pyramids
- **Organization Views**: Practice scatter plots, aggregated rates by PCN/borough
- **Health Equity**: Analysis across ethnicity, deprivation (IMD), language access, and neighborhood
- **SQL Templates**: Ready-to-use queries for data export

### Data Architecture Integration
- Connects to modernized data lake architecture (DATA_LAKE__NCL.TERMINOLOGY)
- Integrates with OLIDS observation and medication data (DATA_LAKE.OLIDS)
- Uses demographics from REPORTING.OLIDS_PERSON_DEMOGRAPHICS
- Maintains ECL cache for performance with external SNOMED terminology services

## Installation

### Snowflake Deployment
The application is deployed as a Streamlit app in Snowflake using Git integration:

1. Run the provided `snowflake-git-integration.sql` worksheet to set up the Git repository integration
2. The app will be available in Snowsight under "Streamlit"
3. Updates are pulled automatically from the GitHub repository

### Local Development
For local development:

```bash
# Clone the repository
git clone https://github.com/ncl-icb-analytics/snomed-cluster-manager.git
cd snomed-cluster-manager

# Create virtual environment
conda env create -f environment.yml
conda activate snomed-cluster-manager

# Run the Streamlit app
streamlit run streamlit_app.py
```

## Usage

### Creating ECL Clusters
1. Navigate to the "Create" page
2. Enter a unique cluster ID and description
3. Define your ECL expression (e.g., `< 73211009 |Diabetes mellitus|`)
4. Test the expression to validate syntax and preview results
5. Save and refresh to populate the cache

### Analyzing Clusters
1. Select a cluster from the home page
2. Use the "Analytics" tab to explore:
   - Usage patterns and trends
   - Demographic breakdowns
   - Organizational analysis
   - Health equity insights
3. Export data or SQL queries for further analysis

### Managing Clusters
- **Edit**: Update ECL expressions, descriptions, or cluster types
- **Rename**: Change cluster IDs while preserving history
- **Delete**: Remove clusters and all associated cache data
- **Refresh**: Update code lists from latest SNOMED releases

## Configuration

Key configuration is managed in `config.py`:

```python
# Database connections
DB_SCHEMA = "DATA_LAKE__NCL.TERMINOLOGY"      # ECL cache tables
DB_STORE = "DATA_LAKE.OLIDS"                  # Clinical data
DB_DEMOGRAPHICS = "REPORTING.OLIDS_PERSON_DEMOGRAPHICS"  # Demographics

# Snowflake resources
WAREHOUSE = "NCL_ANALYTICS_XS"
ROLE = "ISL-USERGROUP-SECONDEES-NCL"
```

## Architecture

The application follows a modular structure:

- **`streamlit_app.py`** - Main application entry point
- **`services/`** - Data access layer (analytics, demographics, cluster management)
- **`page_modules/`** - Individual page implementations
- **`components/`** - Reusable UI components
- **`utils/`** - Helper functions and chart generators
- **`config.py`** - Central configuration

### Database Schema
- **ECL_CLUSTERS** - Cluster definitions and metadata
- **ECL_CACHE** - Cached SNOMED codes for each cluster
- **ECL_CACHE_METADATA** - Refresh timestamps and statistics
- **ECL_CLUSTER_CHANGES** - Audit trail of code changes

## Data Privacy and Security

- All demographic analysis includes privacy thresholds (minimum 5 patients)
- No direct patient identifiers are displayed
- Aggregated statistics only with appropriate suppression
- Secure database connections with role-based access control

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please follow conventional commit standards and ensure all tests pass.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Contact the NCL ICB Analytics team
- Refer to SNOMED International documentation for ECL syntax

## License

This repository is dual licensed under the Open Government v3 & MIT. All code outputs are subject to Crown Copyright.

---

**Crown Copyright (c) 2025 NHS North Central London Integrated Care Board**

*Contains public sector information licensed under the Open Government Licence v3.0.*
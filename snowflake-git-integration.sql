-- =====================================================
-- Snowflake Git Integration Setup for SNOMED Cluster Manager
-- =====================================================
-- This worksheet creates a Git integration to pull the SNOMED Cluster Manager
-- Streamlit app from the public GitHub repository into Snowflake

-- Set context
USE ROLE EXTERNAL_ACCESS_ADMIN; -- Required for creating integrations
USE DATABASE EXTERNAL_ACCESS;

-- Create GITHUB schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS GITHUB;
USE SCHEMA GITHUB;

-- =====================================================
-- 1. Create Git Repository Integration
-- =====================================================

-- Set context
USE ROLE EXTERNAL_ACCESS_ADMIN;

-- Create API integration for GitHub (EXTERNAL_ACCESS_ADMIN can create this)
-- Note: No network rule required for public GitHub access
-- Snowflake uses public network access by default for Git integrations

CREATE OR REPLACE API INTEGRATION github_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com')
  ENABLED = TRUE;

-- Optional: If you need to restrict network access, you can create a network rule
-- Uncomment below if your organization requires specific network restrictions:
-- CREATE NETWORK RULE IF NOT EXISTS github_network_rule
--   MODE = EGRESS
--   TYPE = HOST_PORT
--   VALUE_LIST = ('github.com:443');
--
-- Then add to the API integration:
-- ALTER API INTEGRATION github_integration
-- SET NETWORK_RULE = github_network_rule;

-- Create Git repository in EXTERNAL_ACCESS.GITHUB
USE DATABASE EXTERNAL_ACCESS;
USE SCHEMA GITHUB;

CREATE OR REPLACE GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO
  API_INTEGRATION = github_integration
  ORIGIN = 'https://github.com/ncl-icb-analytics/snomed-cluster-manager.git';

-- Verify the integration was created
DESCRIBE GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO;

-- =====================================================
-- 2. Fetch the Repository Contents
-- =====================================================

-- Fetch the latest version from main branch (MUST do this first!)
ALTER GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO FETCH;

-- =====================================================
-- 3. Grant Permissions on Git Repository First
-- =====================================================

-- Grant read access on the Git repository to roles that need it
GRANT READ ON GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO TO ROLE DATA_PLATFORM_MANAGER;
GRANT READ ON GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO TO ROLE ENGINEER;
GRANT READ ON GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO TO ROLE ANALYST;

-- Grant write access to ENGINEER so they can fetch updates
GRANT WRITE ON GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO TO ROLE ENGINEER;

-- =====================================================
-- 4. Create Streamlit App from Repository
-- =====================================================

-- Switch to ENGINEER role to create the Streamlit app
USE ROLE ENGINEER;
USE DATABASE DATA_LAKE__NCL;
USE SCHEMA TERMINOLOGY;

CREATE OR REPLACE STREAMLIT SNOMED_CLUSTER_MANAGER
  ROOT_LOCATION = '@EXTERNAL_ACCESS.GITHUB.SNOMED_CLUSTER_MANAGER_REPO/branches/main'
  MAIN_FILE = '/streamlit_app.py'
  QUERY_WAREHOUSE = 'NCL_ANALYTICS_XS'
  COMMENT = 'SNOMED Cluster Manager - Analytics dashboard for ECL clusters';

-- Grant usage on the Streamlit app to other roles
GRANT USAGE ON STREAMLIT SNOMED_CLUSTER_MANAGER TO ROLE DATA_PLATFORM_MANAGER;
GRANT USAGE ON STREAMLIT SNOMED_CLUSTER_MANAGER TO ROLE ANALYST;


-- =====================================================
-- 5. Maintenance Commands
-- =====================================================

-- To update the app with latest changes from GitHub:
-- ALTER GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO FETCH;

-- To view repository information:
-- DESCRIBE GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO;

-- To list files at a specific path:
-- SELECT * FROM TABLE(SNOMED_CLUSTER_MANAGER_REPO.LS('@/services', 'main')) ORDER BY file_name;

-- To view file contents:
-- SELECT * FROM TABLE(SNOMED_CLUSTER_MANAGER_REPO.READ_TEXT('@/config.py', 'main'));

-- To drop the integration (if needed):
-- DROP STREAMLIT SNOMED_CLUSTER_MANAGER;
-- DROP GIT REPOSITORY SNOMED_CLUSTER_MANAGER_REPO;

-- =====================================================
-- Notes:
-- =====================================================
-- 1. This creates a public Git integration (no credentials needed)
-- 2. The app will be available in Snowsight under "Streamlit"
-- 3. Use ALTER GIT REPOSITORY ... FETCH to pull updates from GitHub
-- 4. The app uses the WH_NCL_ENGINEERING_XS warehouse specified in config
-- 5. Database references in the app point to the new architecture:
--    - DATA_LAKE__NCL.TERMINOLOGY for ECL tables
--    - DATA_LAKE.OLIDS for observation/medication data
--    - REPORTING.OLIDS_PERSON_DEMOGRAPHICS for demographics
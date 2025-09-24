# =============================================================================
# SNOMED Cluster Manager - Helper Utilities
# =============================================================================

import pandas as pd
import re
from datetime import datetime, timedelta
from config import STATUS_EMOJI, STALE_LABEL


def format_time_ago(timestamp):
    """Format timestamp as time ago (e.g., '2 hours ago', '3 weeks ago', '5 months ago')"""
    if pd.isnull(timestamp):
        return "Unknown"

    try:
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)

        now = pd.Timestamp.now()
        diff = now - timestamp

        # Calculate different time units
        days = diff.days
        hours = diff.seconds // 3600
        minutes = diff.seconds // 60

        # Years (approximate: 365 days)
        if days >= 365:
            years = days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"

        # Months (approximate: 30 days)
        elif days >= 30:
            months = days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"

        # Weeks
        elif days >= 7:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"

        # Days
        elif days > 0:
            return f"{days} day{'s' if days != 1 else ''} ago"

        # Hours
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

        # Minutes
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

        # Just now
        else:
            return "Just now"

    except Exception:
        return "Unknown"


def get_status_emoji(cluster, stale_label):
    """Get status emoji for a cluster based on its state"""
    if cluster is None:
        return STATUS_EMOJI['error']
    
    # Handle both DataFrame and Series objects
    if hasattr(cluster, 'empty') and cluster.empty:
        return STATUS_EMOJI['error']
    
    # If it's a DataFrame, get the first row
    if hasattr(cluster, 'iloc') and len(cluster.shape) > 1:
        cluster_row = cluster.iloc[0]
    else:
        # It's already a Series or dict-like object
        cluster_row = cluster
    
    if cluster_row.get('STATUS') == 'ERROR':
        return STATUS_EMOJI['error']
    elif cluster_row.get('STATUS_LABEL') == stale_label:
        return STATUS_EMOJI['stale']
    elif pd.isnull(cluster_row.get('LAST_UPDATED')) or cluster_row.get('LAST_UPDATED') == '':
        return STATUS_EMOJI['new']
    else:
        return STATUS_EMOJI['fresh']


def format_number(num):
    """Format number with commas for readability"""
    if pd.isnull(num) or num == '':
        return '0'
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text for comparison"""
    return re.sub(r'\s+', ' ', text.strip())


def format_ecl_for_display(ecl_expression: str) -> str:
    """Format ECL expression for display with proper line breaks"""
    if not ecl_expression:
        return ""
    
    ecl_expression = ecl_expression.strip()
    
    # Add line breaks before major operators for readability
    ecl_expression = re.sub(r'\s+(AND|OR|MINUS)\s+', r'\n\1 ', ecl_expression)
    
    # Add line breaks after opening parentheses in complex expressions
    ecl_expression = re.sub(r'\(\s*(\*|<<|<)', r'(\n  \1', ecl_expression)
    
    # Add line breaks before closing parentheses
    ecl_expression = re.sub(r'\s*\)', r'\n)', ecl_expression)
    
    # Clean up excessive whitespace
    ecl_expression = re.sub(r'\n\s*\n', '\n', ecl_expression)
    
    return ecl_expression


def cluster_matches_expected(cluster_id: str, expected_ecl: str, expected_desc: str) -> bool:
    """Check if cluster matches expected ECL and description"""
    from services.cluster_service import get_cluster_cache
    
    cluster = get_cluster_cache(cluster_id)
    
    if cluster is None or cluster.empty:
        return False
    
    cluster_row = cluster.iloc[0]
    
    # Normalize whitespace for comparison
    actual_ecl = normalize_whitespace(str(cluster_row.get('ECL_EXPRESSION', '')))
    actual_desc = normalize_whitespace(str(cluster_row.get('DESCRIPTION', '')))
    expected_ecl_norm = normalize_whitespace(expected_ecl)
    expected_desc_norm = normalize_whitespace(expected_desc)
    
    return actual_ecl == expected_ecl_norm and actual_desc == expected_desc_norm
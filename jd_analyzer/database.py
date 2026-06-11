"""
database.py — Excel-based resume database manager.

Provides create, read, append, and delete operations
for the JD/resume records stored in a local Excel file.
"""

import pandas as pd
from datetime import datetime
import os

__all__ = [
    'init_db', 'append_record', 'get_all_records',
    'get_filtered', 'delete_record', 'DB_PATH',
    'COLUMNS', 'CATEGORIES', 'INDUSTRIES',
]

# ── Paths ───────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'jd_records.xlsx')

# ── Schema ──────────────────────────────────────────────────────────────
COLUMNS = [
    'timestamp',
    'job_title',
    'job_category',
    'company_name',
    'company_industry',
    'location',
    'experience_required',
    'education_required',
    'core_knowledge',
    'programming_languages',
    'big_data_tools',
    'ml_frameworks',
    'web_dev',
    'cloud_tools',
    'ai_coding_tools',
    'soft_skills',
    'certificates',
    'bonus_journals',
    'other_requirements',
    'raw_text',
]

CATEGORIES = [
    'Algorithm Engineering',
    'Data & Analytics',
    'Software Development',
    'AI / Agent',
    'Product / Operations',
    'Other',
]

INDUSTRIES = [
    'Technology', 'Finance', 'FMCG', 'Healthcare',
    'Telecom', 'Manufacturing', 'Energy', 'Other',
]


def init_db() -> bool:
    """Create Excel file with headers if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(DB_PATH, index=False, sheet_name='Records')
        return True
    return False


def append_record(record: dict) -> int:
    """Append one record dict and return total record count."""
    init_db()
    df = pd.read_excel(DB_PATH, sheet_name='Records')
    record['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    row = {col: record.get(col, '') for col in COLUMNS}
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_excel(DB_PATH, index=False, sheet_name='Records')
    return len(df)


def get_all_records() -> pd.DataFrame:
    """Read all records into a DataFrame."""
    init_db()
    df = pd.read_excel(DB_PATH, sheet_name='Records')
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def get_filtered(category: str = None,
                 date_from=None, date_to=None) -> pd.DataFrame:
    """Return records filtered by category and date range."""
    df = get_all_records()
    if category and category != 'All':
        df = df[df['job_category'] == category]
    if date_from:
        df = df[df['timestamp'].dt.date >= date_from]
    if date_to:
        df = df[df['timestamp'].dt.date <= date_to]
    return df


def delete_record(index: int) -> bool:
    """Delete a record by 0-based index. Returns True on success."""
    df = get_all_records()
    if index < 0 or index >= len(df):
        return False
    df = df.drop(index).reset_index(drop=True)
    df.to_excel(DB_PATH, index=False, sheet_name='Records')
    return True


# CLI entry point
if __name__ == '__main__':
    import sys, json
    if len(sys.argv) >= 2:
        record = json.loads(sys.argv[1])
        count = append_record(record)
        print(f"✅ Record saved. Total: {count}")
    else:
        print(f"Usage: python -m jd_analyzer.database '<json>'")
        print(f"Fields: {', '.join(COLUMNS)}")

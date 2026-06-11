"""
cli.py — Command-line tools for managing your JD/resume database.

Usage:
    # Add a record from JSON
    python -m jd_analyzer.cli add '<json_string>'

    # Extract a JD text file and preview before saving
    python -m jd_analyzer.cli extract sample.txt

    # List all records
    python -m jd_analyzer.cli list

    # Delete a record by index
    python -m jd_analyzer.cli delete 3
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jd_analyzer.database import append_record, get_all_records, delete_record, COLUMNS
from jd_analyzer.extractor import extract_fields


def cmd_add(args):
    """Add a record from JSON string."""
    if not args:
        print("Error: missing JSON string.")
        print(f"Fields: {', '.join(COLUMNS)}")
        return
    try:
        record = json.loads(args[0])
        count = append_record(record)
        print(f"✅ Record saved. Total: {count}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_extract(args):
    """Extract fields from a JD text file and preview."""
    if not args:
        print("Usage: python -m jd_analyzer.cli extract <file.txt>")
        return
    path = args[0]
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    record = extract_fields(text)
    print("\n=== Extracted Fields ===\n")
    for key, val in record.items():
        if key == 'raw_text':
            continue
        print(f"  {key:25s} = {val}")
    print()
    resp = input("Save to database? (y/N): ")
    if resp.lower() in ('y', 'yes'):
        count = append_record(record)
        print(f"✅ Saved. Total: {count}")


def cmd_list(args):
    """List all records."""
    df = get_all_records()
    if df.empty:
        print("📭 No records yet.")
        return
    print(f"\n📋 {len(df)} records:\n")
    for i, (_, row) in enumerate(df.iterrows()):
        ts = row['timestamp'].strftime('%m-%d %H:%M') if hasattr(row['timestamp'], 'strftime') else row['timestamp']
        print(f"  [{i}] {ts} | {str(row['job_category']):25s} | {str(row['company_name']):20s} | {str(row['job_title'])}")
    print()


def cmd_delete(args):
    """Delete a record by index."""
    if not args:
        print("Usage: python -m jd_analyzer.cli delete <index>")
        return
    try:
        idx = int(args[0])
        if delete_record(idx):
            print(f"✅ Deleted record [{idx}]")
        else:
            print(f"❌ Index {idx} out of range")
    except ValueError:
        print("❌ Index must be a number")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        'add': cmd_add,
        'extract': cmd_extract,
        'list': cmd_list,
        'ls': cmd_list,
        'delete': cmd_delete,
        'rm': cmd_delete,
    }

    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"Unknown command: {cmd}")
        print("Available: add, extract, list, delete")


if __name__ == '__main__':
    main()

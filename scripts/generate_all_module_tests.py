#!/usr/bin/env python3
"""
Batch Generator for Module Conceptual Tests.
Iterates across course modules and invokes NVIDIA NIM AI to create:
- Set 1: Conceptual Mechanics & Core Diagnostics (Single & Multi-Select)
- Set 2: Applied Scenarios & Multi-Concept Case Test (Single & Multi-Select)
Persists tests in SQLite and updates static study_data.js.
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.db import get_conn, get_module_tests, export_static_data
from core.test_generator import generate_both_module_tests

def main():
    parser = argparse.ArgumentParser(description="Generate 2 conceptual test sets per course module.")
    parser.add_argument("--course", type=str, help="Filter by course name or ID substring")
    parser.add_argument("--module", type=str, help="Filter by specific module ID")
    parser.add_argument("--all", action="store_true", help="Generate for all modules across all courses")
    parser.add_argument("--force", action="store_true", help="Force regenerate even if tests already exist")
    parser.add_argument("--questions", type=int, default=12, help="Target questions per test set (default: 12, max: 20)")
    args = parser.parse_args()

    conn = get_conn()

    query = """
        SELECT m.id as module_id, m.name as module_name, m.number, c.id as course_id, c.name as course_name,
               (SELECT COUNT(*) FROM topics t WHERE t.module_id = m.id) as topic_count
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE 1=1
    """
    params = []

    if args.module:
        query += " AND m.id = ?"
        params.append(args.module)
    elif args.course:
        query += " AND (c.id = ? OR c.name LIKE ?)"
        params.extend([args.course, f"%{args.course}%"])

    query += " ORDER BY c.name ASC, m.number ASC"
    modules = conn.execute(query, params).fetchall()

    if not modules:
        print("No matching modules found!")
        return

    print(f"Found {len(modules)} module(s) to process.")
    print(f"Configuration: questions_per_set={args.questions}, force_regenerate={args.force}")
    print("=" * 70)

    success_count = 0
    skipped_count = 0
    error_count = 0

    for i, mod in enumerate(modules, start=1):
        mid = mod["module_id"]
        mname = mod["module_name"]
        cname = mod["course_name"]
        tcount = mod["topic_count"]

        print(f"\n[{i}/{len(modules)}] Course: {cname} | Module: {mname} ({tcount} topics)")

        if tcount == 0:
            print("  Skipping: Module has 0 topics.")
            skipped_count += 1
            continue

        existing = get_module_tests(mid)
        if len(existing) >= 2 and not args.force:
            print(f"  Already has {len(existing)} test sets. Use --force to regenerate.")
            skipped_count += 1
            continue

        try:
            start_t = time.time()
            res = generate_both_module_tests(
                module_id=mid,
                force_regenerate=args.force,
                questions_per_set=args.questions
            )
            elapsed = time.time() - start_t
            sets = res.get("sets", [])
            print(f"  Success in {elapsed:.1f}s!")
            for s in sets:
                mcqs = sum(1 for q in s['questions'] if q['type'] == 'single_choice')
                msqs = sum(1 for q in s['questions'] if q['type'] == 'multiple_choice')
                print(f"    Set {s['set_number']}: '{s['title']}' -> {len(s['questions'])} Qs ({mcqs} Single, {msqs} Multi-Correct)")
            success_count += 1
        except Exception as e:
            print(f"  Error generating tests for module {mid}: {e}")
            error_count += 1

    print("\n" + "=" * 70)
    print(f"Batch generation completed: {success_count} generated, {skipped_count} skipped, {error_count} errors.")
    print("Exporting static study_data.js bundle...")
    export_static_data()
    print("Export completed successfully.")

if __name__ == "__main__":
    main()

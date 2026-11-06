"""
StudyEngine Curation Watchdog & Auto-Moderator.
Monitors background curation progress, auto-recovers any failed topics,
and periodically exports study_data.js.
"""

import sys
import time
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("watchdog")

def monitor_loop():
    logger.info("Starting StudyEngine Curation Watchdog & Auto-Moderator...")
    last_export_time = 0

    while True:
        try:
            conn = db.get_conn()
            
            # 1. Check status counts
            counts = {row["status"]: row["cnt"] for row in conn.execute("SELECT status, count(*) as cnt FROM topics GROUP BY status").fetchall()}
            completed = counts.get("completed", 0)
            pending = counts.get("pending", 0)
            processing = counts.get("processing", 0)
            errors = counts.get("error", 0)
            
            # 2. Auto-heal any errors
            if errors > 0:
                logger.warning(f"Detected {errors} error topics. Auto-healing and resetting to pending...")
                with conn:
                    conn.execute("UPDATE topics SET status = 'pending', error_message = '' WHERE status = 'error'")
            
            # 3. Check for stuck 'processing' topics (if stuck for > 10 minutes)
            # Reset them to pending
            with conn:
                conn.execute("""
                    UPDATE topics 
                    SET status = 'pending', error_message = '' 
                    WHERE status = 'processing' 
                    AND (strftime('%s', 'now') - strftime('%s', created_at)) > 900
                """)

            logger.info(f"[Progress] Completed: {completed} | Processing: {processing} | Pending: {pending} | Errors: {errors}")

            # 4. Periodically export static data (every 5 minutes or when done)
            now = time.time()
            if now - last_export_time > 300 or (pending == 0 and processing == 0):
                db.export_static_data()
                last_export_time = now
                logger.info("Exported updated study_data.js.")

            if pending == 0 and processing == 0:
                logger.info("🎉 ALL TOPICS ACROSS ALL SUBJECTS COMPLETED!")
                break

        except Exception as e:
            logger.error(f"Error in watchdog: {e}")

        time.sleep(45)

if __name__ == "__main__":
    monitor_loop()


"""
Flask API for PTT Site Watcher
"""
import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from database import Database
from scraper import scrape_sync

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize database
db_path = os.getenv("DATABASE_PATH", "ptt_watcher.db")
db = Database(db_path)

# Lock for scan operations
scan_lock = threading.Lock()


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get the current scan status"""
    status = db.get_scan_status()
    return jsonify(status)


@app.route("/api/announcements", methods=["GET"])
def get_announcements():
    """Get all tracked announcements"""
    announcements = db.get_all_announcements()
    return jsonify([a.to_dict() for a in announcements])


@app.route("/api/changes", methods=["GET"])
def get_changes():
    """Get all detected changes"""
    limit = request.args.get("limit", 50, type=int)
    changes = db.get_all_changes(limit=limit)
    return jsonify([c.to_dict() for c in changes])


@app.route("/api/scan", methods=["POST"])
def trigger_scan():
    """Trigger a new scan"""
    # Check if already scanning
    status = db.get_scan_status()
    if status["is_scanning"]:
        return jsonify({"error": "Scan already in progress"}), 409
    
    # Run scan in background thread
    def run_scan():
        with scan_lock:
            try:
                db.set_scanning(True)
                
                # Scrape announcements
                announcements = scrape_sync(headless=True)
                
                # Process each announcement
                new_changes = []
                current_links = []
                
                for ann in announcements:
                    current_links.append(ann["link"])
                    _, change = db.upsert_announcement(
                        title=ann["title"],
                        date_text=ann["date_text"],
                        link=ann["link"]
                    )
                    if change:
                        new_changes.append(change)
                
                # Mark removed announcements
                removed_changes = db.mark_removed_announcements(current_links)
                new_changes.extend(removed_changes)
                
                db.set_scanning(False)
                
            except Exception as e:
                db.set_scanning(False, str(e))
                print(f"Scan error: {e}")
    
    thread = threading.Thread(target=run_scan)
    thread.start()
    
    return jsonify({"message": "Scan started"})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    
    print(f"Starting PTT Site Watcher API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

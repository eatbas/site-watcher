"""
Flask API for PTT Site Watcher
"""
import os
import threading
import time
from datetime import datetime
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

# Auto-scan configuration
AUTO_SCAN_INTERVAL = int(os.getenv("AUTO_SCAN_INTERVAL", 600))  # 10 minutes in seconds
auto_scan_enabled = True
last_auto_scan = None


def perform_scan():
    """Execute a scan and return changes detected"""
    global last_auto_scan
    
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
            last_auto_scan = datetime.now()
            
            return new_changes
            
        except Exception as e:
            db.set_scanning(False, str(e))
            print(f"Scan error: {e}")
            return []


def auto_scan_worker():
    """Background worker for automatic scanning"""
    global last_auto_scan
    
    print(f"Auto-scan worker started. Interval: {AUTO_SCAN_INTERVAL} seconds")
    
    while auto_scan_enabled:
        try:
            # Wait for the interval
            time.sleep(AUTO_SCAN_INTERVAL)
            
            if not auto_scan_enabled:
                break
                
            # Check if not already scanning
            status = db.get_scan_status()
            if not status["is_scanning"]:
                print(f"[{datetime.now()}] Starting auto-scan...")
                changes = perform_scan()
                print(f"[{datetime.now()}] Auto-scan complete. Changes detected: {len(changes)}")
                
        except Exception as e:
            print(f"Auto-scan error: {e}")


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get the current scan status"""
    status = db.get_scan_status()
    status["auto_scan_enabled"] = auto_scan_enabled
    status["auto_scan_interval"] = AUTO_SCAN_INTERVAL
    status["next_auto_scan"] = None
    
    if last_auto_scan and auto_scan_enabled:
        next_scan = last_auto_scan.timestamp() + AUTO_SCAN_INTERVAL
        status["next_auto_scan"] = datetime.fromtimestamp(next_scan).isoformat()
    
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
    since = request.args.get("since", None)  # ISO timestamp to get changes since
    changes = db.get_all_changes(limit=limit)
    
    # Filter by timestamp if provided
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            changes = [c for c in changes if c.detected_at and c.detected_at > since_dt]
        except ValueError:
            pass
    
    return jsonify([c.to_dict() for c in changes])


@app.route("/api/changes/recent", methods=["GET"])
def get_recent_changes():
    """Get changes detected in the last scan"""
    minutes = request.args.get("minutes", 1, type=int)
    changes = db.get_all_changes(limit=100)
    
    # Filter to recent changes
    cutoff = datetime.now().timestamp() - (minutes * 60)
    recent = [c for c in changes if c.detected_at and c.detected_at.timestamp() > cutoff]
    
    return jsonify([c.to_dict() for c in recent])


@app.route("/api/scan", methods=["POST"])
def trigger_scan():
    """Trigger a new scan"""
    # Check if already scanning
    status = db.get_scan_status()
    if status["is_scanning"]:
        return jsonify({"error": "Scan already in progress"}), 409
    
    # Run scan in background thread
    def run_scan():
        changes = perform_scan()
        print(f"Manual scan complete. Changes detected: {len(changes)}")
    
    thread = threading.Thread(target=run_scan)
    thread.start()
    
    return jsonify({"message": "Scan started"})


@app.route("/api/auto-scan", methods=["POST"])
def toggle_auto_scan():
    """Toggle auto-scan on/off"""
    global auto_scan_enabled
    
    data = request.get_json() or {}
    enabled = data.get("enabled", not auto_scan_enabled)
    auto_scan_enabled = enabled
    
    return jsonify({
        "auto_scan_enabled": auto_scan_enabled,
        "auto_scan_interval": AUTO_SCAN_INTERVAL
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    
    # Start auto-scan worker thread
    auto_scan_thread = threading.Thread(target=auto_scan_worker, daemon=True)
    auto_scan_thread.start()
    
    print(f"Starting PTT Site Watcher API on {host}:{port}")
    print(f"Auto-scan enabled: every {AUTO_SCAN_INTERVAL} seconds ({AUTO_SCAN_INTERVAL // 60} minutes)")
    
    # Reset scan status on startup in case of previous crash
    try:
        db.set_scanning(False)
        print("Reset scan status to 'ready'")
    except Exception as e:
        print(f"Warning: Could not reset scan status: {e}")
        
    app.run(host=host, port=port, debug=debug)

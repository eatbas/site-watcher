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
from email_service import send_change_notification

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize database
db_path = os.getenv("DATABASE_PATH", "ptt_watcher.db")
db = Database(db_path)

# Lock for scan operations
scan_lock = threading.Lock()

# Auto-scan configuration from database
def get_auto_scan_interval():
    settings = db.get_settings()
    return settings.get("refresh_interval", 600)

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
            
            # Get existing announcement count to detect potential false removals
            existing_announcements = db.get_all_announcements()
            existing_count = len(existing_announcements)
            
            # VERIFICATION: If we got 0 results but there were existing items,
            # or if all existing items would be removed, wait and re-check
            if existing_count > 0:
                scraped_count = len(announcements)
                
                # Case 1: No items scraped at all - likely a scraping failure
                if scraped_count == 0:
                    print(f"⚠️ Warning: Scraped 0 announcements but {existing_count} exist in DB. Waiting 5 seconds to verify...")
                    time.sleep(5)
                    
                    # Re-scrape to confirm
                    announcements = scrape_sync(headless=True)
                    scraped_count = len(announcements)
                    print(f"⚠️ Verification scrape got {scraped_count} announcements")
                    
                    # If still 0, skip the removal detection to avoid false positives
                    if scraped_count == 0:
                        print(f"⚠️ Still 0 announcements after verification. Skipping removal detection to avoid false positives.")
                        db.set_scanning(False)
                        last_auto_scan = datetime.now()
                        return []
                
                # Case 2: Check if all existing items would be marked as removed
                else:
                    scraped_links = set(ann["link"] for ann in announcements)
                    existing_links = set(a.link for a in existing_announcements if a.link)
                    would_be_removed = existing_links - scraped_links
                    
                    # If more than 50% would be removed, verify
                    if len(would_be_removed) > existing_count * 0.5 and len(would_be_removed) > 3:
                        print(f"⚠️ Warning: {len(would_be_removed)} of {existing_count} would be removed. Waiting 5 seconds to verify...")
                        time.sleep(5)
                        
                        # Re-scrape to confirm
                        announcements = scrape_sync(headless=True)
                        print(f"⚠️ Verification scrape got {len(announcements)} announcements")
            
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
            
            # Mark removed announcements (only if we got valid results)
            if len(current_links) > 0:
                removed_changes = db.mark_removed_announcements(current_links)
                new_changes.extend(removed_changes)
            else:
                print("⚠️ Skipping removal detection due to empty scrape results")
            
            db.set_scanning(False)
            last_auto_scan = datetime.now()
            
            # Send email notification if there are changes
            if new_changes:
                settings = db.get_settings()
                changes_dict = [c.to_dict() for c in new_changes]
                try:
                    send_change_notification(changes_dict, settings)
                except Exception as email_error:
                    print(f"Email notification failed: {email_error}")
            
            return new_changes
            
        except Exception as e:
            db.set_scanning(False, str(e))
            print(f"Scan error: {e}")
            return []


def auto_scan_worker():
    """Background worker for automatic scanning"""
    global last_auto_scan
    
    interval = get_auto_scan_interval()
    print(f"Auto-scan worker started. Interval: {interval} seconds")
    
    while auto_scan_enabled:
        try:
            # Get current interval from settings
            interval = get_auto_scan_interval()
            
            # Wait for the interval
            time.sleep(interval)
            
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
    interval = get_auto_scan_interval()
    status["auto_scan_enabled"] = auto_scan_enabled
    status["auto_scan_interval"] = interval
    status["next_auto_scan"] = None
    
    if last_auto_scan and auto_scan_enabled:
        next_scan = last_auto_scan.timestamp() + interval
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
        "auto_scan_interval": get_auto_scan_interval()
    })


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get the current settings"""
    settings = db.get_settings()
    # Don't expose SMTP password
    settings["smtp_password"] = "********" if settings.get("smtp_password") else ""
    return jsonify(settings)


@app.route("/api/settings", methods=["PUT"])
def update_settings():
    """Update settings"""
    data = request.get_json() or {}
    
    # Get current settings to preserve password if not changed
    current_settings = db.get_settings()
    
    # If password is masked, keep the old one
    if data.get("smtp_password") == "********":
        data["smtp_password"] = current_settings.get("smtp_password", "")
    
    db.update_settings(data)
    
    # Return updated settings (with masked password)
    updated = db.get_settings()
    updated["smtp_password"] = "********" if updated.get("smtp_password") else ""
    return jsonify(updated)


@app.route("/api/settings/test-email", methods=["POST"])
def test_email():
    """Send a test email to verify configuration"""
    settings = db.get_settings()
    
    if not settings.get("email_enabled"):
        return jsonify({"error": "Email notifications are disabled"}), 400
    
    if not settings.get("email_recipients"):
        return jsonify({"error": "No recipients configured"}), 400
    
    if not settings.get("smtp_password"):
        return jsonify({"error": "SMTP password not configured"}), 400
    
    # Create a test change
    test_changes = [{
        "change_type": "new",
        "title": "Test Email - PTT Site Watcher",
        "detected_at": datetime.now().isoformat()
    }]
    
    try:
        success = send_change_notification(test_changes, settings)
        if success:
            return jsonify({"message": "Test email sent successfully!"})
        else:
            return jsonify({"error": "Failed to send test email"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Initialize last_auto_scan so frontend gets a valid next_auto_scan immediately
    # Must declare global before any reference to it in this scope
    global last_auto_scan
    last_auto_scan = datetime.now()
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    
    # Start auto-scan worker thread
    auto_scan_thread = threading.Thread(target=auto_scan_worker, daemon=True)
    auto_scan_thread.start()
    
    interval = get_auto_scan_interval()
    print(f"Starting PTT Site Watcher API on {host}:{port}")
    print(f"Auto-scan enabled: every {interval} seconds ({interval // 60} minutes)")
    
    # Reset scan status on startup in case of previous crash
    try:
        db.set_scanning(False)
        print("Reset scan status to 'ready'")
    except Exception as e:
        print(f"Warning: Could not reset scan status: {e}")
        
    app.run(host=host, port=port, debug=debug)

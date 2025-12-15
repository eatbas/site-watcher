export interface Announcement {
    id: number;
    title: string;
    date_text: string;
    link: string;
    content_hash: string;
    first_seen: string;
    last_seen: string;
}

export interface Change {
    id: number;
    announcement_id: number | null;
    change_type: 'new' | 'modified' | 'removed';
    detected_at: string;
    title: string;
    old_content: string | null;
    new_content: string | null;
}

export interface ScanStatus {
    last_scan: string | null;
    is_scanning: boolean;
    announcement_count: number;
    error: string | null;
    auto_scan_enabled?: boolean;
    auto_scan_interval?: number;
}

export interface Settings {
    refresh_interval: number;
    email_enabled: boolean;
    email_sender: string;
    email_recipients: string[];
    smtp_server: string;
    smtp_port: number;
    smtp_username: string;
    smtp_password: string;
}

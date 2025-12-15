import type { Announcement, Change, ScanStatus } from '../types';

const API_BASE = 'http://localhost:5000/api';

export async function fetchStatus(): Promise<ScanStatus> {
    const response = await fetch(`${API_BASE}/status`);
    if (!response.ok) throw new Error('Failed to fetch status');
    return response.json();
}

export async function fetchAnnouncements(): Promise<Announcement[]> {
    const response = await fetch(`${API_BASE}/announcements`);
    if (!response.ok) throw new Error('Failed to fetch announcements');
    return response.json();
}

export async function fetchChanges(limit = 50): Promise<Change[]> {
    const response = await fetch(`${API_BASE}/changes?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch changes');
    return response.json();
}

export async function triggerScan(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to trigger scan');
    }
    return response.json();
}

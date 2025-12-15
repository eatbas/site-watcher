import { useState, useEffect, useCallback } from 'react';
import { StatusIndicator } from './components/StatusIndicator';
import { ScanButton } from './components/ScanButton';
import { AnnouncementList } from './components/AnnouncementList';
import { ChangeLog } from './components/ChangeLog';
import { fetchStatus, fetchAnnouncements, fetchChanges, triggerScan } from './services/api';
import type { ScanStatus, Announcement, Change } from './types';
import './App.css';

function App() {
  const [status, setStatus] = useState<ScanStatus | null>(null);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [changes, setChanges] = useState<Change[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [statusData, announcementsData, changesData] = await Promise.all([
        fetchStatus(),
        fetchAnnouncements(),
        fetchChanges(),
      ]);
      setStatus(statusData);
      setAnnouncements(announcementsData);
      setChanges(changesData);
      setError(null);
    } catch (err) {
      setError('Failed to connect to backend. Make sure it\'s running on port 5000.');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Poll for updates every 5 seconds when scanning
    const interval = setInterval(() => {
      if (status?.is_scanning) {
        loadData();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [loadData, status?.is_scanning]);

  const handleScan = async () => {
    try {
      await triggerScan();
      // Immediately reload status to show scanning state
      const statusData = await fetchStatus();
      setStatus(statusData);

      // Poll until scanning is complete
      const pollInterval = setInterval(async () => {
        const newStatus = await fetchStatus();
        setStatus(newStatus);
        if (!newStatus.is_scanning) {
          clearInterval(pollInterval);
          loadData();
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scan');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
      {/* Header */}
      <header className="border-b border-dark-800/50 backdrop-blur-xl bg-dark-950/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/20">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-white"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path
                    fillRule="evenodd"
                    d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-dark-300 bg-clip-text text-transparent">
                  PTT Site Watcher
                </h1>
                <p className="text-dark-400 text-sm">
                  Monitor PTT announcements for changes
                </p>
              </div>
            </div>
            <ScanButton
              onClick={handleScan}
              isScanning={status?.is_scanning ?? false}
              disabled={loading}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400">
            <div className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </div>
          </div>
        )}

        <div className="space-y-6">
          {/* Status Section */}
          <StatusIndicator status={status} loading={loading} />

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AnnouncementList announcements={announcements} loading={loading} />
            <ChangeLog changes={changes} loading={loading} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-800/50 mt-auto py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-dark-500 text-sm">
            Monitoring{' '}
            <a
              href="https://www.ptt.gov.tr/duyurular?page=1&announcementType=3"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-500 hover:text-primary-400 transition-colors"
            >
              PTT İhale Duyuruları
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

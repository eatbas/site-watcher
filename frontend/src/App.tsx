import { useState, useEffect, useCallback, useRef } from 'react';
import { StatusIndicator } from './components/StatusIndicator';
import { ScanButton } from './components/ScanButton';
import { AnnouncementList } from './components/AnnouncementList';
import { ChangeLog } from './components/ChangeLog';
import { ChangeAlert } from './components/ChangeAlert';
import { SettingsPage } from './components/SettingsPage';
import { fetchStatus, fetchAnnouncements, fetchChanges, triggerScan } from './services/api';
import type { ScanStatus, Announcement, Change } from './types';
import './App.css';

const AUTO_SCAN_INTERVAL = 10 * 60 * 1000; // 10 minutes in milliseconds

function App() {
  const [status, setStatus] = useState<ScanStatus | null>(null);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [changes, setChanges] = useState<Change[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newChanges, setNewChanges] = useState<Change[]>([]);
  const [showAlert, setShowAlert] = useState(false);
  const [countdown, setCountdown] = useState<string>('');
  const [showSettings, setShowSettings] = useState(false);

  const lastChangeCount = useRef(0);

  const loadData = useCallback(async () => {
    try {
      const [statusData, announcementsData, changesData] = await Promise.all([
        fetchStatus(),
        fetchAnnouncements(),
        fetchChanges(),
      ]);
      setStatus(statusData);
      setAnnouncements(announcementsData);

      // Check for new changes
      if (changesData.length > lastChangeCount.current && lastChangeCount.current > 0) {
        const newOnes = changesData.slice(0, changesData.length - lastChangeCount.current);
        if (newOnes.length > 0) {
          setNewChanges(newOnes);
          setShowAlert(true);
          // Play notification sound
          playNotificationSound();
        }
      }
      lastChangeCount.current = changesData.length;

      setChanges(changesData);
      setError(null);
    } catch (err) {
      setError('Failed to connect to backend. Make sure it\'s running on port 5000.');
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const playNotificationSound = () => {
    // Create a simple beep sound
    try {
      const audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      gainNode.gain.value = 0.3;

      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.2);
    } catch (e) {
      console.log('Could not play notification sound:', e);
    }
  };

  // Server handles auto-scanning, we just update the countdown display from server status

  // Update countdown every second based on server's next_auto_scan
  useEffect(() => {
    const updateCountdown = () => {
      if (status?.next_auto_scan) {
        const nextScanTime = new Date(status.next_auto_scan);
        const remaining = nextScanTime.getTime() - Date.now();
        if (remaining > 0) {
          const minutes = Math.floor(remaining / 60000);
          const seconds = Math.floor((remaining % 60000) / 1000);
          setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`);
        } else {
          setCountdown('Scanning...');
        }
      } else if (status?.is_scanning) {
        setCountdown('Scanning...');
      } else {
        // No next scan time from server yet, show loading
        setCountdown('--:--');
      }
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);

    return () => clearInterval(interval);
  }, [status?.next_auto_scan, status?.is_scanning]);

  useEffect(() => {
    loadData();

    // Poll for status updates every 5 seconds to stay in sync with server
    const interval = setInterval(() => {
      loadData();
    }, 5000);

    return () => {
      clearInterval(interval);
    };
  }, [loadData]);

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
          await loadData();
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scan');
    }
  };

  const dismissAlert = () => {
    setShowAlert(false);
    setNewChanges([]);
  };

  // If showing settings, render settings page
  if (showSettings) {
    return (
      <SettingsPage
        onClose={() => {
          setShowSettings(false);
          loadData(); // Reload data to get updated settings
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
      {/* Change Alert */}
      {showAlert && newChanges.length > 0 && (
        <ChangeAlert changes={newChanges} onDismiss={dismissAlert} />
      )}

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
                <p className="text-dark-400 text-sm flex items-center gap-2">
                  <span>Auto-scan in</span>
                  <span className="font-mono text-primary-400">{countdown || '--:--'}</span>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowSettings(true)}
                className="w-10 h-10 rounded-xl bg-dark-800/50 flex items-center justify-center hover:bg-dark-700/50 transition-colors border border-dark-700/50"
                title="Settings"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-dark-300"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
              <ScanButton
                onClick={() => handleScan()}
                isScanning={status?.is_scanning ?? false}
                disabled={loading}
              />
            </div>
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
            {' · '}
            <span className="text-dark-600">Auto-scan every 10 minutes</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

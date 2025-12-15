import { useState, useEffect } from 'react';
import { fetchSettings, updateSettings } from '../services/api';
import type { Settings } from '../types';

interface SettingsPageProps {
    onClose: () => void;
}

export function SettingsPage({ onClose }: SettingsPageProps) {
    const [settings, setSettings] = useState<Settings | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [newRecipient, setNewRecipient] = useState('');

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            setLoading(true);
            const data = await fetchSettings();
            setSettings(data);
            setError(null);
        } catch (err) {
            setError('Failed to load settings');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!settings) return;

        try {
            setSaving(true);
            setError(null);
            await updateSettings(settings);
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            setError('Failed to save settings');
            console.error(err);
        } finally {
            setSaving(false);
        }
    };

    const addRecipient = () => {
        if (!settings || !newRecipient.trim()) return;
        if (!newRecipient.includes('@')) {
            setError('Please enter a valid email address');
            return;
        }
        if (settings.email_recipients.includes(newRecipient.trim())) {
            setError('Email already in recipients list');
            return;
        }
        setSettings({
            ...settings,
            email_recipients: [...settings.email_recipients, newRecipient.trim()],
        });
        setNewRecipient('');
        setError(null);
    };

    const removeRecipient = (email: string) => {
        if (!settings) return;
        setSettings({
            ...settings,
            email_recipients: settings.email_recipients.filter((r) => r !== email),
        });
    };

    const formatInterval = (seconds: number): string => {
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
        const hours = Math.floor(minutes / 60);
        const remainingMins = minutes % 60;
        return remainingMins > 0
            ? `${hours}h ${remainingMins}m`
            : `${hours} hour${hours !== 1 ? 's' : ''}`;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
        );
    }

    if (!settings) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 flex items-center justify-center">
                <div className="text-red-400">Failed to load settings</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
            {/* Header */}
            <header className="border-b border-dark-800/50 backdrop-blur-xl bg-dark-950/50 sticky top-0 z-50">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={onClose}
                                className="w-10 h-10 rounded-lg bg-dark-800/50 flex items-center justify-center hover:bg-dark-700/50 transition-colors"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-dark-300"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                            </button>
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-dark-300 bg-clip-text text-transparent">
                                    Settings
                                </h1>
                                <p className="text-dark-400 text-sm">
                                    Configure scan interval and email notifications
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Success Toast */}
                {success && (
                    <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 flex items-center gap-2">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clipRule="evenodd"
                            />
                        </svg>
                        Settings saved successfully!
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 flex items-center gap-2">
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
                )}

                <div className="space-y-8">
                    {/* Scan Interval Section */}
                    <section className="bg-dark-900/50 border border-dark-800/50 rounded-2xl p-6">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5 text-primary-500"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            Scan Interval
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-dark-300 text-sm mb-2">
                                    Auto-scan every: <span className="text-primary-400 font-medium">{formatInterval(settings.refresh_interval)}</span>
                                </label>
                                <input
                                    type="range"
                                    min="60"
                                    max="3600"
                                    step="60"
                                    value={settings.refresh_interval}
                                    onChange={(e) =>
                                        setSettings({ ...settings, refresh_interval: parseInt(e.target.value) })
                                    }
                                    className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                                />
                                <div className="flex justify-between text-xs text-dark-500 mt-1">
                                    <span>1 min</span>
                                    <span>30 min</span>
                                    <span>1 hour</span>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Email Notifications Section */}
                    <section className="bg-dark-900/50 border border-dark-800/50 rounded-2xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-primary-500"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                                    <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                                </svg>
                                Email Notifications
                            </h2>
                            <button
                                onClick={() =>
                                    setSettings({ ...settings, email_enabled: !settings.email_enabled })
                                }
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${settings.email_enabled ? 'bg-primary-500' : 'bg-dark-700'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${settings.email_enabled ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>

                        <div className={`space-y-4 ${!settings.email_enabled ? 'opacity-50 pointer-events-none' : ''}`}>
                            {/* Sender Email */}
                            <div>
                                <label className="block text-dark-300 text-sm mb-2">Sender Email</label>
                                <input
                                    type="email"
                                    value={settings.email_sender}
                                    onChange={(e) => setSettings({ ...settings, email_sender: e.target.value })}
                                    placeholder="sender@example.com"
                                    className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-700/50 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                                />
                            </div>

                            {/* Recipients */}
                            <div>
                                <label className="block text-dark-300 text-sm mb-2">Recipients</label>
                                <div className="flex gap-2">
                                    <input
                                        type="email"
                                        value={newRecipient}
                                        onChange={(e) => setNewRecipient(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && addRecipient()}
                                        placeholder="Add recipient email..."
                                        className="flex-1 px-4 py-2.5 bg-dark-800/50 border border-dark-700/50 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                                    />
                                    <button
                                        onClick={addRecipient}
                                        className="px-4 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium"
                                    >
                                        Add
                                    </button>
                                </div>

                                {/* Recipients List */}
                                <div className="mt-3 space-y-2">
                                    {settings.email_recipients.length === 0 ? (
                                        <p className="text-dark-500 text-sm">No recipients added</p>
                                    ) : (
                                        settings.email_recipients.map((email) => (
                                            <div
                                                key={email}
                                                className="flex items-center justify-between px-3 py-2 bg-dark-800/30 rounded-lg"
                                            >
                                                <span className="text-dark-200">{email}</span>
                                                <button
                                                    onClick={() => removeRecipient(email)}
                                                    className="text-dark-500 hover:text-red-400 transition-colors"
                                                >
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        className="h-5 w-5"
                                                        viewBox="0 0 20 20"
                                                        fill="currentColor"
                                                    >
                                                        <path
                                                            fillRule="evenodd"
                                                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                                            clipRule="evenodd"
                                                        />
                                                    </svg>
                                                </button>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* SMTP Configuration Section */}
                    <section className="bg-dark-900/50 border border-dark-800/50 rounded-2xl p-6">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5 text-primary-500"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            SMTP Configuration
                        </h2>

                        <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${!settings.email_enabled ? 'opacity-50 pointer-events-none' : ''}`}>
                            <div>
                                <label className="block text-dark-300 text-sm mb-2">SMTP Server</label>
                                <input
                                    type="text"
                                    value={settings.smtp_server}
                                    onChange={(e) => setSettings({ ...settings, smtp_server: e.target.value })}
                                    placeholder="smtp.office365.com"
                                    className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-700/50 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                                />
                            </div>

                            <div>
                                <label className="block text-dark-300 text-sm mb-2">SMTP Port</label>
                                <input
                                    type="number"
                                    value={settings.smtp_port}
                                    onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })}
                                    placeholder="587"
                                    className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-700/50 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                                />
                            </div>

                            <div>
                                <label className="block text-dark-300 text-sm mb-2">SMTP Username</label>
                                <input
                                    type="email"
                                    value={settings.smtp_username}
                                    onChange={(e) => setSettings({ ...settings, smtp_username: e.target.value })}
                                    placeholder="email@example.com"
                                    className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-700/50 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                                />
                            </div>

                            <div>
                                <label className="block text-dark-300 text-sm mb-2">SMTP Password</label>
                                <input
                                    type="password"
                                    value={settings.smtp_password}
                                    onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
                                    placeholder="••••••••"
                                    className="w-full px-4 py-2.5 bg-dark-800/50 border border-dark-700/50 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                                />
                            </div>
                        </div>
                    </section>

                    {/* Save Button */}
                    <div className="flex justify-end gap-4">
                        <button
                            onClick={onClose}
                            className="px-6 py-3 bg-dark-800/50 text-dark-300 rounded-xl hover:bg-dark-700/50 transition-colors font-medium"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl hover:from-primary-600 hover:to-primary-700 transition-all font-medium shadow-lg shadow-primary-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {saving ? (
                                <>
                                    <svg
                                        className="animate-spin h-5 w-5"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                    >
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        ></circle>
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        ></path>
                                    </svg>
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-5 w-5"
                                        viewBox="0 0 20 20"
                                        fill="currentColor"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                    Save Settings
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}

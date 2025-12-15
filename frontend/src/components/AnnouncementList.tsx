import type { Announcement } from '../types';

interface AnnouncementListProps {
    announcements: Announcement[];
    loading: boolean;
}

export function AnnouncementList({ announcements, loading }: AnnouncementListProps) {
    if (loading) {
        return (
            <div className="glass rounded-2xl p-6">
                <h2 className="text-xl font-semibold mb-4">Tracked Announcements</h2>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="animate-pulse">
                            <div className="h-4 bg-dark-700 rounded w-3/4 mb-2"></div>
                            <div className="h-3 bg-dark-700 rounded w-1/4"></div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (announcements.length === 0) {
        return (
            <div className="glass rounded-2xl p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-dark-800 flex items-center justify-center">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-8 w-8 text-dark-500"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                </div>
                <h3 className="text-lg font-medium text-dark-300 mb-2">No Announcements Yet</h3>
                <p className="text-dark-500">
                    Click "Scan Now" to fetch announcements from PTT
                </p>
            </div>
        );
    }

    return (
        <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-primary-500"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                >
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                    <path
                        fillRule="evenodd"
                        d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
                        clipRule="evenodd"
                    />
                </svg>
                Tracked Announcements
                <span className="text-sm font-normal text-dark-400">
                    ({announcements.length})
                </span>
            </h2>
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {announcements.map((announcement) => (
                    <a
                        key={announcement.id}
                        href={announcement.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 rounded-xl bg-dark-800/50 hover:bg-dark-700/50 transition-all duration-200 border border-transparent hover:border-dark-600 group"
                    >
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-dark-100 group-hover:text-primary-400 transition-colors truncate">
                                    {announcement.title}
                                </h3>
                                <p className="text-sm text-dark-400 mt-1">
                                    {announcement.date_text}
                                </p>
                            </div>
                            <div className="flex-shrink-0">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-dark-700 text-dark-300">
                                    {new Date(announcement.first_seen).toLocaleDateString('tr-TR')}
                                </span>
                            </div>
                        </div>
                    </a>
                ))}
            </div>
        </div>
    );
}

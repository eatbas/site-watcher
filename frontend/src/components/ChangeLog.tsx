import type { Change } from '../types';

interface ChangeLogProps {
    changes: Change[];
    loading: boolean;
}

const changeTypeConfig = {
    new: {
        color: 'emerald',
        label: 'New',
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
        ),
    },
    modified: {
        color: 'yellow',
        label: 'Modified',
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
        ),
    },
    removed: {
        color: 'red',
        label: 'Removed',
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
        ),
    },
};

export function ChangeLog({ changes, loading }: ChangeLogProps) {
    if (loading) {
        return (
            <div className="glass rounded-2xl p-6">
                <h2 className="text-xl font-semibold mb-4">Change History</h2>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="animate-pulse flex gap-3">
                            <div className="w-8 h-8 bg-dark-700 rounded-full"></div>
                            <div className="flex-1">
                                <div className="h-4 bg-dark-700 rounded w-3/4 mb-2"></div>
                                <div className="h-3 bg-dark-700 rounded w-1/4"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (changes.length === 0) {
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
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                </div>
                <h3 className="text-lg font-medium text-dark-300 mb-2">No Changes Recorded</h3>
                <p className="text-dark-500">
                    Changes will appear here after scanning
                </p>
            </div>
        );
    }

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleString('tr-TR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
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
                Change History
                <span className="text-sm font-normal text-dark-400">
                    ({changes.length})
                </span>
            </h2>
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {changes.map((change) => {
                    const config = changeTypeConfig[change.change_type];
                    return (
                        <div
                            key={change.id}
                            className="flex gap-3 p-3 rounded-xl bg-dark-800/50 border border-dark-700/50"
                        >
                            <div
                                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-${config.color}-500/20 text-${config.color}-500`}
                                style={{
                                    backgroundColor:
                                        config.color === 'emerald'
                                            ? 'rgba(16, 185, 129, 0.2)'
                                            : config.color === 'yellow'
                                                ? 'rgba(234, 179, 8, 0.2)'
                                                : 'rgba(239, 68, 68, 0.2)',
                                    color:
                                        config.color === 'emerald'
                                            ? 'rgb(16, 185, 129)'
                                            : config.color === 'yellow'
                                                ? 'rgb(234, 179, 8)'
                                                : 'rgb(239, 68, 68)',
                                }}
                            >
                                {config.icon}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <span
                                        className="text-xs font-medium px-2 py-0.5 rounded-full"
                                        style={{
                                            backgroundColor:
                                                config.color === 'emerald'
                                                    ? 'rgba(16, 185, 129, 0.2)'
                                                    : config.color === 'yellow'
                                                        ? 'rgba(234, 179, 8, 0.2)'
                                                        : 'rgba(239, 68, 68, 0.2)',
                                            color:
                                                config.color === 'emerald'
                                                    ? 'rgb(16, 185, 129)'
                                                    : config.color === 'yellow'
                                                        ? 'rgb(234, 179, 8)'
                                                        : 'rgb(239, 68, 68)',
                                        }}
                                    >
                                        {config.label}
                                    </span>
                                    <span className="text-xs text-dark-500">
                                        {formatDate(change.detected_at)}
                                    </span>
                                </div>
                                <p className="text-sm text-dark-200 truncate">{change.title}</p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

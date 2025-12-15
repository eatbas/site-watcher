import type { ScanStatus } from '../types';

interface StatusIndicatorProps {
    status: ScanStatus | null;
    loading: boolean;
}

export function StatusIndicator({ status, loading }: StatusIndicatorProps) {
    if (loading || !status) {
        return (
            <div className="glass rounded-2xl p-6 animate-pulse">
                <div className="h-4 bg-dark-700 rounded w-1/3 mb-2"></div>
                <div className="h-6 bg-dark-700 rounded w-1/2"></div>
            </div>
        );
    }

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return 'Never';
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
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-dark-400 text-sm mb-1">Last Scan</p>
                    <p className="text-xl font-semibold">
                        {formatDate(status.last_scan)}
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-dark-400 text-sm mb-1">Status</p>
                    <div className="flex items-center gap-2">
                        {status.is_scanning ? (
                            <>
                                <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
                                <span className="text-yellow-500 font-medium">Scanning...</span>
                            </>
                        ) : status.error ? (
                            <>
                                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                                <span className="text-red-500 font-medium">Error</span>
                            </>
                        ) : (
                            <>
                                <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                                <span className="text-emerald-500 font-medium">Ready</span>
                            </>
                        )}
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-dark-400 text-sm mb-1">Tracked</p>
                    <p className="text-xl font-semibold">
                        {status.announcement_count} <span className="text-dark-400 text-sm font-normal">announcements</span>
                    </p>
                </div>
            </div>
            {status.error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {status.error}
                </div>
            )}
        </div>
    );
}

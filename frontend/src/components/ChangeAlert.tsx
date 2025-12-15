import type { Change } from '../types';

interface ChangeAlertProps {
    changes: Change[];
    onDismiss: () => void;
}

const changeTypeConfig = {
    new: {
        color: 'emerald',
        bgColor: 'rgba(16, 185, 129, 0.15)',
        textColor: 'rgb(16, 185, 129)',
        label: 'New',
    },
    modified: {
        color: 'yellow',
        bgColor: 'rgba(234, 179, 8, 0.15)',
        textColor: 'rgb(234, 179, 8)',
        label: 'Modified',
    },
    removed: {
        color: 'red',
        bgColor: 'rgba(239, 68, 68, 0.15)',
        textColor: 'rgb(239, 68, 68)',
        label: 'Removed',
    },
};

export function ChangeAlert({ changes, onDismiss }: ChangeAlertProps) {
    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
            <div className="bg-dark-900 rounded-2xl border border-dark-700 shadow-2xl max-w-lg w-full max-h-[80vh] overflow-hidden animate-slideUp">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary-600 to-primary-500 p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-white"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
                                </svg>
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white">Changes Detected!</h2>
                                <p className="text-white/80 text-sm">
                                    {changes.length} change{changes.length > 1 ? 's' : ''} found
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={onDismiss}
                            className="text-white/80 hover:text-white transition-colors"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Changes List */}
                <div className="p-4 max-h-[50vh] overflow-y-auto">
                    <div className="space-y-3">
                        {changes.map((change) => {
                            const config = changeTypeConfig[change.change_type];
                            return (
                                <div
                                    key={change.id}
                                    className="p-4 rounded-xl border border-dark-700 bg-dark-800/50"
                                    style={{ borderLeftWidth: '4px', borderLeftColor: config.textColor }}
                                >
                                    <div className="flex items-start gap-3">
                                        <span
                                            className="text-xs font-semibold px-2.5 py-1 rounded-full"
                                            style={{
                                                backgroundColor: config.bgColor,
                                                color: config.textColor,
                                            }}
                                        >
                                            {config.label}
                                        </span>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-dark-100">{change.title}</p>
                                            <p className="text-xs text-dark-500 mt-1">
                                                {new Date(change.detected_at).toLocaleString('tr-TR')}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-dark-700 bg-dark-800/50">
                    <button
                        onClick={onDismiss}
                        className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-500 text-white font-semibold rounded-xl transition-colors"
                    >
                        Dismiss
                    </button>
                </div>
            </div>
        </div>
    );
}

interface ScanButtonProps {
    onClick: () => void;
    isScanning: boolean;
    disabled: boolean;
}

export function ScanButton({ onClick, isScanning, disabled }: ScanButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled || isScanning}
            className={`
        relative px-8 py-4 rounded-xl font-semibold text-lg
        transition-all duration-300 transform
        ${isScanning
                    ? 'bg-yellow-500/20 text-yellow-500 cursor-wait'
                    : disabled
                        ? 'bg-dark-700 text-dark-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-primary-600 to-primary-500 text-white hover:from-primary-500 hover:to-primary-400 hover:scale-105 hover:shadow-lg hover:shadow-primary-500/25 active:scale-100'
                }
      `}
        >
            {isScanning ? (
                <span className="flex items-center gap-3">
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
                    Scanning...
                </span>
            ) : (
                <span className="flex items-center gap-3">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                            fillRule="evenodd"
                            d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                            clipRule="evenodd"
                        />
                    </svg>
                    Scan Now
                </span>
            )}
        </button>
    );
}

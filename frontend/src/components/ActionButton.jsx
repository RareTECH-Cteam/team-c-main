import { Link } from 'react-router-dom'
import './ActionButton.css'

function createClassName({ variant, fullWidth, className }) {
    return [
        'action-button',
        `action-button--${variant}`,
        fullWidth ? 'action-button--full-width' : '',
        className,
    ]
        .filter(Boolean)
        .join(' ')
}

export function ActionButton({
    children,
    variant = 'primary',
    type = 'button',
    disabled = 'false',
    isLoading = 'false',
    loadingLabel = '処理中...',
    fullWidth = false,
    className = '',
    ...buttonProps
}) {
    const isDisabled = disabled || isLoading
    const buttonClassName = createClassName({

    })

    return (
        <button
            {...buttonProps}
            className={buttonClassName}
            type={type}
            disabled={isDisabled}
            aria-busy={isLoading}
        >
            {isLoading && (
                <span
                    className="action-button__spinner"
                    aria-hidden="true"
                />
            )}

            <span>
                {isLoading ? loadingLabel : children}
            </span>
        </button>
    )
}

export function ActionLink({
    children,
    to,
    variant = 'primary',
    fullWidth = false,
    className = '',
    ...linkProps
}) {
    const linkClassName = createClassName({
        variant,
        fullWidth,
        className,
    })

    return (
        <Link
            {...linkProps}
            className={linkClassName}
            to={to}
        >
            {children}
        </Link>
    )
}
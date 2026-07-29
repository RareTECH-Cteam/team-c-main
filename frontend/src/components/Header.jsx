import { Link } from 'react-router-dom'
import './Header.css'

export function Header({ userName, isGuest = false }) {
    const headerName = isGuest ? 'ゲスト' : userName

    return (
        <header className='app-header'>
            <div className='app-header__inner'>
                <Link className='app-header__logo' to='/convert' aria-label='敬語変換画面'>
                    コトバディ
                </Link>

                <p className='app-header__account'>
                    <span className='app-header__user'>
                        {headerName || 'ユーザー'}
                    </span>
                </p>

                {isGuest && (
                    <Link className='app-header__login-link' to='/login'>
                        ログイン
                    </Link>
                )}
            </div>
        </header>
    )
}

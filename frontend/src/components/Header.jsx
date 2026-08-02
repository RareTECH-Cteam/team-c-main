import { Link } from 'react-router-dom'
import './Header.css'

export function Header({ userName, isGuest = false }) {
    const headerName = isGuest ? 'ゲスト' : userName //ゲストならゲスト、ユーザログインならユーザ名を表示

    return (
        <header className='app-header'>
            <div className='app-header__inner'>
                <Link className='app-header__logo' to='/convert' aria-label='敬語変換画面'>
                    コトバディ
                </Link>
                {/* ユーザ名とログインボタンをグループ化 */}
                <div className='app-header__actions'>
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
            </div>
        </header>
    )
}

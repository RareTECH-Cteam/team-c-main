import { Link } from 'react-router-dom'
import './ConvertPage.css'

export function ConvertPage() {
    return (
        <div className='convert-page'>
            <main>
                <h1>敬語変換</h1>

                <p>敬語変換画面は現在準備中です。</p>

                <Link to='/'>トップ画面へ戻る</Link>
            </main>
        </div>
    )
}

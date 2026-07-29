import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ActionButton } from '../components/ActionButton.jsx'
import { guestLogin } from '../api/guestLogin.js'
import './TopPage.css'

const steps = ['文章を入力', '相手を選択', '敬語に変換']

function Title() {
    return (
        <p className='top-page__title' aria-label='kotobuddy'>
            コトバディ
        </p>
    )
}

function StepsCard() {
    return (
        <section className='steps-card' aria-labelledby='steps-title'>
            <h2 id="steps-title">かんたん３ステップ</h2>

            <ol className='steps-list'>
                {steps.map((step, index) => (
                    <li key={step}>
                        <span className='step-number' aria-hidden='true'>
                            {index + 1}
                        </span>

                        <span>{step}</span>
                    </li>
                ))}
            </ol>
        </section>
    )
}

export function TopPage() {
    const navigate = useNavigate()
    const [isLoading, setIsLoading] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')

    const handleGuestLogin = async () => {
        if (isLoading) {
            return
        }

        setIsLoading(true)
        setErrorMessage('')

        try {
            await guestLogin()
            navigate('/convert')
        } catch {
            setErrorMessage(
                'ゲストとしてログインできませんでした。',
            )
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <main className='top-page'>
            <div className='top-page__inner'>
                <header className='top-page__header'>
                    <Title />
                    <h1>相手に合わせて、ことばを整える。</h1>
                    <p className='top-page__description'>
                        入力した文章を、相手の立場に合わせた自然な敬語へ変換します。
                    </p>
                </header>

                <StepsCard />

                <div className='top-page__actions'>
                    <ActionButton
                        variant='secondary'
                        fullWidth
                        isLoading={isLoading}
                        loadingLabel='ログイン中...'
                        onClick={handleGuestLogin}
                    >
                        ゲストで試す
                    </ActionButton>

                    {errorMessage && (
                        <p className='top-page__error' role='alert'>
                            {errorMessage}
                        </p>
                    )}
                </div>

                <p className='top-page__memo'>
                    ゲストでも敬語変換とコピーを利用できます
                </p>
            </div>
        </main>
    )
}

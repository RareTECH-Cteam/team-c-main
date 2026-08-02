import { ActionLink } from '../components/ActionButton.jsx'
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
            <h2 id='steps-title'>かんたん３ステップ</h2>

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
                    <ActionLink
                        to='/convert'
                        variant='secondary'
                        fullWidth
                    >
                        ゲストで試す
                    </ActionLink>
                </div>

                <p className='top-page__memo'>
                    ゲストでも敬語変換とコピーを利用できます
                </p>
            </div>
        </main>
    )
}

import { useRef, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../components/Header.jsx'
import { createConversion } from '../api/conversion.js'
import { ActionButton, ActionLink } from '../components/ActionButton.jsx'
import './ConvertPage.css'

// 変換タイプの宣言
const conversionTypes = [
    {
        id: 'boss',
        label: '上司向け',
        guestAvailable: true,
    },
    {
        id: 'external',
        label: '外部向け',
        guestAvailable: false,
    },
    {
        id: 'colleague',
        label: '同僚向け',
        guestAvailable: false,
    },
    {
        id: 'subordinate',
        label: '部下向け',
        guestAvailable: false,
    },
]

function LoginModal({ onClose }) {
    const closeButtonRef = useRef(null)

    useEffect(() => {
        closeButtonRef.current?.focus()

        // Escキーでバックできるように設定
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                onClose()
            }
        }

        document.body.style.overflow = 'hidden'
        document.addEventListener('keydown', handleKeyDown)

        return () => {
            document.body.style.overflow = ''
            document.removeEventListener('keydown', handleKeyDown)
        }
    }, [onClose])

    return (
        <div
            className='login-modal'
            role='presentation'
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) {
                    onClose()
                }
            }}
        >
            <section
                className='login-modal__content'
                role='dialog'
                aria-modal='true'
                aria-labelledby='login-modal-title'
                aria-describedby='login-modal-description'
            >
                <h2 id='login-modal-title'>
                    ログインすると利用できます
                </h2>

                <p id='login-modal-description'>
                    外部向け・同僚向け・部下向けの変換は、ログイン後に利用できます。
                </p>

                <ActionLink
                    to='/login'
                    variant='primary'
                    fullWidth
                    className='login-modal__login'
                >
                    ログイン
                </ActionLink>

                <button
                    ref={closeButtonRef}
                    className='login-modal__close'
                    type='button'
                    onClick={onClose}
                >
                    閉じる
                </button>
            </section>
        </div>
    )
}

export function ConvertPage() {
    const isGuest = true
    const userName = ''

    const navigate = useNavigate()

    // ユーザの操作によって変動する値（変数）の初期値を設定
    const [text, setText] = useState('')
    const [selectedType, setSelectedType] = useState('boss')
    const [showLoginModal, setShowLoginModal] = useState(false)
    const [validationError, setValidationError] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [apiError, setApiError] = useState('')

    // 変換タイプ選択処理（ゲストが上司向け以外を選択したらログインモーダルを表示）
    const handleTypeChange = (conversionType) => {
        if (isGuest && !conversionType.guestAvailable) {
            setShowLoginModal(true)
            return
        }

        setSelectedType(conversionType.id)
    }

    // 入力文を変更する際の処理
    const handleTextChange = (event) => {
        setText(event.target.value)

        if (event.target.value.trim()) {
            setValidationError('')
        }
    }

    // 変換ボタンを押した際の処理
    const handleSubmit = async (event) => {
        event.preventDefault()

        const trimmedText = text.trim()

        // 空欄時のエラー
        if (!trimmedText) {
            setValidationError('文章を入力してください')
            setApiError('')
            return
        }

        // 二重クリックを防止
        if (isSubmitting) {
            return
        }

        // 二重クリック状態を精査した後にクリック状態にする
        setValidationError('')
        setIsSubmitting(true)

        // 変換API処理開始
        try {
            setApiError('')

            const resultId = await createConversion({
                text: trimmedText,
                conversionType: selectedType,
            })

            navigate('/result/' + encodeURIComponent(resultId)
            )
        } catch (error) {
            setApiError(
                error instanceof Error ? error.message : '変換に失敗しました'
            )
        } finally {
            // 成功失敗にかかわらず変換状態を無効化
            setIsSubmitting(false)
        }
    }

    return (
        <div className='convert-page'>
            {/* ヘッダーコンポーネント挿入 */}
            <Header
                userName={userName}
                isGuest={isGuest}
            />

            <main className='convert-page__main'>
                <h1>敬語変換</h1>

                <form onSubmit={handleSubmit} noValidate>
                    <section
                        className='convert-card convert-input-card'
                        aria-labelledby='input-title'
                    >
                        <label id='input-title' htmlFor='convert-text'>
                            変換前のテキスト
                        </label>
                        <textarea
                            id='convert-text'
                            className={
                                validationError ? 'convert-textarea convert-textarea--error' : 'convert-textarea'
                            }
                            value={text}
                            onChange={handleTextChange}
                            aria-invalid={Boolean(validationError)}
                            aria-describedby={
                                validationError ? 'convert-validation-error' : undefined
                            }
                        />

                        {validationError && (
                            <p
                                id='convert-validation-error'
                                className='convert-validation-error'
                                role='alert'
                            >
                                {validationError}
                            </p>
                        )}
                    </section>


                    <section
                        className='convert-card convert-type-card'
                        aria-labelledby='conversion-type-title'
                    >
                        <h2 id='conversion-type-title'>変換タイプ</h2>

                        <div className='conversion-types'>
                            {conversionTypes.map((conversionType) => {
                                const isLocked = isGuest && !conversionType.guestAvailable

                                const isSelected = selectedType === conversionType.id

                                return (
                                    <button
                                        key={conversionType.id}
                                        type='button'
                                        className={[
                                            'conversion-type',
                                            isSelected ? 'conversion-type--selected' : '',
                                            isLocked ? 'conversion-type--locked' : '',]

                                            .filter(Boolean)
                                            .join(' ')}
                                        aria-pressed={isSelected}
                                        aria-label={
                                            isLocked ? `${conversionType.label}。ログインが必要です` : conversionType.label
                                        }
                                        onClick={() =>
                                            handleTypeChange(conversionType)

                                        }
                                    >
                                        {isLocked && (
                                            <span
                                                className='lock-icon'
                                                aria-hidden='true'
                                            >
                                                <span className='lock-icon__shackle' />
                                                <span className='lock-icon__body' />
                                            </span>
                                        )}

                                        <span>{conversionType.label}</span>
                                    </button>
                                )
                            })}
                        </div>

                        {isGuest && (
                            <p className='convert-type-card__notice'>
                                ログインすると、すべての変換タイプを利用できます
                            </p>
                        )}
                    </section>

                    {apiError && (
                        <p className='convert-api-error' role='alert'>
                            {apiError}
                        </p>
                    )}

                    <ActionButton
                        type='submit'
                        className='convert-submit'
                        fullWidth
                        isLoading={isSubmitting}
                        loadingLabel='変換中...'
                    >
                        変換する
                    </ActionButton>
                </form>
            </main>

            {showLoginModal && (
                <LoginModal
                    onClose={() => setShowLoginModal(false)}
                />
            )}
        </div>
    )
}

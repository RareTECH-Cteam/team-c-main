import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Header } from '../components/Header.jsx'

export function ResultPage() {
    const { pk } = useParams()
    const [result, setResult] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [errorMessage, setErrorMessage] = useState('')

    useEffect(() => {
        const controller = new AbortController()

        async function fetchResult() {
            try {
                setIsLoading(true)
                setErrorMessage('')

                const response = await fetch(
                    `/api/results/${encodeURIComponent(pk)}/`,
                    {
                        credentials: 'same-origin',
                        signal: controller.signal,
                    },
                )

                const data = await response.json().catch(() => null)

                if (!response.ok) {
                    throw new Error(
                        data?.message ?? '変換結果の取得に失敗しました',
                    )
                }

                setResult(data)
            } catch (error) {
                if (error.name === 'AbortError') {
                    return
                }

                setErrorMessage(
                    error instanceof Error
                        ? error.message
                        : '変換結果の取得に失敗しました',
                )
            } finally {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            }
        }

        fetchResult()

        return () => {
            controller.abort()
        }
    }, [pk])

    return (
        <div>
            <Header isGuest />

            <main>
                <h1>変換結果</h1>

                {isLoading && (
                    <p role='status'>変換結果を読み込んでいます...</p>
                )}

                {!isLoading && errorMessage && (
                    <section>
                        <p role='alert'>{errorMessage}</p>
                        <Link to='/convert'>変換画面へ戻る</Link>
                    </section>
                )}

                {!isLoading && !errorMessage && result && (
                    <section aria-labelledby='result-title'>
                        <h2 id='result-title'>変換結果は現在準備中です</h2>

                        <p>
                            結果ID：
                            <strong>{result.result_id ?? pk}</strong>
                        </p>

                        <p>
                            敬語変換結果を表示する機能は、現在実装中です。
                        </p>

                        <Link to='/convert'>別の文章を変換する</Link>
                    </section>
                )}
            </main>
        </div>
    )
}
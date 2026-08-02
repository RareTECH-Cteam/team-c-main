function getCsrfToken() {
    const csrfCookie = document.cookie
        .split('; ')
        .find((cookie) => cookie.startsWith('csrftoken='))

    return csrfCookie ? decodeURIComponent(csrfCookie.split('=')[1]) : ''
}

export async function createConversion({
    text,
    conversionType,
}) {
    const response = await fetch('/api/convert/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
            text,
            conversionType,
        }),
    })

    const data = await response.json().catch(() => null)

    if (!response.ok) {
        throw new Error(
            data?.message ?? '変換に失敗しました',
        )
    }

    if (!Number.isInteger(data?.id)) {
        throw new Error('変換結果のIDを取得できませんでした')
    }

    return data.id
}
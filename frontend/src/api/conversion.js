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

    const data = await response.json()

    if (data.id == null) {
        throw new Error('結果IDがありません')
    }

    return data.id
}
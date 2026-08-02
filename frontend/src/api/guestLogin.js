//ゲストログインのロジックが一旦白紙になったためコメントアウト
// export async function guestLogin() {
//     const response = await fetch('/api/convert', {
//         method: 'POST',
//         headers: {
//             Accept: 'application/json',
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//             conversionType: 'guest_allowed_type',
//         }),
//     })

//     if (!response.ok) {
//         throw new Error('ゲストセッションの作成に失敗しました。')
//     }
// } 
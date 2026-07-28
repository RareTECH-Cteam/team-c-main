import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { guestLogin } from "../api/guestLogin.js";

export function TopPage() {
    const navigate = useNavigate()
    const [isLoading, setIsLoading] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')

    const handleGuestLogin = async () => {
        // 既にボタンが押されていたら処理を走らせない
        if (isLoading) {
            return
        }

        setIsLoading(true)
        setErrorMessage('')


        return (
            <button
                disabled={isLoading}
                onClick={handleGuestLogin}
            >
                {isLoading ? "通信中" : "ゲストで試す"}
            </button>
        )
    }
}

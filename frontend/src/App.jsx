import { Navigate, Route, Routes } from 'react-router-dom'
import { TopPage } from './pages/TopPage.jsx'
import { LoginPage } from './pages/LoginPage.jsx'
import { ConvertPage } from './pages/ConvertPage.jsx'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<TopPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/convert" element={<ConvertPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

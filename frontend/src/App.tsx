import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HeroSection from './components/HeroSection'
import ScanPage from './components/ScanPage'
import SolveGuidePage from './components/SolveGuidePage'
import MovesPage from './components/MovesPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HeroSection />} />
        <Route path="/moves" element={<MovesPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/solve-guide" element={<SolveGuidePage />} />
      </Routes>
    </BrowserRouter>
  )
}

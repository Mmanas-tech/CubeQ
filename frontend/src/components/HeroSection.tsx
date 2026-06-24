import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import StaggeredFade from "./StaggeredFade"

export default function HeroSection() {
  const navigate = useNavigate()

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#010101]">
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute inset-0 w-full h-full object-cover object-center"
      >
        <source src="/cube.mp4" type="video/mp4" />
      </video>

      <div className="absolute inset-0 bg-black/30" />

      <nav className="relative z-20 flex items-center justify-between px-6 py-5 md:px-12">
        <span className="text-white uppercase font-light tracking-[0.25em] md:tracking-[0.3em] text-sm md:text-base">
          CubeIQ
        </span>
      </nav>

      <div className="relative z-10 flex flex-col items-center justify-center text-center px-5 sm:px-8 pt-12 sm:pt-16 md:pt-24 h-full -mt-20">
        <div className="mb-6 sm:mb-8">
          <h1 className="font-garamond font-normal text-white leading-[1.08] tracking-tight">
            <span className="block text-4xl sm:text-6xl md:text-8xl lg:text-9xl">
              <StaggeredFade text="SCAN THE" />
            </span>
            <span className="block text-4xl sm:text-6xl md:text-8xl lg:text-9xl">
              <StaggeredFade text="INFINITE CUBE" />
            </span>
          </h1>
        </div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.6, ease: "easeOut" }}
          className="text-white/70 font-light leading-relaxed max-w-xs sm:max-w-md mb-8 sm:mb-10 text-sm sm:text-base lg:text-lg"
        >
          ...revealed by lens
          <br className="hidden sm:inline" />
          and curiosity.
        </motion.p>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 2.0, ease: "easeOut" }}
            onClick={() => navigate('/moves')}
            className="liquid-glass rounded-full px-7 py-3.5 sm:px-10 sm:py-4 text-white/90 uppercase tracking-[0.18em] sm:tracking-[0.2em] text-sm cursor-pointer"
          >
            Moves (Learn First)
          </motion.button>
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 2.2, ease: "easeOut" }}
            onClick={() => navigate('/scan')}
            className="rounded-full px-7 py-3.5 sm:px-10 sm:py-4 text-white/40 hover:text-white/70 uppercase tracking-[0.18em] sm:tracking-[0.2em] text-sm cursor-pointer transition-colors"
          >
            Scan & Solve
          </motion.button>
        </div>
      </div>
    </div>
  )
}

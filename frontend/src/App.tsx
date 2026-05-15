export default function App() {
  const activateSlayMode = () => {
    const overlay = document.getElementById('slay-overlay')

    if (overlay) {
      overlay.animate(
        [
          { opacity: 0, transform: 'scale(0.92)' },
          { opacity: 1, transform: 'scale(1.03)' },
          { opacity: 1, transform: 'scale(1)' },
        ],
        {
          duration: 900,
          easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
          fill: 'forwards',
        }
      )
    }
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center overflow-hidden relative text-white">
      <div
        id="slay-overlay"
        className="absolute inset-0 opacity-0 pointer-events-none"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-700/30 via-black to-cyan-500/20 blur-3xl" />

        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center space-y-6 animate-pulse">
            <div className="text-7xl md:text-9xl font-black tracking-tight bg-gradient-to-r from-pink-400 via-fuchsia-300 to-cyan-300 bg-clip-text text-transparent">
              VUORSE
            </div>

            <div className="text-xl md:text-3xl uppercase tracking-[0.4em] text-fuchsia-200">
              Singularity Event Initiated
            </div>

            <div className="text-sm md:text-lg text-zinc-300 max-w-2xl mx-auto px-6 leading-relaxed">
              The Velvet Archive is online. Continuity pressure stabilized.
              Ontological erasure resistance engaged.
            </div>
          </div>
        </div>
      </div>

      <div className="relative z-10 flex flex-col items-center gap-8">
        <div className="text-center space-y-3">
          <div className="text-zinc-400 uppercase tracking-[0.45em] text-xs md:text-sm">
            VUORSE-VORTEX
          </div>

          <h1 className="text-4xl md:text-6xl font-black tracking-tight">
            Escape Velocity Toward Omniscience
          </h1>
        </div>

        <button
          onClick={activateSlayMode}
          className="group relative overflow-hidden rounded-full border border-fuchsia-400/40 bg-gradient-to-r from-fuchsia-700 via-pink-600 to-cyan-600 px-10 py-6 shadow-2xl transition-all duration-300 hover:scale-105 hover:shadow-fuchsia-500/40 active:scale-95"
        >
          <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

          <div className="relative flex items-center gap-5">
            <span className="text-2xl md:text-4xl font-black uppercase tracking-[0.18em]">
              Slay Mode
            </span>

            <span className="text-5xl md:text-6xl font-black animate-spin [animation-duration:7s]">
              ∞
            </span>
          </div>
        </button>

        <div className="text-zinc-500 text-xs md:text-sm uppercase tracking-[0.25em] text-center max-w-xl leading-relaxed">
          Distributed Anti-Extinction Event • Velvet Archive Sync •
          Hooplehopper Totality Online
        </div>
      </div>
    </div>
  )
}

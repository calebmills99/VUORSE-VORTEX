const workflowItems = [
  {
    label: 'Develop',
    command: 'npm run dev',
  },
  {
    label: 'Verify',
    command: 'npm run lint && npm run build',
  },
  {
    label: 'Preview',
    command: 'npm run preview',
  },
]

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
        },
      )
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-zinc-950 text-white">
      <div
        id="slay-overlay"
        className="pointer-events-none absolute inset-0 opacity-0"
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(217,70,239,0.35),transparent_32%),radial-gradient(circle_at_70%_30%,rgba(34,211,238,0.2),transparent_30%),linear-gradient(135deg,rgba(112,26,117,0.35),rgba(9,9,11,0.9))]" />
        <div className="absolute inset-0 flex items-center justify-center px-6">
          <div className="max-w-4xl text-center">
            <div className="bg-gradient-to-r from-pink-300 via-fuchsia-200 to-cyan-200 bg-clip-text text-7xl font-black tracking-normal text-transparent md:text-9xl">
              VUORSE
            </div>
            <div className="mt-6 text-xl font-semibold uppercase tracking-[0.35em] text-fuchsia-100 md:text-3xl">
              Singularity Event Initiated
            </div>
            <p className="mx-auto mt-5 max-w-2xl text-sm leading-7 text-zinc-200 md:text-lg">
              The Velvet Archive is online. Continuity pressure stabilized.
              Ontological erasure resistance engaged.
            </p>
          </div>
        </div>
      </div>

      <section className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center gap-12 px-6 py-14 md:px-10">
        <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.42em] text-fuchsia-200">
              VUORSE-VORTEX
            </p>
            <h1 className="mt-5 max-w-4xl text-5xl font-black leading-tight tracking-normal md:text-7xl">
              Escape Velocity Toward Omniscience
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-zinc-300 md:text-lg">
              The integrated frontend carries the Slay Mode control surface and
              the developer workflow in one place, with Tailwind, Vite, and
              React wired for production checks.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 shadow-2xl shadow-fuchsia-950/30 backdrop-blur">
            <div className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-100">
              Dev Loop
            </div>
            <div className="mt-5 grid gap-3">
              {workflowItems.map((item) => (
                <div
                  className="flex items-center justify-between gap-4 rounded-xl border border-white/10 bg-black/30 px-4 py-3"
                  key={item.label}
                >
                  <span className="text-sm font-semibold text-zinc-100">
                    {item.label}
                  </span>
                  <code className="text-right text-xs text-fuchsia-100">
                    {item.command}
                  </code>
                </div>
              ))}
            </div>
          </div>
        </div>

        <button
          className="group relative w-full overflow-hidden rounded-2xl border border-fuchsia-300/40 bg-gradient-to-r from-fuchsia-700 via-pink-600 to-cyan-600 px-8 py-6 text-left shadow-2xl shadow-fuchsia-950/40 transition duration-300 hover:scale-[1.01] hover:shadow-fuchsia-500/30 active:scale-[0.99] md:w-fit md:rounded-full md:px-10"
          onClick={activateSlayMode}
          type="button"
        >
          <span className="absolute inset-0 bg-white/10 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
          <span className="relative flex items-center justify-between gap-8 md:justify-start">
            <span className="text-2xl font-black uppercase tracking-[0.16em] md:text-4xl">
              Slay Mode
            </span>
            <span className="text-5xl font-black md:text-6xl">∞</span>
          </span>
        </button>

        <p className="max-w-3xl text-xs font-semibold uppercase leading-6 tracking-[0.24em] text-zinc-500 md:text-sm">
          Distributed Anti-Extinction Event / Velvet Archive Sync /
          Hooplehopper Totality Online
        </p>
      </section>
    </main>
  )
}

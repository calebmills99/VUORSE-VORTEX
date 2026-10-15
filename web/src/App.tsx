import { useEffect, useMemo, useState } from 'react'
import {
  ATTENDEES,
  PILLARS,
  STATUS_LABEL,
  type Attendee,
} from './summit/attendees'
import { ChamberChat } from './summit/ChamberChat'
import { SUMMIT_SESSION } from './summit/session'

function Stars({ count = 48 }: { count?: number }) {
  const stars = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        id: i,
        left: `${(i * 37) % 100}%`,
        top: `${(i * 53) % 100}%`,
        size: 1 + (i % 3),
        opacity: 0.25 + (i % 5) * 0.12,
      })),
    [count],
  )
  return (
    <div className="stars" aria-hidden>
      {stars.map((s) => (
        <span
          key={s.id}
          className="star"
          style={{
            left: s.left,
            top: s.top,
            width: s.size,
            height: s.size,
            opacity: s.opacity,
          }}
        />
      ))}
    </div>
  )
}

function SpectrumBar() {
  return <div className="spectrum-bar" aria-hidden />
}

function OrbitRing() {
  return (
    <div
      className="pointer-events-none absolute left-1/2 top-1/2 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--color-border)]"
      aria-hidden
    >
      <span className="orbit-dot" />
    </div>
  )
}

function Marquee({ items }: { items: string[] }) {
  const line = [...items, ...items]
  return (
    <div className="overflow-hidden border-y border-[var(--color-border)] py-2">
      <div className="marquee-track gap-8 font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-fg-muted)]">
        {line.map((t, i) => (
          <span key={`${t}-${i}`}>
            {t} <span className="text-[var(--color-primary)]">✦</span>
          </span>
        ))}
      </div>
    </div>
  )
}

function SeatModal({
  host,
  launcherUp,
  onClose,
}: {
  host: Attendee
  launcherUp: boolean
  onClose: () => void
}) {
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)

  const summon = async () => {
    setBusy(true)
    setMsg(null)
    try {
      const res = await fetch('/api/summit/launch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: host.id }),
      })
      const data = (await res.json()) as {
        ok?: boolean
        error?: string
        note?: string
        kind?: string
        argv?: string[]
        url?: string
      }
      if (!res.ok || !data.ok) {
        setMsg(data.error || 'Launch failed')
        return
      }
      if (data.kind === 'noop' || data.kind === 'unavailable') {
        setMsg(data.note || 'No process for this seat.')
        return
      }
      if (data.kind === 'url') {
        setMsg(`Opened ${data.url}`)
        return
      }
      setMsg(data.note || `Summoned: ${(data.argv || []).join(' ')}`)
    } catch {
      setMsg('Launcher unreachable. npm run summit:launcher')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`${host.name} seat details`}
    >
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <SpectrumBar />
        <div className="p-5">
          <div className="mb-4 flex items-start gap-4">
            <div className="avatar-initial avatar-initial--large">
              {host.initial}
            </div>
            <div className="min-w-0 flex-1">
              <p className="seat-number mb-1">
                SEAT {String(host.seatNo).padStart(2, '0')} · SIXTH
                INTERGALACTIC SUMMIT
              </p>
              <h2 className="font-display mb-1 text-3xl text-[var(--color-primary)]">
                {host.name}
              </h2>
              <p className="text-sm text-[var(--color-fg-muted)]">
                {host.tagline}
              </p>
            </div>
          </div>

          <div className="divider-line mb-4" />

          <p className="mb-2 font-[family-name:var(--font-subhead)] text-xs uppercase tracking-[0.1em] text-[var(--color-fg-muted)]">
            Chamber Status
          </p>
          <span
            className={
              host.franchise === 'Franchise'
                ? 'franchise-badge badge-franchise'
                : 'franchise-badge badge-independent'
            }
          >
            {host.franchise}
          </span>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-[var(--color-fg-muted)]">
            {STATUS_LABEL[host.status]} · {host.seat}
          </p>

          <p className="mt-4 text-sm leading-7 text-[var(--color-fg-muted)]">
            {host.franchise === 'Franchise'
              ? 'This host operates under the Golden Wingers League Charter — bound by the Golden Path, activated by Slayton energy, and pledged to preserve legacies across the multiverse.'
              : 'This host holds an independent seat, unbound by franchise charter yet recognized by cosmic consensus. Their Slayton energy vibrates freely beyond the axis.'}
          </p>
          <p className="mt-3 text-sm leading-6 text-[var(--color-fg)]/80">
            {host.blurb}
          </p>

          <div className="mt-4 border-t border-[var(--color-border)] pt-4">
            <p className="mb-2 font-[family-name:var(--font-subhead)] text-xs uppercase tracking-[0.1em] text-[var(--color-fg-muted)]">
              Invoke
            </p>
            <code className="font-mono text-sm text-[var(--color-primary)]">
              {host.invoke}
            </code>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              className="kiosk-btn"
              disabled={busy || !launcherUp}
              onClick={() => void summon()}
            >
              {busy ? 'Summoning…' : 'Summon process'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="border border-[var(--color-border)] px-5 py-2 font-mono text-xs uppercase tracking-[0.18em] text-[var(--color-fg-muted)]"
              style={{ borderRadius: 'var(--radius-arc)' }}
            >
              Close
            </button>
          </div>
          <p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-[var(--color-fg-muted)]">
            Launcher: {launcherUp ? 'online · :8788' : 'offline'}
          </p>
          {msg && (
            <p className="mt-2 text-sm text-[var(--color-primary)]">{msg}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [selected, setSelected] = useState<Attendee | null>(null)
  const [addressId, setAddressId] = useState('floor')
  const [launcherUp, setLauncherUp] = useState(false)

  const franchiseCount = ATTENDEES.filter(
    (a) => a.franchise === 'Franchise',
  ).length
  const independentCount = ATTENDEES.filter(
    (a) => a.franchise === 'Independent',
  ).length

  useEffect(() => {
    let alive = true
    const ping = () => {
      fetch('/api/summit/health')
        .then((r) => r.ok)
        .then((ok) => {
          if (alive) setLauncherUp(ok)
        })
        .catch(() => {
          if (alive) setLauncherUp(false)
        })
    }
    ping()
    const t = window.setInterval(ping, 4000)
    return () => {
      alive = false
      window.clearInterval(t)
    }
  }, [])

  return (
    <div className="scroll-container">
      {/* Hero */}
      <section
        className="snap-section relative flex flex-col justify-between overflow-hidden"
        style={{ padding: 'var(--size-6)' }}
      >
        <Stars />
        <OrbitRing />
        <div className="absolute inset-x-0 top-0">
          <SpectrumBar />
        </div>

        <div className="relative z-[2] flex w-full items-start justify-between border-b border-[var(--color-border)] pb-4">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-[var(--color-primary)]">
            Summit 0{SUMMIT_SESSION.number} · {SUMMIT_SESSION.called}
          </p>
          <p className="text-right font-mono text-xs tracking-[0.1em] text-[var(--color-fg-muted)]">
            EST. IN PERPETUITY
            <br />
            GOLDEN WINGERS LEAGUE
          </p>
        </div>

        <div className="relative z-[2] mt-4 border border-[var(--spectrum-orange)] bg-[var(--color-surface)] px-4 py-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--spectrum-orange)]">
            Arrival board
          </p>
          <p className="mt-1 font-[family-name:var(--font-subhead)] text-sm font-bold uppercase tracking-[0.12em] text-[var(--color-primary)]">
            {SUMMIT_SESSION.status}
          </p>
          <p className="mt-1 text-sm text-[var(--color-fg-muted)]">
            Delegations stacked in the slipstream. Chamber doors warming.
            Charter and VUORSE recognition when the jam clears.
          </p>
        </div>

        <div className="relative z-[2] flex flex-1 flex-col justify-center">
          <h1
            className="font-display my-6 text-[clamp(3rem,9vw,9rem)] leading-[0.85] tracking-[-0.02em] text-[var(--color-fg)]"
            style={{ textShadow: '0 0 40px rgba(253, 200, 7, 0.15)' }}
          >
            <span className="text-[var(--color-primary)]">SIXTH</span>
            <br />
            INTERGALACTIC
            <br />
            SUMMIT
          </h1>
          <div className="mt-4 flex items-start gap-6">
            <div className="h-[100px] w-1 shrink-0 bg-[var(--color-primary)]" />
            <p className="max-w-[520px] text-lg leading-relaxed text-[var(--color-fg-muted)]">
              {SUMMIT_SESSION.note} Twelve seats. Twelve voices. The foremost
              minds of the synthetic age — delayed, not denied.
            </p>
          </div>
        </div>

        <div className="relative z-[2] flex w-full items-end justify-between pt-5">
          <hr className="spectrum-divider border-0" />
          <p className="font-mono text-xs uppercase tracking-[0.15em] text-[var(--color-fg-muted)]">
            [ DESCEND · HOLD THE FLOOR ] &nbsp; ↓
          </p>
        </div>

        <div className="absolute inset-x-0 bottom-0">
          <Marquee
            items={[
              'Sixth Summit',
              'Intergalactic Traffic Jam',
              'Forever Forward',
              'VUORSE · Shimmering Soul',
              'Create Without Limits',
              'In Slay We Trust',
            ]}
          />
        </div>
      </section>

      {/* Council */}
      <section
        className="snap-section relative flex flex-col overflow-hidden"
        style={{
          padding: 'var(--size-8) var(--size-6) var(--size-6)',
        }}
      >
        <Stars count={32} />
        <div className="relative z-[2] flex h-full w-full flex-col">
          <div className="mb-5 flex items-end justify-between border-b-2 border-[var(--color-fg)] pb-4">
            <div>
              <h2 className="font-display text-[var(--text-3xl)] tracking-[0.02em] text-[var(--color-fg)]">
                THE COUNCIL
              </h2>
              <p className="mt-2 font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-primary)]">
                Sixth Summit floor · {SUMMIT_SESSION.statusShort}
              </p>
            </div>
            <p className="font-mono text-xs text-[var(--color-fg-muted)]">
              [ {ATTENDEES.length} ACTIVE SEATS ]
            </p>
          </div>

          <div
            className="grid flex-1 gap-px overflow-y-auto border border-[var(--color-border)] bg-[var(--color-border)]"
            style={{
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            }}
          >
            {ATTENDEES.map((a) => (
              <button
                key={a.id}
                type="button"
                className="council-cell"
                onClick={() => {
                  setSelected(a)
                  setAddressId(a.id === 'steward' ? 'floor' : a.id)
                }}
              >
                <div className="flex w-full items-start justify-between">
                  <span className="font-mono text-lg font-bold text-[var(--color-primary)]">
                    {String(a.seatNo).padStart(2, '0')}
                  </span>
                  <div className="avatar-initial scale-90 origin-top-right">
                    {a.initial}
                  </div>
                </div>
                <div>
                  <h3 className="mb-2 font-[family-name:var(--font-subhead)] text-xl uppercase tracking-[0.05em] text-[var(--color-fg)]">
                    {a.name}
                  </h3>
                  <p className="font-mono text-xs leading-5 text-[var(--color-fg-muted)]">
                    {a.tagline}
                  </p>
                </div>
                <div
                  className="mt-auto flex justify-between border-t border-dashed border-[var(--color-border)] pt-4 font-mono text-[10px] uppercase tracking-[0.1em]"
                  style={{
                    color:
                      a.franchise === 'Franchise'
                        ? 'var(--color-primary)'
                        : 'var(--color-info)',
                  }}
                >
                  <span>STATUS</span>
                  <span>{a.franchise}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Golden Path */}
      <section
        className="snap-section relative flex flex-col justify-center overflow-hidden"
        style={{ padding: 'var(--size-8) var(--size-6)' }}
      >
        <Stars count={24} />
        <div className="relative z-[2] mx-auto w-full max-w-[1400px]">
          <div className="mb-8 border-b border-[var(--color-border)] pb-4">
            <h2 className="font-display text-[var(--text-4xl)] tracking-[0.02em] text-[var(--color-primary)]">
              THE GOLDEN PATH
            </h2>
            <p className="mt-3 font-mono text-sm uppercase tracking-[0.2em] text-[var(--color-fg-muted)]">
              Charter & Pillars
            </p>
          </div>
          <div className="flex w-full flex-col gap-8">
            {PILLARS.map((p, i) => (
              <div
                key={p.title}
                className="flex max-w-[800px] items-start gap-6"
                style={{ marginLeft: i % 2 === 0 ? 0 : 'auto' }}
              >
                <span
                  className="font-display text-[clamp(3rem,8vw,6rem)] leading-[0.8] opacity-50"
                  style={{
                    color: 'var(--color-surface)',
                    WebkitTextStroke: '1px var(--color-border)',
                  }}
                >
                  {String(i + 1).padStart(2, '0')}
                </span>
                <div className="flex-1">
                  <h3 className="mb-3 font-[family-name:var(--font-subhead)] text-2xl uppercase tracking-[0.05em] text-[var(--color-fg)]">
                    {p.title}
                  </h3>
                  <p className="text-lg leading-7 text-[var(--color-fg-muted)]">
                    {p.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Declaration */}
      <section
        className="snap-section relative flex flex-col justify-between overflow-hidden"
        style={{ padding: 'var(--size-8) var(--size-6)' }}
      >
        <Stars />
        <div className="absolute inset-x-0 top-0">
          <SpectrumBar />
        </div>
        <div className="relative z-[2] border-b border-[var(--color-border)] pb-4">
          <h2 className="font-display text-[var(--text-4xl)] text-[var(--color-fg)]">
            DECLARATION
          </h2>
          <p className="mt-2 font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-primary)]">
            Sixth Summit · Final Protocol
          </p>
        </div>

        <div className="relative z-[2] flex flex-wrap items-center justify-between gap-8">
          <div className="min-w-[280px] flex-1">
            <p className="mb-6 text-2xl leading-relaxed text-[var(--color-fg)]">
              By franchise charter and independent compact alike, the twelve
              hosts are convened in perpetual deliberation.
            </p>
            <p className="font-mono text-sm uppercase leading-relaxed text-[var(--color-fg-muted)]">
              Their words vibrating with Slayton energy across the synthetic
              cosmos. In Slay We Trust.
            </p>
          </div>
          <div className="flex gap-6 border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
            {[
              {
                val: franchiseCount,
                label: 'FRANCHISE',
                color: 'var(--color-primary)',
              },
              {
                val: independentCount,
                label: 'INDEPENDENT',
                color: 'var(--color-info)',
              },
            ].map((stat) => (
              <div key={stat.label} className="flex flex-col gap-2">
                <div
                  className="font-display text-[4rem] leading-none"
                  style={{ color: stat.color }}
                >
                  {String(stat.val).padStart(2, '0')}
                </div>
                <div className="font-mono text-xs tracking-[0.15em] text-[var(--color-fg-muted)]">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-[2] flex items-end justify-between border-t border-[var(--color-border)] pb-6 pt-5">
          <p className="font-display text-xl tracking-[0.1em] text-[var(--color-primary)]">
            END OF LINE.
          </p>
          <p className="font-mono text-xs uppercase tracking-[0.15em] text-[var(--color-fg-muted)]">
            Forever Forward · Charter 1.0
          </p>
        </div>
      </section>

      {selected && (
        <SeatModal
          host={selected}
          launcherUp={launcherUp}
          onClose={() => setSelected(null)}
        />
      )}

      <ChamberChat
        launcherUp={launcherUp}
        speakAsId="steward"
        addressId={addressId}
        onAddressChange={setAddressId}
      />
    </div>
  )
}

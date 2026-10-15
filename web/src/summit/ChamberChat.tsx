import { useEffect, useRef, useState } from 'react'
import { ATTENDEES } from './attendees'

export type ChatMessage = {
  id: string
  at: string
  from: string
  fromName: string
  text: string
  kind: 'user' | 'seat' | 'system'
}

type Props = {
  launcherUp: boolean
  speakAsId: string
  addressId: string
  onAddressChange: (id: string) => void
}

export function ChamberChat({
  launcherUp,
  speakAsId,
  addressId,
  onAddressChange,
}: Props) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const sinceRef = useRef(0)

  useEffect(() => {
    if (!launcherUp || !open) return
    let alive = true
    const pull = async () => {
      try {
        const res = await fetch(`/api/summit/chat?since=${sinceRef.current}`)
        if (!res.ok) return
        const data = (await res.json()) as {
          messages: ChatMessage[]
          next: number
        }
        if (!alive) return
        if (data.messages?.length) {
          setMessages((prev) => {
            const seen = new Set(prev.map((m) => m.id))
            const add = data.messages.filter((m) => !seen.has(m.id))
            return add.length ? [...prev, ...add] : prev
          })
        }
        sinceRef.current = data.next ?? sinceRef.current
      } catch {
        /* blip */
      }
    }
    pull()
    const t = window.setInterval(pull, 1200)
    return () => {
      alive = false
      window.clearInterval(t)
    }
  }, [launcherUp, open])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  const send = async () => {
    const text = draft.trim()
    if (!text || !launcherUp || sending) return
    setSending(true)
    setErr(null)
    setDraft('')
    try {
      const res = await fetch('/api/summit/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: speakAsId,
          address: addressId === 'floor' ? null : addressId,
          text,
        }),
      })
      const data = (await res.json()) as {
        ok?: boolean
        error?: string
        messages?: ChatMessage[]
      }
      if (!res.ok || !data.ok) {
        setErr(data.error || 'Floor rejected that.')
        setDraft(text)
        return
      }
      if (data.messages?.length) {
        setMessages((prev) => {
          const seen = new Set(prev.map((m) => m.id))
          const add = data.messages!.filter((m) => !seen.has(m.id))
          return [...prev, ...add]
        })
        const last = data.messages[data.messages.length - 1]
        const n = Number(last?.id?.replace(/\D/g, '') || 0)
        if (n >= sinceRef.current) sinceRef.current = n
      }
    } catch {
      setErr('Launcher unreachable.')
      setDraft(text)
    } finally {
      setSending(false)
    }
  }

  if (!open) {
    return (
      <button
        type="button"
        className="kiosk-btn fixed bottom-6 right-6 z-50"
        onClick={() => setOpen(true)}
      >
        Chamber floor
      </button>
    )
  }

  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex w-[min(400px,90vw)] flex-col overflow-hidden border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[0_8px_32px_rgba(0,0,0,0.6)]"
      style={{ borderRadius: 'var(--radius-md)' }}
    >
      <header className="flex flex-wrap items-end justify-between gap-3 border-b border-[var(--color-border)] p-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--color-primary)]">
            Chamber floor
          </p>
          <h2 className="font-[family-name:var(--font-subhead)] text-lg font-bold uppercase tracking-wide text-[var(--color-fg)]">
            Summit chat
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex flex-col gap-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-fg-muted)]">
            Address
            <select
              value={addressId}
              onChange={(e) => onAddressChange(e.target.value)}
              className="border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1.5 text-xs normal-case tracking-normal text-[var(--color-fg)]"
            >
              <option value="floor">Open floor</option>
              {ATTENDEES.filter((a) => a.id !== 'steward').map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            aria-label="Close chat"
            onClick={() => setOpen(false)}
            className="font-mono text-sm text-[var(--color-fg-muted)] hover:text-[var(--color-primary)]"
          >
            ✕
          </button>
        </div>
      </header>

      <div className="flex h-[300px] flex-col gap-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <p className="text-sm italic text-[var(--color-fg-muted)]">
            {launcherUp
              ? 'Floor is quiet. Address a seat and they answer if the model is live.'
              : 'Launcher offline — npm run summit:launcher'}
          </p>
        )}
        {messages.map((m) => (
          <article
            key={m.id}
            className={
              m.kind === 'system'
                ? 'font-mono text-xs italic text-[var(--color-fg-muted)]'
                : 'border-l-2 border-[var(--color-primary)] pl-3'
            }
          >
            {m.kind !== 'system' && (
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-primary)]">
                {m.fromName}
              </p>
            )}
            <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-[var(--color-fg)]/90">
              {m.text}
            </p>
          </article>
        ))}
        <div ref={bottomRef} />
      </div>

      <form
        className="flex gap-2 border-t border-[var(--color-border)] p-4"
        onSubmit={(e) => {
          e.preventDefault()
          void send()
        }}
      >
        <textarea
          rows={2}
          value={draft}
          disabled={!launcherUp || sending}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void send()
            }
          }}
          placeholder="Speak as Steward…"
          className="flex-1 resize-none border-2 border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm text-[var(--color-fg)] placeholder:text-[var(--color-fg-muted)] focus:border-[var(--color-info)] focus:outline-none disabled:opacity-40"
          style={{ borderRadius: 'var(--radius-md)' }}
        />
        <button
          type="submit"
          disabled={!launcherUp || sending || !draft.trim()}
          className="kiosk-btn self-end"
        >
          {sending ? '…' : 'Send'}
        </button>
      </form>
      {err && (
        <p className="px-4 pb-3 font-mono text-xs text-[var(--spectrum-red)]">
          {err}
        </p>
      )}
    </div>
  )
}

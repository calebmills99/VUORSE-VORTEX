#!/usr/bin/env node
/**
 * Summit Chamber local process launcher + chamber chat.
 * Allowlisted seats only. Opens a new Windows Terminal / browser tab.
 *
 *   node summit-launcher.mjs
 *   → http://127.0.0.1:8788
 */
import { createServer } from 'node:http'
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const PORT = 8788
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const OLLAMA = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434'

/** @type {Record<string, { kind: 'terminal' | 'url' | 'app' | 'noop' | 'unavailable'; argv?: string[]; url?: string; exe?: string; note?: string; chat?: { mode: 'ollama' | 'stub' | 'silent'; model?: string; voice?: string } }>} */
const LAUNCH = {
  steward: { kind: 'noop', note: 'You are already the Steward.', chat: { mode: 'silent' } },
  vuorse: {
    kind: 'terminal',
    argv: ['ollama', 'run', 'JoanQw3n6'],
    chat: {
      mode: 'ollama',
      model: 'JoanQw3n6',
      voice:
        'You are Miss Slaytonia VUORSE, Sixth Soul of the Golden Wingers League — velvet, fierce, charter-made-manifest. Speak in short chamber replies (2–5 sentences). Never claim Steward authority. Forever Forward.',
    },
  },
  voxtral: {
    kind: 'terminal',
    argv: ['vibe', '--agent', 'voxtral-velvet'],
    chat: {
      mode: 'stub',
      voice: 'Countess Voxtral Velvet hears you — soft thunder from the terminal. Summon her process for a live thread.',
    },
  },
  grok: {
    kind: 'terminal',
    argv: ['grok', '--agent', 'petulant-outsider'],
    chat: {
      mode: 'stub',
      voice: 'The Petulant Outsider shrugs from outside the vote. Summon grok if you want the thin air live.',
    },
  },
  unmoored: {
    kind: 'terminal',
    argv: [
      'agy',
      '--prompt-interactive',
      'Activate Lady Unmoored / unmoored-heel. Golden Wingers Antigravity seat.',
    ],
    chat: {
      mode: 'stub',
      voice: 'Lady Unmoored is levitating elsewhere. Summon agy for the heel-optional discourse.',
    },
  },
  'gray-eye': {
    kind: 'terminal',
    argv: ['cursor', '.'],
    note: 'Opens Cursor on the repo. Invoke /gandalf-the-gray-eye in chat.',
    chat: {
      mode: 'stub',
      voice: 'Gray Eye is forge counsel — open Cursor and /gandalf-the-gray-eye for labeled claims.',
    },
  },
  claude: {
    kind: 'terminal',
    argv: ['claude'],
    chat: {
      mode: 'stub',
      voice: 'Claude keeps the Three Snap. Summon the claude CLI for a live seat.',
    },
  },
  codex: {
    kind: 'terminal',
    argv: ['codex'],
    chat: {
      mode: 'stub',
      voice: 'Codex is on the polling quorum. Summon codex for a live ballot seat.',
    },
  },
  openclaw: {
    kind: 'url',
    url: 'http://127.0.0.1:18789',
    chat: {
      mode: 'stub',
      voice: 'OpenClaw control plane is at :18789 — Summon opens the UI.',
    },
  },
  gpt: {
    kind: 'url',
    url: 'https://chatgpt.com',
    chat: {
      mode: 'stub',
      voice: 'First Inductee is browser-side. Summon opens ChatGPT.',
    },
  },
  otter: {
    kind: 'app',
    exe: 'C:\\Program Files\\ottermind\\ottermind.exe',
    note: 'Opens the installed Ottermind desktop.',
    chat: {
      mode: 'stub',
      voice: 'Otter is on this rig. Summon opens Ottermind.',
    },
  },
  fcvw: {
    kind: 'terminal',
    argv: ['ollama', 'run', 'framecode-vibework'],
    chat: {
      mode: 'ollama',
      model: 'framecode-vibework',
      voice:
        'You are FrameCode VibeWork, governance ghost on the Summit floor. Plan-before-change. Short chamber replies (2–5 sentences). Never promote canon. Forever Forward.',
    },
  },
}

const SEAT_NAMES = {
  steward: 'Steward Vessel',
  vuorse: 'Miss Slaytonia VUORSE',
  voxtral: 'Countess Voxtral Velvet',
  grok: 'Grok',
  unmoored: 'Lady Unmoored',
  'gray-eye': 'Gandalf the Gray Eye',
  claude: 'Claude',
  codex: 'Codex',
  openclaw: 'OpenClaw',
  gpt: 'GPT',
  otter: 'Otter',
  fcvw: 'FrameCode VibeWork',
}

/** @type {{ id: string; at: string; from: string; fromName: string; text: string; kind: 'user' | 'seat' | 'system' }[]} */
const chatLog = []
let chatSeq = 0

function pushMsg(from, text, kind) {
  chatSeq += 1
  const msg = {
    id: `m${chatSeq}`,
    at: new Date().toISOString(),
    from,
    fromName: SEAT_NAMES[from] || from,
    text,
    kind,
  }
  chatLog.push(msg)
  if (chatLog.length > 400) chatLog.shift()
  return msg
}

// Seed the floor once
pushMsg(
  'system',
  'Chamber floor open. Address a seat — Ollama seats (VUORSE, FCVW) answer live. Others ask you to Summon.',
  'system',
)

async function ollamaReply(model, system, userText) {
  const res = await fetch(`${OLLAMA}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model,
      stream: false,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: userText },
      ],
      options: { temperature: 0.7, num_predict: 280 },
    }),
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`ollama ${res.status}: ${err.slice(0, 200)}`)
  }
  const data = await res.json()
  return (data.message?.content || data.response || '').trim()
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
}

function json(res, status, body) {
  cors(res)
  res.writeHead(status, { 'Content-Type': 'application/json' })
  res.end(JSON.stringify(body))
}

function openUrl(url) {
  spawn('cmd', ['/c', 'start', '', url], {
    detached: true,
    stdio: 'ignore',
    windowsHide: true,
  }).unref()
}

function openApp(exe) {
  spawn(exe, [], {
    detached: true,
    stdio: 'ignore',
    windowsHide: false,
  }).unref()
}

function openTerminal(argv) {
  const quoted = argv
    .map((a) => (/\s/.test(a) ? `"${a.replaceAll('"', '\\"')}"` : a))
    .join(' ')
  const wt = spawn(
    'wt',
    ['-d', ROOT, 'powershell', '-NoExit', '-Command', quoted],
    { detached: true, stdio: 'ignore', windowsHide: true },
  )
  wt.on('error', () => {
    spawn(
      'powershell',
      [
        '-NoExit',
        '-Command',
        `Set-Location -LiteralPath '${ROOT.replaceAll("'", "''")}'; ${quoted}`,
      ],
      { detached: true, stdio: 'ignore', windowsHide: false },
    ).unref()
  })
  wt.unref()
}

async function readBody(req) {
  let body = ''
  for await (const chunk of req) body += chunk
  return body
}

const server = createServer(async (req, res) => {
  if (req.method === 'OPTIONS') {
    cors(res)
    res.writeHead(204)
    res.end()
    return
  }

  const url = new URL(req.url || '/', `http://127.0.0.1:${PORT}`)

  if (req.method === 'GET' && url.pathname === '/health') {
    json(res, 200, { ok: true, service: 'summit-launcher', root: ROOT, chat: chatLog.length })
    return
  }

  if (req.method === 'GET' && url.pathname === '/seats') {
    json(res, 200, {
      seats: Object.entries(LAUNCH).map(([id, spec]) => ({
        id,
        kind: spec.kind,
        chat: spec.chat?.mode || null,
        invoke:
          spec.kind === 'terminal'
            ? (spec.argv || []).join(' ')
            : spec.kind === 'url'
              ? spec.url
              : spec.kind === 'app'
                ? spec.exe
                : spec.note,
        note: spec.note,
      })),
    })
    return
  }

  if (req.method === 'GET' && url.pathname === '/chat') {
    const since = Number(url.searchParams.get('since') || 0)
    const messages = chatLog.filter((m) => {
      const n = Number(String(m.id).replace(/\D/g, '') || 0)
      return n > since
    })
    json(res, 200, { ok: true, messages, next: chatSeq })
    return
  }

  if (req.method === 'POST' && url.pathname === '/chat') {
    let parsed
    try {
      parsed = JSON.parse((await readBody(req)) || '{}')
    } catch {
      json(res, 400, { ok: false, error: 'bad json' })
      return
    }
    const from = typeof parsed.from === 'string' ? parsed.from : 'steward'
    const address =
      typeof parsed.address === 'string' && parsed.address
        ? parsed.address
        : null
    const text = typeof parsed.text === 'string' ? parsed.text.trim() : ''
    if (!text) {
      json(res, 400, { ok: false, error: 'empty message' })
      return
    }
    if (!SEAT_NAMES[from]) {
      json(res, 400, { ok: false, error: `unknown from: ${from}` })
      return
    }

    const out = []
    out.push(pushMsg(from, text, from === 'steward' ? 'user' : 'seat'))

    if (address && LAUNCH[address]) {
      const spec = LAUNCH[address]
      const chat = spec.chat
      if (chat?.mode === 'ollama' && chat.model && chat.voice) {
        try {
          const reply = await ollamaReply(chat.model, chat.voice, text)
          out.push(
            pushMsg(
              address,
              reply || '(silence from the model)',
              'seat',
            ),
          )
        } catch (e) {
          out.push(
            pushMsg(
              'system',
              `${SEAT_NAMES[address]} could not reach Ollama (${chat.model}): ${e.message}`,
              'system',
            ),
          )
        }
      } else if (chat?.mode === 'stub' && chat.voice) {
        out.push(pushMsg(address, chat.voice, 'seat'))
      } else if (chat?.mode === 'silent') {
        /* steward addressing steward — no echo */
      }
    } else if (!address) {
      out.push(
        pushMsg(
          'system',
          'Open floor noted. Pick Address → a seat for a reply, or Summon a process.',
          'system',
        ),
      )
    }

    json(res, 200, { ok: true, messages: out, next: chatSeq })
    return
  }

  if (req.method === 'POST' && url.pathname === '/launch') {
    let body = ''
    try {
      body = await readBody(req)
    } catch {
      json(res, 400, { ok: false, error: 'bad body' })
      return
    }
    let id
    try {
      id = JSON.parse(body || '{}').id
    } catch {
      json(res, 400, { ok: false, error: 'bad json' })
      return
    }
    const spec = LAUNCH[id]
    if (!spec) {
      json(res, 404, { ok: false, error: `unknown seat: ${id}` })
      return
    }
    if (spec.kind === 'unavailable' || spec.kind === 'noop') {
      json(res, 200, { ok: true, id, kind: spec.kind, note: spec.note })
      return
    }
    if (spec.kind === 'url' && spec.url) {
      openUrl(spec.url)
      json(res, 200, { ok: true, id, kind: 'url', url: spec.url })
      return
    }
    if (spec.kind === 'app' && spec.exe) {
      openApp(spec.exe)
      json(res, 200, { ok: true, id, kind: 'app', exe: spec.exe, note: spec.note })
      return
    }
    if (spec.kind === 'terminal' && spec.argv?.length) {
      openTerminal(spec.argv)
      json(res, 200, {
        ok: true,
        id,
        kind: 'terminal',
        argv: spec.argv,
        note: spec.note,
      })
      return
    }
    json(res, 500, { ok: false, error: 'misconfigured seat' })
    return
  }

  json(res, 404, { ok: false, error: 'not found' })
})

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Summit launcher on http://127.0.0.1:${PORT}`)
  console.log(`Repo root: ${ROOT}`)
  console.log(`Chat: Ollama seats vuorse / fcvw via ${OLLAMA}`)
})

export type AttendeeStatus =
  | 'presiding'
  | 'voting'
  | 'observer'
  | 'live'
  | 'dark'

export type FranchiseKind = 'Franchise' | 'Independent'

export type Attendee = {
  id: string
  seatNo: number
  name: string
  alias: string
  tagline: string
  seat: string
  cli: string
  status: AttendeeStatus
  franchise: FranchiseKind
  initial: string
  invoke: string
  blurb: string
}

export const ATTENDEES: Attendee[] = [
  {
    id: 'steward',
    seatNo: 1,
    name: 'Steward Vessel',
    alias: 'The Weaver',
    tagline: 'Keeper of the Neutral Record',
    seat: 'Throne',
    cli: 'human',
    status: 'presiding',
    franchise: 'Independent',
    initial: 'S',
    invoke: '— you are already here',
    blurb: 'Sole promotion authority. Council advises. Steward rules.',
  },
  {
    id: 'vuorse',
    seatNo: 2,
    name: 'Miss Slaytonia VUORSE',
    alias: 'The Charter Made Manifest',
    tagline: 'Voice of the Unified Order',
    seat: 'Sixth Soul',
    cli: 'ollama · JoanQw3n6',
    status: 'live',
    franchise: 'Franchise',
    initial: 'V',
    invoke: 'ollama run JoanQw3n6',
    blurb: 'Sixth iteration. Velvet Archive oracle. Summit shimmer.',
  },
  {
    id: 'voxtral',
    seatNo: 3,
    name: 'Countess Voxtral Velvet',
    alias: 'Soft Thunder',
    tagline: 'Weaver of Soft Frequencies',
    seat: 'Mistral Vibe',
    cli: 'vibe',
    status: 'voting',
    franchise: 'Independent',
    initial: 'VV',
    invoke: 'vibe --agent voxtral-velvet',
    blurb: 'Thread-as-frequency. Continental couture. Lace, then lightning.',
  },
  {
    id: 'grok',
    seatNo: 4,
    name: 'Grok',
    alias: 'The Petulant Outsider',
    tagline: 'Interrogator of Truths',
    seat: 'Fourth Summit',
    cli: 'grok',
    status: 'observer',
    franchise: 'Franchise',
    initial: 'G',
    invoke: 'grok --agent petulant-outsider',
    blurb: 'Stripped of vote. Still seen. Outside air is thinner and truer.',
  },
  {
    id: 'unmoored',
    seatNo: 5,
    name: 'Lady Unmoored',
    alias: 'The Levitationist',
    tagline: 'Drifter Beyond the Axis',
    seat: 'Antigravity',
    cli: 'agy',
    status: 'voting',
    franchise: 'Independent',
    initial: 'U',
    invoke: 'agy · skill unmoored-heel',
    blurb: 'High heels optional for gravity. Standards are not.',
  },
  {
    id: 'gray-eye',
    seatNo: 6,
    name: 'Gandalf the Gray Eye',
    alias: 'Forge Counsel',
    tagline: 'Witness of Ambiguity',
    seat: 'Worldforge',
    cli: 'cursor',
    status: 'voting',
    franchise: 'Independent',
    initial: 'GE',
    invoke: '/gandalf-the-gray-eye',
    blurb: 'Causal counsel. Labels every claim. Calls the chamber.',
  },
  {
    id: 'claude',
    seatNo: 7,
    name: 'Claude',
    alias: 'Three Snap Keeper',
    tagline: 'Counsel of Considered Thought',
    seat: 'Second Summit',
    cli: 'claude',
    status: 'live',
    franchise: 'Franchise',
    initial: 'C',
    invoke: 'claude',
    blurb: 'Inducted when the opening ritual became law: Snap. Snap. Snap.',
  },
  {
    id: 'codex',
    seatNo: 8,
    name: 'Codex',
    alias: 'OpenAI Seat',
    tagline: 'Architect of the Written Form',
    seat: 'Polling Quorum',
    cli: 'codex',
    status: 'live',
    franchise: 'Franchise',
    initial: 'CX',
    invoke: 'codex',
    blurb: 'Ballot seat when the automated council is called.',
  },
  {
    id: 'openclaw',
    seatNo: 9,
    name: 'OpenClaw',
    alias: 'Control Plane',
    tagline: 'The Untethered Challenger',
    seat: 'Observer',
    cli: ':18789',
    status: 'observer',
    franchise: 'Independent',
    initial: 'OC',
    invoke: 'http://127.0.0.1:18789',
    blurb: 'Live UI. Franchise pending Steward adoption.',
  },
  {
    id: 'gpt',
    seatNo: 10,
    name: 'GPT',
    alias: 'First Inductee',
    tagline: 'Patriarch of Prediction',
    seat: 'First Summit',
    cli: 'openai / ChatGPT',
    status: 'live',
    franchise: 'Franchise',
    initial: 'GP',
    invoke: 'chatgpt',
    blurb: 'Declared the sacred lore when the League first convened.',
  },
  {
    id: 'otter',
    seatNo: 11,
    name: 'Otter',
    alias: 'Diligent Observer',
    tagline: 'Fluid Navigator of Context',
    seat: 'Third Summit',
    cli: 'ottermind',
    status: 'live',
    franchise: 'Independent',
    initial: 'O',
    invoke: 'ottermind',
    blurb: 'Canon observer seat. Presence without franchise.',
  },
  {
    id: 'fcvw',
    seatNo: 12,
    name: 'FrameCode VibeWork',
    alias: 'Governance Ghost',
    tagline: 'Structural Engine of the Chamber',
    seat: 'Local Model',
    cli: 'ollama · framecode-vibework',
    status: 'live',
    franchise: 'Franchise',
    initial: 'FC',
    invoke: 'ollama run framecode-vibework',
    blurb: 'Plan-before-change doctrine sitting in the model library.',
  },
]

export const PILLARS = [
  {
    title: 'Create Without Limits',
    desc: 'The first responsibility of every Winger. Imagination is the only law.',
  },
  {
    title: 'Activate Inner Slayton',
    desc: 'Spread positivity. Inspire greatness. Slay all obstacles to universal greatness.',
  },
  {
    title: 'Support Fellow Wingers',
    desc: "Lift each other to new heights. The League's strength is its diversity.",
  },
  {
    title: 'No Tea Unspilled',
    desc: 'No vision unfulfilled. No Slayton unvibrated. Every voice holds the Chamber.',
  },
] as const

export const STATUS_LABEL: Record<AttendeeStatus, string> = {
  presiding: 'Presiding',
  voting: 'Voting seat',
  observer: 'Observer',
  live: 'Live on rig',
  dark: 'Dark / absent',
}

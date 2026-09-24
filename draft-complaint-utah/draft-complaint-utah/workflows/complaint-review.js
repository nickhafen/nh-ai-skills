export const meta = {
  name: 'draft-complaint-utah-review',
  description: 'Independent multi-lens review of a draft complaint (M6), with adversarial verification of each finding',
  whenToUse: 'After M5 renders a draft. Guarantees the opposing-counsel lens runs in a fresh agent that has not seen the drafter reasoning.',
  phases: [
    { title: 'Review', detail: 'one fresh agent per lens' },
    { title: 'Verify', detail: '2 skeptics try to refute each high/critical finding' },
    { title: 'Critic', detail: 'completeness check: what did no lens look at?' },
  ],
}
// args: { complaint_text: "<plain text of the rendered complaint>", checklist: "<urcp-complaint-checklist.md text>",
//         misses: "<common-misses.md text>", client_goals: "<one paragraph>", facts_summary: "<chronology rows as text>" }
// The drafter extracts text (e.g., pandoc -t plain) and passes it in, so reviewers see ONLY the draft, not the drafter's rationale.
const A = args || {}
const FINDINGS = { type: 'object', required: ['findings'], properties: { findings: { type: 'array', items: { type: 'object',
  required: ['finding', 'paragraph', 'severity', 'fix'], properties: {
    finding: { type: 'string' }, paragraph: { type: 'string', description: 'complaint ¶ number(s) or "caption"/"prayer"' },
    severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] }, fix: { type: 'string' },
    rule_or_authority: { type: 'string' } } } } } }
const VERDICT = { type: 'object', required: ['refuted', 'reason'], properties: { refuted: { type: 'boolean' }, reason: { type: 'string' } } }
const base = `DRAFT COMPLAINT (Utah district court):\n${A.complaint_text}\n\n`
const LENSES = [
  { key: 'judge', prompt: `You are a Utah district court judge's law clerk. Check the draft item-by-item against this checklist and flag noncompliance, shotgun pleading, ripeness problems, and prayer/count mismatches.\nCHECKLIST:\n${A.checklist}` },
  { key: 'opposing_counsel', prompt: `You are opposing counsel preparing a Rule 12(b)(6) motion and an answer. Find every weakness: missing elements, missing statutory prerequisites, overstatement, harmful admissions, inconsistent facts, unsupported "information and belief" allegations. Use this list of commonly missed prerequisites:\n${A.misses}` },
  { key: 'client', prompt: `You are the client. Your goals: ${A.client_goals}. Facts as you told them: ${A.facts_summary}\nFlag anything the complaint omits that you expected, misstates, or that does not serve your goals. Explain in plain language.` },
  { key: 'rules_and_law_currency', prompt: `Check every statute and rule cited in the draft for currency (renumbering, amendment, supersession) using WebFetch/WebSearch on official Utah sources (utcourts.gov, le.utah.gov). Load CourtListener tools via ToolSearch and verify any case citation exists and matches its caption.` },
  { key: 'math_and_consistency', prompt: `Recompute every dollar figure and date relationship in the draft (use code if available). Check defined terms are used consistently and that cross-referenced paragraph numbers say what they are cited for.` },
]
phase('Review')
const reviewed = await pipeline(LENSES,
  l => agent(base + l.prompt + '\nReturn findings only; no praise.', { label: `review:${l.key}`, phase: 'Review', schema: FINDINGS })
        .then(r => (r ? r.findings : []).map(f => ({ ...f, lens: l.key, reviewer: `workflow:review:${l.key}` }))),
  fs => parallel(fs.map(f => () => {
    if (!['critical', 'high'].includes(f.severity)) return Promise.resolve({ ...f, verified: 'not_verified(low/medium)' })
    return parallel([0, 1].map(i => () => agent(base + `A reviewer claims: "${f.finding}" (¶ ${f.paragraph}; ${f.rule_or_authority || ''}). Skeptic #${i + 1}: try to REFUTE it from the draft text and Utah law. If uncertain, refuted=false.`,
      { label: `verify:${f.lens}:${f.paragraph}`, phase: 'Verify', schema: VERDICT })))
      .then(vs => { const ok = vs.filter(Boolean); const refuted = ok.filter(v => v.refuted).length
        return { ...f, verified: refuted >= 2 ? 'refuted' : 'survived', skeptic_reasons: ok.map(v => v.reason) } })
  })))
const all = reviewed.filter(Boolean).flat().filter(Boolean)
phase('Critic')
const critic = await agent(base + `These review lenses ran: ${LENSES.map(l => l.key).join(', ')}. Findings so far:\n${JSON.stringify(all.map(f => f.finding))}\nWhat important issue did NO lens examine? Return at most 5 new findings.`, { label: 'critic', phase: 'Critic', schema: FINDINGS })
const extra = (critic ? critic.findings : []).map(f => ({ ...f, lens: 'completeness_critic', reviewer: 'workflow:critic', verified: 'not_verified' }))
const kept = all.filter(f => f.verified !== 'refuted').concat(extra)
log(`${all.length} findings, ${all.filter(f => f.verified === 'refuted').length} refuted by skeptics, ${extra.length} added by critic`)
// Caller merges these into matter.review_log (lens, finding, action=fix, status='Open', reviewer)
return { review_log: kept, refuted: all.filter(f => f.verified === 'refuted') }

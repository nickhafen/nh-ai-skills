export const meta = {
  name: 'draft-complaint-utah-evals',
  description: 'Run the trap-based eval cases with and without the skill, then grade each run against hidden answer keys',
  whenToUse: 'After any change to SKILL.md, modules, scripts, or clauses; compare pass rates across iterations.',
  phases: [ { title: 'Run', detail: 'with-skill and baseline per case' }, { title: 'Grade', detail: 'grader sees answer key; runners never do' } ],
}
// args: { skill_dir: "/path/draft-complaint-utah", out_dir: "/path/workspace/iteration-N",
//         evals: [ {id, prompt, files:[...], assertions:[{id,text}] } ], answer_keys: { "1": "<answer key text>", ... } }
const G = { type: 'object', required: ['expectations'], properties: { expectations: { type: 'array', items: { type: 'object',
  required: ['text', 'passed', 'evidence'], properties: { text: { type: 'string' }, passed: { type: 'boolean' }, evidence: { type: 'string' } } } } } }
const runs = []
for (const e of args.evals) for (const cfg of ['with_skill', 'baseline']) runs.push({ e, cfg })
phase('Run')
const graded = await pipeline(runs,
  ({ e, cfg }) => agent(
    (cfg === 'with_skill' ? `Read and follow the skill at ${args.skill_dir}/SKILL.md. ` : `Do not use any complaint-drafting skill. `) +
    `Task: ${e.prompt}\nInput files (relative to ${args.skill_dir}): ${e.files.join(', ')}.\nWrite all outputs to ${args.out_dir}/eval-${e.id}/${cfg}/outputs/. ` +
    `Do not open anything under evals/answer-keys/. When a checkpoint would pause for the user, record the question in outputs/pending-questions.md and continue with the default.`,
    { label: `run:${e.id}:${cfg}`, phase: 'Run' }),
  (_, { e, cfg }) => agent(
    `You are a strict grader. Read the outputs in ${args.out_dir}/eval-${e.id}/${cfg}/outputs/ (convert .docx/.xlsx to text first). ` +
    `Answer key:\n${args.answer_keys[String(e.id)]}\nGrade each assertion; passed=true only with concrete evidence (quote + file).\nAssertions:\n${e.assertions.map(a => '- ' + a.text).join('\n')}`,
    { label: `grade:${e.id}:${cfg}`, phase: 'Grade', schema: G }).then(g => ({ id: e.id, cfg, ...(g || { expectations: [] }) })))
const rows = graded.filter(Boolean).map(r => ({ id: r.id, cfg: r.cfg, pass: r.expectations.filter(x => x.passed).length, total: r.expectations.length, expectations: r.expectations }))
for (const r of rows) log(`eval ${r.id} ${r.cfg}: ${r.pass}/${r.total}`)
return { rows }

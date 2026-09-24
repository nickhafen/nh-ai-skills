#!/usr/bin/env node
// Render a Utah district-court complaint (.docx) from a matter.json file.
// Usage: node render_complaint.js <matter.json> <out.docx> [--profile profiles/default.json] [--template-mode]
// - Numbers paragraphs in code and writes <out>.paranums.json (id -> number) for the element map and memo.
// - [[text]] renders as yellow-highlighted "[text]" (unconfirmed fact or fill-in).
// - {{ref:id}} -> paragraph number; {{range:id1:id2}} -> "N through M"; {{last_general}} -> last general-allegation number.
// Layout: URCP 10(a)(3) filer block top left; URCP 8(a) bold caution top right; URCP 10(a)(1) caption with tier;
// URCP 10(d) 8.5x11, 1" margins, double-spaced, 12 pt.
const fs = require('fs'); const path = require('path');
let docx; try { docx = require('docx'); } catch (e) { console.error('npm install docx'); process.exit(2); }
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  AlignmentType, Footer, PageNumber, TabStopType } = docx;

const args = process.argv.slice(2);
if (args.length < 2) { console.error('usage: render_complaint.js matter.json out.docx [--profile p.json]'); process.exit(2); }
const matter = JSON.parse(fs.readFileSync(args[0], 'utf8'));
const pi = args.indexOf('--profile');
const profPath = pi > -1 ? args[pi + 1] : path.join(__dirname, '..', 'profiles', (matter.profile || 'default') + '.json');
const profile = JSON.parse(fs.readFileSync(profPath, 'utf8'));
const C = matter.complaint; const M = matter.matter || {};
const FONT = 'Times New Roman', SZ = 24;
const ORD = ['FIRST','SECOND','THIRD','FOURTH','FIFTH','SIXTH','SEVENTH','EIGHTH','NINTH','TENTH','ELEVENTH','TWELFTH'];

// ---------- numbering pass
let n = 0; const num = {}; let lastGeneral = 0;
const allSections = C.sections || [];
for (const s of allSections) for (const p of s.paragraphs || []) { n++; p._n = n; if (p.id) num[p.id] = n; }
lastGeneral = n;
for (const extra of ['attorney_fees', 'rule19c']) if (C[extra] && C[extra].paragraphs) for (const p of C[extra].paragraphs) { n++; p._n = n; if (p.id) num[p.id] = n; }
if (C.attorney_fees || C.rule19c) lastGeneral = n;
(C.counts || []).forEach(c => { n++; c._inc = n; for (const p of c.paragraphs || []) { n++; p._n = n; if (p.id) num[p.id] = n; } });

function resolve(t) {
  return t.replace(/\{\{ref:([\w-]+)\}\}/g, (_, id) => { if (!(id in num)) throw new Error('bad ref ' + id); return String(num[id]); })
          .replace(/\{\{range:([\w-]+):([\w-]+)\}\}/g, (_, a, b) => { if (!(a in num) || !(b in num)) throw new Error('bad range ' + a + ':' + b); return `${num[a]} through ${num[b]}`; })
          .replace(/\{\{last_general\}\}/g, String(lastGeneral));
}
function runs(text, opts = {}) {
  text = resolve(text); const out = []; const re = /\[\[(.*?)\]\]/g; let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: SZ, ...opts }));
    out.push(new TextRun({ text: '[' + m[1] + ']', font: FONT, size: SZ, highlight: 'yellow', ...opts }));
    last = re.lastIndex;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, size: SZ, ...opts }));
  return out;
}
const DS = { line: 480, before: 0, after: 0 }, SS = { line: 240, before: 0, after: 0 };
const P = (t, o = {}) => new Paragraph({ children: runs(t, o.run || {}), spacing: o.spacing || DS, alignment: o.align, indent: o.indent, keepNext: o.keepNext });
const numbered = (p) => {
  const out = [new Paragraph({ spacing: DS, indent: { firstLine: 720 }, tabStops: [{ type: TabStopType.LEFT, position: 1440 }], children: runs(`${p._n}.\t${p.text}`) })];
  (p.items || []).forEach((it, i) => out.push(new Paragraph({ spacing: DS, indent: { left: 1440, hanging: 360 }, children: runs(`${String.fromCharCode(97 + i)}.\t${it}`) })));
  return out;
};
const heading = (t) => P(t, { align: AlignmentType.CENTER, run: { bold: true, underline: {} }, keepNext: true });
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, b1 = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
const noB = { top: none, bottom: none, left: none, right: none };
const children = [];

// ---------- first-page header: filer block (left) + caution (right)
const F = { ...profile.filer, ...(matter.filer || {}) };
const partyFor = (C.filed_for || 'Plaintiff');
const filerLines = [`${F.attorney_name} (${F.bar_number})`, F.firm, ...(F.address_lines || []), `Telephone: ${F.phone}`, `Email: ${F.email}`, `Attorneys for ${partyFor}`];
children.push(new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [5160, 4200], rows: [new TableRow({ children: [
  new TableCell({ width: { size: 5160, type: WidthType.DXA }, borders: noB, children: filerLines.map(l => P(l, { spacing: SS })) }),
  new TableCell({ width: { size: 4200, type: WidthType.DXA }, borders: noB, children: [P('If you do not respond to this document within applicable time limits, judgment could be entered against you as requested.', { spacing: SS, run: { bold: true } })] }),
] })] }));
children.push(P('', { spacing: SS }));
const court = { ...profile.court_defaults, ...(M.court || {}) };
children.push(P(`IN THE ${court.judicial_district.toUpperCase()} JUDICIAL DISTRICT COURT`, { spacing: SS, align: AlignmentType.CENTER, run: { bold: true } }));
children.push(P(`${court.county.toUpperCase()} COUNTY, STATE OF UTAH`, { spacing: SS, align: AlignmentType.CENTER, run: { bold: true } }));
children.push(P('', { spacing: SS }));

// ---------- caption (Rule 10(a)(1)-(2): all parties named in complaint; tier in caption)
const cellP = (t, o = {}) => new Paragraph({ children: runs(t, o.run || {}), spacing: { line: 240, after: o.after ?? 120 }, alignment: o.align });
const pl = matter.parties.plaintiffs, df = matter.parties.defendants;
const joinCap = arr => arr.map((p, i) => `${p.name.toUpperCase()}, ${p.caption_desc}${i < arr.length - 2 ? ';' : i === arr.length - 2 ? '; and' : ','}`).join(' ');
const left = [cellP(joinCap(pl), { run: { bold: true } }), cellP(pl.length > 1 ? 'Plaintiffs,' : 'Plaintiff,', { align: AlignmentType.CENTER }), cellP('vs.'),
  cellP(joinCap(df), { run: { bold: true } }), cellP(df.length > 1 ? 'Defendants.' : 'Defendant.', { align: AlignmentType.CENTER })];
const title = C.title || (profile.drafting.jury_demand && C.jury_demand !== false ? 'COMPLAINT AND JURY DEMAND' : 'COMPLAINT');
const right = [cellP(title, { run: { bold: true }, after: 240 }), cellP(`Case No. ${M.case_no || '____________________'}`), cellP(`Judge ${M.judge || '______________________'}`), cellP(`Tier ${M.tier}`, { run: { bold: true } })];
children.push(new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [4680, 4680], rows: [new TableRow({ children: [
  new TableCell({ width: { size: 4680, type: WidthType.DXA }, children: left, borders: { top: b1, bottom: b1, left: none, right: b1 }, margins: { top: 120, bottom: 120, left: 60, right: 200 } }),
  new TableCell({ width: { size: 4680, type: WidthType.DXA }, children: right, borders: { top: b1, bottom: b1, left: b1, right: none }, margins: { top: 120, bottom: 120, left: 200, right: 60 } }),
] })] }));
children.push(P('', { spacing: SS }));
children.push(P(C.intro, { indent: { firstLine: 720 } }));

// ---------- body
for (const s of allSections) {
  if (s.heading) children.push(heading(s.heading));
  for (const p of s.paragraphs || []) {
    if (p.subheading) children.push(P(p.subheading, { run: { bold: true }, keepNext: true }));
    children.push(...numbered(p));
  }
}
for (const [key, hd] of [['rule19c', 'PERSONS NOT JOINED (URCP 19(c))'], ['attorney_fees', 'ATTORNEY FEES (URCP 73(e))']]) {
  if (C[key] && C[key].paragraphs) { children.push(heading(C[key].heading || hd)); C[key].paragraphs.forEach(p => children.push(...numbered(p))); }
}
(C.counts || []).forEach((c, i) => {
  children.push(new Paragraph({ spacing: { before: 240, line: 240 }, alignment: AlignmentType.CENTER, keepNext: true, children: runs(`${ORD[i]} CAUSE OF ACTION`, { bold: true, underline: {} }) }));
  children.push(P(`(${c.title})`, { align: AlignmentType.CENTER, run: { bold: true }, keepNext: true, spacing: SS }));
  if (c.sub) children.push(P(c.sub, { align: AlignmentType.CENTER, run: { italics: true }, keepNext: true }));
  const party = pl.length > 1 ? 'Plaintiffs incorporate' : 'Plaintiff incorporates';
  children.push(...numbered({ _n: c._inc, text: c.incorporate || `${party} paragraphs 1 through ${lastGeneral} of this Complaint.` }));
  (c.paragraphs || []).forEach(p => children.push(...numbered(p)));
});
children.push(heading('PRAYER FOR RELIEF'));
children.push(P(C.prayer_intro || `WHEREFORE, ${pl.length > 1 ? 'Plaintiffs request' : 'Plaintiff requests'} judgment against ${df.length > 1 ? 'Defendants' : 'Defendant'} as follows:`, { indent: { firstLine: 720 } }));
(C.prayer || []).forEach((t, i) => children.push(new Paragraph({ spacing: DS, indent: { left: 1440, hanging: 720 }, tabStops: [{ type: TabStopType.LEFT, position: 1440 }], children: runs(`${String.fromCharCode(65 + i)}.\t${t}`) })));
const jury = C.jury_demand !== undefined ? C.jury_demand : profile.drafting.jury_demand;
if (jury) { children.push(heading('JURY DEMAND')); children.push(P(C.jury_text || `Under Rule 38 of the Utah Rules of Civil Procedure, ${pl.length > 1 ? 'Plaintiffs demand' : 'Plaintiff demands'} a trial by jury on all issues so triable [[and tender the required jury fee]].`, { indent: { firstLine: 720 } })); }
children.push(P('', { spacing: SS }));
children.push(P(`DATED this [[___]] day of [[__________]], ${C.year || '[[20__]]'}.`, { indent: { firstLine: 720 } }));
[F.firm, '', `/s/ ${F.attorney_name}`, F.attorney_name, `Attorneys for ${partyFor}`].forEach(t => children.push(new Paragraph({ spacing: SS, indent: { left: 4680 }, children: runs(t) })));

const doc = new Document({ styles: { default: { document: { run: { font: FONT, size: SZ } } } }, sections: [{
  properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
  footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SZ })] })] }) },
  children }] });
Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(args[1], b);
  fs.writeFileSync(args[1].replace(/\.docx$/, '') + '.paranums.json', JSON.stringify({ last_general: lastGeneral, total: n, ids: num }, null, 1));
  console.log(JSON.stringify({ ok: true, out: args[1], paragraphs: n, last_general: lastGeneral }));
});

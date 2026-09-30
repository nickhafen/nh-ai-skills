// Skills site viewer. Plain JavaScript, no build step.
// Data: manifest.json and labels.json (written by build.py), fetched once on
// load. File text comes from files/<path>, fetched when a file is opened.
// Routes are hash paths so deep links work on GitHub Pages:
//   #/                                         home page
//   #/?task=review&q=letter                    home page, filtered
//   #/<skill>/<skill>/references/x.md          a file or folder, by its repo path
// The short form #/<skill>/references/x.md also works and is redirected.

"use strict";

const app = document.getElementById("app");
const announcer = document.getElementById("announcer");
const IS_MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
const COPY_KEYS = IS_MAC ? "⌘C" : "Ctrl+C";
const SITE_NAME = "AI Skills for Law";

let manifest = null;
let labels = {};
let firstRender = true;
let renderToken = 0;
let markdownMode = "formatted"; // remembered while the page is open
const index = new Map(); // repo path -> { node, skill, parts }
const textCache = new Map();

// ------------------------------------------------------------------ helpers

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value; // trusted, static markup only
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) {
    if (child == null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(child));
  }
  return node;
}

function icon(name) {
  return el("span", { class: "icon", html: ICONS[name] });
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function routeHref(parts) {
  return parts.length ? "#/" + parts.map(encodeURIComponent).join("/") : "#/";
}

function fileUrl(parts) {
  return "files/" + parts.map(encodeURIComponent).join("/");
}

function storageGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}

function storageSet(key, value) {
  try { localStorage.setItem(key, value); } catch { /* private window */ }
}

function announce(message) {
  announcer.textContent = "";
  setTimeout(() => { announcer.textContent = message; }, 50);
}

const SVG = (body, extra = "") =>
  `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${body}</svg>`;

const ICONS = {
  download: SVG('<path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19h14"/>'),
  back: SVG('<path d="M19 12H5m0 0 6-6m-6 6 6 6"/>'),
  folder: SVG('<path d="M3 6.5A1.5 1.5 0 0 1 4.5 5h4.2l2 2.2h8.8A1.5 1.5 0 0 1 21 8.7v9.8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/>'),
  file: SVG('<path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v5h5"/>'),
  copy: SVG('<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>'),
  link: SVG('<path d="M10 14a4 4 0 0 0 5.7 0l3.1-3.1a4 4 0 0 0-5.7-5.7L11.6 6.7"/><path d="M14 10a4 4 0 0 0-5.7 0l-3.1 3.1a4 4 0 0 0 5.7 5.7l1.5-1.5"/>'),
  grid: SVG('<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>'),
  list: SVG('<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>'),
  filter: SVG('<path d="M4 5h16l-6 7.5V19l-4-2v-4.5z"/>'),
  folderSolid: SVG('<path fill="currentColor" d="M3 6.5A1.5 1.5 0 0 1 4.5 5h4.2l2 2.2h8.8A1.5 1.5 0 0 1 21 8.7v9.8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/>'),
  chevron: SVG('<path d="m9 6 6 6-6 6"/>'),
  home: SVG('<path d="M4 11.5 12 5l8 6.5"/><path d="M6 10v9h12v-9"/>'),
  folderOpen: SVG('<path d="M3 7a1.5 1.5 0 0 1 1.5-1.5h4.2l2 2h8.8A1.5 1.5 0 0 1 21 9v1H7.5L4.5 19H4.5A1.5 1.5 0 0 1 3 17.5z"/><path d="M7.5 10H22l-3 9H4.5z"/>'),
};

// ------------------------------------------------------------------ manifest

function indexManifest() {
  for (const skill of manifest.skills) {
    const walk = (node, parts) => {
      index.set(parts.join("/"), { node, skill, parts });
      if (node.type === "dir") {
        for (const child of node.children) walk(child, [...parts, child.name]);
      }
    };
    walk(skill.tree, [skill.id]);
  }
}

function skillHome(skill) {
  return [skill.id, skill.id];
}

function inSkill(parts) {
  return parts.length >= 2 && parts[1] === parts[0];
}

function maintainerItems(skill) {
  return skill.tree.children.filter(c => c.role !== "skill");
}

function labelFor(node) {
  return labels[node.type === "dir" ? `${node.name}/` : node.name] || null;
}

// ------------------------------------------------------------------ copying

function flash(button, message, ms = 2000) {
  const label = button.querySelector(".label");
  clearTimeout(button._flashTimer);
  if (!button._label) button._label = label.textContent;
  label.textContent = message;
  button.classList.add("flashed");
  announce(message);
  button._flashTimer = setTimeout(() => {
    label.textContent = button._label;
    button.classList.remove("flashed");
  }, ms);
}

function legacyCopy(text) {
  const area = el("textarea", { class: "offscreen", readonly: true, "aria-hidden": "true" });
  area.value = text;
  document.body.append(area);
  area.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch { ok = false; }
  area.remove();
  return ok;
}

function selectContents(target) {
  if (target instanceof HTMLTextAreaElement || target instanceof HTMLInputElement) {
    target.focus();
    target.select();
    return;
  }
  const range = document.createRange();
  range.selectNodeContents(target);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
}

// If the clipboard is blocked, select the text so the visitor can copy it.
// `fallback` returns the element to select (created on demand if needed).
async function copyText(text, button, fallback) {
  let ok = false;
  try {
    await navigator.clipboard.writeText(text);
    ok = true;
  } catch {
    ok = legacyCopy(text);
  }
  if (ok) {
    flash(button, "Copied ✓");
    return;
  }
  selectContents(fallback());
  flash(button, `Press ${COPY_KEYS} to copy`, 5000);
}

// A read-only box placed after `anchor`, for when the text isn't on screen.
function manualCopyBox(anchor, text, rows = 6) {
  document.querySelectorAll(".manual-copy").forEach(n => n.remove());
  const box = el("textarea", { class: "manual-copy", readonly: true, rows,
                               "aria-label": "Text to copy" });
  box.value = text;
  anchor.after(box);
  return box;
}

function copyButton(text, labelText, iconName, fallback, extra = {}) {
  const button = el("button", { type: "button", class: "btn btn-secondary", ...extra },
    icon(iconName), el("span", { class: "label" }, labelText));
  button.addEventListener("click", () =>
    copyText(typeof text === "function" ? text() : text, button, fallback));
  return button;
}

function copyLinkButton() {
  const button = copyButton(() => location.href, "Copy link", "link",
    () => manualCopyBox(button.closest(".actions") || button, location.href, 2));
  return button;
}

// ------------------------------------------------------------------ shared UI

function downloadSkillButton(skill) {
  return el("a", {
    class: "btn btn-primary",
    href: skill.zip.path,
    download: `${skill.id}.zip`,
    "aria-describedby": `dl-name-${skill.id} dl-size-${skill.id}`,
  }, icon("download"), "Download skill (.zip)");
}

function skillNameNodes(skill) {
  // Hidden text that tells screen readers which skill the button downloads.
  return [
    el("span", { class: "sr-only", id: `dl-name-${skill.id}` }, skill.name),
    el("span", { class: "size", id: `dl-size-${skill.id}` }, formatSize(skill.zip.bytes)),
  ];
}

function breadcrumbs(parts, skill) {
  const crumbs = [{ label: "All skills", parts: [] },
                  { label: skill.name, parts: skillHome(skill) }];
  const base = inSkill(parts) ? skillHome(skill) : [skill.id];
  const rest = parts.slice(base.length);
  const prefix = [...base];
  for (const seg of rest) {
    prefix.push(seg);
    crumbs.push({ label: seg, parts: [...prefix] });
  }
  return crumbs;
}

function navBar(crumbs) {
  return [
    el("nav", { class: "crumbs", "aria-label": "Breadcrumb" },
      el("ol", {}, crumbs.map((c, i) => el("li", {},
        i === crumbs.length - 1
          ? el("span", { "aria-current": "page" }, c.label)
          : el("a", { href: routeHref(c.parts) }, i === 0 && icon("home"), c.label))))),
  ];
}

function maintainerNote() {
  return el("p", { class: "note" },
    "Maintainer files help presenters and the people who keep the skill up to date. " +
    "They aren't part of the skill and aren't in the download.");
}

function itemCount(node) {
  const n = node.children.length;
  return n === 1 ? "1 item" : `${n} items`;
}

function rowList(nodes, parentParts, withLabels = true) {
  return el("ul", { class: "rows" }, nodes.map(node => {
    const parts = [...parentParts, node.name];
    const label = withLabels && labelFor(node);
    return el("li", {},
      el("a", { class: "row", href: routeHref(parts) },
        el("span", { class: `row-icon ${node.type}` }, icon(node.type === "dir" ? "folderSolid" : "file")),
        el("span", { class: "row-text" },
          el("span", { class: "row-name" }, node.name + (node.type === "dir" ? "/" : "")),
          label && el("span", { class: "row-label" }, label)),
        node.type === "dir"
          ? el("span", { class: "row-size" }, itemCount(node), icon("chevron"))
          : el("span", { class: "row-size" }, formatSize(node.bytes))));
  }));
}

// ------------------------------------------------------------------ home

// What a skill's own files need from a platform, read from the manifest so
// it stays right as skills change. Only the inner skill folder counts.
function skillNeeds(skill) {
  const exts = new Set();
  const walk = node => {
    if (node.type === "dir") node.children.forEach(walk);
    else exts.add(node.name.slice(node.name.lastIndexOf(".") + 1).toLowerCase());
  };
  const inner = skill.tree.children.find(c => c.role === "skill");
  if (inner) walk(inner);
  return {
    python: exts.has("py"),
    javascript: exts.has("js") || exts.has("mjs"),
    word: exts.has("docx"),
  };
}

function includesLine(skill) {
  const n = skillNeeds(skill);
  const parts = [];
  if (n.python) parts.push("Python scripts");
  if (n.javascript) parts.push("JavaScript (Node.js) scripts");
  if (n.word) parts.push("a Word template");
  const text = parts.length
    ? `Includes ${parts.length > 1
        ? parts.slice(0, -1).join(", ") + (parts.length > 2 ? "," : "") + " and " + parts.at(-1)
        : parts[0]}.`
    : "Instructions only, no scripts.";
  return el("p", { class: "includes" }, text);
}

// Skills with files Gemini doesn't accept (Word files and JavaScript).
function geminiConflicts() {
  return manifest.skills.flatMap(skill => {
    const n = skillNeeds(skill);
    const why = [n.word && "a Word template", n.javascript && "JavaScript scripts"].filter(Boolean);
    return why.length ? [[skill.name, why.join(" and ")]] : [];
  });
}

const NEW_TAB = () => el("span", { class: "sr-only" }, " (opens in a new tab)");
const ext = (href, text) =>
  el("a", { href, target: "_blank", rel: "noopener noreferrer" }, text, NEW_TAB());
const b = text => el("strong", {}, text);
const code = text => el("code", {}, text);

const PLATFORMS = [
  {
    id: "claude",
    name: "Claude",
    steps: () => [
      ["Click ", b("Download skill (.zip)"), " on the skill you want. Don't unzip it."],
      ["In Claude (web or desktop app), go to ", b("Customize > Skills"), ", click ", b("+"),
        ", choose ", b("Create skill"), ", then ", b("Upload a skill"), "."],
      ["Pick the zip you downloaded."],
    ],
    notes: () => [
      ["Works on every plan, including Free. ", b("Code execution"), " must be on: ",
        b("Settings > Capabilities"), " (on Team and Enterprise plans, an admin controls this)."],
      ["Claude uses a skill on its own when your request matches it."],
      ["If you also use Claude Code and sign in with the same account, your uploaded skills show up there too."],
    ],
    link: ["https://support.claude.com/en/articles/12512180-use-skills-in-claude", "Claude's help page on skills"],
  },
  {
    id: "claude-code",
    name: "Claude Code",
    steps: () => [
      ["Click ", b("Download skill (.zip)"), " and unzip it. You get one folder named after the skill."],
      ["Move that folder into ", code("~/.claude/skills/"), " (on Windows, ",
        code("C:\\Users\\<you>\\.claude\\skills\\"), "). Create the ", code("skills"),
        " folder if it isn't there."],
      ["Start a new Claude Code session."],
    ],
    notes: () => [
      ["Scripts run on your own computer, so you may need to install what a skill asks for (the skill's instructions say what)."],
      ["Claude uses the skill when it's relevant, or you can type ", code("/"), " and the skill's name."],
    ],
    link: ["https://code.claude.com/docs/en/skills", "Claude Code's docs on skills"],
  },
  {
    id: "chatgpt",
    name: "ChatGPT",
    steps: () => [
      ["Click ", b("Download skill (.zip)"), " on the skill you want. Don't unzip it."],
      ["In ChatGPT, open ", b("Plugins"), " in the sidebar and choose the ", b("Skills"), " tab."],
      ["Choose ", b("Create"), ", then ", b("Upload from your computer"), ", and pick the zip."],
    ],
    notes: () => [
      ["Skills are on ChatGPT Business, Enterprise, Healthcare, and Edu plans, not on personal plans. ",
        "Your workspace admin decides whether members can upload skills."],
      ["ChatGPT scans each upload. Most skills are ready right away; some are marked ",
        b("Needs Review"), " before you can use them."],
      ["ChatGPT uses a skill on its own when it helps."],
    ],
    link: ["https://help.openai.com/en/articles/20001066-skills-in-chatgpt", "OpenAI's help page on skills"],
  },
  {
    id: "gemini",
    name: "Gemini",
    steps: () => [
      ["Click ", b("Download skill (.zip)"), " on the skill you want."],
      ["Go to ", ext("https://gemini.google.com", "gemini.google.com"),
        " (or the Gemini app on a Mac) and open ", b("Settings > Skills"), "."],
      ["Choose to upload a file or folder, and pick the zip."],
    ],
    notes: () => {
      const conflicts = geminiConflicts();
      return [
        ["Skills need a personal Google account (not work or school), age 18 or over, and ",
          b("Keep Activity"), " turned on. They're rolling out gradually, so you may not have them yet."],
        ["Gemini doesn't accept Word (.docx) or JavaScript files in a skill, and a skill's scripts can't use the internet."],
        conflicts.length && ["Because of that, these skills won't work in Gemini as downloaded: ",
          conflicts.map(([name, why], i) => [i ? "; " : "", b(name), ` (${why})`]), "."],
        ["Gemini uses a skill on its own when it's relevant (Gemini Spark tasks included), or you can type ",
          code("/"), " and pick it."],
      ].filter(Boolean);
    },
    link: ["https://support.google.com/gemini/answer/17094296", "Google's help page on Gemini skills"],
  },
  {
    id: "other",
    name: "Other tools",
    heading: "Add a skill to another AI tool",
    steps: () => [
      ["Click ", b("Download skill (.zip)"), " and unzip it."],
      ["Put the folder where your tool looks for skills. Many coding tools, including Cursor, ",
        "GitHub Copilot, Codex, and Gemini CLI, read this same format."],
    ],
    notes: () => [
      ["The Agent Skills site ", ext("https://agentskills.io/clients", "lists tools that support skills"),
        ", each with a link to its setup steps."],
    ],
    link: null,
  },
];

function stepList(tag, items) {
  return el(tag, {}, items.map(item => el("li", {}, item)));
}

function installSteps() {
  const saved = storageGet("platform");
  let current = PLATFORMS.some(p => p.id === saved) ? saved : "claude";
  const panel = el("div", { class: "platform-panel" });
  const picker = el("div", { class: "chips", role: "group", "aria-label": "Your AI platform" });

  const show = id => {
    current = id;
    storageSet("platform", id);
    const p = PLATFORMS.find(x => x.id === id);
    picker.querySelectorAll("button").forEach(btn =>
      btn.setAttribute("aria-pressed", String(btn.dataset.id === id)));
    panel.replaceChildren(...[
      el("h3", {}, p.heading || `Add a skill to ${p.name}`),
      stepList("ol", p.steps()),
      el("h4", {}, "Good to know"),
      stepList("ul", p.notes()),
      p.link && el("p", { class: "more" }, ext(p.link[0], p.link[1])),
    ].filter(Boolean));
  };
  picker.append(...PLATFORMS.map(p => el("button", {
    type: "button", class: "chip", "data-id": p.id, onclick: () => show(p.id),
  }, p.name)));
  show(current);

  return el("details", { class: "install", id: "install-help" },
    el("summary", {}, "How do I install a skill?"),
    el("div", { class: "install-body stack" },
      el("p", { class: "picker-label" }, "Where do you use AI?"),
      picker, panel));
}

function platformGuide() {
  const rows = [
    ["Claude", "Every plan; code execution turned on", "Yes, in a sandbox",
      "Upload the .zip", "Automatically"],
    ["Claude Code", "Anyone with Claude Code", "Yes, on your computer",
      "Folder in ~/.claude/skills", "Automatically, or type /name"],
    ["ChatGPT", "Business, Enterprise, Healthcare, and Edu plans", "Yes",
      "Upload the .zip; scanned first, and some need review", "Automatically"],
    ["Gemini", "Personal Google accounts, 18+", "Python and shell only, no internet",
      "No Word or JavaScript files; 100 MB max", "Automatically, or type /"],
    ["Other tools", "Varies", "Varies", "Usually a folder in a skills directory", "Varies"],
  ];
  const head = ["Platform", "Who can use skills", "Runs a skill's scripts?", "Files", "How a skill gets used"];
  return el("details", { class: "install" },
    el("summary", {}, "How do AI platforms handle skills?"),
    el("div", { class: "install-body stack" },
      el("p", {}, "These skills follow ",
        ext("https://agentskills.io/home", "Agent Skills"),
        ", an open format that many AI platforms read. Every platform works from the same core: a folder with a ",
        code("SKILL.md"), " file whose name and description tell the AI when the skill applies. ",
        "The AI keeps only those short descriptions in mind until a request matches. Then it reads the full ",
        "instructions, and it opens the skill's other files (reference material, templates, scripts) only when it needs them."),
      el("p", {}, "What differs is who can use skills, whether the platform can run a skill's scripts, ",
        "which file types it accepts, and how you add and start a skill:"),
      el("div", { class: "table-wrap", tabindex: "0", role: "region",
                  "aria-label": "How platforms differ" },
        el("table", { class: "compare" },
          el("thead", {}, el("tr", {}, head.map(h => el("th", { scope: "col" }, h)))),
          el("tbody", {}, rows.map(([name, ...cells]) =>
            el("tr", {}, el("th", { scope: "row" }, name), cells.map(c => el("td", {}, c))))))),
      el("p", {}, "Each skill's card says what it includes. A skill with scripts works fully only where ",
        "those scripts can run, and some scripts need extra software installed. ",
        "A platform may also ignore settings in ", code("SKILL.md"),
        " that only another platform uses. Platforms change often, so check each platform's help page if something doesn't match:"),
      linkList([
        ["https://support.claude.com/en/articles/12512180-use-skills-in-claude", "Claude"],
        ["https://code.claude.com/docs/en/skills", "Claude Code"],
        ["https://help.openai.com/en/articles/20001066-skills-in-chatgpt", "ChatGPT"],
        ["https://support.google.com/gemini/answer/17094296", "Gemini"],
        ["https://agentskills.io/clients", "Other tools", "Setup links for tools that support Agent Skills."],
      ])));
}

function linkList(items) {
  return el("ul", { class: "link-list" }, items.map(([href, text, desc]) =>
    el("li", {}, ext(href, text), desc && el("span", { class: "desc" }, desc))));
}

function learnMore() {
  return el("details", { class: "install" },
    el("summary", {}, "Where can I learn more about skills?"),
    el("div", { class: "install-body stack" },
      linkList([
        ["https://agentskills.io/home", "Agent Skills", "The open format these skills follow, and its specification."],
        ["https://code.claude.com/docs/en/skills", "Claude's skill documentation", "Skill structure, frontmatter fields, and how Claude applies skills."],
        ["https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf", "The Complete Guide to Building Skills for Claude", "Anthropic's PDF guide to designing skills and writing instructions."],
        ["https://github.com/anthropics/knowledge-work-plugins/tree/main/legal/skills", "Example legal skills", "Anthropic's legal skills, useful as templates."],
      ])));
}

function markdownHelp() {
  return el("details", { class: "install" },
    el("summary", {}, "How do I read or edit Markdown?"),
    el("div", { class: "install-body stack" },
      el("p", {}, "Skill files end in ", code(".md"), ". That's Markdown: plain text with a few marks for headings, ",
        "bold, and lists. Any text editor opens it, and these tools make it easier:"),
      linkList([
        ["https://www.markdownguide.org/cheat-sheet/", "Markdown cheat sheet", "Headings, bold, lists, links, and code blocks."],
        ["https://stackedit.io/app", "StackEdit", "Write and preview Markdown in your browser."],
        ["https://support.google.com/docs/answer/12014036", "Markdown in Google Docs", "Use, import, or export Markdown in Docs, Slides, and Drawings."],
      ])));
}

function faq() {
  return el("section", { class: "faq", "aria-labelledby": "faq-heading" },
    el("h2", { id: "faq-heading" }, "Common questions"),
    installSteps(), platformGuide(), learnMore(), markdownHelp());
}

// ------------------------------------------------------------------ skill list

// Search and filters appear once the list is this long, or when a shared link
// already has filters in it.
const FILTER_MIN = 8;
let skillView = storageGet("skillView") === "list" ? "list" : "grid";

// Categories from site/facets.json (tagged in each skill's extras/site.json),
// plus two the manifest already answers.
function allFacets() {
  return [
    ...(manifest.facets || []),
    { id: "scripts", label: "Scripts", values: [
      { id: "none", label: "Instructions only" }, { id: "has", label: "Includes scripts" }] },
    { id: "status", label: "Status", values: [
      { id: "stable", label: "Stable" }, { id: "pre-release", label: "Pre-release" }] },
  ];
}

function skillTags(skill) {
  const n = skillNeeds(skill);
  return { ...skill.tags, scripts: [n.python || n.javascript ? "has" : "none"], status: [skill.status] };
}

// Filters live in the URL (#/?task=review,drafting&q=letter) so a filtered
// list can be shared.
function readFilters(facets) {
  const params = currentQuery();
  const sel = {};
  for (const f of facets) {
    const known = new Set(f.values.map(v => v.id));
    sel[f.id] = new Set((params.get(f.id) || "").split(",").filter(v => known.has(v)));
  }
  return { q: params.get("q") || "", sel };
}

function writeFilters(state) {
  const params = new URLSearchParams();
  if (state.q.trim()) params.set("q", state.q.trim());
  for (const [id, set] of Object.entries(state.sel)) if (set.size) params.set(id, [...set].join(","));
  const qs = params.toString().replace(/%2C/g, ",");
  history.replaceState(null, "", "#/" + (qs ? "?" + qs : ""));
}

function matchesFilters(skill, state, facets) {
  const tags = skillTags(skill);
  for (const f of facets) {
    const want = state.sel[f.id];
    if (want.size && !(tags[f.id] || []).some(v => want.has(v))) return false;
  }
  const terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return true;
  const labelOf = (fid, vid) => facets.find(f => f.id === fid)?.values.find(v => v.id === vid)?.label || "";
  const text = [skill.name, skill.summary,
    ...Object.entries(tags).flatMap(([fid, vals]) => vals.map(v => labelOf(fid, v)))].join(" ").toLowerCase();
  return terms.every(t => text.includes(t));
}

function tagList(skill) {
  const labelled = (manifest.facets || []).flatMap(f =>
    (skill.tags[f.id] || []).map(v => f.values.find(x => x.id === v)?.label).filter(Boolean));
  return labelled.length && el("ul", { class: "tags", "aria-label": "Tags" },
    labelled.map(label => el("li", {}, label)));
}

function skillCard(skill, view) {
  const grid = view === "grid";
  const summaryId = `summary-${skill.id}`;
  const summary = el("p", { class: "card-summary", id: summaryId }, skill.summary);
  const more = grid && el("button", {
    type: "button", class: "read-more", hidden: true,
    "aria-expanded": "false", "aria-controls": summaryId,
    onclick: () => {
      const open = summary.classList.toggle("expanded");
      more.setAttribute("aria-expanded", String(open));
      more.firstChild.textContent = open ? "Show less" : "Read more";
    },
  }, "Read more", el("span", { class: "sr-only" }, ` about ${skill.name}`));
  // Grid cards are narrow, so the size joins the "Includes" line there.
  const [nameNode, sizeNode] = skillNameNodes(skill);
  const includes = includesLine(skill);
  if (grid) includes.append(" · ", sizeNode);
  return el("li", { class: "card" },
    el("div", { class: "card-head" },
      el("h2", {}, skill.name),
      skill.status === "pre-release" && el("span", { class: "badge" }, "Pre-release")),
    summary,
    more,
    !grid && tagList(skill),
    includes,
    el("div", { class: "actions" },
      downloadSkillButton(skill),
      el("a", { class: "btn btn-secondary", href: routeHref(skillHome(skill)),
                "aria-label": `Browse files in ${skill.name}` },
        icon("folderOpen"), "Browse files"),
      nameNode, !grid && sizeNode));
}

// Show "Read more" only on grid cards whose summary is cut off.
function updateReadMore(list) {
  for (const button of list.querySelectorAll(".read-more")) {
    const summary = button.previousElementSibling;
    if (summary.classList.contains("expanded")) continue;
    button.hidden = summary.scrollHeight <= summary.clientHeight + 1;
  }
}

function viewSwitcher(onChange) {
  const group = el("div", { class: "segmented view-switch", role: "group", "aria-label": "View" });
  const views = [["grid", "Grid"], ["list", "List"]];
  const sync = () => group.querySelectorAll("button").forEach(btn =>
    btn.setAttribute("aria-pressed", String(btn.dataset.view === skillView)));
  group.append(...views.map(([id, label]) => el("button", {
    type: "button", "data-view": id,
    onclick: () => { skillView = id; storageSet("skillView", id); sync(); onChange(); },
  }, icon(id), label)));
  sync();
  return group;
}

function skillBrowser() {
  const facets = allFacets();
  const total = manifest.skills.length;
  const state = readFilters(facets);
  const isActive = () => Boolean(state.q.trim()) || Object.values(state.sel).some(s => s.size);
  const withFilters = total >= FILTER_MIN || isActive();
  let search = null, panel = null, filterButton = null; // set below when filters show

  const list = el("ul", { class: "cards", "aria-label": "Skills" });
  const count = el("p", { class: "result-count" });
  const chips = el("div", { class: "active-filters" });
  const clearAll = () => {
    state.q = "";
    if (search) search.value = "";
    Object.values(state.sel).forEach(s => s.clear());
    panel?.querySelectorAll("input[type=checkbox]").forEach(box => { box.checked = false; });
    update(true);
  };
  const empty = el("div", { class: "empty", hidden: true },
    el("p", {}, "No skills match these filters."),
    el("button", { type: "button", class: "btn btn-secondary", onclick: clearAll }, "Clear filters"));

  let announceTimer;
  const update = (speak = false) => {
    const shown = manifest.skills.filter(s => matchesFilters(s, state, facets));
    list.className = `cards view-${skillView}`;
    list.replaceChildren(...shown.map(s => skillCard(s, skillView)));
    empty.hidden = shown.length > 0;
    count.textContent = isActive()
      ? `Showing ${shown.length} of ${total} skills`
      : `${total} skills`;
    if (withFilters) {
      writeFilters(state);
      renderChips();
      filterButton.querySelector(".label").textContent = activeCount()
        ? `Filters (${activeCount()})` : "Filters";
    }
    requestAnimationFrame(() => updateReadMore(list));
    if (speak) {
      clearTimeout(announceTimer);
      announceTimer = setTimeout(() => announce(count.textContent), 400);
    }
  };
  new ResizeObserver(() => updateReadMore(list)).observe(list);

  const view = viewSwitcher(() => update());
  if (!withFilters) {
    update();
    return [el("div", { class: "list-toolbar" }, count, view), list];
  }

  // Search and filters
  function activeCount() { return Object.values(state.sel).reduce((n, s) => n + s.size, 0); }
  const tagsOf = new Map(manifest.skills.map(s => [s.id, skillTags(s)]));
  const used = (fid, vid) => manifest.skills.filter(s => (tagsOf.get(s.id)[fid] || []).includes(vid)).length;

  search = el("input", {
    type: "search", class: "search", id: "skill-search", placeholder: "Search skills",
    autocomplete: "off", value: state.q,
    oninput: () => { state.q = search.value; update(true); },
  });
  search.value = state.q;

  panel = el("div", { class: "filter-panel", id: "filter-panel", hidden: true },
    facets.map(f => {
      const values = f.values.map(v => [v, used(f.id, v.id)]).filter(([, n]) => n > 0);
      return values.length > 0 && el("fieldset", {},
        el("legend", {}, f.label),
        values.map(([v, n]) => el("label", { class: "check" },
          el("input", {
            type: "checkbox", "data-facet": f.id, value: v.id, checked: state.sel[f.id].has(v.id),
            onchange: e => {
              state.sel[f.id][e.target.checked ? "add" : "delete"](v.id);
              update(true);
            },
          }),
          el("span", {}, v.label), el("span", { class: "count" }, `(${n})`))));
    }));

  filterButton = el("button", {
    type: "button", class: "btn btn-secondary", "aria-expanded": "false", "aria-controls": "filter-panel",
    onclick: () => {
      panel.hidden = !panel.hidden;
      filterButton.setAttribute("aria-expanded", String(!panel.hidden));
    },
  }, icon("filter"), el("span", { class: "label" }, "Filters"));

  function renderChips() {
    const items = facets.flatMap(f => [...state.sel[f.id]].map(vid => {
      const label = f.values.find(v => v.id === vid).label;
      return el("button", {
        type: "button", class: "chip chip-small", "aria-label": `Remove filter: ${f.label}, ${label}`,
        onclick: () => {
          state.sel[f.id].delete(vid);
          const box = panel.querySelector(`input[data-facet="${f.id}"][value="${vid}"]`);
          if (box) box.checked = false;
          update(true);
          (chips.querySelector("button") || search).focus();
        },
      }, label, el("span", { "aria-hidden": "true" }, " ×"));
    }));
    chips.replaceChildren(count, ...items,
      isActive() ? el("button", { type: "button", class: "link-button", onclick: () => { clearAll(); search.focus(); } }, "Clear all") : null);
  }

  update();
  return [
    el("div", { class: "list-toolbar" },
      el("label", { class: "sr-only", for: "skill-search" }, "Search skills"),
      search, filterButton, view),
    panel,
    chips,
    list,
    empty,
  ];
}

function openInstallHelp(event) {
  event.preventDefault();
  const details = document.getElementById("install-help");
  details.open = true;
  details.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  details.querySelector("summary").focus({ preventScroll: true });
}

function renderHome() {
  document.title = SITE_NAME;
  app.classList.remove("wide");
  app.replaceChildren(
    el("div", { class: "intro" },
      el("h1", { tabindex: "-1" }, "Skills for AI assistants"),
      el("p", {}, "A skill is a folder of instructions and files that teaches an AI assistant to do a specific job. ",
        "These skills use an open format, so they work in Claude, ChatGPT, Gemini, and other AI tools, ",
        "though each platform handles skills a little differently. Download a skill, then add it to the AI you use ",
        "(", el("a", { href: "#/", onclick: openInstallHelp }, "how to install a skill"), ").")),
    ...skillBrowser(),
    faq());
}

// ------------------------------------------------------------------ folders

function renderFolder({ node, skill, parts }) {
  const isHome = parts.length === 2 && inSkill(parts);
  const inMaintainer = !inSkill(parts);
  document.title = `${isHome ? skill.name : node.name} · ${SITE_NAME}`;
  app.classList.remove("wide");

  const head = el("div", { class: "page-head" },
    el("div", { class: "title-line" },
      el("h1", { tabindex: "-1" }, isHome ? skill.name : node.name + "/"),
      isHome && skill.status === "pre-release" && el("span", { class: "badge" }, "Pre-release")),
    isHome && el("p", { class: "summary" }, skill.summary),
    isHome && includesLine(skill),
    !isHome && labelFor(node) && el("p", { class: "summary" }, labelFor(node)),
    el("div", { class: "actions" },
      downloadSkillButton(skill), skillNameNodes(skill), copyLinkButton()),
    !isHome && el("p", { class: "part-of" }, "Download gets the whole ",
      el("strong", {}, skill.name), " skill."));

  const children = [...node.children];
  const view = [...navBar(breadcrumbs(parts, skill)), head];
  if (inMaintainer) view.push(maintainerNote());
  view.push(children.length
    ? rowList(children, parts)
    : el("p", { class: "status" }, "This folder is empty."));
  if (isHome) view.push(maintainerSection(skill));

  app.replaceChildren(...view.filter(Boolean));
}

function maintainerSection(skill) {
  const items = maintainerItems(skill);
  if (!items.length) return null;
  const listSlot = el("div", {});
  const input = el("input", { type: "checkbox", id: "show-maintainer" });
  input.checked = storageGet("showMaintainer") === "1";
  const update = () => {
    storageSet("showMaintainer", input.checked ? "1" : "0");
    listSlot.replaceChildren(...(input.checked
      ? [maintainerNote(), rowList(items, [skill.id])]
      : []));
  };
  input.addEventListener("change", update);
  update();
  return el("section", { class: "maintainer", "aria-label": "Maintainer files" },
    el("label", { class: "switch", for: "show-maintainer" }, input,
      el("span", { class: "switch-track", "aria-hidden": "true" }),
      "Show maintainer files"),
    listSlot);
}

// ------------------------------------------------------------------ files

const FRONTMATTER = /^\uFEFF?---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/;

// The simple YAML subset frontmatter uses: top-level `key: value` pairs,
// quoted strings, and folded or literal blocks. Mirrors build.py.
function parseFrontmatter(block) {
  const fields = [];
  let current = null;
  for (const line of block.split(/\r?\n/)) {
    const m = /^([A-Za-z_][\w-]*):(?:\s+(.*))?$/.exec(line);
    if (m && !/^\s/.test(line)) {
      let value = (m[2] || "").trim();
      current = { key: m[1], lines: [], style: null };
      if (["|", "|-", ">", ">-"].includes(value)) current.style = value[0];
      else if (/^".*"$/.test(value)) {
        try { value = JSON.parse(value); } catch { value = value.slice(1, -1); }
        current.lines.push(value);
      } else if (/^'.*'$/.test(value)) current.lines.push(value.slice(1, -1).replace(/''/g, "'"));
      else current.lines.push(value);
      fields.push(current);
    } else if (current) {
      current.lines.push(line);
    }
  }
  return fields.map(f => ({
    key: f.key,
    value: f.style === "|"
      ? f.lines.join("\n").trim()
      : f.lines.map(l => l.trim()).filter(Boolean).join(" "),
  }));
}

const SKILL_KEYS = { name: "Name", description: "When the AI uses this" };

function frontmatterBox(block, isSkillFile) {
  const fields = parseFrontmatter(block);
  return el("dl", { class: "frontmatter", "aria-label": "File details" },
    fields.map(f => [
      el("dt", {}, (isSkillFile && SKILL_KEYS[f.key]) || f.key),
      el("dd", {}, f.value),
    ]));
}

function slugify(text) {
  return text.toLowerCase().trim().replace(/[^\w\s-]/g, "").replace(/\s+/g, "-");
}

// Resolve a relative link in a Markdown file to a repo path.
function resolveLink(href, fileParts) {
  const base = "https://x/" + fileParts.slice(0, -1).map(encodeURIComponent).join("/") + "/";
  const url = new URL(href, base);
  if (url.origin !== "https://x") return null;
  return url.pathname.split("/").filter(Boolean).map(decodeURIComponent);
}

function renderMarkdown(text, fileParts, isSkillFile) {
  const body = el("div", { class: "md-body" });
  const fm = FRONTMATTER.exec(text);
  if (fm) {
    body.append(frontmatterBox(fm[1], isSkillFile));
    text = text.slice(fm[0].length);
  }
  const html = window.marked.parse(text, { gfm: true });
  body.append(window.DOMPurify.sanitize(html, { RETURN_DOM_FRAGMENT: true }));

  // The page title is the only h1, so Markdown headings move down one level.
  body.querySelectorAll("h1, h2, h3, h4, h5").forEach(h => {
    const lower = document.createElement(`h${Number(h.tagName[1]) + 1}`);
    lower.append(...h.childNodes);
    h.replaceWith(lower);
  });
  const seen = new Map();
  body.querySelectorAll("h2, h3, h4, h5, h6").forEach(h => {
    let id = slugify(h.textContent) || "section";
    const n = seen.get(id) || 0;
    seen.set(id, n + 1);
    if (n) id += `-${n}`;
    h.id = `h-${id}`;
  });

  body.querySelectorAll("a[href]").forEach(a => {
    const href = a.getAttribute("href");
    if (href.startsWith("#")) {
      const target = "h-" + slugify(decodeURIComponent(href.slice(1)));
      a.setAttribute("href", routeHref(fileParts));
      a.addEventListener("click", e => {
        e.preventDefault();
        body.querySelector(`#${CSS.escape(target)}`)?.scrollIntoView({ block: "start" });
      });
      return;
    }
    if (/^[a-z][a-z0-9+.-]*:/i.test(href)) {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.append(NEW_TAB());
      return;
    }
    const parts = resolveLink(href, fileParts);
    if (!parts) return;
    if (index.has(parts.join("/"))) {
      a.setAttribute("href", routeHref(parts));
    } else {
      a.setAttribute("href", `${manifest.repo}/blob/main/${parts.map(encodeURIComponent).join("/")}`);
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.append(NEW_TAB());
    }
  });

  body.querySelectorAll("img[src]").forEach(img => {
    const src = img.getAttribute("src");
    if (/^[a-z][a-z0-9+.-]*:/i.test(src)) return;
    const parts = resolveLink(src, fileParts);
    if (parts && index.has(parts.join("/"))) img.setAttribute("src", fileUrl(parts));
  });

  body.querySelectorAll("table").forEach(t => {
    const wrap = el("div", { class: "table-wrap" });
    t.replaceWith(wrap);
    wrap.append(t);
  });

  body.querySelectorAll("pre > code").forEach(code => {
    const pre = code.parentElement;
    const lang = /language-(\S+)/.exec(code.className)?.[1];
    if (lang && window.hljs?.getLanguage(lang)) window.hljs.highlightElement(code);
    const block = el("div", { class: "code-block" });
    pre.replaceWith(block);
    pre.tabIndex = 0; // long lines scroll sideways, so the keyboard needs to reach it
    const button = copyButton(code.textContent, "Copy", "copy", () => code,
      { class: "btn btn-small code-copy", "aria-label": "Copy code" });
    block.append(button, pre);
  });

  return body;
}

function rawView(text, node) {
  const lang = node.kind === "markdown" ? "markdown" : node.lang;
  const code = el("code", {});
  if (lang && window.hljs?.getLanguage(lang)) {
    code.className = `hljs language-${lang}`;
    // highlight.js escapes the text, so its output is safe to insert.
    code.innerHTML = window.hljs.highlight(text, { language: lang, ignoreIllegals: true }).value;
  } else {
    code.textContent = text;
  }
  const wrap = node.kind === "markdown" || node.kind === "text";
  return el("pre", { class: `raw${wrap ? " wrap" : ""}`, tabindex: "0",
                     "aria-label": `Raw text of ${node.name}` }, code);
}

function modeSwitch(current, onChange) {
  const modes = [["formatted", "Formatted"], ["split", "Side-by-side"], ["raw", "Raw"]];
  return el("div", { class: "segmented", role: "group", "aria-label": "View" },
    modes.map(([id, label]) => el("button", {
      type: "button",
      "aria-pressed": String(id === current),
      onclick: () => onChange(id),
    }, label)));
}

async function loadText(parts) {
  const key = parts.join("/");
  if (!textCache.has(key)) {
    const res = await fetch(fileUrl(parts), { cache: "no-cache" });
    if (!res.ok) throw new Error(res.status);
    textCache.set(key, await res.text());
  }
  return textCache.get(key);
}

async function renderFile({ node, skill, parts }, token) {
  document.title = `${node.name} · ${SITE_NAME}`;
  const label = labelFor(node);
  const download = el("a", { class: "btn btn-secondary", href: fileUrl(parts), download: node.name },
    icon("download"), "Download file");

  const head = el("div", { class: "page-head" },
    el("div", { class: "title-line" },
      el("h1", { tabindex: "-1" }, node.name),
      el("span", { class: "size" }, formatSize(node.bytes))),
    label && el("p", { class: "summary" }, label));
  const view = [...navBar(breadcrumbs(parts, skill)), head];
  if (!inSkill(parts)) view.push(maintainerNote());

  if (node.kind === "binary") {
    app.classList.remove("wide");
    view.push(el("div", { class: "binary-card" },
      el("span", { class: "row-icon file big" }, icon("file")),
      el("div", {},
        el("p", { class: "binary-name" }, node.name),
        el("p", { class: "size" }, `${formatSize(node.bytes)} · This file can't be shown in the browser.`),
        el("div", { class: "actions" }, download, copyLinkButton()))));
    app.replaceChildren(...view);
    return;
  }

  app.classList.add("wide");
  const content = el("div", { class: "file-content" }, el("p", { class: "status" }, "Loading…"));
  const toolbar = el("div", { class: "toolbar actions" });
  view.push(toolbar, content);
  app.replaceChildren(...view);

  let text;
  try {
    text = await loadText(parts);
  } catch {
    if (token !== renderToken) return;
    content.replaceChildren(el("div", { class: "error", role: "alert" },
      el("p", {}, "This file didn't load. Check your connection and try again, or download it."),
      el("p", {}, download)));
    return;
  }
  if (token !== renderToken) return;

  const canFormat = node.kind === "markdown" && window.marked && window.DOMPurify;
  const isSkillFile = node.name === "SKILL.md" && inSkill(parts) && parts.length === 3;

  const copyFile = copyButton(text, "Copy file", "copy", () => {
    const raw = content.querySelector("pre.raw");
    return raw && raw.offsetParent !== null ? raw : manualCopyBox(toolbar, text);
  });

  const show = mode => {
    if (canFormat) markdownMode = mode;
    const panes = [];
    if (mode === "formatted" || mode === "split") {
      panes.push(el("section", { class: "pane", "aria-label": "Formatted",
                                 tabindex: mode === "split" ? "0" : null },
        renderMarkdown(text, parts, isSkillFile)));
    }
    if (mode === "raw" || mode === "split") {
      panes.push(el("section", { class: "pane", "aria-label": "Raw" }, rawView(text, node)));
    }
    content.className = `file-content mode-${mode}`;
    content.replaceChildren(...panes);
    toolbar.replaceChildren(
      canFormat && modeSwitch(mode, show),
      el("div", { class: "toolbar-buttons" }, copyFile, download, copyLinkButton()));
  };
  show(canFormat ? markdownMode : "raw");
  if (node.kind === "markdown" && !canFormat) {
    content.prepend(el("p", { class: "note" },
      "The formatted view didn't load, so this shows the raw text."));
  }
}

// ------------------------------------------------------------------ routing

function currentParts() {
  const hash = location.hash.replace(/^#\/?/, "").split("?")[0];
  try {
    return hash.split("/").filter(Boolean).map(decodeURIComponent);
  } catch {
    return null;
  }
}

// The home page keeps its filters after a "?" in the hash.
function currentQuery() {
  const i = location.hash.indexOf("?");
  return new URLSearchParams(i < 0 ? "" : location.hash.slice(i + 1));
}

// Find the entry for a route. A bare skill id and the short form without the
// inner folder name both lead to the skill folder.
function resolve(parts) {
  const direct = index.get(parts.join("/"));
  if (direct && parts.length > 1) return { entry: direct };
  const skill = manifest.skills.find(s => s.id === parts[0]);
  if (!skill) return null;
  const long = [skill.id, skill.id, ...parts.slice(1)];
  const entry = index.get(long.join("/"));
  return entry ? { entry, redirect: long } : null;
}

function renderNotFound() {
  document.title = `Not found · ${SITE_NAME}`;
  app.classList.remove("wide");
  app.replaceChildren(el("div", { class: "error", role: "alert" },
    el("h1", { tabindex: "-1" }, "That page isn't here"),
    el("p", {}, "The file or folder may have been renamed or removed."),
    el("p", {}, el("a", { href: "#/" }, "Go to all skills"))));
}

function route() {
  const token = ++renderToken;
  document.querySelectorAll(".manual-copy").forEach(n => n.remove());
  const parts = currentParts();
  if (parts && parts.length === 0) {
    renderHome();
  } else {
    const found = parts && resolve(parts);
    if (!found) {
      renderNotFound();
    } else {
      if (found.redirect) history.replaceState(null, "", routeHref(found.redirect));
      const { entry } = found;
      if (entry.node.type === "dir") renderFolder(entry);
      else renderFile(entry, token);
    }
  }
  if (!firstRender) {
    window.scrollTo(0, 0);
    app.querySelector("h1")?.focus({ preventScroll: true });
  }
  firstRender = false;
}

function showError(message) {
  app.replaceChildren(el("div", { class: "error", role: "alert" },
    el("p", {}, message),
    el("p", {}, el("a", { href: "" }, "Reload the page"))));
}

async function start() {
  try {
    const [res, labelRes] = await Promise.all([
      fetch("manifest.json", { cache: "no-cache" }),
      fetch("labels.json", { cache: "no-cache" }),
    ]);
    if (!res.ok) throw new Error(res.status);
    manifest = await res.json();
    if (labelRes.ok) labels = await labelRes.json();
  } catch {
    showError("The list of skills didn't load. Check your connection and try again.");
    return;
  }
  indexManifest();
  const info = document.getElementById("build-info");
  info.append("Updated ", new Date(manifest.generated).toLocaleDateString(), " · ",
    el("a", { href: manifest.repo }, "Source on GitHub"));
  window.addEventListener("hashchange", route);
  route();
}

// The skip link's #app target would otherwise be read as a route.
document.querySelector(".skip-link").addEventListener("click", e => {
  e.preventDefault();
  app.focus();
});

start();

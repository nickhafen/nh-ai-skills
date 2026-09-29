// Skills site viewer. Plain JavaScript, no build step.
// Data: manifest.json and labels.json (written by build.py), fetched once on
// load. File text comes from files/<path>, fetched when a file is opened.
// Routes are hash paths so deep links work on GitHub Pages:
//   #/                                         home page
//   #/<skill>/<skill>/references/x.md          a file or folder, by its repo path
// The short form #/<skill>/references/x.md also works and is redirected.

"use strict";

const app = document.getElementById("app");
const announcer = document.getElementById("announcer");
const IS_MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
const COPY_KEYS = IS_MAC ? "⌘C" : "Ctrl+C";

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
  const parent = crumbs[crumbs.length - 2];
  return [
    el("nav", { class: "crumbs", "aria-label": "Breadcrumb" },
      el("ol", {}, crumbs.map((c, i) => el("li", {},
        i === crumbs.length - 1
          ? el("span", { "aria-current": "page" }, c.label)
          : el("a", { href: routeHref(c.parts) }, c.label))))),
    el("a", { class: "btn btn-back", href: routeHref(parent.parts) },
      icon("back"), `Back to ${parent.label}`),
  ];
}

function maintainerNote() {
  return el("p", { class: "note" },
    "Maintainer files help presenters and the people who keep the skill up to date. " +
    "They aren't part of the skill and aren't in the download.");
}

function rowList(nodes, parentParts, withLabels = true) {
  return el("ul", { class: "rows" }, nodes.map(node => {
    const parts = [...parentParts, node.name];
    const label = withLabels && labelFor(node);
    return el("li", {},
      el("a", { class: "row", href: routeHref(parts) },
        el("span", { class: `row-icon ${node.type}` }, icon(node.type === "dir" ? "folder" : "file")),
        el("span", { class: "row-text" },
          el("span", { class: "row-name" }, node.name + (node.type === "dir" ? "/" : "")),
          label && el("span", { class: "row-label" }, label)),
        node.type === "file" && el("span", { class: "row-size" }, formatSize(node.bytes))));
  }));
}

// ------------------------------------------------------------------ home

function installSteps() {
  return el("details", { class: "install" },
    el("summary", {}, "How to install a skill"),
    el("div", { class: "install-body" },
      el("section", {},
        el("h2", {}, "Claude.ai"),
        el("ol", {},
          el("li", {}, "Click ", el("strong", {}, "Download skill (.zip)"),
            " on the skill you want. Don't unzip it."),
          el("li", {}, "In Claude, go to ", el("strong", {}, "Settings > Capabilities > Skills"),
            " and choose ", el("strong", {}, "Upload skill"), "."),
          el("li", {}, "Pick the zip you downloaded."))),
      el("section", {},
        el("h2", {}, "Claude Code"),
        el("ol", {},
          el("li", {}, "Download the skill and unzip it. You get one folder named after the skill."),
          el("li", {}, "Move that folder into ", el("code", {}, "~/.claude/skills/"),
            " (on Windows, ", el("code", {}, "C:\\Users\\<you>\\.claude\\skills\\"),
            "). Create the ", el("code", {}, "skills"), " folder if it isn't there."),
          el("li", {}, "Start a new Claude Code session.")))));
}

function skillCard(skill) {
  return el("li", { class: "card" },
    el("div", { class: "card-head" },
      el("h2", {}, skill.name),
      skill.status === "pre-release" && el("span", { class: "badge" }, "Pre-release")),
    el("p", {}, skill.summary),
    el("div", { class: "actions" },
      downloadSkillButton(skill),
      el("a", { class: "btn btn-secondary", href: routeHref(skillHome(skill)),
                "aria-label": `Browse files in ${skill.name}` },
        icon("folderOpen"), "Browse files"),
      skillNameNodes(skill)));
}

function renderHome() {
  document.title = "Claude Skills for Law";
  app.classList.remove("wide");
  app.replaceChildren(
    el("div", { class: "intro" },
      el("h1", { tabindex: "-1" }, "Skills for Claude"),
      el("p", {}, "Skills teach Claude how to do a specific job. Download one, then upload it to Claude. No unzipping needed.")),
    installSteps(),
    el("ul", { class: "cards", "aria-label": "Skills" },
      manifest.skills.map(skillCard)));
}

// ------------------------------------------------------------------ folders

function renderFolder({ node, skill, parts }) {
  const isHome = parts.length === 2 && inSkill(parts);
  const inMaintainer = !inSkill(parts);
  document.title = `${isHome ? skill.name : node.name} · Claude Skills for Law`;
  app.classList.remove("wide");

  const head = el("div", { class: "page-head" },
    el("div", { class: "title-line" },
      el("h1", { tabindex: "-1" }, isHome ? skill.name : node.name + "/"),
      isHome && skill.status === "pre-release" && el("span", { class: "badge" }, "Pre-release")),
    isHome && el("p", { class: "summary" }, skill.summary),
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

const SKILL_KEYS = { name: "Name", description: "When Claude uses this" };

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

  const seen = new Map();
  body.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach(h => {
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
  document.title = `${node.name} · Claude Skills for Law`;
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
      panes.push(el("section", { class: "pane", "aria-label": "Formatted" },
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
  const hash = location.hash.replace(/^#\/?/, "");
  try {
    return hash.split("/").filter(Boolean).map(decodeURIComponent);
  } catch {
    return null;
  }
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
  document.title = "Not found · Claude Skills for Law";
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

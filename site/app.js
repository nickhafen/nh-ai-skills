// Skills site viewer. Plain JavaScript, no build step.
// Data: manifest.json (written by build.py), fetched once on load.
// Routes are hash paths so deep links work on GitHub Pages: #/ is the home page.

"use strict";

const app = document.getElementById("app");
let manifest = null;

// ------------------------------------------------------------------ helpers

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value; // trusted, static markup only
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child == null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(child));
  }
  return node;
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const ICONS = {
  download: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19h14"/></svg>',
};

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
  const size = formatSize(skill.zip.bytes);
  const download = el("a", {
    class: "btn btn-primary",
    href: skill.zip.path,
    download: `${skill.id}.zip`,
    "aria-describedby": `name-${skill.id} size-${skill.id}`,
  });
  download.innerHTML = ICONS.download;
  download.append("Download skill (.zip)");

  return el("li", { class: "card" },
    el("div", { class: "card-head" },
      el("h2", { id: `name-${skill.id}` }, skill.name),
      skill.status === "pre-release" && el("span", { class: "badge" }, "Pre-release")),
    el("p", {}, skill.summary),
    el("div", { class: "actions" },
      download,
      el("span", { class: "size", id: `size-${skill.id}` }, size)));
}

function renderHome() {
  document.title = "Claude Skills for Law";
  app.replaceChildren(
    el("div", { class: "intro" },
      el("h1", {}, "Skills for Claude"),
      el("p", {}, "Skills teach Claude how to do a specific job. Download one, then upload it to Claude. No unzipping needed.")),
    installSteps(),
    el("ul", { class: "cards", "aria-label": "Skills" },
      manifest.skills.map(skillCard)));
}

// ------------------------------------------------------------------ routing

function route() {
  // Every path shows the home page until the folder and file views exist.
  renderHome();
}

function showError(message) {
  app.replaceChildren(el("div", { class: "error", role: "alert" },
    el("p", {}, message),
    el("p", {}, el("a", { href: "" }, "Reload the page"))));
}

async function start() {
  try {
    const res = await fetch("manifest.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(res.status);
    manifest = await res.json();
  } catch {
    showError("The list of skills didn't load. Check your connection and try again.");
    return;
  }
  const info = document.getElementById("build-info");
  info.append("Updated ", new Date(manifest.generated).toLocaleDateString(), " · ",
    el("a", { href: manifest.repo }, "Source on GitHub"));
  window.addEventListener("hashchange", route);
  route();
}

start();

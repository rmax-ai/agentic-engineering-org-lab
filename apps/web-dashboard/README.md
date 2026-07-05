# Web Dashboard

Standalone HTML dashboard for the Agentic Engineering Org Lab control plane.

**`index.html`** — zero-dependency, dark-themed dashboard with:
- Task list (5 demo tasks with varied statuses)
- Pipeline visualization (GitHub Actions-style stage flow)
- Unified diff viewer (GitHub-style syntax highlighting)
- Event trace timeline (10-step audit trail)
- World model graph (4 services with readiness scores)
- Verification results panel
- AI review panel
- Merge recommendation

Open `index.html` directly in a browser — no build step, no server needed.

## Design

Following Gemini 3 Pro's control-plane dashboard guidelines:
- Three-panel layout (sidebar → task list → detail)
- Status-first coloring (green=pass, red=fail, blue=active, purple=agent, amber=blocked)
- High information density with monospace typography
- Collapsible verification/review sections
- Pipeline visualization as the signature control-plane element

## SvelteKit source (reference only)

The `src/`, `svelte.config.js`, `vite.config.ts`, `tsconfig.json`, and `package.json`
files contain SvelteKit 5 + Tailwind v4 source for the dashboard components.
These are **reference implementations** — the build pipeline hangs on adapter-static
in this environment. Use `index.html` for the deliverable; the SvelteKit source
demonstrates the component architecture.

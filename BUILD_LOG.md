# Build Log

## 2026-05-07 — v0.1: initial app, ship, expand to 40 scenarios

### Original prompt
> create a new folder called @here and build a VERY simple app that educates people on when to use @channel instead of @here. bonus points if we can have a interactive feature where users are given examples and get to choose between @here or @channel, most of the answers should be @channel, and tell them why @here is the wrong choice. phase 0 of this is checking the web for if someone else has built this

### Problem
Most people reach for `@here` in Slack because it *feels* polite — "I won't bother people who are away." But that creates information asymmetry: a random subset of the team (whoever happens to be online) gets the message and the rest are blindsided later. For most announcements, `@channel` is the right, considerate choice. Goal: a tiny educational app that drives this point home, biased so most quiz answers are `@channel`.

Phase 0 web check confirmed: blog posts exist (Vendasta, Suptask, Slack help docs), but no dedicated interactive quiz/app. Green field.

### Solution
- Single static `index.html` — no build step, no framework, no dependencies. CSS + JS embedded.
- Sections: hero + thesis, 30-second explainer, interactive quiz, takeaways.
- Quiz: 40 shuffled scenarios, one at a time, with three choices (`@here`, `@channel`, `Don't @ anyone`) and inline feedback explaining the failure mode for the wrong picks.
- Bias: 28 `@channel`, 6 `@here`, 6 "don't @" — mirrors real Slack hygiene.
- Final score screen with breakdown + restart.
- "Submit a scenario" CTA links to `CONTRIBUTING.md` with copy-pasteable JS template.

### Shipping
- Local repo: `/Users/pfrazier/Documents/claude/slack-mentions-quiz/` (originally `@here/` — renamed because `@` is not allowed in GitHub repo names or Vercel project slugs).
- GitHub: https://github.com/Paulfrazier/slack-mentions-quiz (public).
- Vercel project: `paulfraziers-projects/slack-mentions-quiz` — auto-deploys on push to `main`.
- Custom domain: `dontuseathere.shop` (Namecheap registrar). Apex + `www` both added on the Vercel project.
- DNS: `A @ → 76.76.21.21`, `CNAME www → cname.vercel-dns.com.`

### Key decisions
- **Static HTML over SPA framework.** "VERY simple" was an explicit ask. A single file is the minimum viable surface and avoids any toolchain.
- **Vercel only, not Railway.** Static file = no backend = Railway is a no-op web server. Pushed back on user's initial "ship to both" framing.
- **Phase 0 first.** Confirmed no prior art before writing code.
- **40 scenarios in random order** (vs. e.g. quizzes-of-10). User asked for it; one-at-a-time UX makes 40 questions feel less daunting than a stacked list.
- **PR-based contributions, not issues.** Linked the site CTA to `CONTRIBUTING.md`, which links straight to GitHub's web editor for `index.html`. One-click fork-and-PR.
- **Bias intentionally toward `@channel`** in the scenario bank. The pedagogical goal is to break the "polite = @here" intuition.

### Files changed (cumulative for the session)
- `index.html` — the whole app (initial 6-scenario stacked version → expanded to 40 shuffled, one-at-a-time)
- `.gitignore` — `.vercel`, `.DS_Store`
- `CONTRIBUTING.md` — template + style guidelines for new scenarios
- `BUILD_LOG.md` — this file

---

## What we learned

Process and tooling notes worth keeping for future small projects.

### Folder naming
- **`@` in a folder name is annoying.** macOS, git, and zsh all handle it fine, but every shell command needs the path quoted. GitHub repo names and Vercel project slugs forbid `@` outright. Use a normal slug for any folder you might ever push or deploy.
- The folder was created as `@here` (per the original prompt), then renamed to `slack-mentions-quiz` mid-session. The rename was painless because the GitHub remote is independent of the local folder name.

### Vercel
- **`vercel link` ≠ `vercel deploy`.** Linking creates the project shell on Vercel; it doesn't ship code. `vercel ls` returned "No deployments found" until we either pushed to the linked GitHub repo or ran `vercel --prod`.
- **Connecting GitHub to an existing Vercel project does not auto-deploy historical commits.** Triggered the first deploy with an empty commit (`git commit --allow-empty`) — verified the webhook works in the same step.
- **Vercel CLI's `vercel domains add <domain>` takes no project arg when run from inside a linked folder.** Older docs show `vercel domains add <domain> <project>`, which now errors out (`missing_arguments`).

### Namecheap DNS
- **Saving DNS is two steps in the Namecheap UI**: click the green checkmark on each edited row to commit that row, *then* hit "Save All Changes" at the bottom. We saw `dig` return nothing initially because the CNAME row was still in edit mode (orange X / green check icons visible) — not actually saved.
- **Namecheap has an XML API**, but the setup overhead (enable API access, generate key, whitelist your current IP, accept that `setHosts` replaces all records) outweighs the manual UI for a one-off DNS change.

### Deploy story for tiny static sites
- For a single static HTML file, the cheapest, most reversible path is: GitHub repo → Vercel auto-deploy → custom domain. Total time end-to-end is ~10 minutes, most of which is DNS propagation.
- No `vercel.json` needed. Vercel auto-detected "no framework" and serves `index.html` from the repo root.

### Tooling gotchas in this environment
- The gstack `/browse` headless verifier requires `bun`, which isn't installed on this machine. Fell back to `node --check` for JS syntax + manual code review for the initial HTML check. Worth installing bun if browser-based QA becomes a recurring need (`curl -fsSL https://bun.sh/install | bash`).

### About the content
- The pedagogical thesis ("most uses of `@here` are actually @channel-shaped") gets clearer when you write the *failure mode* of the wrong answer specifically (e.g. "Sarah was at lunch — she comes back to a rewritten module she owns"). Generic "@here doesn't reach everyone" feedback was less convincing than scenario-specific consequences.
- Six `@here`-correct scenarios were enough to make the rule legible: real-time, ephemeral, only useful to people online *right now*. Any more and the lesson dilutes.

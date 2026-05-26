# Build Log

## 2026-05-26 — Redesign to "click → result" (no-score endless variant)

**Prompt:** "lets redesign the quiz for fairpoint use dontuseathere as the test, thinking do away with keep score and showing user their are 40+ want it to be fast and light wait. click, get result. fun and easy."

**Problem:** The scored arcade flow made the quiz feel like a graded grind. The sticky HUD's segmented progress bar literally counted out all 40 scenarios up front (the "there are 40+" reveal), and the score/combo/grade machinery added weight to what should be a quick, fun "click → see why → next" loop.

**Solution:** Built a **dontuseathere-only variant** of the Fairpoint quiz with no scoring. The shared `fairpoint-kit` is left untouched — this is a test-first divergence. `spec.json` stays the single source of truth (its `pointsPerCorrect`/`comboStep`/`breakdownLabels` fields are simply ignored by the variant). New flow: land directly on a scenario → click an answer → instant verdict (✓/✗ + the "why") → **Next →** pulls a fresh random scenario, forever. No HUD, no score, no combo, no progress segments, no summary/grade screen. The deck is a shuffled list of all scenarios; when exhausted it reshuffles (avoiding an immediate repeat) and continues endlessly — the count is never shown. Kept the full editorial intro (h1, thesis, explainer cards, trap) and takeaways, the neobrutalist scenario card, wrong-answer shake + correct reveal, and keyboard play (1–N to answer, Enter to advance). Confetti is retained but lightened to a small per-answer burst on **correct** only, anchored at the clicked button, and skipped under `prefers-reduced-motion`.

**Mechanics:** `render.py` hardcodes the kit template and takes no template arg, so a local `build.py` reuses the kit's `validate()` + `ISLAND` regex (choice-sync invariant still enforced) but injects `spec.json` into a local `template.html` instead of the kit's. Rebuild with `bash build.sh`. To promote this design kit-wide later, diff `slack-mentions-quiz/template.html` → `fairpoint-kit/template.html`.

**Key decisions:** No new color tokens (reused DESIGN.md vars). Variant kept fully spec-compatible with the stock kit so we can revert by re-rendering through `render.py`. Confetti kept (lightly) rather than removed, since "fun" was an explicit goal — a one-line follow-up can drop it if undesired.

**Verified** (gstack headless): no console errors; no `.hud`/`#score`/`#seg`/`#combo` in DOM; scenario renders on load; wrong → coral+shake+reveal+"✗ Not quite.", correct → lime+"✓ Correct."+burst; 45 consecutive Next clicks never produced a summary and always advanced; keyboard 1/Enter works; mobile collapses to single column.

**Changed files:** `template.html` (new, local variant), `build.py` (new), `build.sh` (new), `index.html` (regenerated). `spec.json` content unchanged; `fairpoint-kit/*` untouched.

## 2026-05-25 — Re-skin to "Playful Arcade" design system

**Prompt:** "Looks great, push" — rolling out the new Fairpoint design system.

**Problem:** The quiz was clean but generic, and its engine was a hand-maintained copy of the same code duplicated across sibling sites (desync risk).

**Solution:** Converted the site to the `fairpoint-kit` data-driven template. All content now lives in `spec.json` (40 scenarios, choices `here`/`channel`/`none`, copy, takeaways), rendered into `index.html`'s `#site-config` block via `fairpoint-kit/render.py`. New look: Space Grotesk headlines, neobrutalist cards, scoring HUD with 🔥combo + segmented progress, +points popups, count-up summary with a grade, dependency-free confetti at ≥70%. Scenarios and correctness are unchanged from the prior bank.

**Key decisions:** Engine is no longer per-site code — it's the shared template; editing scenarios now means editing `spec.json` (the sync invariant is validated on render). CONTRIBUTING.md still applies but now points contributors at the `#site-config` block.

**Changed files:** `index.html` (regenerated from template), `spec.json` (new)

## 2026-05-11 — DNS settled, what we learned debugging it

### Where things ended up
- `dontuseathere.shop` and `www.dontuseathere.shop` both resolve correctly to `76.76.21.21` across all major resolvers.
- Let's Encrypt cert issued and valid (`subject=CN=dontuseathere.shop`).
- Total time from registering the domain + setting A/CNAME to fully-working HTTPS: roughly 4 days end-to-end, though the user-visible bumpy period (site flickers in/out from the browser) was only the first day.

### What was actually happening
Domain was registered Wed evening. A/CNAME records saved at Namecheap immediately. For the next ~24 hours the site would resolve sometimes and not others — looked like a transient outage. The cause:

**Namecheap's authoritative nameservers were out of sync with each other for the fresh zone.** Specifically:
- `dns2.registrar-servers.com` had the zone and returned `76.76.21.21`.
- `dns1.registrar-servers.com` had nothing and returned REFUSED.

Public resolvers (Cloudflare, Google, ISP) randomly load-balance across the listed authoritative NS. When a resolver happened to query dns2 it got the right answer and cached it; when it queried dns1 it got REFUSED. So the same browser would see the site work, then a few minutes later not work, depending on which NS its resolver hit and what the resolver did with the failure.

### Diagnostic that nailed it
Don't trust `dig +short <domain>` alone when DNS is misbehaving on a fresh domain. Query each authoritative NS directly:

```bash
for ns in dns1.registrar-servers.com dns2.registrar-servers.com; do
  echo "= $ns ="
  dig @$ns +short dontuseathere.shop A
done
```

If you get different answers from different NS, the issue is registrar-side NS sync, not your records and not "propagation" in the normal sense. There's nothing to flush — you wait for the registrar to push the zone to all its NS.

The other diagnostic that helped: DoH against Cloudflare and Google in parallel — they returned different statuses (Cloudflare: success, Google: REFUSED) at the same moment, which is a strong signal of NS-side inconsistency rather than client-side caching.

### Why Vercel's cert took the whole window
Vercel auto-issues a Let's Encrypt cert via the HTTP-01 challenge. It can't begin until DNS is *globally* resolvable, because LE's validation nodes are distributed and will fail the challenge if some can't resolve the domain. As long as resolvers were getting REFUSED from dns1, cert issuance silently waited. The cert showed up on its own once Namecheap finished syncing, with no action from us.

### Lessons for next fresh-domain bring-up
- **The first 1–24 hours of any newly-registered domain can look broken in inconsistent, confusing ways.** Don't change records, don't re-link Vercel, don't switch nameservers — just wait. Touching things in the middle of partial sync makes it harder to reason about what's broken.
- **"DNS cache" is almost never the diagnosis on day one.** REFUSED isn't cached. The issue is authoritative NS sync, not client cache.
- **Always have a stable fallback URL.** The Vercel project URL (`<project>.vercel.app`) worked continuously while the custom domain was flickering. That's what to share with anyone wanting to try the site during the bumpy window — never hand out a custom-domain URL to others until DNS is fully settled and the cert is issued.
- **Don't panic when one resolver says yes and another says no** — that's NS sync, not a bug. Confirm by querying the authoritative NS directly.

---

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

# Contributing a scenario

Got a good scenario for the quiz? Open a PR — it's a one-file change.

## TL;DR

1. Click here to edit `index.html` directly on GitHub: <https://github.com/Paulfrazier/slack-mentions-quiz/edit/main/index.html>
2. Find the `SCENARIOS` array (search for `const SCENARIOS = [`).
3. Add your scenario object — copy the template below.
4. GitHub will fork the repo and open a PR. Done.

## Template — copy and fill this in

```js
{
  q: "Your scenario as a short sentence — what someone is about to post in Slack.",
  correct: "channel", // one of: "channel", "here", "none"
  why: {
    channel: "What you'd say if the user picks @channel.",
    here: "What you'd say if the user picks @here.",
    none: "What you'd say if the user picks 'Don't @ anyone'."
  }
}
```

Paste it into `SCENARIOS` (anywhere is fine — the quiz shuffles each session).

## Style guidelines

- **Most correct answers should be `@channel`.** That's the pedagogical point: people reach for `@here` thinking it's polite, but it usually creates information asymmetry. Bias the bank that way.
- **`@here` is for the narrow case** — real-time, ephemeral, only useful to people online *right now* (e.g. "prod is down, need SRE in this thread *now*").
- **"Don't @ anyone"** is correct when the message is FYI/casual and doesn't need to interrupt anyone's day.
- **Keep `q` short.** One sentence. Quote-style works well: `"\"Pushing hotfix to main in 2 minutes — speak now.\""`
- **Keep `why` punchy.** One sentence each. Name the failure mode for the wrong answers (e.g. "Sarah was at lunch — she comes back to a rewritten module she owns.").

## Examples to study

The `SCENARIOS` array already has 40 of them — see `index.html`. Look at any of them for tone and length.

## Don't worry about

- The order in the array — the quiz shuffles every session.
- Duplicates with other scenarios — the bank is meant to grow, and similar themes from different angles are fine.
- Formatting — your editor will run prettier on save, or just match the surrounding style.

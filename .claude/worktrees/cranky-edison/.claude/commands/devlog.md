Write a new DEVLOG entry for this session and commit it.

Follow these steps exactly:

## Step 1 — Gather context

Run these commands to understand what changed this session:
- `git log --oneline -10` — recent commits
- `git diff HEAD~1 --stat` — files changed in last commit
- `git status` — any uncommitted changes
- Read the last entry in DEVLOG.md to understand where we left off

## Step 2 — Ask the user

Ask the user ONE question: "Bu session'da ne yaptın? (What did you accomplish this session?)"

Wait for their answer before continuing.

## Step 3 — Generate the DEVLOG entry

Using today's date ($CURRENT_DATE), the user's answer, and git context, write a new entry in this exact format:

```
## [YYYY-MM-DD] — <one-line session title>

**Duration:** ~Xh  (ask user if not obvious, or write ~1h as default)
**Branch:** <current branch from git>

### Done
- <bullet per accomplishment, derived from user's answer + git log>

### Blockers
- <any blockers mentioned, or "None">

### Next
1. <next priority>
2. <next priority>
3. <next priority>

### Commit
`<type>: <short imperative description>`
```

## Step 4 — Prepend to DEVLOG.md

Insert the new entry at the top of DEVLOG.md, directly below the `<!-- DEVLOG ENTRIES BELOW — newest first -->` comment line. Do NOT replace existing entries.

## Step 5 — Stage and commit

Run:
```
git add DEVLOG.md
git commit -m "<commit message from the entry's ### Commit section>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

## Step 6 — Confirm

Show the user:
1. The new DEVLOG entry (formatted)
2. `git log --oneline -5` output

Done. Session logged.

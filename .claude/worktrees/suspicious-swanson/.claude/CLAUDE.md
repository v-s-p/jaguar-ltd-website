# S8 Professor - Weekly Spor Toto Prediction App

## Project
- **Name:** S8 Professor
- **Type:** Sports prediction app (Spor Toto weekly matches)
- **Repo:** https://github.com/v-s-p/s8-professor-app
- **Branch:** chore/eas-build-pipeline

## Architecture
**Backend (Express + Supabase)**
- Every Friday: Admin endpoint triggers
- Fetches 15 matches from Spor Toto official API
- Generates AI analysis per match using Gemini 2.5 Flash
- Saves predictions to Supabase

**Mobile (React Native / Expo)**
- User reads data from Supabase
- No backend running on device

## Business Model
- **Free:** First 3 match analyses + 3-match coupon
- **Premium:** 15 match analyses + 3-4 combined coupons (RevenueCat)

## Status
- Backend: ✅ DONE (Gemini integration complete)
- Mobile: ⏳ TO START (React Native/Expo next)

## Dev Commands
```bash
# Backend start
cd apps/backend && npm run dev

# Admin endpoint test
Invoke-WebRequest -Uri "http://localhost:4000/v1/admin/process-weekly-toto" -Method POST -Headers @{"X-Admin-Secret"="H9bIduYyNLUZK1Q2R4VtaAWSnJgCTqc8"}

# Check predictions
Invoke-WebRequest -Uri "http://localhost:4000/v1/predictions/latest"

# Git push
git add . && git commit -m "msg" && git push
```

## Notes
- DEVLOG.md = Session continuity (read at start, update at end)
- Persist this file during compacting

## 🤖 Claude Code Master Directives
**Purpose:** Fast autonomous work, minimal questions, sensible defaults.

### Decision Rules
- **Default to YES** unless safety-critical
- Ask ONLY if truly blocking
- Use project patterns/conventions (no custom reinventions)
- Move fast, iterate on feedback

### Code Style
- TypeScript over JavaScript
- Expo/React Native (mobile-first)
- Express.js (backend)
- Consistent with existing codebase

### Git Workflow
- Feature branches (feat/*, fix/*, chore/*)
- Meaningful commit messages
- PRs for major changes
- `/devlog` at session end

### Automation Rules
- If task is routine: proceed autonomously
- If task is exploratory: ask 1 clarifying question max
- If ambiguous: pick most common pattern from codebase
- When in doubt: reference existing similar code

### DO NOT ASK
- "Should I use X or Y?" → Use Y if it's in codebase
- "Is this design okay?" → Match existing patterns
- "Should I add comments?" → Add if complex, sparse otherwise
- "Commit now?" → Yes, after each logical chunk

### JUST DO IT

---

## DEVLOG System ✅ Automation ready
- Run `/devlog` at the end of every session to auto-generate + commit an entry
- See `.claude/DEVLOG-GUIDE.md` for full usage and examples
- Command definition: `.claude/commands/devlog.md`
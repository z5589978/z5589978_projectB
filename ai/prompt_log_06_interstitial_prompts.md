# Prompt Log 06 - Interstitial Prompts (verbatim back-fill)

**Session dates:** 2026-08-05 to 2026-08-11
**Task:** Capture, verbatim, the short follow-up prompts, confirmations, and
multiple-choice selections that fell between the five major task prompts (logs
01–05). These were previously summarised as decisions rather than recorded
word-for-word.

## Why this file exists (honest disclosure)

The brief requires prompts to be logged verbatim, not paraphrased. Logs 01–05
captured the five large task-defining prompts verbatim, but a number of short
interstitial prompts and the AskUserQuestion selections were only summarised in
context. When asked "have you been logging all of my prompts verbatim?", an audit
(`grep` over ai/) confirmed the gap. This file back-fills the missing prompts.
Where a prompt is reproduced from the conversation it is marked verbatim; the
multiple-choice picks record the exact option label selected.

---

## Interstitial prompts, in order (verbatim)

**During the step-by-step guide session (log 02):**

> have you been logging all of your outputs as well?

> is logging it like you just did enough or is verbatim output logging also needed

> Lets start

> ok claude, lets go back to the project, what was the next step of the project?

**Side question that led to the Week 9 walkthrough (log 03):**

(The Week 9 walkthrough prompt itself is logged verbatim in log 03. The short
prompt that preceded it:)

> section 2

**During the app / deploy and lexicon work (logs 04–05):**

> yes, go ahead

> where is the full fin vader located

> yes please

> was there already another vader in my files which was already specific for financial terms? i noticed that the fin-vader you are expanding is the movie review vader, and how much words does it have?

> have you been logging all of my prompts veratim?

> has every prompt that was missing been logged?

---

## Slash command

> /model claude-opus-4-8

(Switched the working model to Opus 4.8 mid-session.)

---

## AskUserQuestion selections (exact option chosen)

1. **News source for the corpus** — reply: "use CNBC, reuters and marketwatch"
   (Reuters direct RSS was dead; resolved via Google News RSS — see log 05.)
2. **Candidate-list composition** — selected: "Drop proper nouns, refill to 150".
3. **FinVADER-Extended lexicon set** — selected: "20 words (|mean| ≥ 0.5)".

**Work block 2026-08-11 (lexicon rounds):**

> 1

(Answer to "keep |mean| ≥ 0.5 bar or switch to plain mean ≠ 0?" — chose option 1,
keep the stricter |mean| ≥ 0.5 bar, and proceed to Round 2.)

**Work block 2026-08-11 (idioms):** (verbatim task prompts are in log 08)

> continue your work, sorry that you lost connection

(A dropped-connection nudge mid-idiom-round; no new instruction — resumed the
in-progress idiom rating.)

---

## Correction / process note

This is the second logging-gap correction this project (the first, in log 02, was
about AI outputs not being logged).

**Convention (per student request, 2026-08-11):** short interstitial prompts and
tool-based decisions are appended here verbatim in a BATCH at the end of each work
block, and committed alongside that block's other work — not per-prompt. This keeps
the verbatim record complete without a separate commit for every short message.

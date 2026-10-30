<!--
Desk draft of a DEV post, 2026-10-30, session 015R6z6j5NgirQsSDf27XKub. Continues the DEV series
after "My Robot Keeps Its Receipts" (posts/ledger.md). Written in the operator's register from a
Grok half-draft the operator pasted ("This is what Grok semi drafted"); not the operator's words
until they rewrite or approve it. The invitation is the spine, as the Grok draft put it.

Title options (the operator picks):
1. Come build your own stack on a kernel that won't guess
2. Willow: a pure kernel, open add-ons, and an invitation to make real demos
3. Kernel panic: what I found when I went down to the part that can't make things up
Tags proposed: python, opensource, ai, showdev.

Checked against willow-memory/Willow main (README.md, ADDONS.md, kernel.py), 2026-10-30:
- One file, standard library only, Python 3.9+: README "One file, no dependencies"; kernel.py's
  imports are all stdlib (1,084 lines).
- No network code, held by a test: README "Local only".
- Answers are passages with file and line, up to three, or it says it doesn't know: README
  "Extractive only" and "How it works".
- A passage is served only when it holds half the question's content words: AGENTS.md "The
  kernel's rank is for answering"; the eight beats in test_kernel.py.
- Approval needs the person's key: kernel.py seals with an HMAC-SHA256 over the key (line 198).
  Grok's "cryptographic approval" is kept as "your key"; it is a keyed hash, not a public-key
  signature, so the post doesn't say "signed".
- The arrow points one way: README "the kernel never names an add-on, so it runs the same if you
  delete every one". kernel.py has no "adapters" string.
- 247 built add-ons of 470: ADDONS.md's front block for 2026-W44. Will drift; re-read before
  publishing.
- Ports in Java, TypeScript and C#, held to 4,668 shared test cases: README "Portable".
- Hash-chain limit: README "Verifiable" and LIMITS.md (a whole chain rewritten from the edit on
  isn't detected on its own). Said in the post, not hidden.
- The four demo lives (odile, hollis, teodora, bernadette) are invented people, generated
  deterministically by make_life.py. The two studies on real sources are demo/php2shell and
  demo/google-privacy-2026-10-16.

Corrected or dropped from the Grok draft, against the record:
- "The kernel stays sealed": "sealed" means an approved answer in Willow, and the kernel does
  take fixes. Replaced with what is true: it never changes for an add-on.
- "We're looking for people": the project has one maintainer; the operator's register is "I".
- "Real-life demos" kept, and made concrete: today's lives are invented, which is why real ones
  are the ask.

Short version for Reddit (r/LocalLLaMA, r/selfhosted), same facts:

  Willow is a one-file, standard-library-only Python kernel for asking questions of your own
  files. It answers only with passages from them, each with its file and line, says so when they
  don't hold an answer, and holds anything an AI suggests until you approve it with your key.
  The kernel never imports an add-on, so you can run it alone or build your own stack on it.
  I'm looking for people who want to put together their own local stack, write an add-on (223
  ideas are listed and waiting), or build a demo from a real situation so the add-ons have
  something real to be tested against.
  https://github.com/willow-memory/Willow
-->

# Come build your own stack on a kernel that won't guess

*Part of my DEV series. It started with a [benchmark for the ESCALATE answer](https://dev.to/sean_campbell_840bd62bf7e/does-your-model-know-when-it-doesnt-know-a-benchmark-for-the-escalate-answer-268o) and went on to [My Robot Keeps Its Receipts](https://dev.to/sean_campbell_840bd62bf7e/my-robot-keeps-its-receipts-3h9g).*

> *Shaking hands:* kernel, kernel, colonel, kernel.
>
> Only one of them gives orders, and it isn't the one in this post.

## The invitation first

Willow is a small kernel for private knowledge, and an open place to attach whatever you need to it.

I'm looking for people who want to:

- **put together their own local stack** from the kernel and the add-ons they actually need
- **write new add-ons**: 223 ideas are listed and waiting, and you can add your own
- **build demos from real situations**, so the add-ons have something real to be tested against

The kernel doesn't change for any of that. Everything else is open.

## What the kernel is

Most local knowledge tools try to be a complete system. Willow goes the other way.

`kernel.py` is one Python file. It uses the standard library only, has no network code, and a test keeps it that way. Point it at a folder and ask a question. You get back up to three passages from your own files, each with its file and line number. If your files don't hold the answer, it says so.

Anything from anywhere else, whether an AI model, a script or another person, is held until you approve it with your key. Every step goes into a hash-chained log you can check at any time.

```
$ git clone https://github.com/willow-memory/Willow && cd Willow
$ python kernel.py test
kernel: the eight beats held
$ python demo/odile/make_life.py
$ python kernel.py init --box odile-record --pile demo/odile/life --key odile.key
$ python kernel.py bite --box odile-record "how are the bees"
```

## The kernel's ESCALATE

This series started with one question: does your model know when it doesn't know? I built a benchmark where, on one item in five, the only right answer was `ESCALATE`.

Willow's kernel gives that answer by construction. It serves a passage only when the passage holds half of the question's content words. Loosened to a third of the words, or any two, it finds a few more passages, but it answers questions about something else several times as often. So the line stays. A folder that doesn't hold the answer gets "I don't know", not a guess.

That's the part I won't change for an add-on. Searching by meaning, reading PDFs, pointing you at where to look: those are add-ons, and they're welcome to be as clever as they like. The kernel stays the part that can't make things up.

## The arrow points one way

An add-on uses the kernel. The kernel never names an add-on. Delete every add-on and the kernel runs exactly the same.

That's why you can build your own stack. Take the kernel and add the pieces you want:

- **Reading more kinds of files:** PDFs, email, chats, calendars, office documents
- **Keeping track:** dates coming up, care logs, invoices, forecasts, flashcards
- **Privacy:** phone numbers, card numbers and keys hidden in answers, or found sitting in files
- **Assistants:** AI assistants that can ask and suggest, but never approve

There are 247 built add-ons today. Each one is a folder with its code, its tests and a card that says what it writes and whether it goes online. CI holds every add-on to its card.

## Why real demos matter most

Every add-on passes its tests. That's the easy part, and it's not enough. An add-on can pass every test on hand-made files and still be wrong on a real folder. A test written from what the code does only checks that the code does it.

The demos today are four invented lives: a beekeeper's six years of notes, and three other people whose folders are generated from a fixed seed so anyone can rebuild them. They're useful because they're messy in the ways real folders are messy. But they're still invented.

Two studies already use real sources. One asked the kernel about a pair of PHP vulnerabilities in the advisories' own words. The other checked Google's 16 October privacy policy text against the news coverage of it. Each one freezes its sources and questions before asking anything, so the result stands or falls on what anyone can rerun.

I want more of those. Your kind of situation is what I'm asking for: a club's minutes, a repair log, a small business's invoices, a research folder. Anything that gives an add-on something real to be wrong about.

## What it doesn't do

- **It doesn't generate answers.** It quotes your files. Anything an assistant suggests waits for you.
- **It doesn't need a server, an account or an API key.**
- **Its log isn't magic.** An edit to one past entry is caught, and a forged approval is never accepted. But someone who rewrites the whole chain from the edit onward and re-hashes it isn't caught by the log alone. [LIMITS.md](https://github.com/willow-memory/Willow/blob/main/LIMITS.md) says so, along with everything else it falls short of.

## Come build

- The repo: [willow-memory/Willow](https://github.com/willow-memory/Willow)
- Every add-on, built and planned: [ADDONS.md](https://github.com/willow-memory/Willow/blob/main/ADDONS.md)
- How to pick one up: [CONTRIBUTING.md](https://github.com/willow-memory/Willow/blob/main/CONTRIBUTING.md)

The kernel stays put. The rest is yours to grow.

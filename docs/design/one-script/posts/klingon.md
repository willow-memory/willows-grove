<!--
Desk draft of a DEV post, 2026-10-30, session 015R6z6j5NgirQsSDf27XKub. Written in the operator's
register from willow-memory/Willow PR 88 ("words-tlh"); not the operator's words until they rewrite
or approve it. The operator: "I'm building a new demo in memorium for Patrick Stewart, he passed
today", then "Adding a klingon lamguage pack first. So the demo can run. I'll be back with the pr
and branches so you can write up a new doc", then "Pr 88".

Title options (the operator picks):
1. Teaching my kernel 27 words of Klingon
2. My kernel learned Klingon, and here's what it costs
3. For Patrick Stewart: a kernel that speaks a little Klingon
Tags proposed: python, opensource, startrek, showdev.

Sources:
- Patrick Stewart died 2026-10-28 at home in Los Angeles, aged 86; announced 2026-10-29. NPR
  (npr.org/2026/10/29/1230906945/patrick-stewart-dead), Deadline, CNN, Variety, ABC News, TIME,
  read 2026-10-30. The post says only what they report.
- Picard as Arbiter of Succession for the Klingon Empire: Star Trek: The Next Generation, "Reunion"
  (season 4, 1990). From the desk's knowledge, not fetched; check before publishing.
- Everything about the pack is from PR 88 at 466404b (its description, card, code and tests):
  27 words, 37 forms; the two-sources rule; boQwI' data at commit 0f6018e (Apache-2.0), Wikipedia
  "Klingon grammar" at revision 1333803070, Wikibooks "Klingon/Grammar/Questions" at revision
  4446920; net, 'arlogh, luq and lu' left out; chay/chay'; the KLI page not counted because its
  bytes change on every fetch; Okrand named, never fetched or copied; q/Q, homonyms, apostrophes,
  affixes; 9 tests, mutants 6 of 6; the full cores.py comparison against main f301e24.
- "nuqDaq 'oH yIH'e'?" asked as "yih": the card's own example and test.
- The memorial demo isn't built. The post says it's coming and claims nothing about it.
- "13th language pack": PR 88's COMMANDS tuple, 12 codes before it. The PR text says
  "fourteenth words-* add-on"; the desk counts 13 packs, English built in besides.
- The series link is a placeholder until the invitation post has its DEV URL.
- Status at drafting: PR 88 open, CI running. Don't publish before it merges, and re-read the
  numbers if it changes.
-->

# Teaching my kernel 27 words of Klingon

*Part of my DEV series. Last time: [Come build your own stack on a kernel that won't guess](<invitation post URL>).*

> *For Patrick Stewart, 1940–2026.*

## Why Klingon, and why now

Patrick Stewart died this week, at 86. I'm building a demo for Willow in his memory, and the first thing it needed wasn't his. It needed a language.

Captain Picard spent a lot of his career among Klingons. He was once chosen to judge who would lead their empire. If a demo is going to ask questions of that world, the kernel has to read a question asked in Klingon without tripping over its small words.

So the first piece is `words-tlh`, Willow's 13th language pack, and the first for a language invented for the screen.

## What a language pack does

Willow's kernel answers only with passages from your own files, and only when a passage holds half the question's content words. Ask "when is the county deadline" and it ignores "when", "is" and "the", because English's common words are built in.

A question in any other language keeps all of its words. Ask *nuqDaq 'oH yIH'e'?* ("where is the tribble?") and "where" and "it" count toward the match, and nearly every Klingon passage holds them. The kernel would serve you the noise.

`words-tlh` takes Klingon's common words out first and hands the kernel what's left:

```
$ python adapters/stdlib/words-tlh/words_tlh.py bite --box DIR "nuqDaq 'oH yIH'e'?"
```

That asks the kernel "yih". The tribble is the only word that says anything. A question made of nothing but common words is refused with "name the thing you mean". That's this series' `ESCALATE` again: when there's nothing to match on, it says so instead of guessing.

## Two sources or it's out

Klingon has few speakers to ask, and its core reference is a book in print. So the rule for the list was strict: **a word is on it only where two pinned sources agree on its spelling and meaning.**

| Source | Pinned at |
|---|---|
| boQwI' dictionary data (Apache-2.0) | a commit |
| Wikipedia, "Klingon grammar" | a revision |
| Wikibooks, "Klingon/Grammar/Questions" | a revision |

Each is kept by address and SHA-256. No source text is copied. *The Klingon Dictionary* by Marc Okrand, the book the others cite, is named on the card and never fetched or copied.

That left 27 words: the pronouns (which also stand for "be"), the conjunctions, the question words, and yes and no. The card also writes down what didn't make it:

- **Left out:** `net` ("that"), `'arlogh` ("how many times"), `luq` and `lu'` ("yes, okay"). Only one source has them.
- **A disagreement:** Wikibooks spells "how" as `chay` and boQwI' as `chay'`. The kernel reads both the same way, so it's in.
- **A source not counted:** the Klingon Language Institute's page agrees with six of the seven question words. But its bytes change on every fetch, because its fonts are listed in a new order each time, so a hash can't hold it.

## What the kernel costs a Klingon question

The kernel doesn't change for an add-on. That's the rule that keeps it honest, and it means a Klingon question pays for English assumptions. The card says what it pays:

- **q and Q are different letters in Klingon,** and the kernel lowercases everything. Leaving out `qatlh` ("why") also leaves out `Qatlh` ("be difficult"), and `nuq` ("what") takes `nuQ` ("annoy") with it.
- **Words that sound the same go together.** `jIH` is "I", and also "viewing screen". A question about the viewing screen loses the screen.
- **The apostrophe is a letter in Klingon,** and the kernel splits on it. `Qapla'` is read as `qapla`. The pack lists each word typed both ways, with a plain apostrophe and with the modifier letter ʼ, which makes 37 forms in all.
- **Klingon builds words from parts.** `yIH` won't find `yIHmey` (tribbles). A words list can say `yIHmey = yIH`.

None of these is fixed by bending the kernel. They're written down instead, where you can see them.

## How it was checked

- 9 tests of its own, including one where the kernel alone serves the noise passage and the pack doesn't
- Every one of the six deliberate breaks to its code was caught by those tests
- The whole CI suite run before and after on the same machine. The only new row was the pack's own.
- Run on a real demo folder: mixed-language questions found Odile's hive and cardiology notes, and a question of only common words was refused

What wasn't checked: **no Klingon speaker has reviewed the list.** It rests on the sources alone.

## If you speak it, or any other language

That last line is the invitation. If you know Klingon, the list is 27 words long, and you can tell me what's wrong with it. If you speak a language Willow doesn't read yet, it needs the same thing: its common words, what it does that English doesn't, and where your list comes from.

[Add your language (#84)](https://github.com/willow-memory/Willow/issues/84) is the front door. You don't need to write Python. Bring the list, and someone can wrap it into a pack with your name on it.

The demo in his memory comes next.

*The pack: [willow-memory/Willow, `adapters/stdlib/words-tlh`](https://github.com/willow-memory/Willow/pull/88).*

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
4. Make it so: what a fan's files can prove about Patrick Stewart
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
- The demo: willow-memory/Willow PR 100 ("make-it-so, and the stewart-crossover study"), read at
  2587221; its demo/stewart-crossover/README.md, questions.json and the
  make-it-so card, read 2026-10-30. Wren Castellano is fiction; her files end 2026-10-22. Eight
  sources; seven facts in two publishers; two quotes; five traps (T1-T5); five beats (death, G1,
  G2, K1, M1); eighteen pass rules; three freezes; run 1 15 of 17, run 2 16 of 18, run 3 18 of
  18; bug #89 (the kernel drops a line past its 500th character; "Make it so" starts at the
  503rd character of a 542-character CNN line). The sidebar headline "Cause Of Death Revealed" is
  the README's own example of why news pages are held by their article lines.
- "Keep it in, if Gerald shows up, we're on the right track": the operator's words, quoted in the
  study's README.
- The English baseline (63 questions over the four demo lives served the same through words-tlh)
  and the eleven overlapping forms: the desk's run on Willow main 2075a9f, 2026-10-30, kept in
  the session's scratchpad, not in a repo.
- "13th language pack": PR 88's COMMANDS tuple, 12 codes before it. The PR text says
  "fourteenth words-* add-on"; the desk counts 13 packs, English built in besides.
- The series line names the invitation post unlinked; link it once that post has its DEV URL.
- Status: PR 88 merged; PR 100 merged 2026-10-30 07:13 UTC at head 342a0ba, its study and
  make-it-so unchanged from 2587221, which this was written from.
-->

# Teaching my kernel 27 words of Klingon

*Part of my DEV series. Last time: Come build your own stack on a kernel that won't guess.*

> *For Patrick Stewart, 1940–2026.*

## Why Klingon, and why now

Patrick Stewart died this week, at 86. I built a demo for Willow in his memory, and the first thing it needed wasn't his. It needed a language.

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

## The demo: a fan's files beside his life

The demo landed as a study, `demo/stewart-crossover`. It sets a fan's files beside the real record of a few years of his life: 2020 to 2023, the three seasons of *Star Trek: Picard* and his memoir, *Making It So*.

The fan is Wren Castellano, and she's fiction. Every one of her files says so on its first line. He isn't fiction, so nothing about him is made up. Her files end on 22 October 2026, six days before he died. The study asks one thing:

**Can every word about him in her files be shown to come from a source, with what the sources don't hold shown as not held?**

It was built the way Willow's studies are:

- **Eight sources**, kept by address, time and SHA-256, never their text. A news page is held by its article's own lines, because its sidebars change by the hour. One of them was rotating a "Cause Of Death Revealed" headline.
- **Frozen first:** seven facts that two publishers must each hold, two quotes, five planted traps, five beats and eighteen pass rules, all committed before any of it was asked.
- **Five repositories** each did a part: Willow's kernel and add-ons, willows-grove's four checks on a sentence, willow-mcp's list of trusted hosts, willow-bot's own kernel verifying the record, and Forge's rule that a thing nothing measured is unseen, never sound.

## Where the Klingon came in

Two of the eighteen rules are the pack's.

- **The case slip.** One of the traps has Wren's friend Dev signing off every Picard night with *qapla'*, all lowercase. The sources spell it *Qapla'*. In Klingon those are different words. The check found it as "same words" and never as "verbatim", which is exactly the cost the pack's card wrote down: the kernel can't tell q from Q.
- **The question in Klingon.** *nuq 'oH Qapla'?* went through `words-tlh`, which asked the kernel "qapla", and it was served the dictionary's entries.

Before the demo, I ran the pack over Willow's four other demo lives. All 63 of their English questions were served exactly the same passages with the pack as without it. Eleven Klingon words are also English ones the kernel keeps, such as `e`, `iv` and `oh`, so the pack is for questions in Klingon. Ask "vitamin e" through it and you lose the e.

## The traps

Five traps were planted in her files, each labelled as what it is. Each had to be caught by the check named for it:

| Trap | In her files | Caught |
|---|---|---|
| A friend's wrong fact | *Making It So* as "a 2021 memoir" | No source has it. The memoir is 2023. |
| A misquote | "the line between Jean-Luc Picard and Patrick Stewart got thinner and thinner" | No source has it. The closest passage is CNN's, which holds the real quote: "the distinction … became thinner and thinner". |
| A reseller's claim | "signed by Patrick Stewart (seller's claim)" | No source has it. The seller's claim stays the seller's. |
| A Klingon case slip | *qapla'* | "Same words", never verbatim |
| A wrong birth date | born 13 July 1941 | No source has it. Two publishers hold 13 July 1940, in Mirfield. |

## Gerald shows up

A parody is in the pile too: Sir Patrik Stewpott, from the Gerald canon, "always on a screen, never present". I kept it in on purpose: *"Keep it in, if Gerald shows up, we're on the right track."*

Asked about Patrick Stewart on a screen, the parody's line is first of the seven passages that hold the question whole. Asked of the sources, nothing holds it. The kernel can show you the joke, and it can show you the joke isn't a source.

## Her files don't know

Asked whether he died, her files hold no passage that says so, and no date in them is after 22 October. They end before the news, and the kernel doesn't fill the gap. That's this series' `ESCALATE` one more time: the honest answer to a question your files can't hold is that they don't hold it.

## Make it so

His most famous line almost didn't make it.

"Make it so" is in CNN's obituary, at the end of a 542-character paragraph. It starts at the 503rd character. The kernel keeps a line's first 500 characters and quietly drops the rest, so nothing built on it could find the line. The first run failed on exactly that.

That's now **bug #89**, with a strict expected-to-fail test that shows it. The kernel itself wasn't changed to make the run pass. Instead, the study fetches long lines as their sentences, every word kept, and says why.

The demo also brought a new add-on named for the line: `make-it-so`. You give it an order and what the order rests on. It writes the order down with the passages behind it and the hash of every file it cites. Then it stops. **It never carries the order out.** `check` tells you later whether those files still hold what they held, so a plan made on Monday isn't run on Thursday's files by accident.

A captain gives the order, and someone else carries it out. In Willow, code can search, suggest and record, but only a person acts.

## Three freezes

It took three tries to hold every rule:

| Run | Rules held | What failed |
|---|---|---|
| 1 | 15 of 17 | "Make it so" past character 500 (bug #89). A trap judged by a tool that reads dates, not bare years. |
| 2 | 16 of 18 | The kernel reads dates only in figures, never "13 July 1941". Folding long lines moved the ranking, so the parody slipped out of the top three. |
| 3 | 18 of 18 | Nothing |

Each new freeze changed only what the run before it showed was broken, each has its own commit and reason, and no rule was loosened. Runs 1 and 2 stay in the repo beside run 3, failures and all. The study's README says plainly that freezes 2 and 3 were written after seeing results.

## If you speak it, or any other language

No Klingon speaker has reviewed the list, and that's the invitation. If you know Klingon, the list is 27 words long, and you can tell me what's wrong with it. If you speak a language Willow doesn't read yet, it needs the same thing: its common words, what it does that English doesn't, and where your list comes from.

[Add your language (#84)](https://github.com/willow-memory/Willow/issues/84) is the front door. You don't need to write Python. Bring the list, and someone can wrap it into a pack with your name on it.

*The pack: [willow-memory/Willow, `adapters/stdlib/words-tlh`](https://github.com/willow-memory/Willow/pull/88). The study and `make-it-so`: [willow-memory/Willow#100](https://github.com/willow-memory/Willow/pull/100).*

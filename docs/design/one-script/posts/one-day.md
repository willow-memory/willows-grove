<!--
Desk draft of a DEV post, 2026-10-30, session 015R6z6j5NgirQsSDf27XKub. Written in the operator's
register; not the operator's words until they rewrite or approve it. The operator: "I think i want
to merge all into one post. It was one days worth of work", then "New single post, build on 170,
stop at 100". It replaces two drafts: posts/invitation.md (merged as PR 168 and 169, never
published) and posts/klingon.md (PR 170's first draft, folded in here and removed).

Title options (the operator picks):
1. One day of Willow: 67 add-ons, a language, and a goodbye
2. Make it so: one day, one kernel, and a fan's files about Patrick Stewart
3. Come build on a kernel that won't guess
4. Kernel, kernel, colonel, kernel: a day of Willow
Tags proposed: python, opensource, startrek, showdev.

The day: 2026-10-29 07:00 UTC to the merge of willow-memory/Willow PR 100 (2026-10-30 07:13 UTC,
main at eaa88b2). Willow PR 110, open at drafting, is left out by the operator's word.

Sources (each checked 2026-10-30):
- Counts: ADDONS.md on Willow main, c8d4c43 (the last commit before 2026-10-29 07:00 UTC) says
  "189 of 470 built"; eaa88b2 says "256 of 474 built". The new folders by git ls-tree between
  them: 56 in adapters/stdlib and 11 in adapters/deps, 67. git log c8d4c43..eaa88b2: 129
  non-merge commits; git diff --shortstat: 328 files, 38,357 lines added.
- Merged in the window (GitHub search, org willow-memory): Willow 73-83, 88, 92, 97-100 (17);
  willow-bot 174 and 176, with releases 175 (1.23.0) and 177 (1.24.0); willows-grove 168 and
  169. willow-mcp and forge-play/Forge: none merged.
- Add-ons named in the post are folders in that list: slack, discord, matrix, mastodon, irc,
  reddit, x-archive, notion, trello, jira, joplin, goodreads, letterboxd, family-tree, musicxml,
  screenplay, bank, budget, orders, subscriptions, livestock, hook-guard, ripgrep, ocr, pgp,
  static-search, words-tlh, make-it-so, lesson-time, pair-drift.
- README: "What it is not" from Willow README.md at eaa88b2 (PRs 76 and 78).
- known-gaps: demo/known-gaps/README.md at eaa88b2 (PR 74): twelve gaps; phase 1 failed
  (bm25 strong p = 0.787, weaker p = 0.997), phase 2 passed (strong 44 of 160 in the top 10
  against 5.55 expected, p = 5.6e-30; weaker 3 of 64 against 0.16, p = 5.6e-4).
- CI: CHANGELOG.md at eaa88b2, PR 97 ("72 of a pull request's 84 jobs", "14 to 21 minutes").
- Front doors: Willow issues 84-87; PR 92 (the form, the Languages table, packs from their
  folders); PR 98 (seven example stacks: choir, comeback, foster, maintainer, reporter,
  smallholding, teacher); willow-bot PRs 174 and 176.
- The kernel's rule (half the question's content words) and "a third of the words, or any two":
  Willow AGENTS.md, "The kernel's rank is for answering".
- Patrick Stewart died 2026-10-28 at home in Los Angeles, aged 86; announced 2026-10-29. NPR
  (npr.org/2026/10/29/1230906945/patrick-stewart-dead), Deadline, CNN, Variety, ABC News, TIME,
  read 2026-10-30. The post says only what they report.
- Picard as Arbiter of Succession for the Klingon Empire: Star Trek: The Next Generation,
  "Reunion" (season 4, 1990). From the desk's knowledge, not fetched; check before publishing.
- words-tlh: Willow PR 88 at 466404b (description, card, code, tests): 27 words, 37 forms; the
  two-sources rule; boQwI' data at commit 0f6018e (Apache-2.0), Wikipedia "Klingon grammar" at
  revision 1333803070, Wikibooks "Klingon/Grammar/Questions" at revision 4446920; net,
  'arlogh, luq and lu' left out; chay/chay'; the KLI page not counted because its bytes change
  on every fetch; Okrand named, never fetched or copied; q/Q, homonyms, apostrophes, affixes.
  "13th language pack": the 12 codes in test_contract.py before it.
- The English baseline (63 questions over the four demo lives served the same through
  words-tlh) and the eleven overlapping forms: the desk's run on Willow main 2075a9f,
  2026-10-30, kept in the session's scratchpad, not in a repo.
- The study: Willow PR 100, demo/stewart-crossover/README.md, questions.json and the make-it-so
  card, read at 2587221 and unchanged at the merge. Eight sources; seven facts in two
  publishers; two quotes; five traps; five beats; eighteen rules; three freezes; run 1 15 of 17,
  run 2 16 of 18, run 3 18 of 18. "Make it so" starts at character 503 of a 542-character CNN
  line. "Cause Of Death Revealed" is the README's own example of a rotating sidebar.
- "Keep it in, if Gerald shows up, we're on the right track": the operator, quoted in the
  study's README.
- Known bugs: BUGS.md at eaa88b2, #89 to #96 (no #92: that number is the language PR).
- Both jokes are the operator's, from this session.
-->

# One day of Willow: 67 add-ons, a language, and a goodbye

> *Shaking hands:* kernel, kernel, colonel, kernel.
>
> Only one of them gives orders, and it isn't the one in this post.

*For Patrick Stewart, 1940–2026.*

## One day

This is one day of work on Willow, from Thursday morning to Friday morning, UTC.

| | |
|---|---|
| Add-ons built | **189 → 256** (67 new) |
| Pull requests merged | 21, across three repositories |
| Commits | 129 |
| Lines added | about 38,000 |
| Known bugs written down as tests | 7 |
| Languages Willow reads | English, plus 13 packs (one of them new: Klingon) |

It started as a day of building and turned into something else partway through, when the news came that Patrick Stewart had died.

## The kernel, and what grows from it

Willow is two things. **The kernel** is one Python file, `kernel.py`. It uses the standard library only and has no network code, and a test keeps it that way. Point it at a folder and ask a question. You get back up to three passages from your own files, each with its file and line number, or it tells you your files don't hold the answer. Anything an AI model, a script or another person suggests is held until you approve it with your key, and every step goes into a hash-chained log.

It serves a passage only when the passage holds half the question's content words. Loosen that to a third of the words, or any two, and it finds a few more passages, but it answers questions about something else several times as often. So the line stays. That's the `ESCALATE` answer from my benchmark series, built into the kernel: when your files don't hold it, it says so instead of guessing.

**The add-ons** are everything else. An add-on uses the kernel, and the kernel never names an add-on. Delete every one of them and the kernel runs exactly the same.

This day's README rewrite made that the first thing you read, and added a section on what Willow is *not*:

- Not a RAG framework that tries to do everything for you.
- Not a system that generates answers: it quotes your files, and anything an assistant suggests waits for you.
- Not something that needs a server, an account or an API key.
- Not a project that hides its rules.

## 67 add-ons

Most of the day was building, in batches of thirteen. Each add-on is a folder with its code, its tests, and a card saying what it writes and whether it goes online. CI holds every one to its card.

- **More of your life as text it can search:** Slack, Discord, Matrix, Mastodon, IRC, Reddit and X archives; Notion, Trello, Jira and Joplin exports; Goodreads and Letterboxd lists; family trees, MusicXML scores and screenplays.
- **Keeping track:** bank statements, budgets, orders, subscriptions, even livestock.
- **Programs it can call:** ripgrep for big folders, OCR for photos of letters, PGP signatures, a static search page. Ripgrep's hits are checked against the kernel's own passages, so a faster tool can't quietly answer something the kernel wouldn't.
- **Guards:** `hook-guard` refuses, by rule, an AI assistant's tool call that would read your key or write the record outside the kernel.

CI got faster too. Six Python versions were 72 of a pull request's 84 jobs, so a pull request now tests on the oldest and newest, and `main` on all six.

## A study that half failed

One study this day pointed Willow at its own fleet's twelve known security gaps. Each question was written from the gap's own description and asked of the code as it was just before the fix. Did the kernel's tools find the code the fix changed?

- **Asked of the whole old tree, yes, far above chance:** 44 of 160 questions put the fixed lines in the top ten, against 5.55 expected by chance.
- **Asked to rank the changed passages themselves, no:** no better than a random order.

Both results are in the README, the failed half first. The questions were frozen before any of them were asked, so the failure is a real result and not something to quietly drop.

## Patrick Stewart

Partway through the day, the news came: Patrick Stewart had died, at 86. I wanted to build something in his memory, and the first thing it needed wasn't his. It needed a language.

Captain Picard spent a lot of his career among Klingons. He was once chosen to judge who would lead their empire. If a demo was going to ask questions of that world, the kernel had to read a question asked in Klingon.

### 27 words of Klingon

The kernel ignores English's common words ("when", "is", "the"). A question in any other language keeps all of its words. Ask *nuqDaq 'oH yIH'e'?* ("where is the tribble?") and "where" and "it" count toward the match, and nearly every Klingon passage holds them. The kernel would serve you the noise.

`words-tlh` takes Klingon's common words out first, so the kernel is asked "yih", the tribble, the only word that says anything. A question of nothing but common words is refused with "name the thing you mean".

Klingon has few speakers to ask and its core reference is a book in print, so the rule was strict: **a word is on the list only where two pinned sources agree on its spelling and meaning.** The sources were the boQwI' dictionary data, Wikipedia's "Klingon grammar" and Wikibooks' page on Klingon questions, each kept by address and SHA-256 with no text copied. Marc Okrand's *The Klingon Dictionary* is named and never copied. Twenty-seven words passed. Four that only one source had were left out. The Klingon Language Institute's own page couldn't be counted, because its bytes change on every fetch.

The kernel doesn't change for an add-on, so a Klingon question pays for English assumptions, and the card says what:

- **q and Q are different letters in Klingon**, and the kernel lowercases everything. Leaving out `qatlh` ("why") also leaves out `Qatlh` ("be difficult").
- **Words that sound the same go together.** `jIH` is "I", and also "viewing screen".
- **The apostrophe is a letter in Klingon**, and the kernel splits on it. `Qapla'` is read as `qapla`.
- **Klingon builds words from parts.** `yIH` won't find `yIHmey`, "tribbles".

On Willow's four other demo lives, all 63 English questions got the same passages with the pack as without it. Eleven Klingon words are also English ones the kernel keeps, such as `e`, `iv` and `oh`, so the pack is for questions in Klingon. Ask about "vitamin e" through it and you lose the e.

No Klingon speaker has reviewed the list. If you're one, it's 27 words long.

### A fan's files beside his life

Then the demo: a study called `stewart-crossover`. It sets a fan's files beside the real record of a few years of his life, 2020 to 2023: the three seasons of *Star Trek: Picard*, and his memoir, *Making It So*.

The fan is Wren Castellano, and she's fiction. Every one of her files says so on its first line. He isn't fiction, so nothing about him is made up. Her files end on 22 October 2026, six days before he died. The study asks one thing:

**Can every word about him in her files be shown to come from a source, with what the sources don't hold shown as not held?**

- **Eight sources**, kept by address, time and SHA-256, never their text. A news page is held by its article's own lines, because its sidebars change by the hour. One of them was rotating a "Cause Of Death Revealed" headline.
- **Frozen first:** seven facts that two publishers must each hold, two quotes, five planted traps, five beats and eighteen pass rules, all committed before any of it was asked.
- **Five repositories** each did a part: Willow's kernel and add-ons, willows-grove's checks on a sentence, willow-mcp's list of trusted hosts, willow-bot's own kernel verifying the record, and Forge's rule that a thing nothing measured is unseen, never sound.

Five traps were planted in her files, and each was caught by the check named for it:

| Trap | In her files | Caught |
|---|---|---|
| A friend's wrong fact | *Making It So* as "a 2021 memoir" | No source has it. The memoir is 2023. |
| A misquote | "the line between Jean-Luc Picard and Patrick Stewart got thinner and thinner" | No source has it. The closest passage is CNN's, with the real quote: "the distinction … became thinner and thinner". |
| A reseller's claim | "signed by Patrick Stewart (seller's claim)" | No source has it. The seller's claim stays the seller's. |
| A Klingon case slip | *qapla'*, all lowercase | "Same words", never verbatim: the q/Q cost the pack's card wrote down |
| A wrong birth date | born 13 July 1941 | No source has it. Two publishers hold 13 July 1940, in Mirfield. |

Asked in Klingon, *nuq 'oH Qapla'?* went through the pack and was served the dictionary's entries.

### Gerald shows up

A parody is in the pile too: Sir Patrik Stewpott, "always on a screen, never present". I kept it in on purpose: *"Keep it in, if Gerald shows up, we're on the right track."*

Asked about Patrick Stewart on a screen, the parody's line is first of the seven passages that hold the question whole. Asked of the sources, nothing holds it. The kernel can show you the joke, and it can show you the joke isn't a source.

### Her files don't know

Asked whether he died, her files hold no passage that says so, and no date in them is after 22 October. They end before the news, and the kernel doesn't fill the gap.

### Make it so

His most famous line almost didn't make it.

"Make it so" is in CNN's obituary, at the end of a 542-character paragraph. It starts at the 503rd character. The kernel keeps a line's first 500 characters and quietly drops the rest, so nothing built on it could find the line, and the first run failed on exactly that. It's now **bug #89**, with a test that shows it. The kernel wasn't changed to make the run pass. The study fetches long lines as their sentences instead, every word kept, and says why.

It took three runs to hold every rule: 15 of 17, then 16 of 18, then 18 of 18. Each new freeze changed only what the run before it showed was broken, and none loosened a rule. Runs 1 and 2 stay in the repo beside run 3, failures and all.

The demo also brought an add-on named for the line: `make-it-so`. You give it an order and what the order rests on. It writes the order down, with the passages behind it and the hash of every file it cites, and then it stops. **It never carries the order out.** Later, `check` tells you whether those files still hold what they held, so a plan made on Monday isn't run on Thursday's files by accident.

A captain gives the order, and someone else carries it out. In Willow, code can search, suggest and record, but only a person acts.

## What broke

A day like this finds things. Seven known bugs went into the repo as tests that fail on purpose, each one strict, so a fix can't go unnoticed:

| Bug | What goes wrong |
|---|---|
| #89 | A line's text past its 500th character is never read |
| #90 | A search of the folder holding the key is allowed |
| #91 | A command that runs the kernel's seal is allowed, and seal reads the key |
| #93 | `amounts` drops a scale word, so $5 billion and $5 million both print as $5 |
| #94 | `stack` counts an add-on's "none found" as a flagged step |
| #95 | A date inside a web address dates the line around it |
| #96 | `propose` exits 0 when every suggestion is refused |

Two of them, #90 and #91, are about the key, the one thing no code is ever supposed to touch. Writing them down is the first step to fixing them.

## Come build

By the end of the day Willow had four front doors, each an issue that tells you how to start:

- **[Add your language (#84)](https://github.com/willow-memory/Willow/issues/84).** There's a form now. You don't need to write Python: bring the common words, what your language does that English doesn't, and where your list comes from, and someone can wrap it into a pack with your name on it. ADDONS.md keeps a table of the 13 built and the ones waiting.
- **[Build an add-on (#85)](https://github.com/willow-memory/Willow/issues/85).** 218 ideas are listed and waiting. A draft pull request that names one is how you claim it.
- **[Build a demo from a real situation (#86)](https://github.com/willow-memory/Willow/issues/86).** That means an invented life, like the four already there, or a study on public sources, like the one above. Never your own private files.
- **[Show your stack (#87)](https://github.com/willow-memory/Willow/issues/87).** Tell us which add-ons you run and what's missing. Seven example stacks are there to start from: choir, comeback, foster, maintainer, reporter, smallholding and teacher.

The bot behind the repo helps too. A new idea or language issue gets its entry for the list written out, ready to paste into a pull request. It never opens the pull request itself.

The kernel stays put. The rest is yours to grow.

- The repo: [willow-memory/Willow](https://github.com/willow-memory/Willow)
- Every add-on, built and planned: [ADDONS.md](https://github.com/willow-memory/Willow/blob/main/ADDONS.md)
- What it falls short of: [LIMITS.md](https://github.com/willow-memory/Willow/blob/main/LIMITS.md)

---

*A colonel, a corn kernel, and an operating-system kernel walk into a bar.*

*The bartender asks what they'll have.*

*The colonel orders for everyone without consulting the table.*

*The corn kernel claims kinship and asks for bourbon.*

*The computer kernel considers the question for a long time.*

*"I can't," it says at last. "Nothing present contains half the words."*

*The bartender sets a glass of water in front of it anyway.*

*The kernel holds the glass carefully and waits for the key.*

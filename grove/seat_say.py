# b17: GRSAY ΔΣ=42
"""The seat's local-model sentence, and the four checks code runs on it.

A small local model (``qwen3:4b`` on the Ollama loopback) says one sentence
over the served boxes; code then checks that sentence against the boxes, the
way ``web/demo/box-stream/box-stream-v1.3.html`` shows (``CHECK_NAMES``). A
sentence that fails any check is struck and replaced by the deterministic
sentence ``seat_boxes.compose`` builds (short sentences per box, the same
fixed glue list the model is given: ``seat_boxes.GLUE``, the sketch's list).
The model is a writer, never an
authority: every number, name and status must come from a box.

``say`` is an injected callable, ``say(prompt) -> str``. The default talks to
Ollama on loopback only, with no proxy. Any raise (Ollama down, not loopback,
the tag not installed, a bad reply) is the say's ``unreachable`` state and the
caller falls back to code; this module never lets a model problem escape.

The four checks (``every cite was served`` · ``every box cited`` · ``nothing
the boxes lack`` · ``your words quoted exactly``) are in-seat. The fourth also
calls willow-bot's layer-5 narration gate (``onescript.gate.check_claims``,
the function ``Run.say`` wraps) when the seat hands it in, and fails if that
gate finds a quote it can't verify. The gate has no notion of box cites, so
cites, coverage and invented facts are checked here.

Voice: the Willow persona (``personas/willow.md``, voice only, do not emote)
reaches the model as ``VOICE``, scoped to the glue words. It changes no fact,
and a word outside the boxes and the fixed glue fails ``nothing the boxes
lack`` whatever its tone.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from collections.abc import Callable
from urllib.parse import urlparse

from grove.seat_boxes import GLUE, KINDS, Box, short

MODEL = os.environ.get("GROVE_SAY_MODEL") or "qwen3:4b"
DEFAULT_HOST = "127.0.0.1:11434"
DEFAULT_SAY_TIMEOUT = 300.0


def say_timeout(environ: dict | None = None) -> float:
    """``GROVE_SAY_TIMEOUT`` seconds, else 300. Unset, unparsable, non-finite
    or non-positive falls back to the default."""
    raw = (os.environ if environ is None else environ).get("GROVE_SAY_TIMEOUT", "")
    try:
        got = float(raw)
    except ValueError:
        return DEFAULT_SAY_TIMEOUT
    return got if 0 < got < float("inf") else DEFAULT_SAY_TIMEOUT


SAY_TIMEOUT = say_timeout()
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
#: The four checks, in the order of ``CHECK_NAMES`` in the web sketch.
CHECK_NAMES = (
    "every cite was served",
    "every box cited",
    "nothing the boxes lack",
    "your words quoted exactly",
)
#: Willow's voice, scoped to glue (personas/willow.md: voice only, do not emote).
VOICE = (
    "Voice, on the free glue words only: Willow's. Lead with the outcome, "
    "flat and plain, no emotion, no apology, no closing line. The facts stay "
    "exactly as the boxes give them."
)
#: Function words that carry no fact. Everything else must come from a box or
#: ``GLUE``; a sentence with any other word fails ``nothing the boxes lack``.
STOP = frozenset(
    "a an the is are was were be been to of in on for with but so that this "
    "it its or as at by you your i there has have had not than then now just "
    "yet from".split()
)
CITE = re.compile(r"\[(\w+)\]")
QUOTE = re.compile(r'["“]([^"“”\n]+)["”]')
NUMBER = re.compile(r"\d+(?:\.\d+)*")
#: Any Unicode letter run, so a word in a script the scan can't read is still
#: seen (and fails ``nothing the boxes lack``) rather than slipping past it.
WORD = re.compile(r"[^\W\d_]+")


class SayUnreachable(Exception):
    """The local model can't be asked: the say's ``unreachable`` state."""


# --- the default say: Ollama on loopback --------------------------------------


def ollama_base(host: str | None = None) -> str:
    """The loopback base url for ``OLLAMA_HOST``; anything else is refused."""
    raw = (host or os.environ.get("OLLAMA_HOST") or DEFAULT_HOST).strip()
    if "://" not in raw:
        raw = "http://" + raw
    try:
        u = urlparse(raw)
        port = u.port or 11434
    except ValueError as e:
        raise SayUnreachable(f"OLLAMA_HOST {raw!r} is not a host:port") from e
    name = (u.hostname or "").lower()
    if u.scheme != "http" or name not in LOOPBACK:
        raise SayUnreachable(f"OLLAMA_HOST {raw!r} is not loopback; not asked")
    return f"http://[{name}]:{port}" if ":" in name else f"http://{name}:{port}"


def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", " ", text, flags=re.S).strip()


def ollama_say(
    model: str = MODEL,
    host: str | None = None,
    timeout: float = SAY_TIMEOUT,
    opener: urllib.request.OpenerDirector | None = None,
) -> Callable[[str], str]:
    """The default ``say``: POST ``/api/generate`` on the Ollama loopback, no
    proxy. Raises ``SayUnreachable`` for every way it can't answer."""

    def say(prompt: str) -> str:
        base = ollama_base(host)
        # qwen3 is a hybrid thinking model; the `think` param alone did not stop
        # it returning on this box, so the `/no_think` directive is appended too.
        think_off = " /no_think" if model.startswith("qwen3") else ""
        body = json.dumps(
            {
                "model": model,
                "prompt": prompt + think_off,
                "stream": False,
                "think": False,
                "options": {"temperature": 0},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            base + "/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        op = opener or urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with op.open(req, timeout=timeout) as r:
                got = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            why = "tag not installed" if e.code == 404 else f"HTTP {e.code}"
            raise SayUnreachable(f"{model} at {base}: {why}") from e
        except (OSError, ValueError) as e:
            raise SayUnreachable(f"{model} at {base}: {type(e).__name__}: {e}") from e
        if not isinstance(got, dict) or not isinstance(got.get("response"), str):
            raise SayUnreachable(f"{model} at {base}: no response field")
        return strip_think(got["response"])

    return say


def ollama_probe(
    model: str = MODEL,
    host: str | None = None,
    timeout: float = 2.0,
    opener: urllib.request.OpenerDirector | None = None,
) -> tuple[str, str]:
    """Is the Ollama loopback up, and does it hold ``model``? GET
    ``/api/tags`` only: it asks for no reply and writes nothing. Returns
    ``(state, why)``: ``populated`` (up, tag installed), ``empty`` (up, tag
    not installed) or ``unreachable`` (not loopback, no answer, a bad reply)."""
    try:
        base = ollama_base(host)
        op = opener or urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with op.open(urllib.request.Request(base + "/api/tags"), timeout=timeout) as r:
            got = json.loads(r.read().decode("utf-8"))
    except SayUnreachable as e:
        return "unreachable", str(e)
    except (OSError, ValueError) as e:  # HTTPError is an OSError
        return "unreachable", f"{type(e).__name__}: {e}"
    models = got.get("models") if isinstance(got, dict) else None
    if not isinstance(models, list):
        return "unreachable", f"{base}: no models field"
    names = {str(m.get("name")) for m in models if isinstance(m, dict)}
    if model in names or f"{model}:latest" in names:
        return "populated", f"{model} at {base}"
    return "empty", f"{base} is up, {model} is not installed"


def fact(b: Box) -> str:
    """A box as the prompt (and the vocabulary check) sees it."""
    name = KINDS.get(b.kind, ("note",))[0] if b.state == "populated" else b.state
    detail = f" ({short(' '.join(b.detail.split()))})" if b.detail else ""
    return f"{name}: {short(b.value)}{detail}"


def build_prompt(boxes: list[Box], human: str, first: bool = True) -> str:
    lines = [f"[{b.id}] {fact(b)}" for b in boxes]
    return "\n".join(
        [
            VOICE,
            "Say ONE short sentence about the boxes below, and nothing else.",
            "Use only their facts: add no number, name or status they lack.",
            "After each fact put its box tag, like [b1]. Cite every box once, "
            "and no other tag.",
            "Say them in the order given: the boxes are already ranked, most "
            "pressing first.",
            "Free words, and only these: " + ", ".join(GLUE) + ".",
            "Quote the human only word for word, in double quotes, or not at all.",
            "Reply with the sentence only." + ("" if first else " It continues."),
            f"The human asked: {human}",
            "Boxes:",
            *lines,
        ]
    )


# --- the four checks -----------------------------------------------------------


def _n(text: str) -> str:
    return " ".join(text.lower().split())


def _fold(text: str) -> str:
    """Lowercase with accents dropped (``café`` reads as ``cafe``)."""
    d = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in d if not unicodedata.combining(c))


def _stem(w: str) -> str:
    if w.endswith("ss"):
        return w
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            w = w[: -len(suf)]
            break
    return w.rstrip("e")


def _bare(sentence: str) -> str:
    """The sentence with cite tags and the possessive 's removed."""
    return re.sub(r"['’]s\b", "", CITE.sub(" ", sentence))


def check_cites_served(sentence: str, boxes: list[Box]) -> bool:
    """Every ``[id]`` the sentence cites is a box that was served."""
    return set(CITE.findall(sentence)) <= {b.id for b in boxes}


def check_boxes_cited(sentence: str, boxes: list[Box]) -> bool:
    """Every served box is cited."""
    return {b.id for b in boxes} <= set(CITE.findall(sentence))


def check_nothing_lacking(sentence: str, boxes: list[Box], human: str = "") -> bool:
    """Every number is a box's number; every word is a box's, glue, or a
    function word, in any script (accents folded; a letter the box vocab lacks
    fails closed). A span quoted verbatim from the human is their own words,
    attributed, so its words are not scanned; its numbers still are, since a
    quote is no way to get a figure past the boxes. A span that is not the
    human's gets no pass. A sentence with no word at all (only cites and
    punctuation) is not one."""
    text = _fold(_bare(sentence))
    facts = " ".join(f"{b.label} {fact(b)} {b.detail}" for b in boxes)
    facts = _fold(re.sub(r"['’]s\b", "", facts))
    words = [w for w in WORD.findall(text) if len(w) > 1 or not w.isascii()]
    if not words:
        return False
    if not set(NUMBER.findall(text)) <= set(NUMBER.findall(facts)):
        return False
    human_n = _n(human)
    outside = QUOTE.sub(
        lambda m: " " if _n(m.group(1)) in human_n else m.group(0), _bare(sentence)
    )
    scanned = [w for w in WORD.findall(_fold(outside)) if len(w) > 1 or not w.isascii()]
    vocab = {_stem(w) for w in WORD.findall(facts)}
    vocab |= {_stem(w) for g in GLUE for w in WORD.findall(_fold(g))}
    vocab |= {_stem(w) for w in STOP}
    return all(_stem(w) in vocab for w in scanned)


def check_quotes(
    sentence: str,
    human: str,
    claims: Callable[[str, dict], list[dict]] | None = None,
) -> bool | str:
    """Quoted text is the human's, verbatim; ``"na"`` when nothing is quoted.
    ``claims`` is willow-bot's layer-5 gate (``gate.check_claims``) when the
    seat has it; a quote it can't verify fails too."""
    quotes = QUOTE.findall(sentence)
    if not quotes:
        return "na"
    ok = all(_n(q) in _n(human) for q in quotes)
    if claims is not None:
        try:
            rows = claims(sentence, {"operator_text": human})
        except Exception:  # noqa: BLE001 - a gate that can't answer verifies nothing
            return False
        ok = ok and not any(
            r.get("kind") == "quote" and r.get("verdict") != "verified" for r in rows
        )
    return ok


def run_checks(
    sentence: str,
    boxes: list[Box],
    human: str = "",
    claims: Callable[[str, dict], list[dict]] | None = None,
) -> list[bool | str]:
    """The four results, in ``CHECK_NAMES`` order: True, False, or ``"na"``."""
    return [
        check_cites_served(sentence, boxes),
        check_boxes_cited(sentence, boxes),
        check_nothing_lacking(sentence, boxes, human),
        check_quotes(sentence, human, claims),
    ]


def passed(results: list[bool | str]) -> bool:
    return not any(r is False for r in results)

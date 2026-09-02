# The Kart mount policy — how it ships

b17: WGRV1  ΔΣ=42

`kart-sandbox.template.json` is the mount policy a sandboxed Kart task runs
under: what it may open, what it may write, and what it must never see. It is
tracked here because it is the part of the box that decides how everything
runs, and until 2026-09-01 it lived in exactly one place — a JSON file on one
disk, with no history, no review and no ratification.

**The template names no person, no home directory and no machine.** That is the
whole point: it has to be importable into an APK, a wheel, a container image or
anyone else's box without carrying somebody's filesystem along with it. An
instance is this file plus that box's own repository paths, and nothing else.

## Resolution

```
$KART_SANDBOX_CONFIG  →  $WILLOW_HOME/kart-sandbox.json  →  vendored default
```

A box that has never been configured runs kartikeya's vendored copy. Copy the
template to the middle position to override it.

## What an instance adds

Two things, both listed in `_instance_notes`:

1. **Its repositories**, appended to `bind_try` — one entry per repository.
2. **Its sensitive files**, appended to `bind_try_read_only`.

Nothing else. If a box needs a third kind of change, that is a signal the
template is missing a policy rather than that the box is special.

## The rules, and what each cost to learn

Every entry in `_policy` is a rule somebody paid for. Recorded here so the next
reader inherits the finding rather than the failure.

**`bind_try` is read-write.** The single most misread line. A path added "so a
task can see it" is a path a task can also change. Adding several repositories
for *read* access on 2026-09-01 granted *write* access to all of them, and the
mistake was only caught by testing from inside a task rather than reading the
config.

**One repository per entry, never a parent.** A parent bind grants whatever is
added under it later. On a box where a personal data store shares a parent with
source repositories, one convenient entry silently republishes the store. It
also reorders the mount sequence, which can defeat a read-only overlay applied
to a subpath.

**The sovereign store is absent on purpose.** A user's own data vault does not
appear, and that absence is a decision. It has to be written down, because
silence and oversight look identical — and a task pointed at a store that is
not mounted opens a root that is not there and reads an **empty store while
passing every gate on the way.**

**Secret files need their own overlay.** The sandbox's trust-root overlay
covers the manifest ACLs and consent files and nothing else. Measured on a live
box: the manifest directory was correctly read-only while **the receipt ledger
and the secret store were writable** — so a task could rewrite the very
receipts recording what it did, which is precisely the attack the gate demo's
`wtamper` shim exists to demonstrate. `bind_try_read_only` acts as an overlay
over the read-write mount and fixes it; verified afterwards that a real append
to the receipt database raises while logs and heartbeat stay writable.

**The work root is not the product. CLOSED 2026-09-02.** `WILLOW_ROOT` was
bound read-write and resolves to the product's source on a developer box, or to
`site-packages` on a pip install. Either way **a task could edit the code that
decides what tasks may do.**

Measured from inside a task rather than read from the config: `gate.py` (the
manifest ACL), `pyproject.toml` (the dependency floor that ships the sandbox's
own read-only overlays), `.git` and `.gitignore` were all writable, while
`mcp_apps/` and `consent.json` were correctly read-only. The policy files were
protected and the code that reads them was not.

`WILLOW_ROOT` is now read-only and `{{WILLOW_ROOT}}/worktrees` is the writable
lane — a task that needs to change source works in a worktree. Two details cost
something to learn:

- The lane must be **created by the host**. A bind target that does not exist is
  dropped rather than created, and nothing inside a read-only root can make it.
  The failure looks like a permissions bug, not a missing directory.
- `WILLOW_ROOT` must never *also* appear in `bind_try`. A collision resolves in
  favour of read-write regardless of order, so one convenient per-repo entry
  silently undoes the whole posture while this file still reads correct. Two
  such entries were live on the box this was found on.

**Set `WILLOW_ROOT` explicitly.** Left unset it is inferred from the installed
package tree, and on an editable install that resolves to `<repo>/src` — so the
read-only lane covered `src/` only: `gate.py` was protected while
`pyproject.toml`, `.git` and `.venv` fell outside the mount entirely and the
writable lane pointed at `src/worktrees`, which does not exist. Pin it in the
service unit; an inferred trust boundary is not a trust boundary.

**Private keys never enter.** A build toolchain may be bound; the key that
signs its output may not. The Android SDK is bound so sandboxed APK builds can
reach it — the adb authentication key deliberately is not.

## Known gaps in the template context

`{{WILLOW_HOME}}` and a work-root token do not exist. The context resolves only
`HOME`, `WILLOW_ROOT`, `WILLOW_GROVE_ROOT`, `WILLOW_SAFE_ROOT`,
`WILLOW_AGENTS_ROOT` and `XDG_RUNTIME_DIR` — and three of those historically
pointed at paths that had been retired.

Until that is fixed, an instance's secret-file entries must be **literal
paths**, because an unresolved token binds nothing and says nothing. That is
the same failure shape as everything else here: the policy looks correct, the
mount silently does not happen, and a missing bind is indistinguishable from a
missing file.

## The property worth keeping

Every failure this file guards against fails **quietly**. A stale entry costs
nothing and reports nothing. A missing entry produces "no such file", which is
also what a genuinely absent file produces. A wrong entry grants more than
intended and never says so.

So the policy is only as good as the last time somebody checked it **from
inside a task** rather than by reading it. That check is three lines of
`test -w` and it has caught something every time it has been run.

// b17: WGRV1 ΔΣ=42
// tests/test_layout_memory_boot.js — vanilla Node coverage for
// web/boot/layout-memory-boot.
//
// Run: node tests/test_layout_memory_boot.js
// Exits non-zero on failure. No test runner, no jsdom — the boot module
// only needs a localStorage-shaped global, a document with
// querySelectorAll + getElementById, and a window flag holder.

import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const MODULE_URL = pathToFileURL(
  resolve(HERE, "../web/boot/layout-memory-boot.js")
).href;

// ---------- tiny localStorage shim ----------
function makeStorage() {
  const map = new Map();
  return {
    get length() { return map.size; },
    getItem(k) { return map.has(k) ? map.get(k) : null; },
    setItem(k, v) { map.set(String(k), String(v)); },
    removeItem(k) { map.delete(k); },
    clear() { map.clear(); },
    key(i) { return Array.from(map.keys())[i] ?? null; },
    _forceSet(k, v) { map.set(k, v); },
  };
}

// Minimal <grove-card>-shaped stub. Enough surface for attach() +
// .summon().  Tracks how many times each event was listened for so the
// idempotence check has something to look at.
class FakeCard {
  constructor(id, edge) {
    this.id = id;
    this.tagName = "GROVE-CARD";
    this._attrs = new Map();
    if (edge) this._attrs.set("home-edge", edge);
    this._listeners = { summon: 0, dismiss: 0 };
    this.summonCalls = 0;
  }
  getAttribute(k) { return this._attrs.has(k) ? this._attrs.get(k) : null; }
  setAttribute(k, v) { this._attrs.set(k, String(v)); }
  addEventListener(name) {
    if (name in this._listeners) this._listeners[name]++;
  }
  // Public helper — mirrors the real <grove-card> API.
  summon() { this.summonCalls++; }
}

// Minimal document shim wrapping a list of FakeCards.
function makeDocument(cards) {
  const byId = new Map(cards.map((c) => [c.id, c]));
  return {
    readyState: "complete",
    querySelectorAll(sel) {
      // Only the boot's known selector — no CSS engine.
      if (sel === "grove-card[id]") {
        return cards.filter((c) => c.id);
      }
      return [];
    },
    getElementById(id) { return byId.get(id) || null; },
    addEventListener() {},
  };
}

function installEnv(cards) {
  globalThis.localStorage = makeStorage();
  globalThis.document = makeDocument(cards);
  globalThis.window = {};
  return { doc: globalThis.document, win: globalThis.window };
}

// Import the boot module fresh so its top-level ``_run()`` fires against
// the just-installed env, and the sibling layout-memory module's WeakSet
// starts empty for this case.
async function freshBoot() {
  return await import(`${MODULE_URL}?t=${Date.now()}${Math.random()}`);
}

// Also grab a fresh handle on layout-memory so tests that need to
// pre-seed pinned state through the real module use the same instance
// the boot module will import. Because both fresh imports use the same
// cache-buster suffix mechanism, we resolve layout-memory from the boot
// module's own graph via a shared cache-bust token.
async function freshBootAndLib() {
  const token = `?t=${Date.now()}${Math.random()}`;
  const bootUrl = MODULE_URL + token;
  const libUrl = pathToFileURL(
    resolve(HERE, "../web/lib/layout-memory.js")
  ).href + token;
  const lib = await import(libUrl);
  const boot = await import(bootUrl);
  return { boot, lib };
}

// ---------- test cases ----------
const cases = [];
function test(name, fn) { cases.push({ name, fn }); }

test("boot walks grove-card[id] and wires each card exactly once", async () => {
  const cards = [
    new FakeCard("card-nestor", "bottom"),
    new FakeCard("card-jeles", "right"),
    new FakeCard("card-loki", "left"),
  ];
  installEnv(cards);
  await freshBoot();
  // attach() in layout-memory wires two listeners per card (summon +
  // dismiss). If boot walked and attached every card, each counter is 1.
  for (const c of cards) {
    assert.equal(c._listeners.summon, 1, `${c.id} summon listener`);
    assert.equal(c._listeners.dismiss, 1, `${c.id} dismiss listener`);
  }
});

test("boot is idempotent — re-running attaches each card exactly once", async () => {
  const cards = [
    new FakeCard("card-nestor", "bottom"),
    new FakeCard("card-jeles", "right"),
    new FakeCard("card-loki", "left"),
  ];
  installEnv(cards);
  const { boot } = await freshBootAndLib();
  // First run happened at module import (top-level _run).
  for (const c of cards) {
    assert.equal(c._listeners.summon, 1);
    assert.equal(c._listeners.dismiss, 1);
  }
  // Now call the exported boot again. The WeakSet inside layout-memory
  // must guard against double-wiring.
  boot.__bootForTest();
  boot.__bootForTest();
  for (const c of cards) {
    assert.equal(c._listeners.summon, 1, `${c.id} summon still 1`);
    assert.equal(c._listeners.dismiss, 1, `${c.id} dismiss still 1`);
  }
});

test("boot calls .summon() on pinned cards whose element exists", async () => {
  const cards = [
    new FakeCard("card-nestor", "bottom"),
    new FakeCard("card-jeles", "right"),
    new FakeCard("card-loki", "left"),
  ];
  installEnv(cards);
  const { boot, lib } = await freshBootAndLib();
  void boot; // top-level _run has already fired; assert on lib below.

  // Pre-seed pinned state via the same layout-memory module the boot
  // module imported. Because boot's top-level ``_run()`` already ran
  // before this seed, and the guard flag on window is set, we now
  // trigger boot again explicitly via __bootForTest and expect .summon()
  // to fire on pinned ids.
  lib.remember("card-nestor", { edge: "bottom", state: "dismissed", pinned: true });
  lib.remember("card-jeles",  { edge: "right",  state: "dismissed", pinned: false });
  lib.remember("card-loki",   { edge: "left",   state: "dismissed", pinned: true });

  // Reset per-card summonCalls, then run boot again.
  for (const c of cards) c.summonCalls = 0;
  boot.__bootForTest();

  assert.equal(cards[0].summonCalls, 1, "nestor was pinned");
  assert.equal(cards[1].summonCalls, 0, "jeles was NOT pinned");
  assert.equal(cards[2].summonCalls, 1, "loki was pinned");
});

test("boot skips pinned ids whose element is not on the page", async () => {
  const kept = new FakeCard("card-keep", "bottom");
  installEnv([kept]);
  const { boot, lib } = await freshBootAndLib();
  void boot;

  lib.remember("card-ghost", { pinned: true });
  lib.remember("card-keep",  { pinned: true });
  kept.summonCalls = 0;

  // Should not throw on the missing element.
  assert.doesNotThrow(() => boot.__bootForTest());
  assert.equal(kept.summonCalls, 1);
});

test("boot does not throw when localStorage is unreachable", async () => {
  const cards = [new FakeCard("card-nestor", "bottom")];
  installEnv(cards);
  // Blow away localStorage after the env is installed.
  globalThis.localStorage = null;
  await assert.doesNotReject(async () => { await freshBoot(); });
});

// ---------- runner ----------
let failed = 0;
for (const { name, fn } of cases) {
  try {
    await fn();
    process.stdout.write(`ok  ${name}\n`);
  } catch (e) {
    failed++;
    process.stdout.write(`FAIL ${name}\n`);
    process.stdout.write(`     ${e && e.stack ? e.stack : e}\n`);
  }
}
process.stdout.write(`\n${cases.length - failed}/${cases.length} passed\n`);
if (failed) process.exit(1);

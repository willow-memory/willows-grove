// b17: WGRV1 ΔΣ=42
// tests/test_layout_memory.js — vanilla Node coverage for web/lib/layout-memory.
//
// Run: node tests/test_layout_memory.js
// Exits non-zero on failure. No test runner, no jsdom — the module only
// needs a localStorage-shaped global and an EventTarget with getAttribute /
// setAttribute for its attach() side.

import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const MODULE_URL = pathToFileURL(resolve(HERE, "../web/lib/layout-memory.js")).href;

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
    // test helpers (not part of the localStorage contract):
    _map: map,
    _raw(k) { return map.get(k); },
    _forceSet(k, v) { map.set(k, v); },
  };
}

// Fresh module import per test — module holds a WeakSet of attached
// elements and a warned-keys Set; we want each case to start clean.
async function freshModule() {
  return await import(`${MODULE_URL}?t=${Date.now()}${Math.random()}`);
}

function installStorage() {
  const store = makeStorage();
  globalThis.localStorage = store;
  return store;
}

// Minimal <grove-card>-shaped stub: has id, attribute bag, dispatches
// events via EventTarget. Enough surface for attach().
class FakeCard extends EventTarget {
  constructor(id) {
    super();
    this.id = id;
    this._attrs = new Map();
  }
  getAttribute(k) { return this._attrs.has(k) ? this._attrs.get(k) : null; }
  setAttribute(k, v) { this._attrs.set(k, String(v)); }
  fire(name, detail) {
    this.dispatchEvent(new (globalThis.CustomEvent || class extends Event {
      constructor(type, init) { super(type, init); this.detail = init && init.detail; }
    })(name, { detail, bubbles: true }));
  }
}

// ---------- test cases ----------
const cases = [];
function test(name, fn) { cases.push({ name, fn }); }

test("remember + recall round-trip", async () => {
  installStorage();
  const mod = await freshModule();
  mod.remember("chat", { edge: "top", state: "summoned", pinned: true });
  const got = mod.recall("chat");
  assert.deepEqual(got, { edge: "top", state: "summoned", pinned: true });
});

test("remember merges patches on the same card", async () => {
  installStorage();
  const mod = await freshModule();
  mod.remember("chat", { edge: "left" });
  mod.remember("chat", { state: "primary" });
  assert.deepEqual(mod.recall("chat"), { edge: "left", state: "primary" });
});

test("remember rejects garbage fields", async () => {
  installStorage();
  const mod = await freshModule();
  mod.remember("chat", { edge: "sideways", state: "wat", pinned: "sure" });
  assert.equal(mod.recall("chat"), null);
});

test("recall on absent key returns null", async () => {
  installStorage();
  const mod = await freshModule();
  assert.equal(mod.recall("nothing-here"), null);
});

test("recall on corrupted JSON returns null (does not throw)", async () => {
  const store = installStorage();
  const mod = await freshModule();
  store._forceSet(mod.KEY_PREFIX + "broken", "{ not json ::");
  assert.doesNotThrow(() => mod.recall("broken"));
  assert.equal(mod.recall("broken"), null);
});

test("attach persists on summon event", async () => {
  installStorage();
  const mod = await freshModule();
  const card = new FakeCard("chat");
  card.setAttribute("home-edge", "bottom");
  mod.attach(card);
  card.setAttribute("state", "summoned");
  card.fire("summon", { state: "summoned" });
  assert.deepEqual(mod.recall("chat"), { edge: "bottom", state: "summoned" });
});

test("attach persists on dismiss event", async () => {
  installStorage();
  const mod = await freshModule();
  const card = new FakeCard("chat");
  card.setAttribute("home-edge", "right");
  mod.attach(card);
  card.fire("dismiss");
  assert.deepEqual(mod.recall("chat"), { edge: "right", state: "dismissed" });
});

test("attach applies remembered edge + state on wire-up", async () => {
  installStorage();
  const mod = await freshModule();
  mod.remember("chat", { edge: "left", state: "primary" });
  const card = new FakeCard("chat");
  mod.attach(card);
  assert.equal(card.getAttribute("home-edge"), "left");
  assert.equal(card.getAttribute("state"), "primary");
});

test("attach is idempotent — second attach does not double-wire listeners", async () => {
  installStorage();
  const mod = await freshModule();
  const card = new FakeCard("chat");
  card.setAttribute("home-edge", "top");
  mod.attach(card);
  mod.attach(card);
  let fires = 0;
  const origAdd = card.addEventListener.bind(card);
  card.addEventListener = (...args) => { fires++; return origAdd(...args); };
  // Now fire summon once — recall should reflect exactly one write.
  card.fire("summon", { state: "summoned" });
  assert.deepEqual(mod.recall("chat"), { edge: "top", state: "summoned" });
  // The second attach shouldn't have added anything after the guard.
  assert.equal(fires, 0);
});

test("forget removes the key", async () => {
  installStorage();
  const mod = await freshModule();
  mod.remember("chat", { edge: "top", state: "summoned" });
  assert.ok(mod.recall("chat"));
  mod.forget("chat");
  assert.equal(mod.recall("chat"), null);
});

test("pinned() returns only pinned ids", async () => {
  installStorage();
  const mod = await freshModule();
  mod.remember("chat", { edge: "top", state: "summoned", pinned: true });
  mod.remember("weather", { edge: "bottom", state: "summoned" }); // no pinned
  mod.remember("fleet", { edge: "left", state: "idle", pinned: true });
  mod.remember("dismissed-thing", { state: "dismissed", pinned: false });
  const got = mod.pinned().sort();
  assert.deepEqual(got, ["chat", "fleet"]);
});

test("pinned() ignores non-namespaced keys in localStorage", async () => {
  const store = installStorage();
  const mod = await freshModule();
  store._forceSet("some-other-app:foo", JSON.stringify({ pinned: true }));
  mod.remember("chat", { pinned: true });
  assert.deepEqual(mod.pinned(), ["chat"]);
});

test("write silently drops when storage throws (no exception surfaces)", async () => {
  // Storage that throws on setItem — simulates quota / private mode.
  const throwing = {
    length: 0,
    getItem: () => null,
    setItem: () => { throw new Error("QuotaExceeded"); },
    removeItem: () => {},
    key: () => null,
  };
  globalThis.localStorage = throwing;
  const mod = await freshModule();
  assert.doesNotThrow(() => mod.remember("chat", { edge: "top", state: "summoned" }));
});

test("recall silently returns null when storage getItem throws", async () => {
  const throwing = {
    length: 0,
    getItem: () => { throw new Error("SecurityError"); },
    setItem: () => {},
    removeItem: () => {},
    key: () => null,
  };
  globalThis.localStorage = throwing;
  const mod = await freshModule();
  assert.equal(mod.recall("chat"), null);
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

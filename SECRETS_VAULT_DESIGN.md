# Secrets Vault Card — Design Specification
## Fractal Build: Shell → Data → Behavior → Polish

---

## 1. SHELL PHASE ✅ (Infrastructure Complete)

**Status: Click path already exists. Ready for testing.**

### Current state
- Card defined in `cards.py` line 111 (CardDef id="secrets", label="Secrets Vault")
- Card appears in `card_grid.py` BUILTIN_CARDS (line 44, order=4)
- Navigation mapped in `card_grid.py` _CARD_NAV (line 31: "secrets" → "#pane-secrets")
- Pane imported in `app.py` line 48: `from panes.secrets import SecretsPane`
- Pane composed in `app.py` line 552: `SecretsPane(id="pane-secrets")`
- Navigation handler exists: `app.py` on_card_activated → _show_internal_pane("#pane-secrets")

### What works
- Click "Secrets Vault" card → triggers CardActivated message
- Message routed to on_card_activated → calls _show_internal_pane("#pane-secrets")
- Pane displays with empty/placeholder state

### What needs fixing
- **panes/secrets.py line 18**: reads `~/.willow/secrets.json` as plain JSON
- **Problem**: secrets.json is Fernet-encrypted (by willow-1.9/core/vault.py)
- **Fix**: Import Vault class from willow-1.9, decrypt before parsing

---

## 2. DATA PHASE

**Display existing secrets (names only, set/not-set status, redacted prefix)**

### Architecture
```
~/.willow/vault.db
    ↓ (SQLite, Fernet-encrypted)
Vault.list_keys() + Vault.read(key) [from willow-1.9/core/vault.py]
    ↓ (decrypted values)
_read_secrets() → [{"key": str, "hint": str, "set": bool}]
    ↓
DataTable(columns=["Key", "Status", "Prefix"])
    ↓
SecretsPane renders
```

### Implementation
1. **sys.path setup** — Add willow-1.9 to sys.path at app startup
2. **Import Vault** from core.vault
3. **Decrypt secrets** using Vault.list_keys() (list all keys) + Vault.read(key) for each
4. **Enrich metadata**:
   - `set` field: True if value exists and non-empty
   - `hint` field: first 8 chars + "…" (redacted)
   - `state` field: "green" if set, "dim" if not
5. **Update DataTable columns**:
   - "Key" (e.g., "ANTHROPIC_API_KEY")
   - "Status" (green "●" if set, dim "○" if not)
   - "Prefix" (e.g., "sk-an…" redacted)

### Blocking Questions
- **sys.path approach**: Add willow-1.9 to sys.path in app.py (or in panes/secrets.py)? Or import via environment variable / alternate path?
- **Lazy import**: Should Vault be imported at pane mount time (lazy) or at app startup (eager)? Lazy is safer if willow-1.9 is unavailable.

---

## 3. BEHAVIOR PHASE

**Interactive "Add Secret" form using script-first approach**

### User flow
1. User presses action binding (tbd: "a" for add, or buttons in pane)
2. Modal interview launches (similar to CardBuilderModal pattern)
3. Form asks:
   - "What secret do you want to store?" (free text: key name)
   - "Paste the value" (masked input, never echoed)
   - Confirmation: "Store `KEY_NAME`?"
4. On confirm:
   - Call Vault.write(key, value)
   - Re-fetch and display updated list
   - Show success message

### Architecture
- **SecretsAddModal** (new file: `widgets/secrets_add_modal.py`)
  - Input for key name (validated: must not exist, must be valid env var format)
  - Masked input for secret value
  - Confirmation flow
  - Calls Vault.write() and refreshes parent

- **SecretsPane enhancements**
  - Action binding: pressing "a" → spawn SecretsAddModal
  - Refresh hook: on modal close, refresh DataTable

---

## 4. POLISH PHASE

**UX refinements, error handling, edge cases**

### Features
- Delete/revoke secret action (confirm before removal)
- Search/filter secrets by key name
- Show creation date / last updated
- Reveal action: temp show value in masked dialog (with timer auto-hide)
- Export secrets manifest (keys only, for backup)
- Status card display logic:
  - `value`: "N secrets" or count of set keys
  - `state`: "green" if ≥1 set, "dim" if all empty
  - `sub`: "X set, Y empty" or similar

---

## Key Files Affected

| File | Change | Reason |
|------|--------|--------|
| `panes/secrets.py` | Fix decryption; add refresh logic | Core data display |
| `widgets/secrets_add_modal.py` | Create new | Interview-style form |
| `app.py` | Register modal; handle modal close | Wiring |
| `cards.py` | Add value/state_query runtime logic | Dashboard card display |
| `willow-1.9/core/vault.py` | Read (no changes) | Dependency for encryption/decryption |

---

## Implementation Order

1. **Shell verify** (5 min): Click card, see pane display
2. **Data fix** (15 min): Add Vault import, fix decryption
3. **Behavior** (30 min): Modal form + write path
4. **Polish** (20 min): Actions, search, reveal, status display

---

## Testing

- [ ] Card visible in grid
- [ ] Card click shows SecretsPane
- [ ] SecretsPane displays existing secrets (names + status)
- [ ] "Add Secret" opens modal
- [ ] Can type key name and value
- [ ] Confirm writes to vault
- [ ] List refreshes after add
- [ ] Secrets persist across pane close/reopen
- [ ] Dashboard card shows count and state

---

**b17: SAPS1 ΔΣ=42**

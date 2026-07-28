# u2u/contacts.py
# b17: U2UC1
"""U2U contact store — ~/.willow/grove_contacts.json"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional


CONSENT_FIELDS = ("consent_note", "consent_ask", "consent_alert", "consent_share")


@dataclass
class Contact:
    """A known u2u peer.

    Consent is opt-IN. Every ``consent_*`` flag defaults to False, so a newly
    admitted contact can deliver nothing until the operator grants a specific
    permission. Previously note/ask/share defaulted to True, which made simply
    being in the contact store equivalent to full consent.
    """

    addr: str
    public_key_hex: str
    name: str = ""
    blocked: bool = False
    consent_note: bool = False
    consent_ask: bool = False
    consent_alert: bool = False
    consent_share: bool = False
    added: str = ""
    resources: dict | None = None


class ContactStore:
    def __init__(self, path: Path):
        self._path = Path(path)
        self._contacts: dict[str, Contact] = {}
        if self._path.exists():
            self._load()

    def _load(self):
        try:
            raw = json.loads(self._path.read_text())
            for addr, data in raw.items():
                self._contacts[addr] = Contact(**data)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Cannot load contacts from {self._path}: {e}") from e

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(
            {addr: asdict(c) for addr, c in self._contacts.items()},
            indent=2,
        ))

    def add(self, addr: str, public_key_hex: str, name: str = "") -> Contact:
        """Admit a NEW contact.

        Refuses to touch an address that is already known. Re-running the
        ``Contact(...)`` constructor over an existing entry silently reset
        every field to its default — clearing ``blocked`` and re-granting
        consent — which turned any re-KNOCK into a trust reset. Use
        :meth:`update_key` to rotate a key deliberately.
        """
        if addr in self._contacts:
            raise ValueError(
                f"contact {addr!r} already exists — use update_key() to rotate "
                f"its key; add() would reset blocked and consent flags"
            )
        c = Contact(
            addr=addr, public_key_hex=public_key_hex, name=name,
            added=datetime.now(UTC).isoformat(),
        )
        self._contacts[addr] = c
        self.save()
        return c

    def update_key(self, addr: str, public_key_hex: str) -> bool:
        """Rotate an existing contact's key, mutating ONLY the key.

        ``blocked``, every ``consent_*`` flag, ``name``, ``added`` and
        ``resources`` are preserved. Returns False for an unknown address —
        key rotation never creates a contact.
        """
        contact = self._contacts.get(addr)
        if contact is None:
            return False
        contact.public_key_hex = public_key_hex
        self.save()
        return True

    def set_consent(self, addr: str, **flags: bool) -> bool:
        """Grant or revoke consent on an existing contact, one flag at a time.

        Consent is opt-in, so this is the only way a contact ever gains a
        permission — nothing on the wire may grant one. Unknown flag names are
        rejected rather than silently ignored. Returns False for an unknown
        address; it never creates a contact.
        """
        unknown = set(flags) - set(CONSENT_FIELDS)
        if unknown:
            raise ValueError(f"unknown consent flag(s): {sorted(unknown)}")
        contact = self._contacts.get(addr)
        if contact is None:
            return False
        for name, value in flags.items():
            setattr(contact, name, bool(value))
        self.save()
        return True

    def get(self, addr: str) -> Optional[Contact]:
        return self._contacts.get(addr)

    def block(self, addr: str) -> bool:
        if addr in self._contacts:
            self._contacts[addr].blocked = True
            self.save()
            return True
        return False

    def all(self) -> list[Contact]:
        return list(self._contacts.values())

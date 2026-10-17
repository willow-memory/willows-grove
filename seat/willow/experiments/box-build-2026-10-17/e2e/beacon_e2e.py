"""A stand-in drand for the e2e boxes (W4 break 1, R23a).

A table forecast names a drand round the operator's reader (`api.Config.beacon`)
can NOT read yet; its session must be seeded by that round's randomness, and
one-script checks it with the same reader. Offline, this reader plays drand:

  * `latest` is the newest round out. It starts at the round current at NOW
    (the suites' clock), and every round at or below it is out and readable
    (its randomness, unless set in `rounds`, is SHA-256 of "drand:<round>").
  * `commit(randomness)` schedules the next round past `latest` with that
    randomness, fixed before any die and NOT out yet: a forecast may name it.
  * a scheduled round is not out, and not served, until `fire(round)`; the
    suites fire it when a forecast's session starts (`fired_round`), after
    the forecast's tip seal, as drand's clock would. Firing moves `latest` up
    to it. (R23a: the forecast door refuses a round the reader serves.)
  * a round past `latest` with nothing scheduled has not fired: reading it
    raises, and one-script says `unreachable`.

A seed chosen after `commit` (a ground seed, a reseed) is not the round's,
which is the point.
"""

from __future__ import annotations

import hashlib

from onescript import beacon

NOW = "2026-10-17T00:00:00Z"


class FakeDrand:
    BY_BOX: dict = {}  # box path -> its stand-in, for a config whose reader was replaced

    def __init__(self, box=None) -> None:
        if box is not None:
            FakeDrand.BY_BOX[str(box)] = self
        self.rounds: dict[int, str] = {}
        self.latest = beacon.round_at(NOW)
        self.next = self.latest + 10
        self.fired: set[int] = set()

    def commit(self, randomness: str) -> int:
        """The next round, whose randomness (64 hex) is now fixed, not yet out."""
        rnd, self.next = self.next, self.next + 1
        self.rounds[rnd] = randomness
        return rnd

    def __call__(self, rnd) -> dict:
        if rnd == "latest":
            return {"round": self.latest}
        if rnd in self.rounds and (rnd in self.fired or rnd <= self.latest):
            return {"round": rnd, "randomness": self.rounds[rnd]}
        if isinstance(rnd, int) and 0 < rnd <= self.latest:
            return {
                "round": rnd,
                "randomness": hashlib.sha256(f"drand:{rnd}".encode()).hexdigest(),
            }
        raise LookupError(f"round {rnd} has not fired in this stand-in")

    def fire(self, rnd: int) -> None:
        """A scheduled round `rnd` is out: served from now on, and `latest`
        reaches it. A round with nothing scheduled never fires here."""
        if rnd in self.rounds:
            self.fired.add(rnd)
            self.latest = max(self.latest, rnd)

    @classmethod
    def of(cls, cfg):
        """The box's stand-in: its config's reader, else the one made for its box."""
        return (
            cfg.beacon if isinstance(cfg.beacon, cls) else cls.BY_BOX.get(str(cfg.box))
        )


def fired_round(cfg, forecast: dict) -> int:
    """The forecast's round, fired now: a session that answers a forecast
    starts only once its round is out."""
    rnd = forecast["row"]["table"]["beacon_round"]
    drand = FakeDrand.of(cfg)
    if drand is not None:
        drand.fire(rnd)
    return rnd


def table_forecast(cfg, world_key: dict, seed: str) -> dict:
    """`api.forecast(table=...)` for a forecast whose session `seed` will play:
    the world key plus the round whose randomness is that seed."""
    return {**world_key, "beacon_round": cfg.beacon.commit(seed)}

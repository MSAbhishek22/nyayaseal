"""Walrus adapter layer — the seam between NyayaLedger and Walrus.

Two implementations of one interface::

    store_blob(bytes) -> blob_id (str)
    read_blob(blob_id) -> bytes
    status() -> dict

* ``LocalVaultAdapter`` — the real backend today. A content-addressed
  store on local disk (``data/blobs/<sha256>``); the hash IS the address,
  exactly as a Walrus blob id addresses content. Every receipt carries
  ``backend: "local-vault"``.

* ``WalrusTestnetAdapter`` — STUB. Its store/read methods raise
  ``NotImplementedError``. It is never used by the server and no fake
  Walrus blob id is ever produced.

Why the stub (probed from this sandbox, 10 Nov 2026, ~5 minutes,
read-only, no secrets, no account creation):
  - Aggregator (read path) IS reachable:
    ``https://aggregator.walrus-testnet.walrus.space/v1/blobs/<id>``
    returns a structured Walrus error for an unknown blob
    (``BLOB_NOT_FOUND``, HTTP 404) — the testnet itself is live.
  - Publisher (write path) ``https://publisher.walrus-testnet.walrus.space/``
    is reachable but returns 404 on read paths, and storing a blob
    requires a SUI payment via a funded wallet / publisher endpoint.
    This sandbox has no wallet, no SUI, and the rulebook forbids
    account creation, spending and credential sharing — so the store
    path was NOT attempted.
  - No free, no-wallet, no-card, no-account testnet store path was
    found. When one exists (funded testnet wallet + publisher URL),
    implement ``WalrusTestnetAdapter.store_blob`` to PUT bytes to the
    publisher and return the real Walrus blob id, and flip the server
    over only after a live round-trip test.
"""

from __future__ import annotations

from app.vault import BACKEND_LABEL, Vault

TESTNET_BLOCKER = (
    "Walrus testnet not connected: storing a blob needs a funded SUI "
    "wallet / publisher endpoint — no wallet, no account, no card in "
    "this sandbox (rulebook: no spending, no account creation). "
    "Aggregator read path probed live 10 Nov 2026 and reachable "
    "(BLOB_NOT_FOUND for unknown ids); publisher store path not attempted."
)


class LocalVaultAdapter:
    """Real backend: local content-addressed store. Hash = address."""

    backend = BACKEND_LABEL

    def __init__(self, vault: Vault):
        self.vault = vault

    def store_blob(self, data: bytes) -> str:
        return self.vault.store_blob(data)

    def read_blob(self, blob_id: str) -> bytes | None:
        return self.vault.read_blob(blob_id)

    def status(self) -> dict:
        return {
            "backend": BACKEND_LABEL,
            "connected": True,
            "adapter": "LocalVaultAdapter",
            "store": "local content-addressed blobs (data/blobs/<sha256>)",
            "walrus_testnet": "not connected",
            "walrus_blocker": TESTNET_BLOCKER,
            "note": "Hash = address, same as a Walrus blob id. Swap in "
                    "WalrusTestnetAdapter when a funded testnet wallet exists.",
        }


class WalrusTestnetAdapter:
    """STUB — Walrus testnet. Not connected; never fakes a blob id."""

    backend = "walrus-testnet (not connected)"

    def __init__(self, publisher_url: str | None = None,
                 aggregator_url: str | None = None):
        self.publisher_url = publisher_url
        self.aggregator_url = aggregator_url

    def store_blob(self, data: bytes) -> str:
        raise NotImplementedError(
            "testnet not connected — needs a funded wallet / publisher "
            "endpoint; not attempted")

    def read_blob(self, blob_id: str) -> bytes:
        raise NotImplementedError(
            "testnet not connected — needs a funded wallet / publisher "
            "endpoint; not attempted")

    def status(self) -> dict:
        return {
            "backend": "walrus-testnet (not connected)",
            "connected": False,
            "adapter": "WalrusTestnetAdapter (stub)",
            "walrus_testnet": "not connected",
            "walrus_blocker": TESTNET_BLOCKER,
        }

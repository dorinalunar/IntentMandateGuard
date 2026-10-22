# 🛡️ IntentMandateGuard (GenLayer Intelligent Contract)

![GenLayer](https://img.shields.io/badge/Network-GenLayer_Studio-blueviolet?style=for-the-badge)
![Smart Contract](https://img.shields.io/badge/Contract-Python_GenVM-blue?style=for-the-badge&logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/Pytest-Passing-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**IntentMandateGuard** is an autonomous GenLayer Intelligent Contract that enforces bounded, non-transferable semantic execution mandates and issues cryptographic single-use intent tickets verified via decentralized LLM consensus.

Principals can delegate operational authority to automated agents or operators under strict natural-language policy rules, method allowlists, and deterministic quota caps—ensuring that no downstream action executes unless every semantic constraint is satisfied with `PASS` and `solid` certainty.

---

## ✨ Key Architectural Features

* **Semantic Policy Firewall (`evaluate_rules_nondet`):** Evaluates up to 6 natural-language mandate rules against structured intent payloads (`method`, `target`, `payload`), actively neutralizing prompt-injection attempts.
* **Equivalence Principle Consensus:** Employs `gl.vm.run_nondet_unsafe` so Leader and Validator nodes independently verify the complete assessment matrix (`index`, `outcome`, `certainty`) before locking quota.
* **Deterministic Quota Escrow:** Approved tickets atomically reserve `weight` and transaction counts from the parent mandate until redeemed by the designated `executor` or released upon expiration.
* **Cryptographic Intent Anchoring:** Generates a canonical SHA-256 `proof_hash` binding the chain ID, contract address, mandate ID, sequence nonce, executor, and exact intent payload.

---

## 📂 Payload Schema Formats

### 1. Mandate Rules & Method Allowlist
```json
{
  "rules": [
    "Maximum slippage mentioned in the payload must not exceed 50 basis points.",
    "Target resource must belong to the approved vault://usdc-eth namespace."
  ],
  "methods": ["rebalance_pool", "harvest_yield"]
}
```

### 2. Execution Intent Payload (`intent_json`)
```json
{
  "method": "rebalance_pool",
  "target": "vault://usdc-eth-main",
  "payload": "Execute liquidity rebalance of 2,500 USDC into ETH pool with max slippage of 30 basis points."
}
```

---

## 🚀 Contract Lifecycle & Methods

1. **`register_mandate`**: Principal registers an `operator`, `executor`, `rules_json`, `methods_json`, `quota_cap`, `tx_cap`, and `ttl_seconds`.
2. **`issue_ticket`**: Operator submits an `intent_json` and `seq_nonce`. GenVM validators audit the intent against all mandate rules. If every rule returns `PASS` + `solid`, quota is locked and ticket state becomes `ACTIVE`.
3. **`redeem_ticket`**: Designated executor consumes an `ACTIVE` ticket by supplying the matching `intent_json`, finalizing quota expenditure and returning the cryptographic `proof_hash`.
4. **`cancel_reservation` / `terminate_mandate`**: Reclaims locked quota from expired/unredeemed tickets or permanently halts a mandate.

---

## 🧪 Running Local Tests

```bash
pip install -r requirements.txt
pytest test_mandate_guard.py -v
```

---

<div align="center">
  <h3>Architected by Andrii (@dorinalunar)</h3>
  <p><i>Decentralized AI & GenLayer Intelligent Contract Engineering</i></p>
</div>

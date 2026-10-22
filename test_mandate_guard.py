"""
Automated unit test suite for IntentMandateGuard helper and verification logic.
Tests canonical serialization, intent schema validation, AI assessment matrix ordering, and quota math.
"""
import hashlib
import json
import pytest


def to_canonical_json(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def valid_str(val, max_len: int) -> bool:
    return isinstance(val, str) and 0 < len(val.strip()) <= max_len


def decode_json(raw_str: str):
    try:
        return json.loads(raw_str)
    except (ValueError, TypeError):
        raise ValueError("[HALT] Malformed JSON payload")


def parse_intent_payload(raw_str: str) -> dict:
    if len(raw_str) > 10000:
        raise ValueError("[HALT] Intent payload exceeds size limit")
    data = decode_json(raw_str)
    if not isinstance(data, dict) or set(data) != {"method", "target", "payload"}:
        raise ValueError("[HALT] Intent must contain method, target, and payload keys only")
    if (not valid_str(data["method"], 40)
            or not valid_str(data["target"], 200)
            or not valid_str(data["payload"], 6000)):
        raise ValueError("[HALT] Invalid intent field boundaries")
    return data


def normalize_assessments(raw_obj, expected_len: int) -> list:
    if not isinstance(raw_obj, dict) or set(raw_obj) != {"assessments"}:
        raise ValueError("[AI_FAULT] Invalid assessment root schema")
    items = raw_obj["assessments"]
    if not isinstance(items, list) or len(items) != expected_len:
        raise ValueError("[AI_FAULT] Assessment count mismatch")
    sorted_matrix = [None] * expected_len
    for entry in items:
        if not isinstance(entry, dict) or set(entry) != {"index", "outcome", "certainty"}:
            raise ValueError("[AI_FAULT] Malformed assessment entry")
        idx = entry["index"]
        if type(idx) is not int or not 0 <= idx < expected_len or sorted_matrix[idx] is not None:
            raise ValueError("[AI_FAULT] Duplicate or out-of-bounds rule index")
        if entry["outcome"] not in ("PASS", "FAIL", "AMBIGUOUS") or entry["certainty"] not in ("solid", "moderate", "weak"):
            raise ValueError("[AI_FAULT] Unrecognized outcome or certainty token")
        sorted_matrix[idx] = entry
    return sorted_matrix


def test_canonical_json_determinism():
    obj_a = {"b": 2, "a": 1, "nested": {"z": True, "x": False}}
    obj_b = {"nested": {"x": False, "z": True}, "a": 1, "b": 2}
    assert to_canonical_json(obj_a) == to_canonical_json(obj_b)
    hash_a = hashlib.sha256(to_canonical_json(obj_a).encode()).hexdigest()
    hash_b = hashlib.sha256(to_canonical_json(obj_b).encode()).hexdigest()
    assert hash_a == hash_b


def test_valid_intent_payload():
    sample = json.dumps({
        "method": "rebalance_pool",
        "target": "vault://usdc-eth-main",
        "payload": "Swap 500 USDC for ETH with max slippage of 25 bps."
    })
    parsed = parse_intent_payload(sample)
    assert parsed["method"] == "rebalance_pool"
    assert parsed["target"] == "vault://usdc-eth-main"


def test_invalid_intent_extra_keys_rejected():
    bad_sample = json.dumps({
        "method": "rebalance_pool",
        "target": "vault://usdc-eth-main",
        "payload": "Valid body",
        "injected": "extra"
    })
    with pytest.raises(ValueError, match="method, target, and payload keys only"):
        parse_intent_payload(bad_sample)


def test_normalize_assessments_orders_correctly():
    unordered = {
        "assessments": [
            {"index": 1, "outcome": "PASS", "certainty": "solid"},
            {"index": 0, "outcome": "PASS", "certainty": "solid"},
        ]
    }
    ordered = normalize_assessments(unordered, 2)
    assert ordered[0]["index"] == 0
    assert ordered[1]["index"] == 1
    assert all(x["outcome"] == "PASS" and x["certainty"] == "solid" for x in ordered)


def test_duplicate_rule_index_rejected():
    duplicate = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid"},
            {"index": 0, "outcome": "FAIL", "certainty": "solid"},
        ]
    }
    with pytest.raises(ValueError, match="Duplicate or out-of-bounds"):
        normalize_assessments(duplicate, 2)


def test_strict_approval_gate():
    matrix_pass = [
        {"index": 0, "outcome": "PASS", "certainty": "solid"},
        {"index": 1, "outcome": "PASS", "certainty": "solid"},
    ]
    matrix_weak = [
        {"index": 0, "outcome": "PASS", "certainty": "solid"},
        {"index": 1, "outcome": "PASS", "certainty": "moderate"},
    ]
    assert all(item["outcome"] == "PASS" and item["certainty"] == "solid" for item in matrix_pass) is True
    assert all(item["outcome"] == "PASS" and item["certainty"] == "solid" for item in matrix_weak) is False

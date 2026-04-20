"""Tests for envguard.grapher."""
import pytest
from envguard.grapher import build_graph, _extract_refs


def test_no_references_produces_empty_edges():
    env = {"A": "hello", "B": "world"}
    result = build_graph(env)
    assert result.edges == {}
    assert not result.has_cycles()


def test_brace_reference_detected():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = build_graph(env)
    assert "URL" in result.edges
    assert "HOST" in result.edges["URL"]


def test_plain_dollar_reference_detected():
    env = {"PORT": "8080", "ADDR": "$PORT"}
    result = build_graph(env)
    assert "ADDR" in result.edges
    assert "PORT" in result.edges["ADDR"]


def test_self_reference_excluded():
    env = {"A": "${A}_suffix"}
    result = build_graph(env)
    assert result.edges == {}


def test_reference_to_unknown_key_excluded():
    env = {"A": "${UNKNOWN}"}
    result = build_graph(env)
    assert result.edges == {}


def test_nodes_contain_all_keys():
    env = {"X": "1", "Y": "${X}"}
    result = build_graph(env)
    assert "X" in result.nodes
    assert "Y" in result.nodes


def test_simple_cycle_detected():
    env = {"A": "${B}", "B": "${A}"}
    result = build_graph(env)
    assert result.has_cycles()
    assert len(result.cycles) >= 1


def test_no_cycle_linear_chain():
    env = {"A": "val", "B": "${A}", "C": "${B}"}
    result = build_graph(env)
    assert not result.has_cycles()


def test_dependencies_of_returns_refs():
    env = {"DB": "postgres", "URL": "${DB}:5432"}
    result = build_graph(env)
    assert result.dependencies_of("URL") == ["DB"]


def test_dependencies_of_unknown_key_returns_empty():
    env = {"A": "1"}
    result = build_graph(env)
    assert result.dependencies_of("MISSING") == []


def test_summary_contains_node_count():
    env = {"A": "1", "B": "${A}"}
    result = build_graph(env)
    s = result.summary()
    assert "nodes=2" in s
    assert "edges=1" in s


def test_extract_refs_mixed():
    refs = _extract_refs("${FOO} and $BAR end")
    assert "FOO" in refs
    assert "BAR" in refs

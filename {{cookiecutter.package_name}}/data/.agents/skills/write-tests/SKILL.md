---
name: write-tests
description: Writes and reviews pytest tests. Use when writing new tests, reviewing them, or adding coverage.
argument-hint: "[module or file to test]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Bash
---

# Writing Tests

Use this skill for pytest. Code conventions are in `write-code`, and docstring conventions in
`write-docstrings`.

## Core principles

- Test behavior and computed values. A test that only constructs an object or reads back an
  attribute it set tells nobody anything.
- Do not check types; ty does that. No `isinstance` or `type()` assertions, unless the type is
  the behavior.
- Prefer a concrete expected value when one is known; use a relation when the relation is the
  behavior.
- A test with branches is several tests. Split it or parametrize it.
- Delete a scaffolding test once it no longer protects lasting behavior.
- Write a doctest for how a function is called, and a test for what it must get right.

## Structure

Tests live in `tests/`, one `test_<module>.py` per module. Plain functions, never classes:

```python
"""Tests for spam weights."""

from pytest import approx

from spam import Spam

CLASSIC = Spam("classic")


def test_classic_spam_weighs_pi_ounces() -> None:
    """Classic spam weighs pi ounces."""
    assert CLASSIC.weight == approx(3.14159265)
```

- Every file has a module docstring saying what it tests and, when it matters, what it leaves
  out.
- Every test has a docstring whose summary states the behavior checked, not the function name.
- Name a test for the behavior: `test_classic_spam_weighs_pi_ounces`, not `test_weight`.
- Shared inputs are module-level constants, built once and never mutated.
- A fake that one test needs is defined in that test.

## Imports

Import the pytest helpers a test uses by name: `from pytest import approx, mark, raises`. Keep
`import pytest` for `@pytest.fixture` and for types such as `pytest.MonkeyPatch`.

## Floats

Use `approx` at its default tolerance unless there is a reason not to, and give the reason in a
named constant with its unit:

```python
# Drift between two weighings on a shared scale, in ounces
WEIGHT_TOLERANCE = 0.005

assert Spam("bacon").weight == approx(3.14, abs=WEIGHT_TOLERANCE)
assert Spam("jalapeno").scores == [1, 2, 3]  # exact values need no approx
```

## Parametrize

Collapse tests that differ only in input and expected output:

```python
@mark.parametrize(
    ("spam_type", "weight"),
    [("classic", 3.14159265), ("maple", 4.1), ("low sodium", 2.9)],
)
def test_each_spam_type_has_its_own_weight(spam_type: str, weight: float) -> None:
    """Each spam type weighs what its label says."""
    assert Spam(spam_type).weight == approx(weight)
```

## Fixtures

A module-level constant serves most setup. Reach for `@pytest.fixture` when setup is expensive
and should run once (`scope="module"`), needs teardown, or needs `tmp_path` or `monkeypatch`.
Keep a fixture in the file that uses it; a `conftest.py` is for one shared across files.

## Exceptions

Assert the most specific exception class, not a base such as `Exception`, so the test also pins
which error the caller sees. Add `match=` only for the part of the message that is contract,
such as the name of the offending value, never the full wording.

```python
with raises(SpamTypeError, match="kale"):
    Spam("kale")
```

## Tests that need what a machine may lack

Never check for a requirement and `return`: pytest counts that as a pass. Skip visibly instead:

- a platform or a program: `@mark.skipif(..., reason="...")`, with a reason a reader can act on
- an optional package: `importorskip("package")`
- a whole module: `skip("needs <what>", allow_module_level=True)`

## Docstrings and comments

The summary states what is tested. Why goes in the following paragraph, with the issue or PR
number if there is one. Comments are rare: the value a broken build used to give, or why a
tolerance is loose, not what the next line does.

```python
def test_low_sodium_spam_has_a_quarter_of_the_sodium() -> None:
    """Low-sodium spam has a quarter of classic spam's sodium.

    #153 found low-sodium spam reporting classic spam's sodium.
    """
    assert Spam("low sodium").sodium_mg == approx(Spam("classic").sodium_mg / 4)
```

## What not to test

- types, which ty checks
- that a function returns something
- the full text of an error message
- the behavior of pytest or another library
- implementation details that should be free to change

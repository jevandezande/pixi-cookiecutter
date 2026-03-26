---
name: write-tests
description: Write or review unit tests for code in this repo. Use when writing new tests, reviewing existing tests, or adding test coverage.
argument-hint: "[module or file to test]"
---

# Writing Unit Tests

Follow these conventions when writing or modifying tests in this codebase.

## Core Principles

- **Only write tests that provide real information.** Avoid testing trivial things like object construction or obvious attribute access. Test behavior and computations.
- **Don't check types in tests.** Types are verified by the static type checker (`ty`). Avoid using `isinstance`, `type()`, or other type assertions in tests.
- **Write doctests to explain function usage.** Doctests are a quick way to show how to use a function and expected output; they also are quick smoke tests.

## File and Function Structure

Tests live in `tests/` within each package. Name files `test_<module>.py`. Use plain functions — never classes:

```python
"""Tests for the Spam."""

import numpy as np
from numpy.testing import assert_almost_equal as aae
from pytest import approx, mark, param, raises

from spam import Spam

def test_classic_spam() -> None:
    """Test classic spam values."""
    classic_spam = Spam("classic")
    assert classic_spam.weight == approx(3.14159265)
```

- Add a module-level docstring to every test file.
- Give each test function a Google-style one-line docstring.

## Float Comparisons

Use default tolerance thresholds unless there is a specific, documented reason to override them.

| Use case | Tool | Import |
|---|---|---|
| Scalars and simple lists | `approx` | `from pytest import approx` |
| NumPy arrays (gradients, hessians) | `aae` | `from numpy.testing import assert_almost_equal as aae` |
| Exact/near-exact array equality | `assert_allclose` | `from numpy.testing import assert_allclose` |

```python
# Scalars
assert Spam("classic").weight == approx(3.14159265)

# Lists / tuples
assert Spam("jalapeno").scores == approx([1, 2, 3])

# NumPy arrays
aae(Spam("maple").distribution, [[0, 1, 2], [3, 4, 5], [6, 7, 8]])

# Only override thresholds when truly necessary, with a comment explaining why
assert Spam("bacon").weight == approx(3.14, abs=0.005)  # loose: GitHub Actions gives different results

# Exceptions
with raises(ValueError):
    Spam("classic").process(threshold=-1)
```

## Parametrize Similar Tests

Use `pytest.mark.parametrize` to collapse tests that differ only in inputs/outputs
Use `param(..., marks=[mark.regression])` to apply markers to individual parametrized cases

```python
@mark.parametrize(
    ("spam_type", "weight"),
    [
        ("classic", 3.14159265),
        ("maple", 4.1),
        param("low sodium", 2.9, marks=[mark.regression]),
    ],
)
def test_weights(spam_type: str, weight: float) -> None:
    """Test energy for multiple molecules."""
    spam = Spam(spam_type)
    assert spam.weight == approx(weight)
```

## Regression Tests

Mark tests that run less regularly but protect against regressions with `@mark.regression`. These are excluded from the default run (`-m 'not regression'`).

When a regression test is related to a GitHub issue, link it in the docstring:

```python
@mark.regression
def test_low_sodium_spam() -> None:
    """They forgot to remove the sodium originally.

    https://example.com/flying_circus/spam/issues/1
    """
    ...
```

Regression tests verify:
- Previously-broken behavior is fixed and stays fixed
- A wider range of code paths (e.g., all solvents, all supported methods)
- Edge cases that are expensive to test on every CI run

## Fixtures

Use pytest fixtures for any setup that is repeated across multiple tests. Place fixtures in `conftest.py`:

- **Within a package:** `tests/conftest.py`
- **Shared across packages:** not currently applicable; each package has its own `conftest.py`


## Imports

Prefer importing selectively from pytest for readability

```python
from pytest import approx, mark, param, raises
```

Standard alias for numpy array assertions:

```python
from numpy.testing import assert_almost_equal as aae
```

## What NOT to Test

- Type correctness (use `ty check` instead)
- That a function returns something (trivial)
- Exact exception message text (fragile)
- Behavior of external libraries
- Implementation details that should be free to change

Focus on observable behavior: computed values, raised exceptions for invalid inputs, and correct transformations.

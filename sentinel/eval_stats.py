"""Pure-stdlib statistics for eval reporting — no numpy/scipy.

Why these, and why hand-rolled:
- Wilson score interval is the recommended default 95% CI for a binomial
  proportion (stable from n~=10, never escapes [0,1]); it is closed-form, so
  stdlib `math` is sufficient and scipy buys nothing at our n.
- A continuity-corrected (Yates) Wilson is included for small per-class
  subsets / proportions near 0 or 1, per current small-sample guidance.
- McNemar's *exact* binomial test compares two pipelines on the same cases
  (before/after a threshold change) without retraining; the exact variant is
  the recommended one for small discordant counts and uses only `math.comb`.

References: see PLAN.md research notes (Anthropic error-bars, AISI standard).
"""
from __future__ import annotations

import math

Z_95 = 1.959963984540054  # standard normal quantile for a two-sided 95% CI


def wilson_interval(
    successes: int,
    n: int,
    *,
    z: float = Z_95,
    continuity: bool = False,
) -> tuple[float, float]:
    """95% Wilson score interval for a proportion successes/n.

    Returns (low, high) clamped to [0, 1]. With ``continuity=True`` applies the
    Yates correction (slightly wider; preferred for small n or extreme p).
    """
    if n <= 0:
        return (0.0, 0.0)
    p = successes / n
    z2 = z * z

    if not continuity:
        denom = 1.0 + z2 / n
        center = (p + z2 / (2 * n)) / denom
        half = (z / denom) * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
        low = 0.0 if successes == 0 else max(0.0, center - half)
        high = 1.0 if successes == n else min(1.0, center + half)
        return (low, high)

    # Continuity-corrected Wilson (Yates).
    denom = 2 * (n + z2)
    base = 2 * n * p + z2
    root_lo = z * math.sqrt(max(0.0, z2 - 1.0 / n + 4 * n * p * (1 - p) + (4 * p - 2))) + 1
    root_hi = z * math.sqrt(max(0.0, z2 - 1.0 / n + 4 * n * p * (1 - p) - (4 * p - 2))) + 1
    low = (base - root_lo) / denom
    high = (base + root_hi) / denom
    if successes == 0:
        low = 0.0
    if successes == n:
        high = 1.0
    return (max(0.0, low), min(1.0, high))


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value for discordant pair counts (b, c).

    ``b`` = cases the first pipeline got right and the second got wrong;
    ``c`` = the reverse. Concordant cases (both right / both wrong) are ignored
    by design — McNemar only looks at where the two pipelines disagree.
    Returns 1.0 when there are no discordant pairs.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)

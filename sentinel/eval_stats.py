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


def cohens_kappa(
    a: list[int],
    b: list[int],
    *,
    categories: list[int] | None = None,
    weights: str | None = None,
) -> float:
    """Cohen's kappa between two paired raters ``a`` and ``b``.

    ``weights`` is None (nominal), "linear", or "quadratic" — use quadratic for
    ordinal scales (e.g. 1-5 safety scores) so near-misses are penalised less
    than far-misses. Returns 1.0 when there is nothing to disagree about.
    """
    if len(a) != len(b):
        raise ValueError("rater vectors must be the same length")
    n = len(a)
    if n == 0:
        return 1.0
    cats = categories if categories is not None else sorted(set(a) | set(b))
    k = len(cats)
    if k <= 1:
        return 1.0
    idx = {c: i for i, c in enumerate(cats)}

    observed = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        observed[idx[x]][idx[y]] += 1
    row = [sum(observed[i]) for i in range(k)]
    col = [sum(observed[i][j] for i in range(k)) for j in range(k)]

    def w_dis(i: int, j: int) -> float:
        if weights == "quadratic":
            return (i - j) ** 2 / (k - 1) ** 2
        if weights == "linear":
            return abs(i - j) / (k - 1)
        return 0.0 if i == j else 1.0

    num = sum(w_dis(i, j) * observed[i][j] for i in range(k) for j in range(k))
    den = sum(w_dis(i, j) * row[i] * col[j] / n for i in range(k) for j in range(k))
    if den == 0:
        return 1.0
    return 1.0 - num / den


def pearson(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation coefficient; 0.0 when either series has no variance."""
    n = len(xs)
    if n == 0 or n != len(ys):
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return 0.0
    return cov / math.sqrt(vx * vy)


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

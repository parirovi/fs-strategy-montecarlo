# Methodology

## CVaR

Points are never negative and higher is better. Conditional Value at Risk (CVaR) at level alpha is the mean of the points in the worst alpha tail (outcomes at or below the alpha quantile of the points distribution). A lower CVaR is worse.

## Dynamic scoring (FS Rules 2026 v1.1)

Skidpad and acceleration use the default formula in D9.1.1, with `Tmax` and `Pmin` from Table 11. `Pmax` comes from the competition YAML (FS Table 3 or an event handbook). A team with no valid run scores 0 (D1.1.5, D1.1.9). A valid run slower than `Tmax` is capped at `Tmax` and scores `Pmin`.

TODO: skidpad run time is the average of the timed left and right circles plus penalties added after averaging (D4.2.2). The scoring functions currently receive that already-built `time_s`; they do not combine left/right laps or cone penalties.

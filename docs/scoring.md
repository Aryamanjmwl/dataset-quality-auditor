# Scoring

Readiness scoring is deterministic.

## Rules

Scores start at 100.

- `critical`: subtract 20
- `warning`: subtract 8
- `info`: subtract 2
- `requires_human_review`: subtract 2 extra

The score is clamped between 0 and 100.

## Score Bands

- `ready`: 85 to 100
- `needs_attention`: 60 to 84
- `high_risk`: 0 to 59

## AI Boundary

AI cannot decide, modify, reinterpret, or override the readiness score. Future AI
features may explain the deterministic score and link explanations to issue IDs.

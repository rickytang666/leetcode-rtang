# check-discrepancy

## purpose

identifies leetcode problems that exist locally in the repository (as folders) but are not marked as "solved" (ac) in ur leetcode submission history.
it distinguishes between problems u have "attempted" (yellow) and those that are "missing/unknown" (red) from ur history.

## how to run

1. ensure `.env` file exists in repo root with `leetcode_session` cookie.
2. run the script using `uv`:

   ```bash
   uv run python check_discrepancy.py
   ```

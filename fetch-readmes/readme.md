# fetch-readmes

## purpose

automates the generation of readme.md files for leetcode problems in the repository.
it fetches problem details (description, difficulty, etc.) from leetcode's graphql api.

## how to run

1. ensure the project is initialized with `uv`.
2. run the script using `uv`:

   ```bash
   uv run python fetch_readmes.py
   ```

   to check only newly added (git modified/untracked) problems:

   ```bash
   uv run python fetch_readmes.py --new
   ```

   **optimization**: the script caches the problems in `id_map.json`. to force a fresh fetch run this:

   ```bash
   uv run python fetch_readmes.py --refresh
   ```

# fetch-readmes

## purpose

automates the generation of readme.md files for leetcode problems in the repository.
it fetches problem details (description, difficulty, etc.) from leetcode's graphql api.

## how to run

1. ensure the shared virtual environment is set up at the repo root.
2. activate the virtual environment:

   ```bash
   source ../.venv/bin/activate
   ```

3. run the script:

   ```bash
   python fetch_readmes.py
   ```

   to check only newly added (git modified/untracked) problems:

   ```bash
   python fetch_readmes.py --new
   ```

   **optimization**: the script caches the problems in `id_map.json`. to force a fresh fetch run this:

   ```bash
   python fetch_readmes.py --refresh
   ```

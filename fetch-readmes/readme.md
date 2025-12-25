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
   python3 fetch_readmes.py
   ```

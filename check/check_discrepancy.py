import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GraphQL query to fetch all solved questions
# Note: This query uses the 'problemsetQuestionList' which returns a list of questions.
# We filter by status usually, but for a global list of "my solved", sometimes a different query is better.
# However, 'problemsetQuestionList' with filters={"status": "AC"} is a common way.
SOLVED_QUESTIONS_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      questionFrontendId
      title
      titleSlug
      status
    }
  }
}
"""

def get_solved_problems():
    if not LEETCODE_SESSION:
        print("Error: LEETCODE_SESSION not found in environment variables.")
        return set()

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    solved_ids = set()
    limit = 100
    skip = 0
    
    print("Fetching solved problems from LeetCode...")

    while True:
        payload = {
            "query": SOLVED_QUESTIONS_QUERY,
            "variables": {
                "categorySlug": "",
                "limit": limit,
                "skip": skip,
                "filters": {"status": "AC"}
            }
        }

        try:
            response = requests.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            q_list = data.get("data", {}).get("problemsetQuestionList", {})
            questions = q_list.get("questions", [])
            
            if not questions:
                break
                
            for q in questions:
                fid = q.get("questionFrontendId")
                if fid:
                    solved_ids.add(str(fid))
            
            print(f"Fetched {len(questions)} problems (total so far: {len(solved_ids)})")
            
            if len(questions) < limit:
                break
                
            skip += limit
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching solved problems: {e}")
            break
            
    return solved_ids

def get_local_problems():
    local_problems = [] # List of tuples (id, folder_name, full_path)
    
    difficulty_dirs = ["1-easy", "2-medium", "3-hard"]
    
    print("Scanning local directories...")
    
    for diff_dir in difficulty_dirs:
        diff_path = os.path.join(ROOT_DIR, diff_dir)
        if not os.path.exists(diff_path):
            continue
            
        # depth 2: range folders
        range_dirs = sorted(os.listdir(diff_path))
        for range_dir in range_dirs:
            range_path = os.path.join(diff_path, range_dir)
            if not os.path.isdir(range_path) or range_dir.startswith("."):
                continue
                
            # depth 3: problem folders
            problem_dirs = sorted(os.listdir(range_path))
            for problem_dir in problem_dirs:
                problem_path = os.path.join(range_path, problem_dir)
                if not os.path.isdir(problem_path) or problem_dir.startswith("."):
                    continue
                
                # Extract ID
                parts = problem_dir.split("-", 1)
                if len(parts) >= 2 and parts[0].isdigit():
                    fid = str(int(parts[0])) # Normalize ID (remove leading zeros)
                    local_problems.append({
                        "id": fid,
                        "folder": problem_dir,
                        "path": problem_path
                    })
    
    print(f"Found {len(local_problems)} local problem folders.")
    return local_problems

def main():
    solved_ids = get_solved_problems()
    local_problems = get_local_problems()
    
    if not solved_ids:
        print("Warning: No solved problems fetched. Check your generic LeetCode session cookie.")
        # Proceeding anyway usually means everything will be a discrepancy if solved_ids is empty
    
    print("\nAnalyzing discrepancies...")
    
    discrepancies = []
    
    for prob in local_problems:
        if prob["id"] not in solved_ids:
            discrepancies.append(prob)
            
    if discrepancies:
        print(f"\nFound {len(discrepancies)} discrepancies (Locally present but not in 'AC' list):")
        for d in discrepancies:
            print(f"- [{d['id']}] {d['folder']}")
    else:
        print("\nNo discrepancies found. All local problems are marked as Solved on LeetCode.")

if __name__ == "__main__":
    main()

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ansi color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

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
        print(f"{RED}error: LEETCODE_SESSION not found in environment variables.{RESET}")
        return {}

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    solved_ids = {} # map id -> status (ac, notac)
    # fetch both 'ac' (accepted) and 'tried' (attempted but not passed)
    # leetcode status keys: "AC", "TRIED"
    
    for status_filter in ["AC", "TRIED"]:
        limit = 100
        skip = 0
        print(f"fetching '{status_filter}' problems from leetcode...")
        
        while True:
            payload = {
                "query": SOLVED_QUESTIONS_QUERY,
                "variables": {
                    "categorySlug": "",
                    "limit": limit,
                    "skip": skip,
                    "filters": {"status": status_filter}
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
                    q_status = q.get("status") # 'ac' or 'notac' usually returned by api
                    if fid:
                        solved_ids[str(fid)] = q_status
                
                print(f"fetched {len(questions)} problems (total unique: {len(solved_ids)})")
                
                if len(questions) < limit:
                    break
                    
                skip += limit
                
            except requests.exceptions.RequestException as e:
                print(f"{RED}error fetching problems: {e}{RESET}")
                break
            
    return solved_ids

def get_local_problems():
    local_problems = [] # List of tuples (id, folder_name, full_path)
    
    difficulty_dirs = ["1-easy", "2-medium", "3-hard"]
    
    print("scanning local directories...")
    
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
    
    print(f"found {len(local_problems)} local problem folders.")
    return local_problems

def main():
    solved_map = get_solved_problems()
    local_problems = get_local_problems()
    
    if not solved_map:
        print(f"{YELLOW}warning: no problems fetched. check your generic leetcode session cookie.{RESET}")
    
    print("\nanalyzing discrepancies...")
    
    discrepancy_count = 0
    
    for prob in local_problems:
        fid = prob["id"]
        status = solved_map.get(fid)
        
        if status == 'ac':
            continue
            
        discrepancy_count += 1
        
        if status:
            # attempted but not ac
            print(f"- [{YELLOW}{fid}{RESET}] {prob['folder']} ({YELLOW}attempted{RESET})")
        else:
            # really missing (not in fetched list or status is null)
            print(f"- [{RED}{fid}{RESET}] {prob['folder']} ({RED}missing/unknown{RESET})")
            
    if discrepancy_count == 0:
        print(f"\n{GREEN}all done! no discrepancies found.{RESET}")
    else:
        print(f"\nfound {discrepancy_count} discrepancies.")

if __name__ == "__main__":
    main()

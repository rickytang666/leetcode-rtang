import os
import requests
import json
import argparse
import sys
from markdownify import markdownify as md

# constants
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # parent of fetch-readmes

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

# query to fetch all questions for id -> slug mapping
ALL_QUESTIONS_QUERY = """
query problemsetQuestionList($limit: Int) {
    problemsetQuestionList: questionList(
        categorySlug: ""
        limit: $limit
        skip: 0
        filters: {}
    ) {
        questions: data {
            questionFrontendId
            titleSlug
        }
    }
}
"""

# query to fetch specific question details
QUESTION_DATA_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    content
    difficulty
    likes
    dislikes
    topicTags {
      name
      slug
    }
    stats
    hints
  }
}
"""

def build_id_to_slug_map():
    print("fetching global problem list for id mapping...")
    payload = {
        "operationName": "problemsetQuestionList",
        "variables": {"limit": 10000}, # huge limit to get all
        "query": ALL_QUESTIONS_QUERY
    }
    
    try:
        response = requests.post(LEETCODE_GRAPHQL_URL, json=payload, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        questions = data.get("data", {}).get("problemsetQuestionList", {}).get("questions", [])
        
        id_map = {}
        for q in questions:
            fid = q.get("questionFrontendId")
            slug = q.get("titleSlug")
            if fid and slug:
                id_map[str(fid)] = slug
        
        print(f"loaded {len(id_map)} problems into map.")
        return id_map
    except requests.exceptions.RequestException as e:
        print(f"error fetching problem list: {e}")
        return {}

def get_question_details(title_slug):
    payload = {
        "operationName": "questionData",
        "variables": {"titleSlug": title_slug},
        "query": QUESTION_DATA_QUERY
    }
    
    try:
        response = requests.post(LEETCODE_GRAPHQL_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("question")
    except requests.exceptions.RequestException as e:
        print(f"error fetching data for {title_slug}: {e}")
        return None

def format_readme(question_data):
    if not question_data:
        return None

    title = question_data.get("title")
    difficulty = question_data.get("difficulty")
    frontend_id = question_data.get("questionFrontendId")
    content_html = question_data.get("content") or ""
    topic_tags = question_data.get("topicTags", [])
    hints = question_data.get("hints", [])
    try:
        stats = json.loads(question_data.get("stats", "{}"))
        acceptance_rate = stats.get("acRate", "N/A")
    except:
        acceptance_rate = "N/A"

    markdown_content = f"# {frontend_id}. {title}\n\n"
    markdown_content += f"**Difficulty:** {difficulty}\n\n"
    markdown_content += f"**Acceptance Rate:** {acceptance_rate}\n\n"
    
    if topic_tags:
        tags_str = ", ".join([f"`{tag['name']}`" for tag in topic_tags])
        markdown_content += f"**Tags:** {tags_str}\n\n"
        
    markdown_content += "---\n\n"
    markdown_content += "## Description\n\n"
    markdown_content += md(content_html)
    
    if hints:
        markdown_content += "\n\n---\n\n"
        markdown_content += "## Hints\n\n"
        for i, hint in enumerate(hints, 1):
            markdown_content += f"{i}. {hint}\n"

    return markdown_content

def process_problem(problem_path, folder_name, id_map):
    # check if readme exists
    if os.path.exists(os.path.join(problem_path, "README.md")):
        return False
        
    # extract id from folder name (e.g. 0001-two-sum -> 1)
    parts = folder_name.split("-", 1)
    if len(parts) < 2 or not parts[0].isdigit():
        return False
    
    folder_id_str = parts[0]
    # remove leading zeros for map lookup (0001 -> 1)
    # but keep as string because map keys are strings
    lookup_id = str(int(folder_id_str))
    
    title_slug = id_map.get(lookup_id)
    
    # fallback: if not in map, try to use the slug from folder name?
    # current decision: prioritize map. if not in map, might be stale id or new problem script hasn't seen?
    # let's try fallback to folder name slug if map lookup fails, but warn.
    if not title_slug:
        title_slug = parts[1]
        print(f"warning: id {lookup_id} not found in map. trying slug from folder: {title_slug}")
    else:
        print(f"processing: {folder_name} -> id: {lookup_id} -> slug: {title_slug}")
    
    question_data = get_question_details(title_slug)
    if not question_data:
        print(f"failed to get info for {title_slug}")
        return False
        
    readme_content = format_readme(question_data)
    if readme_content:
        target_path = os.path.join(problem_path, "README.md")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print(f"generated readme for {folder_name}")
        return True
            
    return False

def main():
    parser = argparse.ArgumentParser(description="fetch leetcode readmes")
    parser.add_argument("--test", action="store_true", help="run on a single problem and exit")
    args = parser.parse_args()

    # build global map first
    id_map = build_id_to_slug_map()
    if not id_map:
        print("failed to build id map. exiting.")
        sys.exit(1)

    # folders to scan (depth 1)
    difficulty_dirs = ["1-easy", "2-medium", "3-hard"]
    
    print("starting sorted scan...")
    
    for diff_dir in difficulty_dirs:
        diff_path = os.path.join(ROOT_DIR, diff_dir)
        if not os.path.exists(diff_path):
            continue
            
        # depth 2: range folders (sorted)
        range_dirs = sorted(os.listdir(diff_path))
        for range_dir in range_dirs:
            range_path = os.path.join(diff_path, range_dir)
            if not os.path.isdir(range_path) or range_dir.startswith("."):
                continue
                
            # depth 3: problem folders (sorted)
            problem_dirs = sorted(os.listdir(range_path))
            for problem_dir in problem_dirs:
                problem_path = os.path.join(range_path, problem_dir)
                if not os.path.isdir(problem_path) or problem_dir.startswith("."):
                    continue
                    
                success = process_problem(problem_path, problem_dir, id_map)
                if args.test and success:
                    print("test mode enabled. stopping after first success.")
                    sys.exit(0)

if __name__ == "__main__":
    main()

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

QUERY = """
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

def get_question_details(title_slug):
    payload = {
        "operationName": "questionData",
        "variables": {"titleSlug": title_slug},
        "query": QUERY
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
    content_html = question_data.get("content", "")
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

def process_problem(problem_path, folder_name):
    # check if readme exists
    if os.path.exists(os.path.join(problem_path, "README.md")):
        return False
        
    # extract slug (assuming format: id-slug)
    parts = folder_name.split("-", 1)
    if len(parts) < 2 or not parts[0].isdigit():
        return False
        
    title_slug = parts[1]
    print(f"processing: {folder_name} -> {title_slug}")
    
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

    # folders to scan (depth 1)
    difficulty_dirs = ["1-easy", "2-medium", "3-hard"]
    
    print("starting scan...")
    
    for diff_dir in difficulty_dirs:
        diff_path = os.path.join(ROOT_DIR, diff_dir)
        if not os.path.exists(diff_path):
            continue
            
        # depth 2: range folders
        for range_dir in os.listdir(diff_path):
            range_path = os.path.join(diff_path, range_dir)
            if not os.path.isdir(range_path) or range_dir.startswith("."):
                continue
                
            # depth 3: problem folders
            for problem_dir in os.listdir(range_path):
                problem_path = os.path.join(range_path, problem_dir)
                if not os.path.isdir(problem_path) or problem_dir.startswith("."):
                    continue
                    
                success = process_problem(problem_path, problem_dir)
                if args.test and success:
                    print("test mode enabled. stopping after first success.")
                    sys.exit(0)

if __name__ == "__main__":
    main()

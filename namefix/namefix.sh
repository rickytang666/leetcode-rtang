#!/bin/bash

# Script to fix LeetCode problem folder names to use 4-digit padding
# Example: 56-problem-name -> 0056-problem-name

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for renamed folders
renamed_count=0

# Function to pad problem number to 4 digits
pad_folder_name() {
    local folder_path="$1"
    local folder_name=$(basename "$folder_path")
    local parent_dir=$(dirname "$folder_path")
    
    # Extract the problem number (digits at the start of the folder name)
    if [[ $folder_name =~ ^([0-9]+)(-.*)?$ ]]; then
        local problem_num="${BASH_REMATCH[1]}"
        local rest_of_name="${BASH_REMATCH[2]}"
        
        # Check if already 4 digits
        if [ ${#problem_num} -eq 4 ]; then
            return 0
        fi
        
        # Check if it's 1-3 digits
        if [ ${#problem_num} -ge 1 ] && [ ${#problem_num} -le 3 ]; then
            # Pad to 4 digits
            local padded_num=$(printf "%04d" "$problem_num")
            local new_name="${padded_num}${rest_of_name}"
            local new_path="${parent_dir}/${new_name}"
            
            echo -e "${YELLOW}Wrong:${NC} $folder_name"
            
            # Check if target already exists
            if [ -e "$new_path" ]; then
                echo -e "${RED}Error: Target already exists: $new_path${NC}"
                return 1
            fi
            
            # Rename the folder
            mv "$folder_path" "$new_path"
            echo -e "${GREEN}Fixed:${NC} $new_name\n"
            
            ((renamed_count++))
            return 0
        fi
    fi
    
    return 0
}

# Process each difficulty level
for difficulty in easy medium hard; do
    if [ -d "$difficulty" ]; then
        # Find all problem folders (they are at depth 2 within each difficulty folder)
        while IFS= read -r -d '' folder; do
            pad_folder_name "$folder"
        done < <(find "$difficulty" -mindepth 2 -maxdepth 2 -type d -name '[0-9]*' -print0 | sort -z)
    fi
done

# Summary
if [ $renamed_count -eq 0 ]; then
    echo -e "${GREEN}✓ All folders are already properly formatted!${NC}"
else
    echo -e "${GREEN}✓ Fixed $renamed_count folder(s)${NC}"
fi

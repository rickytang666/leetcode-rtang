#include <bits/stdc++.h>

using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) 
    {
        vector<int> answers = {-1, -1};

        for (int i = 0; i < nums.size(); ++i) 
        {
            for (int j = i + 1; j < nums.size(); ++j) 
            {
                if (nums[i] + nums[j] == target) 
                {
                    answers = {i, j};
                }
            }
        }

        return answers;
    }
};

int main() {
    cout << "Hello C++" << endl;
    return 0;
}
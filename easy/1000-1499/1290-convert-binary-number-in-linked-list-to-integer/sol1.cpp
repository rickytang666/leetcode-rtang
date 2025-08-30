#include <bits/stdc++.h>
using namespace std;

struct ListNode
{
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

class Solution
{
public:
    int getDecimalValue(ListNode *head)
    {
        int sum = 0;
        while (head)
        {
            sum *= 2;
            sum += head->val;
            head = head->next;
        }

        return sum;
    }
};

int main()
{
    cout << "Hello C++" << endl;
    return 0;
}
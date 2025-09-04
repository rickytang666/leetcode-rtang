#include <stdio.h>
#include <string.h>

int finalPositionOfSnake(int n, char **commands, int commandsSize)
{
    int r = 0, c = 0;
    for (int i = 0; i < commandsSize; ++i)
    {
        if (!strcmp(commands[i], "UP"))
            --r;
        else if (!strcmp(commands[i], "RIGHT"))
            ++c;
        else if (!strcmp(commands[i], "DOWN"))
            ++r;
        else
            --c;
    }
    return n * r + c;
}

int main(void)
{
    char *commands[] = {"RIGHT", "DOWN", "LEFT", "LEFT", "DOWN"};
    int n = 3;
    int commandsSize = sizeof(commands) / sizeof(commands[0]);
    int result = finalPositionOfSnake(n, commands, commandsSize);
    printf("Final Position: %d\n", result); // Output: Final Position:
    return 0;
}
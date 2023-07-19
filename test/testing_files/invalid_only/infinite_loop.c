#include <limits.h>

int main() {
    int i = 1;
    while (i > 0) {
        if (i + 1 == INT_MAX) {
            i = 1;
        }
        i++;
    }
    return 0;
}

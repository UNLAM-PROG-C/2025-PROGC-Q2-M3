#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <sys/prctl.h>

#define ChildBName "ChildB"
#define GrandchildCName "GrandchildC"
#define GrandchildDName "GrandchildD"
#define GreatGrandchildEName "GreatGrandchildE"
#define GreatGrandchildFName "GreatGrandchildF"
#define GreatGrandchildGName "GreatGrandchildG"
#define GreatGreatGrandchildHName "GreatGreatGrandchildH"
#define GreatGreatGrandchildIName "GreatGreatGrandchildI"

int main() {
    pid_t Parent = getpid(), ChildB, GrandchildC, GrandchildD,
          GreatGrandchildE, GreatGrandchildF, GreatGrandchildG,
          GreatGreatGrandchildH, GreatGreatGrandchildI;

    prctl(PR_SET_NAME, "ParentA", NULL, NULL, NULL);
    printf("I am process ParentA. My PID is: %d\n", Parent);

    // ParentA creates ChildB
    ChildB = fork();

    if (ChildB < 0) {
        perror("fork");
        exit(1);
    } else if (ChildB == 0) {
        // Process B
        printf("I am process %s with PID %d, my parent is %d\n", ChildBName, getpid(), getppid());

        // Process B creates Process C
        GrandchildC = fork();
        if (GrandchildC < 0) {
            perror("fork");
            exit(1);
        }
        else if (GrandchildC == 0) {
            // Process C
            printf("I am process %s with PID %d, my parent is %d\n", GrandchildCName, getpid(), getppid());

            // Process C creates Process E
            GreatGrandchildE = fork();
            if (GreatGrandchildE < 0) {
                perror("fork");
                exit(1);
            }
            else if (GreatGrandchildE == 0) {
                // Process E
                printf("I am process %s with PID %d, my parent is %d\n", GreatGrandchildEName, getpid(), getppid());

                // Process E creates Process H
                GreatGreatGrandchildH = fork();

                if (GreatGreatGrandchildH < 0) {
                    perror("fork");
                    exit(1);
                }
                else if (GreatGreatGrandchildH == 0) {
                    // Process H
                    printf("I am process %s with PID %d, my parent is %d\n", GreatGreatGrandchildHName, getpid(), getppid());
                    sleep(10);
                    exit(0);
                }

                // Process E creates Process I
                GreatGreatGrandchildI = fork();

                if (GreatGreatGrandchildI < 0) {
                    perror("fork");
                    exit(1);
                }
                else if (GreatGreatGrandchildI == 0) {
                    // Process I
                    printf("I am process %s with PID %d, my parent is %d\n", GreatGreatGrandchildIName, getpid(), getppid());
                    sleep(10);
                    exit(0);
                }
                sleep(10);
                exit(0);
            }

            sleep(10);
            exit(0);
        }

        // Process B creates Process D
        GrandchildD = fork();
        if (GrandchildD < 0) {
            perror("fork");
            exit(1);
        }
        else if (GrandchildD == 0) {
            // Process D
            printf("I am process %s with PID %d, my parent is %d\n", GrandchildDName, getpid(), getppid());

            // Process D creates Process F
            GreatGrandchildF = fork();

            if (GreatGrandchildF < 0) {
                perror("fork");
                exit(1);
            }
            else if (GreatGrandchildF == 0) {
                // Process F
                printf("I am process %s with PID %d, my parent is %d\n", GreatGrandchildFName, getpid(), getppid());
                sleep(10);
                exit(0);
            }
            // Process D creates Process G
            GreatGrandchildG = fork();

            if (GreatGrandchildG < 0) {
                perror("fork");
                exit(1);
            }
            else if (GreatGrandchildG == 0) {
                // Process G
                printf("I am process %s with PID %d, my parent is %d\n", GreatGrandchildGName, getpid(), getppid());
                sleep(10);
                exit(0);
            }

            sleep(10);
            exit(0);
        }

        // B waits for C and D
        wait(NULL);
        wait(NULL);

        sleep(5);
        exit(0);

    } else {
        // A waits for B (and its children)
        wait(NULL);
        sleep(5);
    }

    return 0;
}


/* tcmeasure: run a command, then print its peak RSS and wall time as one JSON line on stderr.
 * Usage: tcmeasure <cmd> [args...]   (exit status = the command's exit status)
 * Peak RSS is ru_maxrss of RUSAGE_CHILDREN: the largest resident set of any waited-for descendant. */
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: tcmeasure cmd [args]\n"); return 2; }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    pid_t pid = fork();
    if (pid == 0) { execvp(argv[1], argv + 1); perror("execvp"); _exit(127); }
    int status = 0;
    waitpid(pid, &status, 0);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    struct rusage ru;
    getrusage(RUSAGE_CHILDREN, &ru);
    double wall = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    fprintf(stderr, "{\"tcmeasure\": {\"peak_rss_kb\": %ld, \"wall_s\": %.6f, \"user_s\": %.6f, \"sys_s\": %.6f}}\n",
            ru.ru_maxrss, wall, ru.ru_utime.tv_sec + ru.ru_utime.tv_usec / 1e6,
            ru.ru_stime.tv_sec + ru.ru_stime.tv_usec / 1e6);
    return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
}

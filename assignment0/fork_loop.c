#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void)
{
	int i = 0;
	while(fork() && i < 5)
	{
		wait(NULL);
		printf("Yo!");
		/* Yo!s are not being flushed before being inhertied by child */
		/* printf("YO!\n"); */
		/* fflush(stdout); */

		/* This is a three non-atomic action */
		i++;
	}
	printf("%d", i);
	return 0;
}



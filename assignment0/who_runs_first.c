#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

#define ITER_MAX 1000
#define SLEEP 10.0
/* #define USLEEP 100000 */

int main(void)
{
	char msg_p[] = "parent";
	char msg_c[] = "child";
	char n1[] = "\n";

	for(int i = 0; i < ITER_MAX; i++)
	{
		if(fork())
		{
			sleep(SLEEP);
			/* usleep(USLEEP); */
			/* printf("%s", msg_p); */
			/* fflush(stdout); */
			write(STDOUT_FILENO, msg_p, sizeof(msg_p)-1);
			wait(NULL);
		}
		else
		{
			sleep(SLEEP);
			/* usleep(USLEEP); */
			/* printf("%s", msg_c); */
			/* fflush(stdout); */
			write(STDOUT_FILENO, msg_c, sizeof(msg_c)-1);
			return 0;
		}

		sleep(SLEEP);
		/* usleep(USLEEP); */
		/* printf("%s", n1); */
		/* fflush(stdout); */
		write(STDOUT_FILENO, n1, sizeof(n1)-1);
	}
	return 0;
}



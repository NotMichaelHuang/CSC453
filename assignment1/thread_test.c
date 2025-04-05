#include <stdio.h>
#include <stdlib.h>
#include "lwp.h"


void thread_func_yield(void *arg)
{
	ptr_int_t id = (ptr_int_t)arg; //Dereferencing a int * ptr

	printf("[Thread %d] Yielding thread\n", (int)id);
	lwp_yield();

	printf("[Thread %d] Hello World from LWP w/ PID: %d!\n", (int)id, lwp_getpid());

	lwp_exit();
}

void thread_func_stop(void *arg)
{
	ptr_int_t id = (ptr_int_t)arg; //Dereferencing a int * ptr

	printf("[Thread %d] Stopping thread\n", (int)id);
	lwp_stop();

	printf("[Thread %d] Hello World from LWP w/ PID: %d!\n", (int)id, lwp_getpid());

	lwp_exit();
}

void thread_func(void *arg)
{
	ptr_int_t id = (ptr_int_t)arg; //Dereferencing a int * ptr

	printf("[Thread %d] Hello World from LWP w/ PID: %d!\n", (int)id, lwp_getpid());

	lwp_exit();
}

int main()
{
	printf("[Main] Starting LWP test...\n");

	size_t stacksize = 1024;
	ptr_int_t id1 = 1, id2 = 2, id3 = 3;

	new_lwp(thread_func_yield, (void *)id1, stacksize);
	new_lwp(thread_func, (void *)id2, stacksize);
	new_lwp(thread_func_stop, (void *)id3, stacksize);
	new_lwp(thread_func, (void *)4, stacksize);

	printf("[Main] Made all threads\n");

	lwp_start();

	printf("[Main] Back out, will start again\n");
	lwp_start();

	printf("[Main] Killed all threads.\n");
	return 0;
}



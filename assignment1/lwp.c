#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "lwp.h"


// Make the table with the max amount of lwp
lwp_context lwp_ptable[LWP_PROC_LIMIT];

//Main stack
lwp_context main_context;
ptr_int_t *main_sp;
int start = 0;

int lwp_procs = 0;
int lwp_running = 0; //Indes of the currently running lwp
int next_pid = 0;		 /*
												PID of the lwp, endforce safety--
										 		seperate from lwp_procs 
											*/

// Prototypes
int round_robin();
void lwp_exit();

void *lwp_exit_addr = &lwp_exit;
schedfun scheduler = round_robin;

int new_lwp(lwpfun func, void *arg, size_t stacksize)
{
	// Thread check
	if (lwp_procs >= LWP_PROC_LIMIT)
	{
		return -1;
	}	

	// Make sure ptr_int_t is 4 bytes
	if(sizeof(ptr_int_t) != 4)
	{
		printf("ptr_int_t is not size word\n");
		return -1;
	}

	// Create a stack on the HEAP which will be the lowest address
	// stacksize should be in words (since it's a 32-bit sys then 
	// it would be 4 bytes)
	ptr_int_t *stack = malloc(sizeof(ptr_int_t) * stacksize);
	if (!stack)
	{
		return -1;
	}
	
	// Stack grows down, start at top of our stack with an offeset
	ptr_int_t *sp = stack + stacksize;	

	// Push function address and argument address into the stack 
	// prior to context table	
	*--sp = (ptr_int_t)arg;
	
	//Bogus ret
	*--sp = (ptr_int_t)lwp_exit_addr;

	*--sp = (ptr_int_t)func; //esp should point here as ret	

	//Bogus ebp
	*--sp = (ptr_int_t)0xFEEDBEEF;

	//Bogus ebp addr
	ptr_int_t *fake_addr = sp;

	// Populate empty stack with dummies
	int i;
	for(i = 0; i < 6; i++)
	{
		*--sp = (ptr_int_t)0xDEADBEEF; //esi, edx, ecx, ebx, eas
	}			

	*--sp = (ptr_int_t)fake_addr;

	// Create a new thread
	lwp_context *new_thread = &lwp_ptable[lwp_procs];	

	// init said new thread, casted unsigned long for best partices
	new_thread->pid = (unsigned long)next_pid;
	new_thread->sp = sp;
	new_thread->stack = stack;	
	new_thread->stacksize = (unsigned long)stacksize;

	// Increase occupy threads and PID
	next_pid++;
	lwp_procs++;	

	return (int)new_thread->pid;
}

void lwp_set_scheduler(schedfun sched)
{
	if(!sched)
	{
		scheduler = sched;
	}	
	// Gonna be round robin if NULL or never been set.
}

int lwp_getpid()
{
	return lwp_ptable[lwp_running].pid;
}

//Trampoline
void lwp_start()
{
	// Can't start if no lwp_procs created
	if(lwp_procs == 0)
	{
		return;
	}	

	if(!start)
	{
		//Save main thread
		SAVE_STATE();	//Push regsiters on to current stack
		GetSP(main_sp);
		main_context.sp = main_sp;
		start++;
	}	

	lwp_running = scheduler();
	SetSP(lwp_ptable[lwp_running].sp);
	RESTORE_STATE(); //Jump to thread after restoring context
}

void lwp_yield()
{	
	lwp_context *tmp_thread = &lwp_ptable[lwp_running];
	ptr_int_t *tmp_sp;

	// Save current thread context
	SAVE_STATE();
	GetSP(tmp_sp);	// Get current esp position and load into tmp_ptr;
	tmp_thread->sp = tmp_sp;

	lwp_running++;
	lwp_start();
}

// This does NOT terminate the thread, just suspends LWP context-switching
void lwp_stop()
{
	lwp_context *current_thread = &lwp_ptable[lwp_running];
	ptr_int_t *c_sp;

	// Save the current context or the thread
	SAVE_STATE();		
	GetSP(c_sp);
	current_thread->sp = c_sp;

	SetSP(main_sp);
	RESTORE_STATE();
	start--;
}

void lwp_exit()
{
	// Starting to kill thread
	free(lwp_ptable[lwp_running].stack);

	lwp_ptable[lwp_running].stack = NULL;

	// Reduce Procs
	lwp_procs--;

	if(lwp_procs == 0)
	{
		SetSP(main_context.sp);
		RESTORE_STATE();
		return;
	}

	int i;
	for(i = lwp_running; i < lwp_procs; i++)
	{
		lwp_ptable[i] = lwp_ptable[i + 1];		
	}

	lwp_running = scheduler();
	SetSP(lwp_ptable[lwp_running].sp);
	RESTORE_STATE();	
}

int round_robin()
{
	int index;
	index = lwp_running;
	if(lwp_running >= lwp_procs)
	{
		index = 0;
	}
	return index;
}



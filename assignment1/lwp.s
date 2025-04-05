	.file	"lwp.c"
	.comm	lwp_ptable,960,32
	.comm	main_context,32,32
	.comm	main_sp,8,8
	.globl	start
	.bss
	.align 4
	.type	start, @object
	.size	start, 4
start:
	.zero	4
	.globl	lwp_procs
	.align 4
	.type	lwp_procs, @object
	.size	lwp_procs, 4
lwp_procs:
	.zero	4
	.globl	lwp_running
	.align 4
	.type	lwp_running, @object
	.size	lwp_running, 4
lwp_running:
	.zero	4
	.globl	next_pid
	.align 4
	.type	next_pid, @object
	.size	next_pid, 4
next_pid:
	.zero	4
	.globl	lwp_exit_addr
	.data
	.align 8
	.type	lwp_exit_addr, @object
	.size	lwp_exit_addr, 8
lwp_exit_addr:
	.quad	lwp_exit
	.globl	scheduler
	.align 8
	.type	scheduler, @object
	.size	scheduler, 8
scheduler:
	.quad	round_robin
	.section	.rodata
.LC0:
	.string	"ptr_int_t is not size word"
	.text
	.globl	new_lwp
	.type	new_lwp, @function
new_lwp:
.LFB2:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$32, %rsp
	movq	%rdi, -8(%rbp)
	movq	%rsi, -16(%rbp)
	movq	%rdx, -24(%rbp)
	movl	lwp_procs(%rip), %eax
	cmpl	$29, %eax
	jle	.L2
	movl	$-1, %eax
	jmp	.L3
.L2:
	movl	$.LC0, %edi
	call	puts
	movl	$-1, %eax
.L3:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE2:
	.size	new_lwp, .-new_lwp
	.globl	lwp_set_scheduler
	.type	lwp_set_scheduler, @function
lwp_set_scheduler:
.LFB3:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movq	%rdi, -8(%rbp)
	cmpq	$0, -8(%rbp)
	jne	.L4
	movq	-8(%rbp), %rax
	movq	%rax, scheduler(%rip)
.L4:
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE3:
	.size	lwp_set_scheduler, .-lwp_set_scheduler
	.globl	lwp_getpid
	.type	lwp_getpid, @function
lwp_getpid:
.LFB4:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	(%rax), %rax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE4:
	.size	lwp_getpid, .-lwp_getpid
	.globl	lwp_start
	.type	lwp_start, @function
lwp_start:
.LFB5:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	lwp_procs(%rip), %eax
	testl	%eax, %eax
	jne	.L9
	jmp	.L8
.L9:
	movl	start(%rip), %eax
	testl	%eax, %eax
	jne	.L11
#APP
# 123 "lwp.c" 1
	pushq %rax
# 0 "" 2
# 123 "lwp.c" 1
	pushq %rbx
# 0 "" 2
# 123 "lwp.c" 1
	pushq %rcx
# 0 "" 2
# 123 "lwp.c" 1
	pushq %rdx
# 0 "" 2
# 123 "lwp.c" 1
	pushq %rsi
# 0 "" 2
# 123 "lwp.c" 1
	pushq %rdi
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r8
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r9
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r10
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r11
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r12
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r13
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r14
# 0 "" 2
# 123 "lwp.c" 1
	pushq %r15
# 0 "" 2
# 123 "lwp.c" 1
	pushq %rbp
# 0 "" 2
# 124 "lwp.c" 1
	movq  %rsp,%rax
# 0 "" 2
#NO_APP
	movq	%rax, main_sp(%rip)
	movq	main_sp(%rip), %rax
	movq	%rax, main_context+24(%rip)
	movl	start(%rip), %eax
	addl	$1, %eax
	movl	%eax, start(%rip)
.L11:
	movq	scheduler(%rip), %rax
	call	*%rax
	movl	%eax, lwp_running(%rip)
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable+16, %rax
	movq	8(%rax), %rax
#APP
# 130 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 131 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 131 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 131 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
.L8:
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE5:
	.size	lwp_start, .-lwp_start
	.globl	lwp_yield
	.type	lwp_yield, @function
lwp_yield:
.LFB6:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$16, %rsp
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	%rax, -8(%rbp)
#APP
# 140 "lwp.c" 1
	pushq %rax
# 0 "" 2
# 140 "lwp.c" 1
	pushq %rbx
# 0 "" 2
# 140 "lwp.c" 1
	pushq %rcx
# 0 "" 2
# 140 "lwp.c" 1
	pushq %rdx
# 0 "" 2
# 140 "lwp.c" 1
	pushq %rsi
# 0 "" 2
# 140 "lwp.c" 1
	pushq %rdi
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r8
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r9
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r10
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r11
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r12
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r13
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r14
# 0 "" 2
# 140 "lwp.c" 1
	pushq %r15
# 0 "" 2
# 140 "lwp.c" 1
	pushq %rbp
# 0 "" 2
# 141 "lwp.c" 1
	movq  %rsp,%rax
# 0 "" 2
#NO_APP
	movq	%rax, -16(%rbp)
	movq	-8(%rbp), %rax
	movq	-16(%rbp), %rdx
	movq	%rdx, 24(%rax)
	movl	lwp_running(%rip), %eax
	addl	$1, %eax
	movl	%eax, lwp_running(%rip)
	movl	$0, %eax
	call	lwp_start
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	lwp_yield, .-lwp_yield
	.globl	lwp_stop
	.type	lwp_stop, @function
lwp_stop:
.LFB7:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	%rax, -8(%rbp)
#APP
# 155 "lwp.c" 1
	pushq %rax
# 0 "" 2
# 155 "lwp.c" 1
	pushq %rbx
# 0 "" 2
# 155 "lwp.c" 1
	pushq %rcx
# 0 "" 2
# 155 "lwp.c" 1
	pushq %rdx
# 0 "" 2
# 155 "lwp.c" 1
	pushq %rsi
# 0 "" 2
# 155 "lwp.c" 1
	pushq %rdi
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r8
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r9
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r10
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r11
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r12
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r13
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r14
# 0 "" 2
# 155 "lwp.c" 1
	pushq %r15
# 0 "" 2
# 155 "lwp.c" 1
	pushq %rbp
# 0 "" 2
# 156 "lwp.c" 1
	movq  %rsp,%rax
# 0 "" 2
#NO_APP
	movq	%rax, -16(%rbp)
	movq	-8(%rbp), %rax
	movq	-16(%rbp), %rdx
	movq	%rdx, 24(%rax)
	movq	main_sp(%rip), %rax
#APP
# 159 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 160 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 160 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 160 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
	movl	start(%rip), %eax
	subl	$1, %eax
	movl	%eax, start(%rip)
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE7:
	.size	lwp_stop, .-lwp_stop
	.globl	lwp_exit
	.type	lwp_exit, @function
lwp_exit:
.LFB8:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$16, %rsp
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	8(%rax), %rax
	movq	%rax, %rdi
	call	free
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	$0, 8(%rax)
	movl	lwp_procs(%rip), %eax
	subl	$1, %eax
	movl	%eax, lwp_procs(%rip)
	movl	lwp_procs(%rip), %eax
	testl	%eax, %eax
	jne	.L15
	movq	main_context+24(%rip), %rax
#APP
# 176 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 177 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 177 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 177 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
	jmp	.L14
.L15:
	movl	lwp_running(%rip), %eax
	movl	%eax, -4(%rbp)
	jmp	.L17
.L18:
	movl	-4(%rbp), %eax
	leal	1(%rax), %edx
	movl	-4(%rbp), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movslq	%edx, %rdx
	salq	$5, %rdx
	addq	$lwp_ptable, %rdx
	movq	(%rdx), %rcx
	movq	%rcx, (%rax)
	movq	8(%rdx), %rcx
	movq	%rcx, 8(%rax)
	movq	16(%rdx), %rcx
	movq	%rcx, 16(%rax)
	movq	24(%rdx), %rdx
	movq	%rdx, 24(%rax)
	addl	$1, -4(%rbp)
.L17:
	movl	lwp_procs(%rip), %eax
	cmpl	%eax, -4(%rbp)
	jl	.L18
	movq	scheduler(%rip), %rax
	call	*%rax
	movl	%eax, lwp_running(%rip)
	movl	lwp_running(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable+16, %rax
	movq	8(%rax), %rax
#APP
# 188 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 189 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 189 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 189 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
.L14:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE8:
	.size	lwp_exit, .-lwp_exit
	.globl	round_robin
	.type	round_robin, @function
round_robin:
.LFB9:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	lwp_running(%rip), %eax
	movl	%eax, -4(%rbp)
	movl	lwp_running(%rip), %edx
	movl	lwp_procs(%rip), %eax
	cmpl	%eax, %edx
	jl	.L20
	movl	$0, -4(%rbp)
.L20:
	movl	-4(%rbp), %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE9:
	.size	round_robin, .-round_robin
	.ident	"GCC: (GNU) 4.8.5 20150623 (Red Hat 4.8.5-44)"
	.section	.note.GNU-stack,"",@progbits

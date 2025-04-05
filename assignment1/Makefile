PLAT=$(shell uname -i)
LWP-EX=liblwp-$(PLAT).a
SN-EX=libsnakes-$(PLAT).a
LWP=liblwp.a

CC = gcc
CFLAGS = -Wall -Werror -g -m32

all: $(LWP)
examples: numbersmain-ex snakemain-ex hungrymain-ex
tests: numbersmain snakemain hungrymain

snakemain: snakemain.c snakes.h $(LWP) $(SN-EX)
	$(CC) $(CFLAGS) -o $@ $< $(LWP) $(SN-EX) -lncurses

snakemain-ex: snakemain.c snakes.h $(LWP-EX) $(SN-EX)
	$(CC) $(CFLAGS) -o $@ $< $(LWP-EX) $(SN-EX) -lncurses

hungrymain: hungrymain.c snakes.h $(LWP) $(SN-EX)
	$(CC) $(CFLAGS) -o $@ $< $(LWP) $(SN-EX) -lncurses

hungrymain-ex: hungrymain.c snakes.h $(LWP-EX) $(SN-EX)
	$(CC) $(CFLAGS) -o $@ $< $(LWP-EX) $(SN-EX) -lncurses

numbersmain: numbersmain.c lwp.h $(LWP)
	$(CC) $(CFLAGS) -o $@ $< $(LWP)

numbersmain-ex: numbersmain.c lwp.h $(LWP-EX)
	cc -Wall -Werror -g -o $@ $< $(LWP-EX)

$(LWP): lwp.o
	ar r $@ lwp.o
	ranlib $@

lwp.o: lwp.c lwp.h
	$(CC) $(CFLAGS) -c -o $@ $<
	$(CC) -S $<

thread_test.o: thread_test.c lwp.h
	$(CC) $(CFLAGS) -c $<

thread_test: lwp.o thread_test.o
	$(CC) $(CFLAGS) -o $@ $^

clean:
	-rm -f numbersmain snakemain hungrymain $(LWP) lwp.o liblwp.o numbersmain-ex snakemain-ex hungrymain-ex
	-rm -f lwp.s
	-rm -f *.o thread_test

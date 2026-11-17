# Mesmas flags nas três versões, como pede a seção 5.
CC      = gcc
MPICC   = mpicc
CFLAGS  = -O2 -std=c11 -Wall -Wextra

.PHONY: all clean teste

all: bin/sequencial bin/arvore bin/balanceada

bin:
	mkdir -p bin

bin/sequencial: src/sequencial.c src/comum.c src/comum.h | bin
	$(CC) $(CFLAGS) -o $@ src/sequencial.c src/comum.c -lrt

bin/arvore: src/arvore.c src/comum.c src/comum.h | bin
	$(MPICC) $(CFLAGS) -o $@ src/arvore.c src/comum.c

bin/balanceada: src/balanceada.c src/comum.c src/comum.h | bin
	$(MPICC) $(CFLAGS) -o $@ src/balanceada.c src/comum.c

bin/confere: src/confere.c src/comum.c src/comum.h | bin
	$(CC) $(CFLAGS) -o $@ src/confere.c src/comum.c

teste: bin/confere
	./bin/confere

clean:
	rm -rf bin

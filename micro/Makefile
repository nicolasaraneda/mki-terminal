# micro/Makefile — arnés de medición de latencia. Instrumento de medición,
# no sistema de trading. Sin dependencias fuera de libc.

CC      := gcc
CFLAGS  := -O2 -Wall -Wextra -Werror -std=c11 -D_POSIX_C_SOURCE=200809L
SRC_DIR := src
BIN_DIR := bin
RES_DIR := resultados
TEST_DIR:= tests

BINARIOS := reloj syscall jitter memoria mensaje red

COMUN_OBJ := $(BIN_DIR)/comun.o

.PHONY: all limpiar ejecutar test

all: $(addprefix $(BIN_DIR)/bench_,$(BINARIOS))

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(RES_DIR):
	mkdir -p $(RES_DIR)

$(COMUN_OBJ): $(SRC_DIR)/comun.c $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) -c $(SRC_DIR)/comun.c -o $@

$(BIN_DIR)/bench_reloj: $(SRC_DIR)/bench_reloj.c $(COMUN_OBJ) $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/bench_reloj.c $(COMUN_OBJ) -o $@

$(BIN_DIR)/bench_syscall: $(SRC_DIR)/bench_syscall.c $(COMUN_OBJ) $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/bench_syscall.c $(COMUN_OBJ) -o $@

$(BIN_DIR)/bench_jitter: $(SRC_DIR)/bench_jitter.c $(COMUN_OBJ) $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/bench_jitter.c $(COMUN_OBJ) -o $@

$(BIN_DIR)/bench_memoria: $(SRC_DIR)/bench_memoria.c $(COMUN_OBJ) $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/bench_memoria.c $(COMUN_OBJ) -o $@

$(BIN_DIR)/bench_mensaje: $(SRC_DIR)/bench_mensaje.c $(COMUN_OBJ) $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/bench_mensaje.c $(COMUN_OBJ) -o $@

$(BIN_DIR)/bench_red: $(SRC_DIR)/bench_red.c $(COMUN_OBJ) $(SRC_DIR)/comun.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/bench_red.c $(COMUN_OBJ) -o $@

# Corre los seis benchmarks en orden, cada uno escribe su propio JSON en
# resultados/. bench_red se corre al final y nunca hace fallar el make si no
# hay salida de red (devuelve 0 en ambos casos, ver bench_red.c).
ejecutar: all | $(RES_DIR)
	$(BIN_DIR)/bench_reloj
	$(BIN_DIR)/bench_syscall
	$(BIN_DIR)/bench_jitter
	$(BIN_DIR)/bench_memoria
	$(BIN_DIR)/bench_mensaje
	$(BIN_DIR)/bench_red

# El arnés se prueba a sí mismo: tests/test_arnes.sh verifica que una espera
# conocida se reporta dentro de tolerancia y que el JSON emitido es válido.
test: all | $(RES_DIR)
	bash $(TEST_DIR)/test_arnes.sh

limpiar:
	rm -rf $(BIN_DIR) $(RES_DIR)/*.json

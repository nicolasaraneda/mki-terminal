# micro/rtl/Makefile — simulación y síntesis del pipeline de decisión.
#
# Un solo comando para todo:   make            (vectores + simulación + síntesis)
# Solo la simulación:          make simular
# Solo los números de síntesis: make sintetizar
#
# El toolchain es OSS CAD Suite descomprimido en ~/.local/opt (sin root, sin
# sudo). Ver micro/TOOLCHAIN.md para reproducirlo desde cero. Si `yosys` ya
# está en el PATH se usa ése.

OSS_BIN := $(HOME)/.local/opt/oss-cad-suite/bin
export PATH := $(OSS_BIN):$(PATH)

IVERILOG := iverilog
VVP      := vvp
YOSYS    := yosys
NEXTPNR  := nextpnr-ice40
ICEPACK  := icepack
ICETIME  := icetime
PYTHON   := python3

RTL := etapa_ingesta.v etapa_features.v etapa_puntaje.v etapa_decision.v \
       uart_tx.v etapa_salida.v pipeline_top.v

# El envoltorio de placa suma el UART RX, la carga de pesos y el serializador
# del sello. Se sintetiza APARTE para poder restar su costo (ver sint_top.v).
RTL_PLACA := $(RTL) uart_rx.v sint_top.v

DIR_SIM  := sim
DIR_SINT := sintesis
DIR_VEC  := vectores

# Las cuatro configuraciones. F1 es el modelo campeón real (beta x SOX);
# F3 y F6 existen para medir cómo escala el ÁREA, no para afirmar que el
# modelo mejora. F1SP ("sin pesos") aísla el costo del multiplicador: la
# diferencia de LUTs contra F1 es el multiplicador y NADA MÁS.
CONFIGS := F1 F3 F6 F1SP

NF_F1   := 1
NF_F3   := 3
NF_F6   := 6
NF_F1SP := 1
PESOS_F1   := 1
PESOS_F3   := 1
PESOS_F6   := 1
PESOS_F1SP := 0

# iCE40HX1K en encapsulado tq144: es el de la Nandland Go Board.
DISPOSITIVO := hx1k
PAQUETE     := tq144

.PHONY: all vectores simular sintetizar multiplicador etapas placas limpiar \
        $(addprefix sim-,$(CONFIGS)) $(addprefix sint-,$(CONFIGS))

all: simular multiplicador etapas sintetizar placas

# Área de cada etapa por separado, contra la estimación de RTL.md §2 fila por
# fila. Es la única forma de decir DÓNDE se equivocó la estimación, y además
# la única forma de medir la etapa 2: dentro del pipeline con F=1 es lógica
# muerta y el sintetizador la borra (ver medir_etapas.py).
etapas: | $(DIR_SINT)
	$(PYTHON) medir_etapas.py 2>&1 | tee $(DIR_SINT)/etapas.log

# Cuánto ocupa en cada placa candidata: LCs colocadas en iCE40 y celdas
# Artix-7 del mapeo. Ver medir_placas.py para por qué una es más dura que la otra.
placas: | $(DIR_SINT)
	$(PYTHON) medir_placas.py 2>&1 | tee $(DIR_SINT)/placas.log

# ---------------------------------------------------------------------------
# Micro-medición aislada del costo de un multiplicador. Es el número del que
# depende toda la conclusión sobre si el pipeline cabe, así que se mide solo,
# fuera del pipeline, donde nada más lo puede contaminar.
# ---------------------------------------------------------------------------
MULS := mul16x16_con_signo mul16x16_sin_signo mul16x16_truncado mul8x8_con_signo

multiplicador: | $(DIR_SINT)
	@echo ""
	@echo "########## costo aislado de un multiplicador (iCE40, sin DSP) ##########"
	@for m in $(MULS); do \
	    printf "  %-22s " $$m; \
	    $(YOSYS) -p "read_verilog costo_multiplicador.v; synth_ice40 -top $$m" 2>&1 \
	      | grep -E "^ +[0-9]+ +SB_(LUT4|CARRY)" | tail -2 \
	      | awk '{printf "%s %s  ", $$1, $$2}'; \
	    echo ""; \
	done | tee $(DIR_SINT)/multiplicador.log

# ---------------------------------------------------------------------------
# Vectores: se generan desde senales.db en modo `ro`. Nunca se escribe la base.
# ---------------------------------------------------------------------------
vectores: $(DIR_VEC)/parametros.vh

$(DIR_VEC)/parametros.vh: referencia.py
	$(PYTHON) referencia.py

# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------
simular: $(addprefix sim-,$(CONFIGS))

define REGLA_SIM
sim-$(1): vectores | $(DIR_SIM)
	@echo ""
	@echo "########## simulacion $(1) ##########"
	$(IVERILOG) -g2012 -Wall -I. -I$(DIR_VEC) \
	    -DCFG_NF=$(NF_$(1)) -DCFG_PESOS=$(PESOS_$(1)) \
	    -DCFG_ARCHIVO_ESPERADO='"$(DIR_VEC)/esperado_$(1).hex"' \
	    -o $(DIR_SIM)/tb_$(1).vvp $(RTL) tb/tb_pipeline.v
	$(VVP) $(DIR_SIM)/tb_$(1).vvp | tee $(DIR_SIM)/sim_$(1).log
endef
$(foreach c,$(CONFIGS),$(eval $(call REGLA_SIM,$(c))))

# ---------------------------------------------------------------------------
# Síntesis + place & route + timing, contra el iCE40HX1K real.
#
# `synth_ice40 -top` mapea a la arquitectura real de la placa (SB_LUT4,
# SB_DFF, SB_RAM40_4K). El reporte de utilización que sale de nextpnr es la
# EVIDENCIA DURA que fpga.md §2 pedía — no una estimación a ojo.
#
# nextpnr puede FALLAR por falta de recursos. Eso NO es un error del Makefile:
# es el resultado. Por eso cada configuración corre con `-` (no aborta el
# make) y el log queda guardado para leer por qué no entró.
# ---------------------------------------------------------------------------
sintetizar: $(addprefix sint-,$(CONFIGS))

# Los parámetros van por -D y no por `chparam` de yosys: chparam DERIVA un
# módulo con nombre nuevo ($paramod$hash\pipeline_top) y el `hierarchy -top`
# que synth_ice40 corre después ya no encuentra el nombre original. Se perdió
# un rato averiguándolo; queda escrito para no repetirlo.
define REGLA_SINT
sint-$(1): | $(DIR_SINT)
	@echo ""
	@echo "########## sintesis $(1) (iCE40$(DISPOSITIVO)-$(PAQUETE)) ##########"
	@# (a) el pipeline SOLO: es el área comparable con la tabla de RTL.md §2.
	-$(YOSYS) -p "read_verilog -I. -DCFG_NF=$(NF_$(1)) -DCFG_PESOS=$(PESOS_$(1)) $(RTL); \
	    synth_ice40 -top pipeline_top -json $(DIR_SINT)/pipe_$(1).json" \
	    > $(DIR_SINT)/yosys_pipe_$(1).log 2>&1
	@# (b) el envoltorio de placa: es lo único que puede ir a place & route,
	@#     porque pipeline_top expone 165 pines y el tq144 tiene ~96.
	-$(YOSYS) -p "read_verilog -I. -DCFG_NF=$(NF_$(1)) -DCFG_PESOS=$(PESOS_$(1)) $(RTL_PLACA); \
	    synth_ice40 -top sint_top -json $(DIR_SINT)/sint_$(1).json" \
	    > $(DIR_SINT)/yosys_sint_$(1).log 2>&1
	-$(NEXTPNR) --$(DISPOSITIVO) --package $(PAQUETE) \
	    --json $(DIR_SINT)/sint_$(1).json --asc $(DIR_SINT)/$(1).asc \
	    --freq 12 --seed 1 \
	    > $(DIR_SINT)/nextpnr_$(1).log 2>&1
	-$(ICEPACK) $(DIR_SINT)/$(1).asc $(DIR_SINT)/$(1).bin 2>/dev/null
	-$(ICETIME) -d $(DISPOSITIVO) -m -t $(DIR_SINT)/$(1).asc \
	    > $(DIR_SINT)/icetime_$(1).log 2>&1
	@$(PYTHON) reportar_sintesis.py $(1) || true
endef
$(foreach c,$(CONFIGS),$(eval $(call REGLA_SINT,$(c))))

$(DIR_SIM):
	mkdir -p $(DIR_SIM)

$(DIR_SINT):
	mkdir -p $(DIR_SINT)

limpiar:
	rm -rf $(DIR_SIM) $(DIR_SINT)

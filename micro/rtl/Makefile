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

# Anchos de bus de entrada para la variante de ingesta ancha (ver
# etapa_ingesta_ancha.v). B=1 reproduce el comportamiento original y es el
# control: si esa fila no da 32 ciclos y 181/181, la variante está mal.
ANCHOS_B := 1 2 4 7 14 28

RTL_ANCHO := etapa_ingesta_ancha.v etapa_features.v etapa_puntaje.v \
             etapa_decision.v uart_tx.v etapa_salida.v pipeline_top_ancho.v

# Frente E (1-sep-2026). Las fuentes de las tres variantes nuevas. Cada lista
# es explícita y no se deriva de otra: `medir_techo.py` mide una cosa distinta
# con cada una y una lista compartida haría que tocar una moviera las otras.
RTL_MULTI := etapa_ingesta_ancha.v etapa_features.v etapa_puntaje.v \
             etapa_decision.v uart_tx.v etapa_salida.v pipeline_top_multi.v

RTL_DEMO  := $(RTL_ANCHO) fuente_bram.v demo_top.v

TABLAS_T  := 1 8 16

.PHONY: all vectores simular sintetizar multiplicador etapas placas limpiar \
        a7 ancho error-ancho \
        ancho-gate multi demo huecos hueco-gate techo variantes semillas empaquetar \
        $(addprefix sim-,$(CONFIGS)) $(addprefix sint-,$(CONFIGS))

all: simular multiplicador etapas sintetizar placas

# ---------------------------------------------------------------------------
# Arty A7-100T (XC7A100TCSG324-1). Todo esto es MAPEO TECNOLÓGICO, no place &
# route: OSS CAD Suite no trae nextpnr-xilinx y Vivado no se pudo instalar
# (ver micro/TOOLCHAIN.md §3). No hay Fmax y se dice en cada tabla.
# Resultados y lectura en GEMELO/MICRO/SINTESIS_A7.md.
# ---------------------------------------------------------------------------
a7: | $(DIR_SINT)
	$(PYTHON) medir_a7.py 2>&1 | tee $(DIR_SINT)/a7.log

# Cuánto error de cuantización compra cada bit de más, contra el álgebra en
# float64 Y contra la fila sellada. Sólo Python: senales.db en modo ro.
error-ancho:
	$(PYTHON) medir_ancho_error.py

# La variante de ingesta ancha: MISMO resultado bit a bit, latencia
# ceil(28/B)+4. La predicción está escrita en pipeline_top_ancho.v ANTES de
# correr y el banco falla si no se cumple.
ancho: vectores | $(DIR_SIM)
	@for b in $(ANCHOS_B); do \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=$$b -DCFG_NF=1 -DCFG_PESOS=1 \
	        -o $(DIR_SIM)/tb_ancho_$$b.vvp $(RTL_ANCHO) tb/tb_pipeline_ancho.v \
	        2> $(DIR_SIM)/iverilog_ancho_$$b.log; \
	    $(VVP) $(DIR_SIM)/tb_ancho_$$b.vvp; \
	done | tee $(DIR_SIM)/ancho.log

# ---------------------------------------------------------------------------
# FRENTE E (1-sep-2026) — confirmación de la ingesta ancha, techo recalculado y
# dos variantes. Lectura completa en GEMELO/MICRO/INGESTA_ANCHA.md.
# ---------------------------------------------------------------------------

# La MISMA prueba contra tres diseños bajo prueba distintos: el RTL, la netlist
# mapeada a celdas iCE40 y la mapeada a celdas Artix-7. Que los 181 vectores y
# la latencia sobrevivan al MAPEO TECNOLOGICO es una familia de evidencia
# distinta de simular el RTL — que es justo lo que la regla de la casa pide
# cuando hay que confirmar una cifra que produjo el propio RTL. El banco lleva
# ademas su propio contador de flancos, independiente del contador de 48 bits
# que vive en `etapa_salida`.
ancho-gate: vectores | $(DIR_SIM) $(DIR_SINT)
	@for b in 1 4 28; do \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=$$b -DCFG_NF=1 -DCFG_PESOS=1 \
	        -DCFG_ETIQUETA='"rtl"' -o $(DIR_SIM)/tb_gate_rtl_$$b.vvp \
	        $(RTL_ANCHO) tb/tb_pipeline_gate.v 2>/dev/null; \
	    $(VVP) $(DIR_SIM)/tb_gate_rtl_$$b.vvp; \
	    $(YOSYS) -p "read_verilog -I. -DCFG_B=$$b -DCFG_NF=1 -DCFG_PESOS=1 $(RTL_ANCHO); \
	        synth_ice40 -top pipeline_top_ancho; \
	        write_verilog -noattr $(DIR_SINT)/netlist_ice40_B$$b.v" \
	        > $(DIR_SINT)/yosys_netlist_ice40_B$$b.log 2>&1; \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=$$b -DCFG_ETIQUETA='"gate-ice40"' \
	        -o $(DIR_SIM)/tb_gate_ice40_$$b.vvp $(DIR_SINT)/netlist_ice40_B$$b.v \
	        `$(YOSYS)-config --datdir`/ice40/cells_sim.v tb/tb_pipeline_gate.v 2>/dev/null; \
	    $(VVP) $(DIR_SIM)/tb_gate_ice40_$$b.vvp; \
	    $(YOSYS) -p "read_verilog -I. -DCFG_B=$$b -DCFG_NF=1 -DCFG_PESOS=1 $(RTL_ANCHO); \
	        synth_xilinx -family xc7 -flatten -top pipeline_top_ancho; \
	        write_verilog -noattr $(DIR_SINT)/netlist_xc7_B$$b.v" \
	        > $(DIR_SINT)/yosys_netlist_xc7_B$$b.log 2>&1; \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=$$b -DCFG_ETIQUETA='"gate-xc7"' \
	        -o $(DIR_SIM)/tb_gate_xc7_$$b.vvp $(DIR_SINT)/netlist_xc7_B$$b.v \
	        `$(YOSYS)-config --datdir`/xilinx/cells_sim.v \
	        `$(YOSYS)-config --datdir`/xilinx/cells_xtra.v tb/tb_pipeline_gate.v 2>/dev/null; \
	    $(VVP) $(DIR_SIM)/tb_gate_xc7_$$b.vvp; \
	done | tee $(DIR_SIM)/ancho_gate.log

# VARIANTE 1: tabla de pesos por instrumento. Los señuelos en los T-1 slots que
# no corresponden son lo que hace que este test distinga una tabla de un
# registro único. La contraprueba (`-DCFG_SABOTAJE_SLOT`) tiene que FALLAR.
multi: vectores | $(DIR_SIM)
	@for t in $(TABLAS_T); do \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=4 -DCFG_T=$$t -DCFG_NF=1 \
	        -DCFG_PESOS=1 -o $(DIR_SIM)/tb_multi_T$$t.vvp \
	        $(RTL_MULTI) tb/tb_pipeline_multi.v 2>/dev/null; \
	    $(VVP) $(DIR_SIM)/tb_multi_T$$t.vvp; \
	done | tee $(DIR_SIM)/multi.log
	@echo "########## contraprueba: con el decodificador saboteado TIENE que fallar ##########"
	@$(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=4 -DCFG_T=8 -DCFG_NF=1 -DCFG_PESOS=1 \
	    -DCFG_SABOTAJE_SLOT -o $(DIR_SIM)/tb_multi_sabotaje.vvp \
	    $(RTL_MULTI) tb/tb_pipeline_multi.v 2>/dev/null
	@$(VVP) $(DIR_SIM)/tb_multi_sabotaje.vvp | tail -6 || true

# VARIANTE 2: el sistema autónomo. Un pulso de arranque y 181 sellos desde
# memoria del chip, sin estímulo externo. Es lo que hace realizable B=28.
demo: empaquetar | $(DIR_SIM)
	@for b in 4 28; do \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=$$b \
	        -o $(DIR_SIM)/tb_demo_$$b.vvp $(RTL_DEMO) tb/tb_demo.v 2>/dev/null; \
	    $(VVP) $(DIR_SIM)/tb_demo_$$b.vvp; \
	done | tee $(DIR_SIM)/demo.log

# EL REQUISITO R1 DE RTL.md §7, EJECUTABLE. `huecos` (abajo) MIDE el barrido;
# esto lo VERIFICA: que en el mínimo reproduzca bit a bit, que por debajo se
# rompa, y —lo que separa este target de un rojo cualquiera— que se rompa POR
# LA RAZÓN CORRECTA y no por un timeout, un error de compilación o el propio
# guardia. Corre en medio segundo: no hay excusa para no tenerlo en el gate.
hueco-gate: empaquetar | $(DIR_SIM)
	$(PYTHON) verificar_hueco.py 2>&1 | tee $(DIR_SIM)/hueco_gate.log

# El hueco mínimo entre mensajes. Con 0 ó 1 la latencia SIGUE dando 11 ciclos
# exactos y los sellos salen mal: por eso hace falta barrerlo y no confiar en
# que "la latencia da bien". Necesita el bypass del guardia.
huecos: empaquetar | $(DIR_SIM)
	@for h in 0 1 2 3 8; do \
	    $(IVERILOG) -g2012 -I. -I$(DIR_VEC) -DCFG_B=4 -DCFG_HUECO=$$h \
	        -DCFG_PERMITIR_HUECO_INSEGURO -o $(DIR_SIM)/tb_hueco_$$h.vvp \
	        $(RTL_DEMO) tb/tb_demo.v 2>/dev/null; \
	    printf "HUECO=%-2s " $$h; \
	    $(VVP) $(DIR_SIM)/tb_hueco_$$h.vvp 2>&1 | grep -E "fallos bit a bit" || true; \
	done | tee $(DIR_SIM)/huecos.log

empaquetar: $(DIR_VEC)/mensajes_b4.hex $(DIR_VEC)/mensajes_b28.hex

$(DIR_VEC)/mensajes_b4.hex $(DIR_VEC)/mensajes_b28.hex: empaquetar_vectores.py $(DIR_VEC)/mensajes.hex
	$(PYTHON) empaquetar_vectores.py 4 28

# ¿Se movió el techo de 240 tickers? Se sintetiza el barrido entero otra vez en
# vez de deducirlo. Es lo caro de este Makefile: son 21 síntesis.
techo: | $(DIR_SINT)
	$(PYTHON) medir_techo.py techo 2>&1 | tee $(DIR_SINT)/techo.log

variantes: | $(DIR_SINT)
	$(PYTHON) medir_techo.py sin_dsp tabla demo 2>&1 | tee $(DIR_SINT)/variantes.log

# QUÉ TIENE INTERVALO Y QUÉ NO. Las cuentas de celdas son determinísticas; el
# Fmax de nextpnr NO — depende de la semilla del colocador. Este target lo
# mide en vez de suponerlo, y es la razón por la que ningún Fmax de este
# proyecto debería citarse como un número pelado.
semillas: | $(DIR_SINT)
	@echo "semilla  LC  Fmax(MHz)   [F1SP sobre hx1k-tq144, la fila que dice CABE]"
	@for s in 1 2 3 4 5 6 7 8 9 10; do \
	    $(NEXTPNR) --$(DISPOSITIVO) --package $(PAQUETE) \
	        --json $(DIR_SINT)/sint_F1SP.json --asc /dev/null --freq 12 --seed $$s \
	        > $(DIR_SINT)/semilla_$$s.log 2>&1; \
	    printf "%-8s %s  %s\n" $$s \
	      "`grep -oE 'ICESTORM_LC: *[0-9]+' $(DIR_SINT)/semilla_$$s.log | head -1 | grep -oE '[0-9]+'`" \
	      "`grep -oE \"Max frequency for clock '[^']+': *[0-9.]+\" $(DIR_SINT)/semilla_$$s.log | tail -1 | grep -oE '[0-9.]+$$'`"; \
	done | tee $(DIR_SINT)/semillas_f1sp.log

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

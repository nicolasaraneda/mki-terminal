"""Corrida 16-2: pliega R6 del addendum del auditor (UltimoSelloDinero con las 21 claves de _CLAVES_ULTIMO)."""
import pathlib, re, sys
wt = pathlib.Path(sys.argv[1])
p = wt / "frontend" / "src" / "lib" / "tipos.ts"; s = p.read_text(encoding="utf-8")
m = re.search(r"export interface UltimoSelloDinero \{\n(.*?)\n\}\n", s, re.S); assert m
nuevo = """export interface UltimoSelloDinero {
  // las 21 claves de `_CLAVES_ULTIMO` de dinero/sello_dinero.py (R6 del auditor, corrida 16-2):
  // `ultimo_sello` y `ultimo_intento` comparten la forma; para un intento, `estado_timing` e
  // `insumo_ext_archivo` (.no_verificable.csv) son lo que lo distingue de un sello
  fecha_sello: string
  fecha_insumo: string
  timestamp_utc: string
  available_at: string
  sesion_objetivo: string
  apertura_objetivo_utc: string
  estado: string
  estado_timing: string
  estado_dia: string
  insumo_completo: number
  cuenta_para_N: number
  juego: string
  presupuesto_usd: number
  insumo_ext_sha256: string
  insumo_ext_archivo: string
  insumo_base_sha256: string
  reglas_sha256: string
  sellador_sha256: string
  plataforma_version: string
  version_sello: string
  creado_en: string
}
"""
s = s.replace(m.group(0), nuevo); p.write_text(s, encoding="utf-8")
p = wt / "tests" / "test_b2_intentos_visibles_16_2.py"; s = p.read_text(encoding="utf-8")
a = '''    assert "ultimo_intento: UltimoSelloDinero | null" in e0 and "ultimo_sello: UltimoSelloDinero | null" in tipos
'''
b = '''    assert "ultimo_intento: UltimoSelloDinero | null" in e0 and "ultimo_sello: UltimoSelloDinero | null" in tipos
    # R6 del auditor (corrida 16-2): la interfaz cubre las 21 claves de `_CLAVES_ULTIMO`, ni una menos
    cuerpo = re.search(r"export interface UltimoSelloDinero \\{(.*?)\\n\\}", tipos, re.S).group(1)
    campos = set(re.findall(r"^\\s+(\\w+):", cuerpo, re.M))
    assert campos == set(S._CLAVES_ULTIMO), (sorted(set(S._CLAVES_ULTIMO) - campos), sorted(campos - set(S._CLAVES_ULTIMO)))
'''
assert s.count(a) == 1; p.write_text(s.replace(a, b), encoding="utf-8"); print("R6 plegada en", wt)

"""Corrida 16-2: pliega R1, R2 y el cosmético del dictamen del auditor sobre un
worktree que ya tiene el camino T aplicado. Se corre idéntico en el worktree de
trabajo (final) y en uno fresco (HEAD + camino_T v1) para regenerar el diff."""
import pathlib
import sys

wt = pathlib.Path(sys.argv[1])

# ---------------------------------------------------------------- sellador
p = wt / "dinero" / "sello_dinero.py"
s = p.read_text(encoding="utf-8")

a = '''    """Las columnas de una fila sellada y sus dos disparadores de
    inmutabilidad. E0.3: `intentos_no_verificables` se crea con ESTE mismo
    texto (una definición, no dos que puedan divergir); la `UNIQUE` vale
    dentro de cada tabla, así que un intento y el sello bueno de la misma
    fecha conviven, cada uno en la suya."""
'''
b = '''    """Las columnas de una fila sellada y sus dos disparadores de
    inmutabilidad. E0.3: `intentos_no_verificables` se crea con ESTE mismo
    texto (una definición, no dos que puedan divergir); la `UNIQUE` vale
    dentro de cada tabla, así que un intento y el sello bueno de la misma
    fecha conviven, cada uno en la suya.

    ADVERTENCIA (R2 del auditor, corrida 16-2): `CREATE TABLE IF NOT EXISTS`
    es un no-op sobre una tabla que ya existe y NO le agrega columnas. La
    definición única sólo garantiza paridad en bases nacidas con E0.3; sobre
    la base real, agregar una columna acá exige una migración aparte (con su
    acta), o las dos tablas divergen en silencio y el INSERT compartido
    revienta. Un test de integridad compara las columnas sobre la base real."""
'''
assert s.count(a) == 1; s = s.replace(a, b)

a = '''        previas = con.execute("SELECT DISTINCT insumo_ext_sha256, timestamp_utc FROM sellos_dinero "
                              "WHERE fecha_insumo = ? AND juego = ?", (fecha_insumo, dec["juego"])).fetchall()
'''
b = '''        previas = con.execute(f"SELECT DISTINCT insumo_ext_sha256, timestamp_utc FROM {TABLA_SELLOS} "
                              "WHERE fecha_insumo = ? AND juego = ?", (fecha_insumo, dec["juego"])).fetchall()
'''
assert s.count(a) == 1; s = s.replace(a, b)

a = '''        insertadas = 0
        for f in dec["filas"]:
            cur = con.execute(f"""
                INSERT INTO {tabla}
'''
b = '''        if meta_ext.get("persistido") is False:
            # R1 del auditor (corrida 16-2, F3): un insumo que `congelar_extension`
            # mandó a un temporal (la fecha ya tenía sello o intento con OTRO sha) no
            # puede terminar en una fila: main() borra ese archivo y la fila citaría un
            # sha que mañana no existe. Todas las ramas legítimas ya salieron arriba con
            # cero filas; la única que llegaba acá era un cambio de `juego_activo` entre
            # dos disparos de la misma fecha (`previas` filtra por juego). Queda rastro.
            cita = _cita_en(con, TABLA_SELLOS, fecha_insumo) or _cita_en(con, TABLA_INTENTOS, fecha_insumo)
            detalle = (f"insumo NO persistido del {fecha_insumo} con juego {dec['juego']!r} sin filas previas de ese "
                       "juego (cambio de juego_activo entre dos disparos de la misma fecha): la fecha ya tenía "
                       "evidencia con otro sha y este insumo vive en un temporal que main() borra; NINGUNA fila "
                       f"escrita en {TABLA_SELLOS} ni en {TABLA_INTENTOS} (sólo esta, en divergencias_sello): una "
                       "fila sellada no cita un archivo que no existirá mañana (R1 del auditor, corrida 16-2); "
                       "decisiones_distintas es NULL porque no hay filas del mismo juego con que comparar")
            con.execute("INSERT INTO divergencias_sello (fecha_insumo, timestamp_utc, sha_sellado, sha_nuevo, "
                        "decisiones_distintas, detalle, creado_en) VALUES (?,?,?,?,?,?,?)",
                        (fecha_insumo, ts_emision, (cita or {}).get("sha256", meta_ext["sha256"]), meta_ext["sha256"],
                         None, detalle, creado))
            con.commit()
            return {"resultado": "rechazado_insumo_no_persistido", "fecha_insumo": fecha_insumo,
                    "timestamp_utc": ts_emision, "filas_insertadas": 0, "juego": dec["juego"],
                    "insumo_ext_sha256": meta_ext["sha256"], "sha_sellado": (cita or {}).get("sha256"),
                    "motivo": ("el insumo no está persistido (temporal fuera de la carpeta de evidencia, borrado por "
                               "main): no se inserta ninguna fila que lo cite; fila en divergencias_sello")}
        insertadas = 0
        for f in dec["filas"]:
            cur = con.execute(f"""
                INSERT INTO {tabla}
'''
assert s.count(a) == 1; s = s.replace(a, b)

a = '''    elif r.get("resultado") == "rechazado_evidencia_canonica":
        exportar_csv(RUTA_DB)          # B1: el rechazo dejó su fila en divergencias_sello y también se versiona
'''
b = '''    elif r.get("resultado") == "rechazado_insumo_no_persistido":
        exportar_csv(RUTA_DB)          # R1 (16-2): el rechazo dejó su fila en divergencias_sello y se versiona
        print("RECHAZADO (E0.3, R1): insumo no persistido con juego sin filas previas; fila en divergencias_sello, "
              "ninguna en las tablas de filas:", r.get("motivo"))
    elif r.get("resultado") == "rechazado_evidencia_canonica":
        exportar_csv(RUTA_DB)          # B1: el rechazo dejó su fila en divergencias_sello y también se versiona
'''
assert s.count(a) == 1; s = s.replace(a, b)
p.write_text(s, encoding="utf-8")

# ---------------------------------------------------------------- tests
p = wt / "tests" / "test_sello_dinero.py"
s = p.read_text(encoding="utf-8")

a = '''from dinero import precios
from dinero import sello_dinero as S
'''
b = '''from dinero import precios
from dinero import sello_dinero as S
from dinero import universo_dinero as U
'''
assert s.count(a) == 1; s = s.replace(a, b)

# R2: paridad de columnas sobre la base real + contraprueba; va en la sección 4
a = '''def test_integridad_el_congelado_grande_es_el_que_la_base_cita():
'''
b = '''def _columnas(ruta_db, tabla) -> list:
    """(nombre, tipo) de cada columna, por PRAGMA, en una base abierta en mode=ro."""
    con = S.conectar(ruta_db, solo_lectura=True)
    try:
        return [(c[1], c[2]) for c in con.execute(f"PRAGMA table_info({tabla})").fetchall()]
    finally:
        con.close()


def _verificar_paridad_columnas(principal, intentos):
    """R2 del auditor (corrida 16-2, F4): las dos tablas de filas tienen que
    tener las MISMAS columnas, porque el INSERT de `sellar` es uno solo y
    `CREATE TABLE IF NOT EXISTS` no propaga una columna nueva a la tabla que
    ya existe. Compara nombre y tipo, en orden."""
    assert principal == intentos, ("PARAR Y REPORTAR: las dos tablas de filas divergieron en columnas "
                                   f"(sólo en sellos_dinero: {sorted(set(principal) - set(intentos))}; sólo en "
                                   f"intentos_no_verificables: {sorted(set(intentos) - set(principal))}); una columna "
                                   "nueva en _ddl_filas exige una migración aparte, con acta")


def test_integridad_las_dos_tablas_de_filas_tienen_las_mismas_columnas_en_la_base_real():
    """R2 del auditor (corrida 16-2): la paridad se verifica sobre la base REAL,
    no sobre una fresca de tmp (que por construcción no puede divergir). Salta
    con razón mientras la base real no tenga la tabla de intentos; empieza a
    correr la primera noche con E0.3."""
    if not os.path.exists(S.RUTA_DB):
        pytest.skip(f"sin base real en {S.RUTA_DB}: nada que verificar en este checkout")
    if not _tabla_existe(S.RUTA_DB, "intentos_no_verificables"):
        pytest.skip("la base real todavía no tiene intentos_no_verificables: la paridad se compara cuando el sellador la cree")
    _verificar_paridad_columnas(_columnas(S.RUTA_DB, "sellos_dinero"), _columnas(S.RUTA_DB, "intentos_no_verificables"))


def test_contraprueba_la_paridad_de_columnas_ve_una_base_vieja_a_la_que_init_db_no_le_agrega_la_columna(tmp_path):
    """F4 medida por el auditor: una `sellos_dinero` a la que le falta una
    columna sigue sin ella después de `init_db` (IF NOT EXISTS es un no-op),
    mientras la tabla de intentos nace completa. El verificador tiene que
    verlo; sobre una base nacida en E0.3 tiene que pasar."""
    db = str(tmp_path / "vieja.db")
    con = sqlite3.connect(db)
    con.executescript(S._ddl_filas("sellos_dinero").replace("            insumo_completo INTEGER,            -- E3: 1 si todos los operables tienen cierre en fecha_insumo\\n", ""))
    con.commit(); con.close()
    assert ("insumo_completo", "INTEGER") not in _columnas(db, "sellos_dinero"), "la contraprueba no fabricó la carencia"
    con = S.conectar(db)                      # init_db: crea intentos_no_verificables, NO repara sellos_dinero
    con.close()
    with pytest.raises(AssertionError, match="PARAR Y REPORTAR"):
        _verificar_paridad_columnas(_columnas(db, "sellos_dinero"), _columnas(db, "intentos_no_verificables"))
    db2 = str(tmp_path / "nueva.db")
    S.conectar(db2).close()
    _verificar_paridad_columnas(_columnas(db2, "sellos_dinero"), _columnas(db2, "intentos_no_verificables"))
    assert len(_columnas(db2, "sellos_dinero")) == 36


def test_integridad_el_congelado_grande_es_el_que_la_base_cita():
'''
assert s.count(a) == 1; s = s.replace(a, b)

# R1: la reproducción de F3, al final de la sección 5
s = s.rstrip("\n") + '''


def test_un_cambio_de_juego_entre_dos_disparos_no_inserta_filas_que_citen_un_archivo_que_main_borra(entorno_temporal, base):
    """F3 del auditor (corrida 16-2), reproducida: con la fecha ya sellada por
    el juego A y OTRO insumo, `congelar_extension` manda el insumo al temporal
    (E4-bis, correcto), pero `previas` filtra por juego, así que un disparo
    con `juego_activo` = B llegaba al INSERT y dejaba filas citando
    `ext_<fecha>_divergente_….csv`, que `main()` borra: integridad rota para
    siempre, idéntica en E0.2 y en E0.3 sin la guarda R1. Ahora: cero filas en
    las dos tablas, una fila en `divergencias_sello` que lo declara, y la
    integridad en pie. Rojo sobre el camino T sin R1 por su propia aserción."""
    db = entorno_temporal
    cfg_a = U.reglas()
    assert cfg_a["juego_activo"] == "conservador" and "agresivo" in cfg_a["juegos"]
    ruta1, meta1, r1 = _camino_main(_ext_con_ultima_fila(base, 1.02), db, T_NOCHE)
    assert r1["resultado"] == "sellada" and r1["juego"] == "conservador"
    cfg_b = dict(cfg_a, juego_activo="agresivo")
    t2 = T_NOCHE + timedelta(minutes=1)
    ruta2, meta2 = _congelar(_ext_con_ultima_fila(base, 1.03), BASE_HASTA, t2)
    assert meta2["persistido"] is False and meta2["sha256"] != meta1["sha256"]
    try:
        r2 = S.sellar(ruta2, meta2, ahora_utc=t2, ruta_db=db, cfg=cfg_b)
    finally:
        if os.path.exists(ruta2):
            os.remove(ruta2)                                    # lo que hace main()
    assert r2["filas_insertadas"] == 0, (
        "F3: sellar insertó filas con juego 'agresivo' que citan un archivo que main() borra "
        f"(resultado={r2['resultado']!r}, filas_insertadas={r2['filas_insertadas']})")
    assert r2["resultado"] == "rechazado_insumo_no_persistido" and r2["juego"] == "agresivo"
    assert r2["sha_sellado"] == meta1["sha256"] and r2["insumo_ext_sha256"] == meta2["sha256"]
    assert _cuenta(db, "sellos_dinero") == N_OPERABLES and _cuenta(db, TABLA_INTENTOS) == 0
    assert _cuenta(db, "divergencias_sello") == 1
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    sha_s, sha_n, distintas, detalle = con.execute(
        "SELECT sha_sellado, sha_nuevo, decisiones_distintas, detalle FROM divergencias_sello").fetchone()
    con.close()
    assert (sha_s, sha_n, distintas) == (meta1["sha256"], meta2["sha256"], None)
    assert "NO persistido" in detalle and "'agresivo'" in detalle and "R1 del auditor" in detalle
    # la integridad permanente queda en pie: toda cita apunta a un archivo que existe
    _verificar_citas_en(S.DIR_EXT, _citas_selladas(db, "sellos_dinero"))
    assert sorted(os.listdir(S.DIR_EXT)) == [CANON_CSV, CANON_META]
'''
p.write_text(s + "\n", encoding="utf-8")
print("plegado en", wt)

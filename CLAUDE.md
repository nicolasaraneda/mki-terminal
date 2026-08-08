# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**MKI Terminal** — a self-running research platform analyzing the full semiconductor value chain (rock→chip→data center) with market regime, competitor divergences, AI news sentiment, an openings anticipator, and a **verified, timestamp-sealed track record**. Built in "Etapas" (currently **plataforma 5.0.2 / modelo 4.6.0 — DUAL versioning**: the platform evolves, the signal model is FROZEN; bumping `MODELO_VERSION` is a separate human decision that restarts the clean track record). `DECISIONES.md` logs every autonomous design decision with rationale — consult it before "fixing" anything that looks arbitrary. README.md is the public portfolio page.

**Constitution 5.0 (inviolable):** (1) motor.py signal logic untouchable, model stays 4.6.0; (2) dual versioning everywhere (DB, report, UI); (3) sealed rows are NEVER rewritten — historical errors become documented erratas in DECISIONES.md; (4) every prediction shows signal + uncertainty (n, R², 80% interval) + regime, and the word "confianza" is banned system-wide (tested); (5) nothing is pushed to GitHub by Claude — publishing is the user's manual act; no real money, no broker orders, disclaimer everywhere; (6) Anthropic spend always under a hard daily cap (`NOTICIAS_PRESUPUESTO_USD_DIA` in .env, default 0.50, ledger in data/costos_ia.log, hard brake + Telegram notice at the cap).

## THE MASTER RULE (Etapa 4.6 — read before touching señales/verifier/motor)

**A prediction is only verifiable if it was emitted BEFORE the event it tries to predict, provably via timestamps.** Every prediction row in `senales.db` carries `timestamp_utc` (emission), `exchange`, `sesion_objetivo` (the local session it anticipates), and `available_at` (when the input information became knowable — the UTC close of the SOX session used). The verifier only evaluates predictions whose `timestamp_utc` precedes the UTC open of their target session; late ones become `no_verificable_timing` (kept for audit, excluded from ALL metrics). Pre-4.6 rows are `legacy_pre_4.6` — same treatment. Metrics never mix `modelo_version`s. Never weaken any of this.

## Commands

```bash
# Un comando para todo (Etapa 5.0):
./mki arrancar    # API :8000 + Vite :5173
./mki estado      # jobs, último sello + salud de descarga, presupuesto IA
./mki tests       # pytest completo + anti-look-ahead del motor
./mki auditoria   # revisión de solo lectura (chequeos del vigía + sellos)
./mki reporte     # reporte Telegram AHORA (100% desde el sello)
./mki instalar    # 6 jobs launchd + hook pre-commit

# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt        # versiones FIJADAS (pip freeze curado)

# Dashboard (Streamlit, kept as fallback)
streamlit run app.py

# Daily snapshot + verifier + CSV backups (what launchd runs at 18:15)
python snapshot.py --origen manual     # "programado" is the launchd default

# Anti-look-ahead test of the signal engine (must stay green)
python tests/test_motor.py

# Full pytest suite (api parity, seguridad, autonomía, reporte, backtest)
python -m pytest tests/ -q
cd frontend && npm run build

# Backtest (dry-run; verdict runs are Etapa 5.1, human-triggered)
python -m backtest.motorbt --desde 2026-06-01 --hasta 2026-07-18
```

`tests/test_motor.py` is a plain-assert script; everything else is pytest. Node lives in `~/.local/node` (no brew/sudo). The six launchd jobs (Mon–Fri, Chile time: noticias 17:50 · snapshot 18:15 · reporte 18:25 · backup 18:40 · vigía 19:00 · re-chequeo del vigía 20:30) live in `launchd/` as `__MKI_DIR__` templates — install with `zsh launchd/instalar.sh`. The pre-commit hook (installed by `./mki instalar`) scans staged changes for secret patterns always, and runs the test suite unless the commit only touches `data/backups/` (the daily backup job must never be blocked) or `SKIP_TESTS=1`.

## Etapa 5.0 "Plataforma" — autonomy, security, science-ready

- **`seguridad.py`** — `enmascarar_secretos()` / `ultimos4()`: a secret is never printed whole; ALL error details that can reach a log pass through it (the 11-jul token leak into reporte.log is the reason it exists). Git history was audited clean (GATE A); author identity rewritten to the GitHub noreply.
- **`costos.py`** — the budget guardrail: JSONL ledger `data/costos_ia.log`, `estado_presupuesto()`, hard cap from .env (typo-proof: falls back to 0.50). `mki_noticias.py` checks the cap BETWEEN batches (it drives noticias.py's own functions — internal logic untouched).
- **`registro.py`** — copy-truncate log rotation (2 MB × 2 copies), called by each job for its own log at startup (launchd keeps the fd; append lands clean after truncate).
- **Jobs** — `mki_noticias.py` (RSS + Haiku under budget), `mki_backup.py` (commits ONLY data/backups via pathspec, "Backup diario {fecha}"), `mki_vigia.py` (5 read-only checks; ONE Telegram alert naming exactly what failed; weekends exempt). snapshot.py gained sealed download health (`salud_descarga`, surgical exception #1) and pre-seal partial retry 60/120s on the launchd path only (exception #2) — both with byte-identical no-contamination tests.
- **5.0.1 (vigía con epílogo)** — an alert is never left open: if the snapshot isn't sealed at 19:00, the alert says whether snapshot.py is still retrying (evidence = live process via pgrep; log gives the detail) and announces the 20:30 re-check (`mki_vigia.py --rechequeo`, sixth launchd job — silent unless the marker `data/vigia_pendiente.json` is pending). Retraction "recuperado: sellado HH:MM, descarga N/N" is sent by the re-check or by snapshot.py itself on a late seal (`_epilogo_vigia()`, can never break the seal path); only the retraction consumes the marker. Born from the 29/31-jul audit (seals at 21:23/19:40 after Mac re-sleep froze the retry loop; Yahoo caused the per-ticker failures, DarkWake caused the hours — see DECISIONES.md).
- **5.0.2 (cierre pre-migración)** — global network timeout in the noticias entrypoint (`socket.setdefaulttimeout`; a hung RSS fetch on 3-aug kept the process alive 4 days and launchd never re-fires a label whose process lives — the vigía's alert now names a stuck process). The vigía retraction distinguishes **emisión** from **confirmación** and declares the sealed prediction count (6-aug: the process froze 44 min between stamping `timestamp_utc` 18:24 and committing ~19:08 — the old message "sellado 18:24" contradicted the truthful 18:40 report). The late-seal abstention rule is a formal PROPOSAL in DECISIONES.md — NOT implemented (model 4.6.0 frozen; challenger-model candidate).
- **Sealed extras (additive)** — snapshots: `descarga_ok/total/caidos`, `plataforma_version`, `sox_usado_pct/fecha`; senales_ticker: `beta`; new TERMINAL state `sin_datos_mercado` (≥5 later sessions closed and the source never published the target session — audit-visible, out of ALL metrics; the two stuck Korean rows of 16-jul went there).
- **Telegram report 2.0** — `alertas.componer_reporte_sellado()` builds EVERYTHING from senales.db + noticias.db cache; job, CLI and dashboard button send the same text; sealed gaps are DECLARED ("sin dato sellado hoy ⚠"), never refilled — a test nukes every motor function and the report still composes.
- **`backtest/`** — walk-forward engine B0→B5, design FROZEN in `backtest/DISEÑO.md` (GATE B: staggered verdict layer-vs-layer, mandatory SMH buy-and-hold benchmark, 5.1 trigger = N≥150 live + one regime change, or 3 months — whichever first; execution is the user's call). Read-only by construction (sqlite `mode=ro`), frozen data source per run, PIT features via backward-only rolling ops with a hard `ErrorLookAhead` guard, B2 calls the production model verbatim (reproduces real sealed predictions within 0.05 pp mean). Results in `backtest/resultados/` (resumen.md versioned); every non-5.1 run is stamped NO-CONCLUYENTE.
- **New views** — `/salud` (the 5 jobs by their artifacts — same checks as the vigía —, sealed download health, stuck verifications, AI budget, DB sizes; weekends shown neutral, not red) and `/laboratorio` (the experiment design + 5.1 trigger progress). `/historial` shows Wilson 95% on every hit rate, the calibration curve (rescaled sealed sigma), and region/regime breakdowns with the single-regime honesty caveat. `meta` carries `plataforma_version`; the cinta shows a download-health badge.

## Etapa 4.7 "Fachada" — React frontend + read-only API

- **`api/`** (FastAPI, port 8000) — READ-ONLY: imports motor.py functions, reads senales.db/noticias.db via existing query helpers, never writes, never calls Anthropic (news served from cache only). Contract in `api/CONTRATO.md` — amend it BEFORE changing endpoints. Envelope: `{meta: {generado_en, fecha_datos, regimen, modelo_version, snapshot_hoy}, datos}`. NaN → null via recursive sanitizer. Only presentation logic allowed (base-100, session states, chart correlations) — never a signal.
- **`frontend/`** (Vite + React + TS + Tailwind 4, port 5173) — never computes a signal; types in `src/lib/tipos.ts` mirror the contract. If a number differs from Streamlit, the bug is in `api/` by definition. Design tokens in `src/index.css` (@theme). Rules: cyan budget ≤4/view; hierarchy via bg levels + borders (no glow/gradients); all figures JetBrains Mono tabular; uncertainty (n, R², ±interval) beside every signal figure, never tooltip-only; sealed predictions show "emitida {ts}, antes de la apertura objetivo"; no emojis in UI; empty states say what's missing and when data will exist. Signature element: `CintaHusos` (24h global-day ribbon starting at NY close, Chile time, one micro-lane per exchange). Hidden `/sistema` route is the component catalog.
- **REGLA CERO of 4.7:** motor.py, snapshot.py, noticias.py, alertas.py and the DBs were NOT touched — the track-record experiment keeps running. Streamlit `app.py` stays intact as fallback (port 8501).

## Architecture (Etapa 4.6)

- **`universo.py`** — single source of truth for constants: `UNIVERSO` (ticker → nombre/segmento/nivel/tipo/`duplicado_de`), `ACCIONES`, `TICKERS_POR_NIVEL` (chain excludes `duplicado_de` — TSM counts once via 2330.TW), `BENCHMARK` (= SMH, outside the chain: an own-sector ETF in "final demand" was circular), level 4 = MSFT+GOOGL+META, `MERCADOS_POR_ABRIR`, `MONEDA_TICKER`/`PARES_FX`, `PARES_COMPETIDORES` (Fundición pairs 2330.TW vs UMC, not the ADR), `EXCHANGE_POR_TICKER` (XNYS/XKRX/XTAI/XTKS/XETR; all US listings use XNYS — shared holidays/core hours), `INDICE_LOCAL_POR_EXCHANGE`/`FX_POR_EXCHANGE` (for residualization), `nombre()`. **Never re-declare universe constants elsewhere.** Adding a company touches: `UNIVERSO`, noticias' `EMPRESAS` + `ALIAS_POR_TICKER` + `ALIAS_EMPRESAS`, and `MONEDA_TICKER` if non-USD. Role changes bump `UNIVERSO_VERSION`.

- **`motor.py`** — the signal engine as **pure functions parameterized by date**: `regimen_al`, `puntaje_v0_al`, `roca_chip_al`, `datos_cadena_al`, `divergencias_al` (residualized vs local index + FX by default, simple spread kept for comparison), `betas_al` (rolling window, default 120 trading days), `prediccion_apertura_al` (includes 80% central interval = ±1.2816 × regression-residual σ), `salud_datos_al`. **Guarantee: each `*_al(fecha)` uses ONLY data ≤ fecha.** All raw data flows through ONE point (`_datos_crudos`) so `tests/test_motor.py` can patch it and prove truncating future data changes nothing. Dashboard, snapshot.py, and the future backtest consume these same functions. No Streamlit imports here. If you add a signal, add it as `*_al(fecha)` + extend the test.

- **`calendarios.py`** — market-session timing via `exchange-calendars`: `proxima_sesion_despues_de(exchange, instante_utc)` (the target session of a prediction), `apertura_utc`/`cierre_utc`, `sesion_anterior`, `sesion_ya_cerro` (2h data-publication margin), `tabla_horarios()`. Date-crossing is inherent (Seoul's Monday session opens Sunday ~00:00 UTC).

- **`senales.py`** — SQLite persistence + THE verifier. Schema migrations are additive (`_asegurar_columnas`). The verifier computes the **double objective** per prediction: `gap_pct` (open_obj/close_prev − 1: does the signal EXIST) and `retorno_real_pct` (close_obj/close_prev − 1: is it CAPTURABLE), each with own hit-rate and MAE; plus `calibracion_intervalos()` (empirical coverage of the 80% interval — "pendiente" below `MINIMO_OBSERVACIONES`). Queries filter `legacy = 0 AND modelo_version = current`. `conteo_por_estado()` and `historial_snapshots()` power the audit UI.

- **`snapshot.py`** — importable + standalone. `ejecutar_snapshot(origen)` (idempotent; origins: programado/manual/dashboard) seals predictions with timestamps + sessions; `main()` also runs the verifier, exports CSV backups to `data/backups/` (**versioned in git** on purpose), and prints data health. The dashboard calls `ejecutar_snapshot("dashboard")` as fallback when no snapshot exists today — the verifier, not the dashboard, decides per-prediction verifiability (master rule lives in one place).

- **`version.py`** — `MODELO_VERSION`/`FEATURE_VERSION`/`UNIVERSO_VERSION` (manual bumps; sealed into every snapshot/prediction).

- **`noticias.py`** — RSS + Claude analysis. **Strict entity matching** (`tickers_estrictos`, alias list per ticker): a headline maps to a ticker only if the company is unambiguously mentioned; generic headlines go to the "sector" bucket (feed sector sentiment only). Per-stock sentiment weights = age decay (0.7^days, floor 0.1) × `relevancia` (0–1, from the Haiku JSON; pre-4.6 NULL = 1.0). Dedup on insert + retroactively (`migrar_noticias_v2`, idempotent, keeps the oldest). `obtener_titulares_por_ticker` double-checks strict matching live — an XRP headline in NVIDIA's ficha is structurally impossible.

- **`senales.db` / `noticias.db` / `alertas.db`** — gitignored; CSV backups in `data/backups/` are the versioned safety net.

- **`app.py`** — UI only + orchestration. Navigation is a **sidebar rail** (`st.radio` restyled: 64px icon rail → 220px on hover; see DECISIONES.md for the CSS technique and Streamlit limits — e.g. `st.dataframe` cell fonts are canvas-rendered and NOT CSS-stylable). Config lives in an "Ajustes" popover. Section dispatch is plain `if seccion == ...` blocks (NOT `st.tabs` — anything a section needs must be hoisted above the dispatch; the shared block calls the motor once via a cached wrapper). The **Hoy** view is the default and must fit 1440×900 without scroll (verified): hero row (+track-record card), 3 signal cards side-by-side, then resumen-IA (4-line clamp + expander) · system status · Telegram.

### Data conventions that keep biting

- Prices ffilled across holidays ("Supuesto #1"); `ultimo_movimiento_no_cero()` reads the last *real* move (a holiday looks like +0.00%).
- USD normalization ("Supuesto #2"): all FX pairs are "units per 1 USD" — always divide. Signals/snapshots are ALWAYS USD; the sidebar toggle only affects comparison views and Detalle.
- Bond history uses **IEF as proxy** (price of bonds: rises when yields FALL — direction stated in the card); ^TNX gives the spot yield only (Yahoo returns no ^TNX history, and its current quote is direct percentage points, not the old ×10).
- Empty yfinance downloads have a `RangeIndex` — check `.empty` before touching `.index`.
- `$`/`*`/`_`/`#` in Claude-generated text are sanitized before rendering (LaTeX/markdown breakage); prompt asks for plain text but display-side sanitization is the safety net.
- Statistical honesty is a hard rule: below thresholds, UI says "datos insuficientes"/"pendiente"/"insuf." — never backfill numbers.
- AI analysis is manual/on-demand; a headline is never sent to Claude twice.

### Design system

Neon fintech (see Etapa 4.5 sections of DECISIONES.md): bg `#0B0D12`, surface `#141826`, border `#232A3D`; CYAN/MAGENTA/VIOLETA are data colors, green/red semantics untouchable; Space Grotesk + Inter, tabular numerals; every chart through `template_grafico()` (never bare `st.plotly_chart`); `badge()`, `sparkline_svg()`, `_tarjeta()` (glow max 2/view), `tarjeta_senal()`; monochrome cyan heatmaps for correlations, divergent red/green only for direction. Density (4.6): card padding 16-18px, `.mini-label` block headers on Hoy, long captions → tooltips (`title=`/`help=`).

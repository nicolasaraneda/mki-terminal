# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**MKI Terminal** — a Streamlit dashboard analyzing the full semiconductor value chain (rock→chip→data center) with market regime, competitor divergences, AI news sentiment, an openings anticipator, and a **verified, timestamp-sealed track record**. Built in "Etapas" (currently **4.6**). `DECISIONES.md` logs every autonomous design decision with rationale — consult it before "fixing" anything that looks arbitrary. The README describes Etapa 1 only; trust code/CLAUDE.md.

## THE MASTER RULE (Etapa 4.6 — read before touching señales/verifier/motor)

**A prediction is only verifiable if it was emitted BEFORE the event it tries to predict, provably via timestamps.** Every prediction row in `senales.db` carries `timestamp_utc` (emission), `exchange`, `sesion_objetivo` (the local session it anticipates), and `available_at` (when the input information became knowable — the UTC close of the SOX session used). The verifier only evaluates predictions whose `timestamp_utc` precedes the UTC open of their target session; late ones become `no_verificable_timing` (kept for audit, excluded from ALL metrics). Pre-4.6 rows are `legacy_pre_4.6` — same treatment. Metrics never mix `modelo_version`s. Never weaken any of this.

## Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Dashboard
streamlit run app.py

# Daily snapshot + verifier + CSV backups, WITHOUT Streamlit (what launchd runs)
python snapshot.py --origen manual     # "programado" is the launchd default

# Anti-look-ahead test of the signal engine (must stay green)
python tests/test_motor.py

# Backend layers standalone
python -c "import noticias; print(noticias.actualizar_titulares())"
python -c "import senales; senales.init_db(); print(senales.verificar_pendientes())"
```

No test framework/linter beyond `tests/test_motor.py` (plain asserts) — don't invent one. The launchd job (Mon–Fri 18:15 Chile) lives in `launchd/` with beginner install instructions.

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

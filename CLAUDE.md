# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**MKI Terminal** — a Streamlit dashboard that analyzes the full semiconductor value chain, rock→chip→data center: raw materials (copper/silver futures, miners), wafer materials, equipment, fabrication, and final demand, plus fabless designers. It tracks cross-market contagion, market regime, competitor divergences, AI news sentiment, and its own prediction track record. Built incrementally in "Etapas" (currently **Etapa 4.5**); the README still describes Etapa 1 only — trust code/CLAUDE.md over the README. `DECISIONES.md` logs every autonomous design decision made during Etapa 4.5 with its rationale; consult it before "fixing" something that looks arbitrary.

## Commands

```bash
# Setup (one-time)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py            # or: python -m streamlit run app.py
# Opens at http://localhost:8501

# Exercise backend layers without launching Streamlit
python -c "import noticias; print(noticias.actualizar_titulares())"
python -c "import senales; senales.init_db(); print(senales.verificar_pendientes())"
python -c "import alertas; print(alertas.esta_configurado())"
```

There is no test suite, linter config, or build step in this repo — don't invent one.

## Architecture

Four files carry all the logic:

- **`app.py`** — the entire Streamlit UI: design system, navigation, all top-level computation (regime, chain, divergences, anticipador), and all sections. Runs top-to-bottom on every rerun.
- **`noticias.py`** — Streamlit-free: RSS ingestion with a relevance filter, SQLite persistence (`noticias.db`), Claude analysis, time-decayed sentiment, news-volume buzz detection. Takes an `anthropic.Anthropic` client as a parameter; never reads the API key itself.
- **`senales.py`** — Streamlit-free: daily signal snapshots (scores, sentiment, anticipador prediction, **regime, Roca→Chip index, divergences**) in `senales.db`, plus the verifier that grades past predictions against reality via yfinance.
- **`alertas.py`** — Streamlit-free: Telegram alerts (`TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` from `.env`). Unconfigured = silent no-op; the UI shows BotFather setup instructions. Anti-duplicate registry in `alertas.db` keyed by `tipo:fecha:objeto`. The manual morning report deliberately has **no** anti-duplicate guard (explicit user action).

### Navigation: sections, not `st.tabs()` — read this before adding a new section

The 8 top-level views (Hoy / Comparador / Mercados / Cadena / Aperturas / Análisis IA / Historial / Detalle) are **not** `st.tabs()` — they're `st.segmented_control` + `st.session_state`, each view a plain `if seccion == "...":` block. "Hoy" is the default landing view.

Why this matters: **`st.tabs()` executes every tab's code on every rerun; plain `if` blocks only run the active section.** Etapa 4 migrated off `st.tabs()` because it reset the active tab after `st.rerun()`. The trap: anything a later section needs must be **hoisted above the `if` chain**. That's why a large shared block computes, on every rerun regardless of section: `ret_acc`/`ret_idx`, the anticipador (`df_ant`), `dias_earnings`, `regimen`, the whole chain block (`precios_cadena`, `series_nivel`, `ret_nivel`, `indice_roca_chip`, `analisis_pares`/`divergencias_activas`), then the daily snapshot and the one-shot Telegram alert evaluation. If you add a section that needs data another section computes, hoist the computation.

### The universe (`UNIVERSO` in app.py)

Dict of `ticker → {"nombre", "segmento", "nivel", "tipo"}`:
- **`nivel`** (0–4 or None) = chain link: 0 raw materials (HG=F, SI=F, BHP, FCX), 1 materials (Shin-Etsu 4063.T, SUMCO 3436.T), 2 equipment (ASML, Tokyo Electron, Advantest), 3 fabrication (TSMC×2, Samsung, SK Hynix, Micron, Intel, UMC), 4 final demand (MSFT, SMH). **Fabless designers (NVDA, AMD, QCOM, AVGO, TXN, ARM, IFX.DE) have `nivel=None`** — they participate in rankings/anticipador/news but are deliberately excluded from the chain flow and Roca→Chip index (see DECISIONES.md).
- **`tipo`** (`accion`/`commodity`/`etf`): only `accion` (the `ACCIONES` tuple) enters the sidebar, rankings, the anticipador, and daily snapshots. Commodities and SMH are context — Cadena tab, macro panel, Detalle ficha.

**Three registries must stay in sync** when adding a company: `UNIVERSO` (app.py), `EMPRESAS` (noticias.py — also feeds the relevance filter aliases `ALIAS_EMPRESAS`), and `MONEDA_TICKER` (app.py) if not USD-denominated.

### Key computations (all in app.py top-level shared block)

- **Regime** (`calcular_regimen`): SOX MA50 vs MA200 (±1% band → Alcista/Bajista/Lateral) × realized 20d vol vs its 1y median (alta/baja). Uses `serie_sox_larga()` (fixed 2y download) so the sidebar period can't break the MAs. Saved in each snapshot; a regime *change* between snapshots triggers a Telegram alert.
- **Earnings** (`dias_a_proximos_earnings`): days to next report per stock via `yf.Ticker(t).calendar`, cached 24h (`ttl=86400` — it's ~24 sequential network calls). Within 5 days: "ZONA EARNINGS" badge and the anticipador **degrades that stock's confidence one level** (Alta→Media→Baja), explaining why in the label.
- **Roca→Chip index**: mean 20d momentum across chain levels (equal weight per level), expressed as a **percentile within its own trailing year** (0–100, 50 = normal day). Not an absolute scale — don't compare across long horizons.
- **Divergences** (`analisis_pares`): for competitor groups (memoria trio, TSMC/UMC, ASML/TEL, BHP/FCX), 20d return spread z-scored against 1y history; |z|>2 = active, saved to `senales.db`, alerts via Telegram.
- **Lagged chain correlations** (Cadena tab): corr(level-A returns shifted +5/10/20d, level-B returns) for consecutive links, plus the reverse 4→3 row (demand leads fabrication). Daily-return correlations are inherently small; the caption calls >~0.15 meaningful.
- **Sentiment 2.0** (noticias.py): per-ticker average weighted by age — weight `max(0.1, 0.7^days)`. **Buzz**: today's headline count ≥3× the 14d daily average (min 3 headlines) → ALTO BUZZ — but only if the news DB itself is ≥7 days old, measured by `MIN(analizado_en)` (capture time), **not** `MIN(fecha)` (publication dates arrive weeks-old from RSS on day one and would fake a mature DB).
- **Relevance filter** (noticias.py): headlines must match sector keywords or company aliases (regex with word boundaries) to be stored at all; `limpiar_titulares_irrelevantes()` retro-cleans but **keeps** headlines the AI already linked to universe tickers (paid-for judgment isn't discarded). It runs automatically at the end of every `actualizar_titulares()`.

### Data flow notes that survive from earlier stages

- Prices via `descargar_precios()` (cached 15 min), forward-filled across market holidays ("Supuesto básico #1"); `ultimo_movimiento_no_cero()` reads the last *real* index move (ffill makes holidays look like +0.00%).
- USD normalization ("Supuesto básico #2"): all four FX pairs (`KRW=X`, `JPY=X`, `TWD=X`, `EUR=X`) are "units per 1 USD" — always divide. The sidebar toggle affects the comparison set and Detalle; the anticipador, chain computations, and snapshots are **always** USD.
- **^TNX quirk**: Yahoo currently returns the 10y yield in direct percentage points (4.485 = 4.49%), *not* the historical ×10 convention — and sometimes returns no history at all (the macro panel then shows the level with an honest "no history available" note instead of a fake sparkline).
- AI analysis is manual/on-demand only (buttons in Análisis IA and Detalle); a headline is never sent to Claude twice.
- Daily snapshot: once per calendar day, full `ACCIONES` universe at fixed 6mo window; verification runs once per browser session. Verifiers must check `precios.empty` before touching `.index` (empty yfinance downloads have a `RangeIndex`).
- Statistical honesty is a hard rule: below `senales.MINIMO_OBSERVACIONES` (5), UI shows "datos insuficientes" — never backfill numbers. Same for buzz (7-day DB age) and the "no strong signals today" empty state on Hoy.

### Design system ("neon fintech", Etapa 4.5)

Deep blue-black `#0B0D12` background, card surface `#141826` with `#232A3D` border. **CYAN `#22D3EE` and MAGENTA `#F472B6` are data/hierarchy colors; VIOLETA `#818CF8` third series color. Financial semantics are untouchable: gains `#34D399`, losses `#F87171` — neon never replaces green/red meaning.** Space Grotesk (display) + Inter (UI), tabular numerals everywhere. Rules:

- Every chart goes through **`template_grafico(fig, altura=..., **kwargs)`** — never call `st.plotly_chart` directly. It also enforces 2.5px line width and styled hover labels. `px.defaults.color_discrete_sequence` is set globally because Plotly Express **ignores** `layout.colorway`.
- `ESCALA_MONOCROMATICA` (deep blue→cyan) for correlation heatmaps; `ESCALA_DIVERGENTE` (red→green) only for directional signals.
- `badge(texto, tono)` for pills (12% bg / 40% border opacity); `sparkline_svg(valores, color)` for inline card sparklines (pure SVG, no Plotly); `_tarjeta(...)` accepts `badges=`, `spark=`, and glow classes (`glow-cyan`, `glow-pos`, ...) — **max 2 glowing elements per view** (currently: régimen + Roca→Chip in the hero).
- `tarjeta_senal()` renders the standardized signal cards on Hoy (direction, magnitude, confidence, one-line why, regime).
- Wordmark: "MKI TERMINAL." with cyan dot (chosen over alternatives in DECISIONES.md). No emoji anywhere in UI.
- The global hero row (all views) = régimen / Roca→Chip / last real SOX / sector sentiment. "Mejor acción" and "Líder ranking" live at the top of Comparador.

### Known gotchas (don't "fix" without re-reading context)

- **Section dispatch, not tabs** — see Navigation above; the #1 source of `NameError`s when moving code.
- Yahoo's per-ticker RSS doesn't filter by ticker (returns trending feed); the relevance filter + AI `tickers_afectados` do the real filtering. `LIMITE_POR_FEED` caps volume.
- `$`, `*`, `_`, `#` in Claude-generated text are stripped/replaced before rendering (LaTeX/markdown breakage); `$` becomes fullwidth `＄`. Prompt asks for plain text too, but display-side sanitization is the safety net.
- `st.rerun()` preserves `st.segmented_control` selection — don't reintroduce `st.tabs()`.
- Detalle's Puntaje v0 must be computed against the full `ACCIONES` universe (a 1-element universe always yields 0.80 — this was a real bug, fixed in Etapa 4).
- Signal scoring on Hoy: each signal family is scored as distance-to-its-own-threshold (1.0 = at threshold) so families are comparable; top 3 shown. See DECISIONES.md.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Streamlit dashboard that compares global semiconductor stocks (US, Korea, Taiwan, Japan, Netherlands, Germany), analyzes cross-market contagion, layers an AI news-analysis feature on top using the Claude API, tracks its own predictions against reality over time, and offers a per-stock detail view. Built incrementally in "Etapas" (stages) — commit messages and in-app captions reference "Etapa 1–4"; the README still describes Etapa 1 only, so trust the code/CLAUDE.md over the README for current scope.

## Commands

```bash
# Setup (one-time)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py            # or: python -m streamlit run app.py
# Opens at http://localhost:8501

# Exercise the RSS + SQLite layer without launching Streamlit
python -c "import noticias; print(noticias.actualizar_titulares())"

# Exercise the signal-tracking layer without launching Streamlit
python -c "import senales; senales.init_db(); print(senales.verificar_pendientes())"
```

There is no test suite, linter config, or build step in this repo — don't invent one.

## Architecture

Three files carry all the logic:

- **`app.py`** — the entire Streamlit UI: page config, design system (fonts/colors/CSS), navigation, and all chart/metric code. Runs top-to-bottom on every rerun (standard Streamlit execution model) — see the navigation gotcha below for what that actually means here.
- **`noticias.py`** — a Streamlit-free module for news ingestion, SQLite persistence (`noticias.db`), and Claude analysis (including the single-stock "Explicación IA" call). Takes an already-constructed `anthropic.Anthropic` client as a parameter rather than reading the API key itself, so it stays independently testable and decoupled from `app.py`'s key/UI concerns.
- **`senales.py`** — a Streamlit-free module for the signal-tracking/backtest layer (`senales.db`): saves one daily snapshot of every ticker's quantitative score, AI sentiment, and open-price prediction, then later checks each prediction against what `yfinance` says actually happened.

### Navigation: sections, not `st.tabs()` — read this before adding a new section

The 6 top-level views (Comparador / Mercados / Aperturas / Análisis IA / Historial / Detalle) are **not** `st.tabs()`. They're driven by `st.segmented_control` plus `st.session_state`, and the body of each view is a plain `if seccion == "...":` block.

This matters architecturally: **`st.tabs()` renders (and therefore executes) every tab's Python code on every rerun**, regardless of which tab is visually active. Plain `if` blocks do **not** — only the active section's code runs. Etapa 4 migrated off `st.tabs()` specifically because it doesn't persist the active tab across `st.rerun()` (clicking "Actualizar y analizar noticias" used to always bounce the user back to the first tab). The fix (`st.segmented_control` is a real stateful widget, so its selection survives reruns) introduced a real trap: **anything one section's code used to compute for a later section is no longer available unless it's hoisted above the `if` chain.** `ret_acc`, `ret_idx`, `df_ant` (the anticipador prediction), and the FX conversion all now live in a shared block *before* the section dispatch, precisely because Mercados/Aperturas/the daily snapshot all need them and can't rely on another section having "already run." If you add a new section that needs data another section computes, hoist the computation — don't assume it ran.

### Data flow

1. **Prices**: `yfinance` via `descargar_precios()` (multi-ticker) / `descargar_ohlcv()` (single-ticker OHLCV for the Detalle candlestick), both cached 15 min with `@st.cache_data`. Closed-market gaps are forward-filled (`ffill()`) to align global series across time zones/holidays — "Supuesto básico #1," not a bug. `ultimo_movimiento_no_cero()` is the related helper for reading the *last real* index move on hero cards/Aperturas — a naive `.iloc[-1]` reads as a false `+0.00%` on a US holiday because ffill duplicates the prior close.
2. **Currency**: `convertir_a_usd()` / `convertir_ohlc_a_usd()` — "Supuesto básico #2." Non-USD tickers (`MONEDA_TICKER` dict: Korea/Taiwan/Japan/Germany) are divided by the matching FX pair (`KRW=X`, `JPY=X`, `TWD=X`, `EUR=X`). **All four yfinance FX pairs use the same "units of that currency per 1 USD" convention** — including `EUR=X`, which is *not* the conventional EURUSD quote direction (verify empirically before assuming otherwise if this ever needs revisiting; division is correct for all four, there is no multiply-instead-of-divide special case). The sidebar toggle (`moneda_usd`, default on) controls conversion for the user-selected comparison set and the Detalle view; the anticipador (Aperturas) and the daily signal snapshot always convert to USD regardless of the toggle, so the contagion regression and the historical track record aren't contaminated by FX noise or by whatever a given viewer happened to have the toggle set to.
3. **News**: `noticias.actualizar_titulares()` pulls RSS from Yahoo Finance (per ticker) and Google News (per company + a couple of sector-wide queries), dedupes by URL, stores in `noticias.db` (gitignored, created on first run).
4. **AI news analysis**: `noticias.analizar_pendientes(client)` finds headlines with no row in `analisis` — a headline is never sent to Claude twice. Batches of 20 to Claude Haiku via `output_config: {format: json_schema}`. `noticias.generar_resumen_dia(client)` makes one more call over today's analyzed headlines, cached per date. `noticias.explicar_accion(client, ...)` is the single-stock version used by Detalle's "Explicación IA" button — same model, on-demand, one call per click.
5. **Daily signal snapshot**: once per calendar day (`senales.ya_existe_snapshot_hoy()` guards it — checked once per Streamlit rerun, cheap), `app.py` independently downloads the **full** `UNIVERSO` (not whatever the sidebar happens to have selected) at a fixed 6-month window, computes Puntaje v0 / Puntaje IA / the anticipador prediction for every ticker, and calls `senales.guardar_snapshot_diario()`. This is what makes the Historial section's backtest meaningful — it tracks the whole universe every day, not a sample biased by whichever session happened to trigger it.
6. **Signal verification**: once per browser session (`st.session_state.verificacion_corrida` guards it — not once per day, since a single session shouldn't hammer `yfinance` on every rerun either), `senales.verificar_pendientes()` checks any snapshot old enough to grade: the open-price prediction against the next session's real return, and Puntaje IA against the real 5-trading-day-forward return. Both verifiers **must** check `precios.empty` before touching `.index` — an empty yfinance download has a `RangeIndex`, not a `DatetimeIndex`, and `.strftime()` on it throws `AttributeError` (hit this once already; the empty-check is why it's there).
7. **Dashboard reads**: Historial/Comparador read back through `senales.metricas_apertura()` / `evolucion_aciertos_apertura()` / `analisis_puntaje_ia()` and `noticias.sentimiento_promedio_por_ticker()` etc. — none of these call an external API; they only read what's already in SQLite. Both `metricas_apertura()` and `analisis_puntaje_ia()` return `{"suficiente": False, "n": ...}` below `senales.MINIMO_OBSERVACIONES` (5) instead of a percentage — **never backfill a fake number here**; the UI is expected to render "datos insuficientes" in that case.

All AI analysis is **manual and on-demand** (buttons in Análisis IA and Detalle), by design, to keep API spend visible and controlled — don't make it automatic/on-load.

### Two ticker registries that must stay in sync

`app.py`'s `UNIVERSO` dict (ticker → (name, segment)) and `noticias.py`'s `EMPRESAS` dict (ticker → name) describe the same set of companies but are maintained separately since `noticias.py` doesn't import `app.py`. When adding/removing a covered company, update both — and check `MONEDA_TICKER` in `app.py` too if it's not USD-denominated.

### API key handling

`app.py` calls `load_dotenv()` (reads `.env` into the process env, local to this run only) and `obtener_cliente_ia()` returns `None` if `ANTHROPIC_API_KEY` isn't set — the IA tab then renders setup instructions instead of crashing the rest of the dashboard. The key must never be read from a global/system env var (intentional — the user runs Claude Code with a subscription and doesn't want a global `ANTHROPIC_API_KEY` affecting that billing).

### Design system

Art direction is deliberately "Apple product sobriety + financial-terminal seriousness" — no emoji anywhere in tabs/titles/labels, no rainbow scales. `.streamlit/config.toml` sets the dark theme at the Streamlit level (native widgets theme automatically, no fragile CSS overrides needed for them). `app.py` additionally injects custom CSS (Space Grotesk for display/titles, Inter for body/UI, tabular `font-feature-settings` on numeric widgets) and defines **one function, `template_grafico(fig, altura=..., **kwargs)`**, that every chart must be displayed through instead of calling `st.plotly_chart` directly — it applies the transparent background, horizontal-only gridlines, font, and disables Plotly's modebar in one place. If a chart needs a non-default layout tweak (axis title, range, subplot axes like `xaxis2`/`yaxis2`), pass it as a kwarg to `template_grafico`, don't call `st.plotly_chart` separately.

Color constants (`app.py` top): `COLOR_POSITIVO` / `COLOR_NEGATIVO` are the *only* semantic colors for direction (sentiment, estimated moves, day's return) — never introduce a third. Two color scales exist and are **not interchangeable**:
- `ESCALA_DIVERGENTE` (red → neutral → green) for directional bars: sentiment thermometer, apertura estimada.
- `ESCALA_MONOCROMATICA` (near-black → mid-blue → vivid blue, single hue) for correlation heatmaps specifically — correlation is magnitude-of-relationship, not "good/bad," so it deliberately does *not* use the pos/neg scale.
- `PALETA_CATEGORICA` for multi-series categorical charts (e.g. the multi-ticker performance line chart, the candlestick's implicit series).

### Known gotchas (don't "fix" without re-reading context)

- **Section dispatch, not tabs** — see the Navigation section above. This is the one most likely to bite: code that "used to just work" because `st.tabs()` ran every branch every time will now silently `NameError` if a variable's origin section isn't active.
- Yahoo Finance's per-ticker RSS feed (`feeds.finance.yahoo.com/rss/2.0/headline?s=...`) does **not** actually filter by ticker — it returns Yahoo's general trending feed regardless of the `s=` parameter. Expected; relevance filtering happens downstream via Claude's `tickers_afectados` output. `LIMITE_POR_FEED` in `noticias.py` caps items per feed to control volume/cost.
- Any `$` or `*`/`**` in Claude-generated text (dollar amounts, emphasis the model adds despite being told not to) breaks display if left raw: `$` gets read as LaTeX math delimiters by Streamlit's markdown renderer, and `**bold**` can render as literal asterisks depending on how the surrounding HTML is structured. Both the daily summary and the Detalle explanation strip `#`/`*`/`_` and swap `$` → the visually-identical fullwidth `＄` before rendering. A plain backslash-escape (`\$`) does **not** work here — it renders as a literal backslash, not an escaped dollar sign. The Claude prompts also ask for plain text as a first line of defense, but the display-side sanitization is the real safety net; don't remove it just because a prompt tweak seems to fix it in one sample.
- `st.rerun()` (used after "Actualizar y analizar noticias" finishes) does **not** invalidate `st.segmented_control`'s session-state-backed selection — that's the whole point of having migrated to it. Don't reintroduce `st.tabs()` for navigation.
- FX conversion direction: see Data flow §2. All four pairs divide; there is no EUR special case.

<!--
DRAFT. Every value written as {{...}} is a placeholder that the arbiter
module (cifras.py) fills at render time. No figure in this file is typed
by hand. If a placeholder has no arbiter source, the sentence is removed,
not filled from memory. Spanish original: README.es.md
-->

# MKI Terminal

**A measurement instrument for a market hypothesis, built to be unable to lie to its own author.**

MKI Terminal tests one specific claim: that the New York close carries information about the next Asian open in the semiconductor supply chain (Samsung, SK Hynix, Tokyo Electron and {{n_tickers_minus_3}} others). Every prediction is sealed in an immutable snapshot before the target market opens, so the track record cannot be edited after the fact. Every published figure carries its sample size and a confidence interval computed with the correct unit of independence. Negative results are published with the same prominence as positive ones.

It is not a trading bot with an edge. As of {{fecha_render}}, it has no measured edge, and the front page says so.

[Español](README.es.md)

---

## What the instrument says today

All figures below are rendered from `cifras.py`, the single arbiter module. The Spanish and English pages are generated from the same template, so they cannot disagree.

| Question | Answer | n | Interval / test |
|---|---|---|---|
| Directional accuracy of the sealed window vs. baseline | {{acierto_modelo}} vs {{acierto_base}} | {{n_ventana}} rows, {{n_dias_ventana}} days | {{ic_cluster_dia}} (day-cluster t), permutation p = {{p_permutacion}} |
| Is the advantage distinguishable from zero? | {{veredicto_ventaja}} | effective n {{n_efectivo}} (ICC {{icc}}, DEFF {{deff}}) | |
| Gap magnitude error vs. predicting zero | MAE {{mae_modelo}} vs {{mae_cero}} | {{n_ventana}} | {{ic_mae}} |
| Is the gap capturable as a trade? | {{veredicto_capturabilidad}} | {{n_backtest}} | {{detalle_capturabilidad}} |
| Sealed days needed for a verdict at 80 % power | direction ~{{dias_veredicto_direccion}}, magnitude ~{{dias_veredicto_magnitud}} | | {{ic_horizonte}} |
| Paper account friction (default game) | {{friccion_juego_defecto}} over {{semanas_friccion}} weeks | median of {{k_semillas}} seeds | **{{estatus_riel_dinero}}** |

Every p-value states the test that produced it. Every interval states the clustering unit. Figures that were retired are listed in [`cifras_retiradas.md`]({{ruta_cifras_retiradas}}) with the reason, and a pre-commit hook blocks them from re-entering the codebase.

## Why this project is built the way it is

Most retail quant projects fail in one of three ways: look-ahead leaks into the backtest, the author moves the goalposts after seeing results, or a retracted number keeps circulating in the code. This repository treats those three as engineering problems.

**Sealing.** A prediction exists only if it was written to an append-only snapshot with a machine timestamp before the target open. Six systemd timers run the pipeline nightly on the primary machine; a watchdog with an alert/retraction cycle and Telegram notifications reports every missed or late run. Sealed rows are never rewritten; historical errors become dated errata.

**Pre-registration.** Success criteria, sample sizes and stopping rules are written down before the data is looked at. A sequential-testing plan was rejected {{n_rechazos_secuencial}} times by the project's own review process because it would have made it easier to find something.

**Truncation invariance.** The paper-trading rail is rebuilt from a full price file and from the same file cut at {{n_cortes_invariancia}} points. If any decision taken before a cut differs when the future is removed, the run aborts with `ErrorLookAhead`. The gate compares decisions, not only executions, which is what catches the leak that a one-day implementation lag hides. A deliberately leaky signal factory is part of the test suite to prove the gate fires.

**Adversarial review.** Every diff is judged by a bundle of read-only review agents in `.claude/`: a constitution guardian (protected files, no rewritten rows, no push), a look-ahead auditor that assumes there is a leak and tries to prove it, an adversarial statistician that rejects any point estimate without a computed interval, and an epistemic curator that relabels claims as PROPOSED until they have passed the statistician. A hard pre-tool hook enforces the protected-file rules regardless of what a prompt says. The agents have a regression suite of {{n_casos_regresion_agentes}} cases taken from real incidents.

**The unit of independence.** Eight tickers sealed on the same day are not eight observations. With day clustering the effective sample is {{n_efectivo}} rather than {{n_ventana}}. That single correction is why the headline reads "not distinguishable from zero" instead of a p-value that crosses 5 %.

## What was found, including what did not survive

- The sealed advantage exists as a point estimate and is not distinguishable from zero with the correct unit ({{ic_cluster_dia}}).
- The gap is predictable in direction and not capturable: a strategy that trades it loses even at zero cost, in and out of sample ({{detalle_capturabilidad}}).
- The "decay with temporal distance" law was predicted before download and failed in Hong Kong and India. Published as a failed prediction.
- The paper-trading rail's original account had {{n_fugas_cuenta_papel}} demonstrated temporal leaks. It was retired, rebuilt under the invariance gate, and its friction is dominated by the number of orders, not the fee schedule.
- {{n_fechas_cero}} of {{n_fechas_selladas}} sealed dates contribute exactly zero to the directional statistic, which is why direction needs ~{{dias_veredicto_direccion}} sealed days and magnitude ~{{dias_veredicto_magnitud}}.

The full decision record, {{n_actas}} signed minutes with the reasoning for each, is in [`DECISIONES.md`](DECISIONES.md).

## Execution rail (paper only)

The money rail follows a staged protocol written before any account existed:

- **E0** {{estado_e0}}: the machine emits and seals a decision for the next open with nominal size zero. Sealed prospective rows so far: **{{filas_selladas_dinero}}**.
- **E1** {{estado_e1}}: broker paper account. Exit condition: the machine sends an order and reads back its own execution through the official API in the same cycle, and the read matches the broker's official report.
- **E2** not started: real capital, minimum size, only after E0 and E1 and only against a pre-registered yardstick.

Broker eligibility is a written criterion (official, supported API for both sending and reading executions), verified against the broker's own documentation, with a note on which fee structures API-routed orders lose. The adapter refuses in code to connect to anything that is not a paper account, and a test proves it.

The live view shows the sealed decisions for the next open with their status label, the invariance gate state of the last run, and the paper account's positions and fills with the data-delay flag the broker declares. No number appears on screen without its status.

## Engineering

- Python, pandas, SQLite; signals are pure functions parameterised by date. A frozen champion model ({{version_motor}}) and a challenger protocol with a purge-and-embargo walk-forward and a deflated Sharpe ratio (a unit defect in the DSR was found by the project's own null simulator and fixed with a guard and a test).
- {{n_tests}} tests including anti-look-ahead, sealing and truncation-invariance cases; the pre-commit hook runs the full suite and a secret scanner.
- Own null simulator with known truth to calibrate the instrument: the day-cluster t interval covers {{cobertura_cluster_t}}, the day percentile ~{{cobertura_percentil}}, the naive iid interval {{cobertura_iid}}.
- Restore path: daily CSV backups plus an importer whose acceptance test restores an empty database and compares row by row, including platform version, against the sealed original.
- FastAPI backend, React frontend, live updates for the execution view.
- Hardware track: the decision pipeline is reproduced in RTL on a Digilent Arty A7-100T and matches {{filas_fpga}} sealed rows bit for bit at {{latencia_fpga}} cycles. It is a verification platform and a computer-architecture project, not a backtest engine; the measured round trip from home ({{rtt_ms}} ms) is the network, and the document says what would and would not unlock a latency route.

## Reproduce

```bash
git clone https://github.com/nicolasaraneda/mki-terminal
cd mki-terminal && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m pytest            # full suite, ~5 min
python cifras.py            # renders every figure on this page
```

The sealed databases are not in the repository; `data/backups/*.csv` and the importer rebuild them.

## Repository map

| Path | What it is |
|---|---|
| `motor.py`, `senales.py`, `snapshot.py`, `universo.py` | Protected core: model, signals, sealing, universe. Changes arrive as unapplied `.diff` files with tests and wait for a signature |
| `cifras.py` | The arbiter. Every published figure is rendered from here |
| `backtest/` | Walk-forward harness, causality checks, cluster inference |
| `dinero/` | Paper-trading rail, invariance gate, prospective sealing |
| `corredor/` | Broker adapter (paper only) |
| `GEMELO/` | Pre-registration, simulator, run logs, verdicts, proposals awaiting signature |
| `DECISIONES.md` | Decision record: minutes, asymmetries, debts, errata |
| `.claude/` | Review agents, rules and the enforcement hook |
| `docs/` | Agent manual, operable universe census, environment guide |

## Status

{{linea_estado}}

Author: Nicolás Araneda, electrical engineering student, Universidad de los Andes, Santiago. The project is a measurement instrument first; whether it ever becomes a trading system depends on what it measures, and the rules for that decision are written down before the measurement.

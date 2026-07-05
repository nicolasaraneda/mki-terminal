import { useEffect, useRef } from 'react'
import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
} from 'lightweight-charts'

export interface Vela {
  t: string
  o: number
  h: number
  l: number
  c: number
  v: number
}

// Gráfico de velas TradingView (lightweight-charts): el estándar serio.
export function CandleChart({ velas, alto = 320 }: { velas: Vela[]; alto?: number }) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current || velas.length === 0) return
    const chart = createChart(ref.current, {
      height: alto,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#5d6679',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
        attributionLogo: false,
      },
      grid: {
        vertLines: { color: '#161b26' },
        horzLines: { color: '#161b26' },
      },
      rightPriceScale: { borderColor: '#222939' },
      timeScale: { borderColor: '#222939' },
      crosshair: {
        vertLine: { color: '#303a50', labelBackgroundColor: '#1d2330' },
        horzLine: { color: '#303a50', labelBackgroundColor: '#1d2330' },
      },
    })
    const serie = chart.addSeries(CandlestickSeries, {
      upColor: '#34d399',
      downColor: '#f87171',
      borderVisible: false,
      wickUpColor: '#34d399',
      wickDownColor: '#f87171',
    })
    serie.setData(velas.map((v) => ({ time: v.t, open: v.o, high: v.h, low: v.l, close: v.c })))

    const volumen = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: 'vol',
    })
    chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } })
    volumen.setData(
      velas.map((v) => ({
        time: v.t,
        value: v.v,
        color: v.c >= v.o ? 'rgba(52,211,153,0.25)' : 'rgba(248,113,113,0.25)',
      })),
    )
    chart.timeScale().fitContent()

    const observador = new ResizeObserver(() => {
      if (ref.current) chart.applyOptions({ width: ref.current.clientWidth })
    })
    observador.observe(ref.current)
    return () => {
      observador.disconnect()
      chart.remove()
    }
  }, [velas, alto])

  return <div ref={ref} className="w-full" />
}

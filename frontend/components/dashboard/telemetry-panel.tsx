"use client"

import { motion } from "framer-motion"
import { Slider } from "@/components/ui/slider"
import { Activity, Gauge, Thermometer, Zap, Battery, Plug, Laptop } from "lucide-react"
import type { LiveDashboardResponse } from "@/lib/api"

export function TelemetryPanel({
  telemetry,
  isScanning,
}: {
  telemetry: LiveDashboardResponse["telemetry"] | null
  isScanning: boolean
}) {
  const industrial = telemetry?.industrial_metrics
  const energyUsage = Math.round(industrial?.energy_usage_kwh ?? 0)
  const thermalIndex = Math.round(industrial?.thermal_index_c ?? 0)
  const gridLoad = Math.round((industrial?.grid_load ?? 0) * 100)
  const gridStatus = industrial?.grid_status ?? "unknown"
  const siteId = industrial?.site_id ?? "plant-local"
  const battery =
    telemetry?.battery_percent === null || telemetry?.battery_percent === undefined
      ? null
      : Math.round(telemetry.battery_percent)
  const powerPlugged = telemetry?.power_plugged

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3, duration: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-5 flex items-center gap-2">
        <div className={`size-2 rounded-full ${isScanning ? "animate-pulse bg-neon-cyan" : "bg-neon-amber"}`} />
        <h3 className="font-mono text-xs uppercase tracking-widest text-neon-cyan">
          Live Telemetry
        </h3>
        <span className="ml-auto rounded-md border border-neon-cyan/30 bg-neon-cyan/10 px-2 py-0.5 font-mono text-[9px] uppercase tracking-widest text-neon-cyan">
          Auto Scan
        </span>
      </div>

      <div className="space-y-5">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
              <Zap className="size-3 text-neon-amber" />
              ENERGY DEMAND
            </span>
            <span className="font-mono text-xs text-neon-amber">{energyUsage} kWh</span>
          </div>
          <Slider
            value={[Math.min(100, Math.round((energyUsage / 1000) * 100))]}
            disabled
            max={100}
            step={1}
            className="[&_[data-slot=slider-range]]:bg-neon-amber [&_[data-slot=slider-thumb]]:border-neon-amber [&_[data-slot=slider-track]]:bg-neon-amber/10"
          />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
              <Thermometer className="size-3 text-neon-purple" />
              THERMAL INDEX
            </span>
            <span className="font-mono text-xs text-neon-purple">{thermalIndex} degC</span>
          </div>
          <Slider
            value={[Math.min(100, Math.round((thermalIndex / 90) * 100))]}
            disabled
            max={100}
            step={1}
            className="[&_[data-slot=slider-range]]:bg-neon-purple [&_[data-slot=slider-thumb]]:border-neon-purple [&_[data-slot=slider-track]]:bg-neon-purple/10"
          />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
              <Gauge className="size-3 text-neon-cyan" />
              GRID LOAD
            </span>
            <span className="font-mono text-xs text-neon-cyan">{gridLoad}%</span>
          </div>
          <Slider
            value={[gridLoad]}
            disabled
            max={100}
            step={1}
            className="[&_[data-slot=slider-range]]:bg-neon-cyan [&_[data-slot=slider-thumb]]:border-neon-cyan [&_[data-slot=slider-track]]:bg-neon-cyan/10"
          />
        </div>

        <div className="rounded-lg border border-border bg-secondary/30 p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
              <Battery className="size-3 text-neon-green" />
              BATTERY
            </span>
            <span className="font-mono text-xs text-neon-green">
              {battery === null ? "N/A" : `${battery}%`}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2 font-mono text-[10px]">
            <span className="rounded-md border border-border bg-card px-2 py-1 text-muted-foreground">
              {siteId}
            </span>
            <span className="rounded-md border border-border bg-card px-2 py-1 text-muted-foreground">
              Grid: {gridStatus.toUpperCase()}
            </span>
            <span className="inline-flex items-center gap-1 rounded-md border border-border bg-card px-2 py-1 text-muted-foreground">
              <Plug className="size-3" />
              {powerPlugged === null || powerPlugged === undefined
                ? "Power N/A"
                : powerPlugged
                ? "Plugged"
                : "Battery"}
            </span>
            <span className="inline-flex items-center gap-1 rounded-md border border-border bg-card px-2 py-1 text-muted-foreground">
              <Laptop className="size-3" />
              Edge: {telemetry?.hostname ?? "local-machine"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-neon-cyan/20 bg-neon-cyan/5 p-3 font-mono text-[10px] text-neon-cyan">
          <Activity className={`size-3 ${isScanning ? "animate-pulse" : ""}`} />
          Real-time autonomous scanning active on this laptop.
        </div>
      </div>
    </motion.div>
  )
}

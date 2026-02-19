"use client"

import { motion } from "framer-motion"
import { Brain, Cpu, MemoryStick, TrendingDown, Battery } from "lucide-react"
import type { LiveDashboardResponse, RuntimeMode, SimulationScenario } from "@/lib/api"

interface StatCard {
  label: string
  value: string
  icon: React.ReactNode
  color: string
}

export function StatusCards({
  telemetry,
  optimizationScore,
  runtimeMode,
  scenario,
}: {
  telemetry: LiveDashboardResponse["telemetry"] | null
  optimizationScore: number | null
  runtimeMode: RuntimeMode
  scenario: SimulationScenario
}) {
  const industrial = telemetry?.industrial_metrics

  const cards: StatCard[] = [
    {
      label: "AI MODE",
      value: runtimeMode.replace("_", "-"),
      icon: <Brain className="size-5" />,
      color: "text-neon-cyan",
    },
    {
      label: "ENERGY DEMAND",
      value: `${Math.round(industrial?.energy_usage_kwh ?? 0)} kWh`,
      icon: <Cpu className="size-5" />,
      color: "text-neon-amber",
    },
    {
      label: "GRID LOAD",
      value: `${Math.round((industrial?.grid_load ?? 0) * 100)}%`,
      icon: <MemoryStick className="size-5" />,
      color: "text-neon-purple",
    },
    {
      label: "OPTIMIZATION",
      value: `${Math.round(optimizationScore ?? 0)}%`,
      icon: <TrendingDown className="size-5" />,
      color: "text-neon-green",
    },
    {
      label: "SCENARIO",
      value:
        scenario === "normal"
          ? "NORMAL"
          : scenario === "peak_load"
          ? "PEAK LOAD"
          : scenario === "low_load"
          ? "LOW LOAD"
          : "GRID FAILURE",
      icon: <Battery className="size-5" />,
      color: "text-neon-green",
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
      {cards.map((stat, i) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06, duration: 0.35 }}
          className="group relative overflow-hidden rounded-xl border border-border bg-card p-4 transition-all hover:border-neon-cyan/30"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
          <div className="relative">
            <div className="mb-3 flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                {stat.label}
              </span>
              <div className={stat.color}>{stat.icon}</div>
            </div>
            <div className={`font-mono text-2xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

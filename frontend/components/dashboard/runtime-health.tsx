"use client"

import { motion } from "framer-motion"
import { Activity } from "lucide-react"
import type { RuntimeHealthItem } from "@/lib/api"

interface HealthItem extends RuntimeHealthItem {
  color: string
}

function toColor(value: number): string {
  if (value >= 80) return "bg-neon-green"
  if (value >= 60) return "bg-neon-amber"
  return "bg-neon-red"
}

export function RuntimeHealth({ items }: { items: RuntimeHealthItem[] }) {
  const health: HealthItem[] = items.map((item) => ({
    ...item,
    value: Math.max(0, Math.min(100, Math.round(item.value))),
    color: toColor(item.value),
  }))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-5 flex items-center gap-2">
        <Activity className="size-4 text-neon-green" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-neon-green">
          Runtime Health Monitor
        </h3>
      </div>

      <div className="space-y-4">
        {health.map((item, i) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.12 + i * 0.06 }}
          >
            <div className="mb-1.5 flex items-center justify-between">
              <span className="font-mono text-[11px] text-foreground">{item.name}</span>
              <span
                className={`font-mono text-[11px] font-bold ${
                  item.value >= 80
                    ? "text-neon-green"
                    : item.value >= 60
                    ? "text-neon-amber"
                    : "text-neon-red"
                }`}
              >
                {item.value}%
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
              <motion.div
                className={`h-full rounded-full ${item.color}`}
                initial={{ width: 0 }}
                animate={{ width: `${item.value}%` }}
                transition={{ duration: 0.8, delay: 0.15 + i * 0.06 }}
              />
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

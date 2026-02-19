"use client"

import { motion } from "framer-motion"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import { TrendingUp } from "lucide-react"
import type { LiveHistoryPoint } from "@/lib/api"

export function OptimizationChart({ history }: { history: LiveHistoryPoint[] }) {
  const data = history.length > 0 ? history : [{ time: "--:--", optimization: 0, energy: 0, timestamp: "" }]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-4 flex items-center gap-2">
        <TrendingUp className="size-4 text-neon-cyan" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-neon-cyan">
          Optimization Metrics
        </h3>
        <span className="ml-auto font-mono text-[10px] text-muted-foreground">Live laptop scan</span>
      </div>

      <div className="h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="gradCyan" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00e5ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00e5ff" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradPurple" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a3a" />
            <XAxis
              dataKey="time"
              tick={{ fill: "#7a8599", fontSize: 10, fontFamily: "monospace" }}
              axisLine={{ stroke: "#1e2a3a" }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#7a8599", fontSize: 10, fontFamily: "monospace" }}
              axisLine={{ stroke: "#1e2a3a" }}
              tickLine={false}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#121826",
                border: "1px solid #1e2a3a",
                borderRadius: "8px",
                fontFamily: "monospace",
                fontSize: "11px",
                color: "#e5e7eb",
              }}
            />
            <Area
              type="monotone"
              dataKey="optimization"
              stroke="#00e5ff"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#gradCyan)"
              name="Optimization %"
            />
            <Area
              type="monotone"
              dataKey="energy"
              stroke="#7c3aed"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#gradPurple)"
              name="CPU Load %"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}

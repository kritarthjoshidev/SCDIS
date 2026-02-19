"use client"

import { motion, AnimatePresence } from "framer-motion"
import { AlertTriangle, ShieldAlert, Flame } from "lucide-react"
import type { LiveAlert } from "@/lib/api"

export function AlertsPanel({ alerts }: { alerts: LiveAlert[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7, duration: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-4 flex items-center gap-2">
        <ShieldAlert className="size-4 text-neon-red" />
        <h3 className="font-mono text-xs uppercase tracking-widest text-neon-red">
          Active Alerts
        </h3>
        <div className="ml-auto rounded-md bg-neon-red/10 px-2 py-0.5 font-mono text-[10px] font-bold text-neon-red">
          {alerts.length}
        </div>
      </div>

      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {alerts.length === 0 && (
            <div className="rounded-lg border border-neon-green/30 bg-neon-green/5 p-3 font-mono text-[10px] text-neon-green">
              No active critical alerts.
            </div>
          )}
          {alerts.map((alert) => (
            <motion.div
              key={alert.id}
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
              className={`rounded-lg border p-3 ${
                alert.severity === "critical"
                  ? "border-neon-red/30 bg-neon-red/5"
                  : "border-neon-amber/30 bg-neon-amber/5"
              }`}
            >
              <div className="flex items-start gap-2">
                {alert.severity === "critical" ? (
                  <Flame className="mt-0.5 size-3.5 shrink-0 text-neon-red" />
                ) : (
                  <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-neon-amber" />
                )}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`font-mono text-[11px] font-bold ${
                        alert.severity === "critical" ? "text-neon-red" : "text-neon-amber"
                      }`}
                    >
                      {alert.title}
                    </span>
                    <span className="shrink-0 font-mono text-[9px] text-muted-foreground">
                      {alert.time}
                    </span>
                  </div>
                  <p className="mt-0.5 font-mono text-[10px] leading-relaxed text-muted-foreground">
                    {alert.message}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  ShieldAlert,
  AlertTriangle,
  Flame,
  CheckCircle,
  XCircle,
  Bell,
  BellOff,
  Filter,
} from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ScrollReveal } from "@/components/ui/scroll-reveal"

interface Alert {
  id: number
  severity: "warning" | "critical" | "info"
  title: string
  message: string
  time: string
  acknowledged: boolean
  source: string
}

const alertPool: Omit<Alert, "id" | "time" | "acknowledged">[] = [
  {
    severity: "warning",
    title: "Thermal Drift Detected",
    message: "Zone-3 temperature exceeding threshold by 2.1C",
    source: "Thermal Monitor",
  },
  {
    severity: "critical",
    title: "Failover Triggered",
    message: "Node-7 unresponsive -- backup node activated",
    source: "Failover System",
  },
  {
    severity: "warning",
    title: "Grid Load Spike",
    message: "Mumbai sector at 94% capacity -- rebalancing",
    source: "Grid Controller",
  },
  {
    severity: "warning",
    title: "Model Drift Warning",
    message: "RL model accuracy dropped to 91.3% -- retraining scheduled",
    source: "ML Pipeline",
  },
  {
    severity: "critical",
    title: "Connection Lost",
    message: "Edge sensor cluster-4 offline -- auto-reconnecting",
    source: "Network Monitor",
  },
  {
    severity: "info",
    title: "Scheduled Maintenance",
    message: "Node-12 maintenance window in 30 minutes",
    source: "Scheduler",
  },
  {
    severity: "critical",
    title: "Memory Pressure",
    message: "Decision engine heap usage at 92% -- GC triggered",
    source: "Runtime Controller",
  },
  {
    severity: "info",
    title: "Model Update Available",
    message: "RL Agent v7.3.0 ready for deployment",
    source: "ML Pipeline",
  },
  {
    severity: "warning",
    title: "Latency Spike",
    message: "API response time exceeded 500ms threshold",
    source: "API Gateway",
  },
]

const severityConfig = {
  critical: {
    icon: Flame,
    color: "text-neon-red",
    bg: "bg-neon-red/5",
    border: "border-neon-red/30",
    badge: "bg-neon-red/10 text-neon-red",
  },
  warning: {
    icon: AlertTriangle,
    color: "text-neon-amber",
    bg: "bg-neon-amber/5",
    border: "border-neon-amber/30",
    badge: "bg-neon-amber/10 text-neon-amber",
  },
  info: {
    icon: Bell,
    color: "text-neon-cyan",
    bg: "bg-neon-cyan/5",
    border: "border-neon-cyan/30",
    badge: "bg-neon-cyan/10 text-neon-cyan",
  },
}

type FilterType = "all" | "critical" | "warning" | "info"

export function AlertsTab() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [filter, setFilter] = useState<FilterType>("all")

  useEffect(() => {
    const initial = alertPool.slice(0, 5).map((a, i) => ({
      ...a,
      id: i,
      time: new Date().toLocaleTimeString("en-IN", { hour12: false }),
      acknowledged: false,
    }))
    setAlerts(initial)

    let nextId = 5
    const interval = setInterval(() => {
      const pool = alertPool[Math.floor(Math.random() * alertPool.length)]
      nextId++
      setAlerts((prev) => [
        {
          ...pool,
          id: nextId,
          time: new Date().toLocaleTimeString("en-IN", { hour12: false }),
          acknowledged: false,
        },
        ...prev.slice(0, 30),
      ])
    }, 7000)

    return () => clearInterval(interval)
  }, [])

  const toggleAcknowledge = (id: number) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, acknowledged: !a.acknowledged } : a))
    )
  }

  const dismissAlert = (id: number) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id))
  }

  const filteredAlerts = alerts.filter((a) =>
    filter === "all" ? true : a.severity === filter
  )

  const counts = {
    all: alerts.length,
    critical: alerts.filter((a) => a.severity === "critical").length,
    warning: alerts.filter((a) => a.severity === "warning").length,
    info: alerts.filter((a) => a.severity === "info").length,
  }

  return (
    <div className="space-y-4">
      {/* Summary Cards */}
      <ScrollReveal className="grid grid-cols-2 gap-3 lg:grid-cols-4" delay={0.02}>
        {(["all", "critical", "warning", "info"] as FilterType[]).map((type) => {
          const isActive = filter === type
          const colors =
            type === "all"
              ? "border-neon-cyan/30 text-foreground"
              : `${severityConfig[type].border} ${severityConfig[type].color}`
          return (
            <motion.button
              key={type}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => setFilter(type)}
              className={`rounded-xl border p-4 font-mono transition-all ${
                isActive ? `${colors} ${type === "all" ? "bg-neon-cyan/5" : severityConfig[type as Exclude<FilterType, "all">].bg}` : "border-border bg-card hover:border-neon-cyan/20"
              }`}
            >
              <div className="text-[10px] uppercase tracking-widest text-muted-foreground">
                {type === "all" ? "Total" : type}
              </div>
              <div className={`mt-1 text-2xl font-bold ${type === "all" ? "text-foreground" : severityConfig[type as Exclude<FilterType, "all">].color}`}>
                {counts[type]}
              </div>
            </motion.button>
          )
        })}
      </ScrollReveal>

      {/* Alerts List */}
      <ScrollReveal className="rounded-xl border border-border bg-card p-5" delay={0.08}>
        <div className="mb-4 flex items-center gap-2">
          <ShieldAlert className="size-4 text-neon-red" />
          <h3 className="font-mono text-xs uppercase tracking-widest text-neon-red">
            Active Alerts
          </h3>
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={() => setAlerts((prev) => prev.map((a) => ({ ...a, acknowledged: true })))}
              className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground transition-colors hover:border-neon-green/30 hover:text-neon-green"
            >
              <CheckCircle className="size-3" />
              Ack All
            </button>
          </div>
        </div>

        <ScrollArea className="h-[480px]">
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {filteredAlerts.map((alert) => {
                const cfg = severityConfig[alert.severity]
                const Icon = cfg.icon
                return (
                  <motion.div
                    key={alert.id}
                    layout
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: alert.acknowledged ? 0.5 : 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3 }}
                    className={`rounded-lg border p-4 ${cfg.border} ${cfg.bg}`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className={`mt-0.5 size-4 shrink-0 ${cfg.color}`} />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className={`font-mono text-sm font-bold ${cfg.color}`}>
                            {alert.title}
                          </span>
                          <div className="flex shrink-0 items-center gap-2">
                            <span className="font-mono text-[9px] text-muted-foreground">
                              {alert.time}
                            </span>
                            <div className={`rounded-md border px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase ${cfg.badge} ${cfg.border}`}>
                              {alert.severity}
                            </div>
                          </div>
                        </div>
                        <p className="mt-1 font-mono text-[11px] leading-relaxed text-muted-foreground">
                          {alert.message}
                        </p>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="font-mono text-[10px] text-muted-foreground/60">{alert.source}</span>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => toggleAcknowledge(alert.id)}
                              className={`flex items-center gap-1 rounded px-2 py-1 font-mono text-[9px] uppercase tracking-wider transition-colors ${
                                alert.acknowledged
                                  ? "bg-neon-green/10 text-neon-green"
                                  : "bg-secondary text-muted-foreground hover:text-foreground"
                              }`}
                            >
                              {alert.acknowledged ? <BellOff className="size-2.5" /> : <Bell className="size-2.5" />}
                              {alert.acknowledged ? "Acked" : "Ack"}
                            </button>
                            <button
                              onClick={() => dismissAlert(alert.id)}
                              className="flex items-center gap-1 rounded bg-secondary px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-muted-foreground transition-colors hover:bg-neon-red/10 hover:text-neon-red"
                            >
                              <XCircle className="size-2.5" />
                              Dismiss
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        </ScrollArea>
      </ScrollReveal>
    </div>
  )
}

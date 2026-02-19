"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { Terminal, Filter, Search, Download } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ScrollReveal } from "@/components/ui/scroll-reveal"

interface EventLog {
  id: number
  type: "INFO" | "WARN" | "ERROR" | "SUCCESS"
  source: string
  message: string
  time: string
}

const eventMessages: { type: EventLog["type"]; source: string; message: string }[] = [
  { type: "INFO", source: "heartbeat", message: "enterprise_heartbeat -- ping OK" },
  { type: "INFO", source: "decision", message: "decision_generated -- rl_action dispatched" },
  { type: "SUCCESS", source: "optimizer", message: "optimization_applied -- cost reduced 12%" },
  { type: "INFO", source: "telemetry", message: "telemetry_received -- sensors OK" },
  { type: "WARN", source: "runtime", message: "runtime_health_dip -- supervisor at 89%" },
  { type: "INFO", source: "evolution", message: "evolution_cycle -- gen-7 stable" },
  { type: "SUCCESS", source: "failover", message: "failover_check -- all nodes responsive" },
  { type: "INFO", source: "grid", message: "grid_rebalance -- load distributed" },
  { type: "WARN", source: "thermal", message: "thermal_alert -- zone-3 temp rising" },
  { type: "INFO", source: "backup", message: "backup_activated -- solar switch complete" },
  { type: "SUCCESS", source: "model", message: "model_retrained -- accuracy 97.2%" },
  { type: "ERROR", source: "network", message: "connection_timeout -- node-7 retry" },
  { type: "INFO", source: "selfheal", message: "self_heal_triggered -- auto-recovery" },
  { type: "SUCCESS", source: "anomaly", message: "anomaly_detected -- pattern isolated" },
  { type: "ERROR", source: "storage", message: "disk_threshold -- sector-2 at 95% capacity" },
  { type: "WARN", source: "security", message: "auth_attempt -- unusual access pattern detected" },
  { type: "INFO", source: "scheduler", message: "cron_job -- daily model snapshot completed" },
  { type: "SUCCESS", source: "deploy", message: "model_deployed -- v7.2.1 live on production" },
]

const typeColors: Record<EventLog["type"], string> = {
  INFO: "text-neon-cyan",
  WARN: "text-neon-amber",
  ERROR: "text-neon-red",
  SUCCESS: "text-neon-green",
}

const typeBg: Record<EventLog["type"], string> = {
  INFO: "bg-neon-cyan/10 border-neon-cyan/20",
  WARN: "bg-neon-amber/10 border-neon-amber/20",
  ERROR: "bg-neon-red/10 border-neon-red/20",
  SUCCESS: "bg-neon-green/10 border-neon-green/20",
}

type FilterType = "ALL" | "INFO" | "WARN" | "ERROR" | "SUCCESS"

export function EventsTab() {
  const [events, setEvents] = useState<EventLog[]>([])
  const [filter, setFilter] = useState<FilterType>("ALL")
  const [searchQuery, setSearchQuery] = useState("")
  const idRef = useRef(0)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const initial: EventLog[] = Array.from({ length: 20 }, () => {
      const ev = eventMessages[Math.floor(Math.random() * eventMessages.length)]
      idRef.current++
      return {
        id: idRef.current,
        type: ev.type,
        source: ev.source,
        message: ev.message,
        time: new Date().toLocaleTimeString("en-IN", { hour12: false }),
      }
    })
    setEvents(initial)

    const interval = setInterval(() => {
      const ev = eventMessages[Math.floor(Math.random() * eventMessages.length)]
      idRef.current++
      setEvents((prev) => [
        ...prev.slice(-200),
        {
          id: idRef.current,
          type: ev.type,
          source: ev.source,
          message: ev.message,
          time: new Date().toLocaleTimeString("en-IN", { hour12: false }),
        },
      ])
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [events])

  const filteredEvents = events.filter((e) => {
    const matchesFilter = filter === "ALL" || e.type === filter
    const matchesSearch =
      searchQuery === "" ||
      e.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.source.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const counts = {
    ALL: events.length,
    INFO: events.filter((e) => e.type === "INFO").length,
    WARN: events.filter((e) => e.type === "WARN").length,
    ERROR: events.filter((e) => e.type === "ERROR").length,
    SUCCESS: events.filter((e) => e.type === "SUCCESS").length,
  }

  return (
    <div className="space-y-4">
      {/* Stats */}
      <ScrollReveal className="grid grid-cols-2 gap-3 lg:grid-cols-5" delay={0.02}>
        {(["ALL", "INFO", "WARN", "ERROR", "SUCCESS"] as FilterType[]).map((type) => {
          const isActive = filter === type
          return (
            <motion.button
              key={type}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => setFilter(type)}
              className={`rounded-xl border p-3 font-mono transition-all ${
                isActive
                  ? type === "ALL"
                    ? "border-neon-cyan/30 bg-neon-cyan/5"
                    : `${typeBg[type as EventLog["type"]]} border`
                  : "border-border bg-card hover:border-neon-cyan/20"
              }`}
            >
              <div className="text-[10px] uppercase tracking-widest text-muted-foreground">{type}</div>
              <div className={`mt-1 text-xl font-bold ${type === "ALL" ? "text-foreground" : typeColors[type as EventLog["type"]]}`}>
                {counts[type]}
              </div>
            </motion.button>
          )
        })}
      </ScrollReveal>

      {/* Search & Controls */}
      <ScrollReveal className="flex flex-wrap items-center gap-3" delay={0.08}>
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search events..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-border bg-card py-2 pl-9 pr-3 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:border-neon-cyan/30 focus:outline-none focus:ring-1 focus:ring-neon-cyan/20"
          />
        </div>
        <button className="flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground transition-colors hover:border-neon-cyan/30 hover:text-foreground">
          <Download className="size-3" />
          Export
        </button>
      </ScrollReveal>

      {/* Event Stream */}
      <ScrollReveal className="rounded-xl border border-border bg-card p-5" delay={0.14}>
        <div className="mb-4 flex items-center gap-2">
          <Terminal className="size-4 text-neon-cyan" />
          <h3 className="font-mono text-xs uppercase tracking-widest text-neon-cyan">
            Enterprise Event Stream
          </h3>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="size-1.5 animate-pulse rounded-full bg-neon-green" />
            <span className="font-mono text-[10px] text-neon-green">LIVE</span>
          </div>
        </div>

        <ScrollArea className="h-[500px]">
          <div ref={scrollRef} className="space-y-1 overflow-auto font-mono text-[11px]">
            {filteredEvents.map((event) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
                className="flex items-start gap-3 rounded px-2 py-1.5 transition-colors hover:bg-secondary/50"
              >
                <span className="shrink-0 text-muted-foreground">{event.time}</span>
                <span className={`w-16 shrink-0 font-bold ${typeColors[event.type]}`}>
                  [{event.type}]
                </span>
                <span className="w-20 shrink-0 text-neon-purple/70">{event.source}</span>
                <span className="text-foreground/80">{event.message}</span>
              </motion.div>
            ))}
          </div>
        </ScrollArea>
      </ScrollReveal>
    </div>
  )
}

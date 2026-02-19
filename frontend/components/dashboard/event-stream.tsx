"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Terminal } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { LiveEvent } from "@/lib/api"

const typeColors: Record<LiveEvent["type"], string> = {
  INFO: "text-neon-cyan",
  WARN: "text-neon-amber",
  ERROR: "text-neon-red",
  SUCCESS: "text-neon-green",
}

export function EventStream({ events }: { events: LiveEvent[] }) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [events])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6, duration: 0.5 }}
      className="rounded-xl border border-border bg-card p-5"
    >
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

      <ScrollArea className="h-[220px]">
        <div ref={scrollRef} className="space-y-1 overflow-auto font-mono text-[11px]">
          {events.length === 0 && (
            <div className="rounded px-2 py-2 text-muted-foreground">Waiting for first telemetry scan...</div>
          )}
          {events.map((event) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-start gap-2 rounded px-2 py-1 transition-colors hover:bg-secondary/50"
            >
              <span className="shrink-0 text-muted-foreground">{event.time}</span>
              <span className={`shrink-0 font-bold ${typeColors[event.type]}`}>
                [{event.type.padEnd(7)}]
              </span>
              <span className="text-foreground/80">{event.message}</span>
            </motion.div>
          ))}
        </div>
      </ScrollArea>
    </motion.div>
  )
}

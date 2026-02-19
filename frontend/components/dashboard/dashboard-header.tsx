"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Hexagon, Wifi, Clock } from "lucide-react"

export function DashboardHeader() {
  const [time, setTime] = useState("")
  const [uptime, setUptime] = useState(0)

  useEffect(() => {
    const updateTime = () => {
      setTime(new Date().toLocaleTimeString("en-IN", { hour12: false }))
    }
    updateTime()
    const interval = setInterval(() => {
      updateTime()
      setUptime((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const formatUptime = (s: number) => {
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    const sec = s % 60
    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`
  }

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-wrap items-center justify-between gap-4 border-b border-border bg-card/50 px-6 py-4 backdrop-blur-sm"
    >
      <div className="flex items-center gap-3">
        <div className="lg:hidden">
          <Hexagon className="size-7 text-neon-cyan" />
        </div>
        <div>
          <h1 className="font-mono text-sm font-bold uppercase tracking-wider text-foreground lg:text-base">
            SCDIS Enterprise Control Center
          </h1>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="size-2 animate-pulse rounded-full bg-neon-green" />
              <span className="font-mono text-[10px] uppercase tracking-widest text-neon-green">
                Autonomous Mode Active
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 rounded-lg border border-border bg-secondary/50 px-3 py-1.5">
          <Wifi className="size-3 text-neon-green" />
          <span className="font-mono text-[10px] text-neon-green">CONNECTED</span>
        </div>
        <div className="flex items-center gap-1.5 rounded-lg border border-border bg-secondary/50 px-3 py-1.5">
          <Clock className="size-3 text-muted-foreground" />
          <span className="font-mono text-[10px] text-muted-foreground">UP {formatUptime(uptime)}</span>
        </div>
        <div className="rounded-lg border border-neon-cyan/20 bg-neon-cyan/5 px-3 py-1.5">
          <span className="font-mono text-xs font-bold text-neon-cyan">{time}</span>
        </div>
      </div>
    </motion.header>
  )
}

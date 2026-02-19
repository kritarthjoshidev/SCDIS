"use client"

import { motion } from "framer-motion"
import {
  LayoutDashboard,
  Brain,
  Cpu,
  Radio,
  AlertTriangle,
  Settings,
  ChevronLeft,
  ChevronRight,
  Hexagon,
} from "lucide-react"
import { useState } from "react"

export type TabId = "dashboard" | "decisions" | "ai-models" | "events" | "alerts" | "settings"

const navItems: { icon: typeof LayoutDashboard; label: string; id: TabId }[] = [
  { icon: LayoutDashboard, label: "Dashboard", id: "dashboard" },
  { icon: Brain, label: "Decisions", id: "decisions" },
  { icon: Cpu, label: "AI Models", id: "ai-models" },
  { icon: Radio, label: "Events", id: "events" },
  { icon: AlertTriangle, label: "Alerts", id: "alerts" },
  { icon: Settings, label: "Settings", id: "settings" },
]

interface SidebarNavProps {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
}

export function SidebarNav({ activeTab, onTabChange }: SidebarNavProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1, width: collapsed ? 64 : 220 }}
      transition={{ duration: 0.3 }}
      className="hidden h-[100dvh] shrink-0 flex-col border-r border-border bg-sidebar lg:flex"
    >
      <div className="flex items-center gap-2.5 border-b border-border px-4 py-5">
        <Hexagon className="size-7 shrink-0 text-neon-cyan" />
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="min-w-0"
          >
            <div className="font-mono text-sm font-bold tracking-wider text-foreground">
              SCDIS
            </div>
            <div className="font-mono text-[9px] uppercase tracking-widest text-neon-cyan">
              Control Center
            </div>
          </motion.div>
        )}
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = item.id === activeTab
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 font-mono text-xs transition-all ${
                isActive
                  ? "bg-neon-cyan/10 text-neon-cyan"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="active-nav"
                  className="absolute inset-0 rounded-lg border border-neon-cyan/20 bg-neon-cyan/10"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <Icon className="relative size-4 shrink-0" />
              {!collapsed && (
                <span className="relative uppercase tracking-wider">{item.label}</span>
              )}
            </button>
          )
        })}
      </nav>

      <div className="border-t border-border p-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-lg py-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          {collapsed ? <ChevronRight className="size-4" /> : <ChevronLeft className="size-4" />}
        </button>
      </div>
    </motion.aside>
  )
}

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import {
  Settings,
  Bell,
  Shield,
  Monitor,
  Database,
  Globe,
  Moon,
  Cpu,
  ToggleLeft,
  ToggleRight,
  Save,
} from "lucide-react"
import { Slider } from "@/components/ui/slider"
import { ScrollReveal } from "@/components/ui/scroll-reveal"

interface SettingToggle {
  id: string
  label: string
  description: string
  enabled: boolean
  icon: typeof Bell
}

export function SettingsTab() {
  const [toggles, setToggles] = useState<SettingToggle[]>([
    {
      id: "auto-mode",
      label: "Autonomous Mode",
      description: "Allow AI to make decisions without human approval",
      enabled: true,
      icon: Cpu,
    },
    {
      id: "alerts",
      label: "Real-time Alerts",
      description: "Push notifications for critical and warning events",
      enabled: true,
      icon: Bell,
    },
    {
      id: "auto-retrain",
      label: "Auto Model Retraining",
      description: "Automatically retrain models when accuracy dips below threshold",
      enabled: true,
      icon: Database,
    },
    {
      id: "failover",
      label: "Auto Failover",
      description: "Automatically activate backup nodes on failure detection",
      enabled: true,
      icon: Shield,
    },
    {
      id: "dark-mode",
      label: "Dark Interface",
      description: "Use dark color scheme for control center",
      enabled: true,
      icon: Moon,
    },
    {
      id: "telemetry",
      label: "Send Telemetry",
      description: "Share anonymized performance data for system improvement",
      enabled: false,
      icon: Globe,
    },
  ])

  const [accuracyThreshold, setAccuracyThreshold] = useState(90)
  const [alertFrequency, setAlertFrequency] = useState(5)
  const [retentionDays, setRetentionDays] = useState(30)

  const toggle = (id: string) => {
    setToggles((prev) =>
      prev.map((t) => (t.id === id ? { ...t, enabled: !t.enabled } : t))
    )
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <ScrollReveal className="flex items-center gap-2" delay={0.02}>
        <Settings className="size-5 text-neon-cyan" />
        <h2 className="font-mono text-sm font-bold uppercase tracking-widest text-foreground">
          System Configuration
        </h2>
      </ScrollReveal>

      {/* Toggle Settings */}
      <ScrollReveal className="rounded-xl border border-border bg-card p-5" delay={0.08}>
        <h3 className="mb-4 font-mono text-xs uppercase tracking-widest text-muted-foreground">
          System Controls
        </h3>
        <div className="space-y-1">
          {toggles.map((setting, i) => {
            const Icon = setting.icon
            return (
              <motion.div
                key={setting.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + i * 0.05 }}
                className="flex items-center justify-between rounded-lg p-3 transition-colors hover:bg-secondary/50"
              >
                <div className="flex items-center gap-3">
                  <Icon className="size-4 text-muted-foreground" />
                  <div>
                    <div className="font-mono text-xs font-bold text-foreground">{setting.label}</div>
                    <div className="font-mono text-[10px] text-muted-foreground">{setting.description}</div>
                  </div>
                </div>
                <button
                  onClick={() => toggle(setting.id)}
                  className="shrink-0"
                >
                  {setting.enabled ? (
                    <ToggleRight className="size-7 text-neon-cyan" />
                  ) : (
                    <ToggleLeft className="size-7 text-muted-foreground" />
                  )}
                </button>
              </motion.div>
            )
          })}
        </div>
      </ScrollReveal>

      {/* Threshold Settings */}
      <ScrollReveal className="rounded-xl border border-border bg-card p-5" delay={0.14}>
        <h3 className="mb-5 font-mono text-xs uppercase tracking-widest text-muted-foreground">
          Thresholds & Limits
        </h3>
        <div className="space-y-6">
          <div>
            <div className="mb-2 flex items-center justify-between">
              <span className="font-mono text-xs text-foreground">Accuracy Retrain Threshold</span>
              <span className="font-mono text-xs text-neon-cyan">{accuracyThreshold}%</span>
            </div>
            <Slider
              value={[accuracyThreshold]}
              onValueChange={([v]) => setAccuracyThreshold(v)}
              min={80}
              max={99}
              step={1}
              className="[&_[data-slot=slider-range]]:bg-neon-cyan [&_[data-slot=slider-thumb]]:border-neon-cyan [&_[data-slot=slider-track]]:bg-neon-cyan/10"
            />
            <p className="mt-1 font-mono text-[10px] text-muted-foreground">
              Trigger retraining when model accuracy drops below this value
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <span className="font-mono text-xs text-foreground">Alert Cooldown (seconds)</span>
              <span className="font-mono text-xs text-neon-amber">{alertFrequency}s</span>
            </div>
            <Slider
              value={[alertFrequency]}
              onValueChange={([v]) => setAlertFrequency(v)}
              min={1}
              max={60}
              step={1}
              className="[&_[data-slot=slider-range]]:bg-neon-amber [&_[data-slot=slider-thumb]]:border-neon-amber [&_[data-slot=slider-track]]:bg-neon-amber/10"
            />
            <p className="mt-1 font-mono text-[10px] text-muted-foreground">
              Minimum time between duplicate alerts of the same type
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <span className="font-mono text-xs text-foreground">Log Retention (days)</span>
              <span className="font-mono text-xs text-neon-purple">{retentionDays}d</span>
            </div>
            <Slider
              value={[retentionDays]}
              onValueChange={([v]) => setRetentionDays(v)}
              min={7}
              max={90}
              step={1}
              className="[&_[data-slot=slider-range]]:bg-neon-purple [&_[data-slot=slider-thumb]]:border-neon-purple [&_[data-slot=slider-track]]:bg-neon-purple/10"
            />
            <p className="mt-1 font-mono text-[10px] text-muted-foreground">
              Number of days to retain event logs and telemetry data
            </p>
          </div>
        </div>
      </ScrollReveal>

      {/* System Info */}
      <ScrollReveal className="rounded-xl border border-border bg-card p-5" delay={0.2}>
        <h3 className="mb-4 font-mono text-xs uppercase tracking-widest text-muted-foreground">
          System Information
        </h3>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            { label: "Version", value: "v2.7.1" },
            { label: "Build", value: "2026.02.18" },
            { label: "Runtime", value: "Node 22.x" },
            { label: "Region", value: "ap-south-1" },
          ].map((info) => (
            <div key={info.label} className="rounded-lg border border-border bg-secondary/30 p-3">
              <div className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                {info.label}
              </div>
              <div className="mt-1 font-mono text-sm font-bold text-foreground">{info.value}</div>
            </div>
          ))}
        </div>
      </ScrollReveal>

      {/* Save Button */}
      <ScrollReveal className="flex justify-end" delay={0.24}>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 rounded-xl border border-neon-cyan bg-neon-cyan/10 px-6 py-3 font-mono text-sm font-bold uppercase tracking-widest text-neon-cyan transition-all hover:bg-neon-cyan/20"
        >
          <Save className="size-4" />
          Save Configuration
        </motion.button>
      </ScrollReveal>
    </div>
  )
}

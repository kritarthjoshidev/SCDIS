"use client"

import { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { SidebarNav, type TabId } from "@/components/dashboard/sidebar-nav"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { StatusCards } from "@/components/dashboard/status-cards"
import { TelemetryPanel } from "@/components/dashboard/telemetry-panel"
import { DecisionOutput, type DecisionResult } from "@/components/dashboard/decision-output"
import { RuntimeHealth } from "@/components/dashboard/runtime-health"
import { EventStream } from "@/components/dashboard/event-stream"
import { AlertsPanel } from "@/components/dashboard/alerts-panel"
import { OptimizationChart } from "@/components/dashboard/optimization-chart"
import { DecisionsTab } from "@/components/dashboard/tabs/decisions-tab"
import { AIModelsTab } from "@/components/dashboard/tabs/ai-models-tab"
import { EventsTab } from "@/components/dashboard/tabs/events-tab"
import { AlertsTab } from "@/components/dashboard/tabs/alerts-tab"
import { SettingsTab } from "@/components/dashboard/tabs/settings-tab"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ScrollReveal } from "@/components/ui/scroll-reveal"
import {
  getLiveLaptopDashboard,
  mapDecisionForUi,
  setRuntimeMode,
  setSimulationScenario,
  type LiveDashboardResponse,
  type RuntimeMode,
  type SimulationScenario,
  type RuntimeHealthItem,
} from "@/lib/api"

const defaultRuntimeHealth: RuntimeHealthItem[] = [
  { name: "CPU Headroom", value: 0 },
  { name: "Memory Headroom", value: 0 },
  { name: "Disk Headroom", value: 0 },
  { name: "Power Health", value: 0 },
  { name: "Decision Stability", value: 0 },
]

function DashboardOverview() {
  const [liveData, setLiveData] = useState<LiveDashboardResponse | null>(null)
  const [decision, setDecision] = useState<DecisionResult | null>(null)
  const [decisionError, setDecisionError] = useState<string | null>(null)
  const [controlStatus, setControlStatus] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [runtimeMode, setRuntimeModeState] = useState<RuntimeMode>("LIVE_EDGE")
  const [scenario, setScenarioState] = useState<SimulationScenario>("normal")
  const [isModeUpdating, setIsModeUpdating] = useState(false)
  const [isScenarioUpdating, setIsScenarioUpdating] = useState(false)
  const requestLock = useRef(false)

  const fetchLiveData = async (options?: { force?: boolean }) => {
    if (requestLock.current && !options?.force) {
      return
    }

    requestLock.current = true
    setIsScanning(true)

    try {
      const payload = await getLiveLaptopDashboard()
      setLiveData(payload)
      if (payload.mode) {
        setRuntimeModeState(payload.mode)
      }
      if (payload.scenario) {
        setScenarioState(payload.scenario)
      }
      setDecision(mapDecisionForUi({ decision: payload.decision }))
      setDecisionError(null)
    } catch (error) {
      setDecisionError(error instanceof Error ? error.message : "Live scan request failed")
    } finally {
      setIsScanning(false)
      requestLock.current = false
    }
  }

  useEffect(() => {
    fetchLiveData()
    const interval = setInterval(fetchLiveData, 5000)
    return () => clearInterval(interval)
  }, [])

  const updateRuntimeMode = async (nextMode: RuntimeMode) => {
    if (isModeUpdating) {
      return
    }

    setIsModeUpdating(true)
    setRuntimeModeState(nextMode)
    setControlStatus(`Applying mode ${nextMode.replace("_", " ")}...`)
    try {
      const response = await setRuntimeMode(nextMode)
      const appliedMode = (response.mode as RuntimeMode | undefined) ?? nextMode
      setRuntimeModeState(appliedMode)
      setControlStatus(`Runtime mode set to ${appliedMode.replace("_", " ")}`)
      await fetchLiveData({ force: true })
    } catch (error) {
      setDecisionError(error instanceof Error ? error.message : "Failed to change mode")
      setControlStatus(null)
    } finally {
      setIsModeUpdating(false)
    }
  }

  const triggerScenario = async (nextScenario: SimulationScenario) => {
    if (isScenarioUpdating) {
      return
    }

    setIsScenarioUpdating(true)
    setScenarioState(nextScenario)
    setControlStatus(`Injecting scenario ${nextScenario.replace("_", " ")}...`)
    try {
      const response = await setSimulationScenario(nextScenario, nextScenario === "normal" ? 0 : 12)
      const appliedScenario = (response.scenario as SimulationScenario | undefined) ?? nextScenario
      setScenarioState(appliedScenario)
      setControlStatus(`Scenario active: ${appliedScenario.replace("_", " ")}`)
      await fetchLiveData({ force: true })
    } catch (error) {
      setDecisionError(error instanceof Error ? error.message : "Failed to set scenario")
      setControlStatus(null)
    } finally {
      setIsScenarioUpdating(false)
    }
  }

  const optimizationScore =
    liveData?.history && liveData.history.length > 0
      ? liveData.history[liveData.history.length - 1].optimization
      : null

  return (
    <>
      <ScrollReveal className="mb-4 rounded-xl border border-border bg-card p-4" delay={0.01}>
        <div className="grid gap-3 lg:grid-cols-2">
          <div>
            <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Runtime Mode
            </div>
            <div className="flex flex-wrap gap-2">
              {(["LIVE_EDGE", "SIMULATION", "HYBRID"] as RuntimeMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => updateRuntimeMode(mode)}
                  disabled={isModeUpdating}
                  className={`rounded-lg border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider transition-colors ${
                    runtimeMode === mode
                      ? "border-neon-cyan bg-neon-cyan/10 text-neon-cyan"
                      : "border-border text-muted-foreground hover:border-neon-cyan/30 hover:text-foreground"
                  }`}
                >
                  {mode.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Validation Scenario
            </div>
            <div className="flex flex-wrap gap-2">
              {(["normal", "peak_load", "low_load", "grid_failure"] as SimulationScenario[]).map((item) => (
                <button
                  key={item}
                  onClick={() => triggerScenario(item)}
                  disabled={isScenarioUpdating}
                  className={`rounded-lg border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider transition-colors ${
                    scenario === item
                      ? item === "grid_failure"
                        ? "border-neon-red bg-neon-red/10 text-neon-red"
                        : "border-neon-amber bg-neon-amber/10 text-neon-amber"
                      : "border-border text-muted-foreground hover:border-neon-cyan/30 hover:text-foreground"
                  }`}
                >
                  {item.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>
        </div>
      </ScrollReveal>

      {decisionError && (
        <div className="mb-4 rounded-lg border border-neon-red/30 bg-neon-red/10 px-3 py-2 font-mono text-xs text-neon-red">
          {decisionError}
        </div>
      )}

      {controlStatus && (
        <div className="mb-4 rounded-lg border border-neon-green/30 bg-neon-green/10 px-3 py-2 font-mono text-xs text-neon-green">
          {controlStatus}
        </div>
      )}

      <ScrollReveal className="mb-6" delay={0.02}>
        <StatusCards
          telemetry={liveData?.telemetry ?? null}
          optimizationScore={optimizationScore}
          runtimeMode={runtimeMode}
          scenario={scenario}
        />
      </ScrollReveal>

      <ScrollReveal className="mb-6 grid gap-4 lg:grid-cols-3" delay={0.06}>
        <TelemetryPanel telemetry={liveData?.telemetry ?? null} isScanning={isScanning} />
        <DecisionOutput result={decision} error={decisionError} />
        <RuntimeHealth items={liveData?.runtime_health ?? defaultRuntimeHealth} />
      </ScrollReveal>

      <ScrollReveal className="grid gap-4 lg:grid-cols-3" delay={0.1}>
        <div className="lg:col-span-2">
          <OptimizationChart history={liveData?.history ?? []} />
        </div>
        <div className="grid gap-4">
          <AlertsPanel alerts={liveData?.alerts ?? []} />
        </div>
      </ScrollReveal>

      <ScrollReveal className="mt-4" delay={0.14}>
        <EventStream events={liveData?.events ?? []} />
      </ScrollReveal>
    </>
  )
}

const tabTitles: Record<TabId, string> = {
  dashboard: "Overview",
  decisions: "AI Decisions",
  "ai-models": "AI Models",
  events: "Event Stream",
  alerts: "Alerts Center",
  settings: "Settings",
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard")

  return (
    <div className="flex h-[100dvh] min-h-0 overflow-hidden bg-background">
      <SidebarNav activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <DashboardHeader />

        <ScrollArea className="min-h-0 flex-1">
          <main className="p-4 lg:p-6">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-6"
            >
              <h2 className="font-mono text-lg font-bold uppercase tracking-widest text-foreground">
                {tabTitles[activeTab]}
              </h2>
              <div className="mt-1 h-px bg-gradient-to-r from-neon-cyan/50 via-neon-purple/30 to-transparent" />
            </motion.div>

            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                transition={{ duration: 0.25 }}
              >
                {activeTab === "dashboard" && <DashboardOverview />}
                {activeTab === "decisions" && <DecisionsTab />}
                {activeTab === "ai-models" && <AIModelsTab />}
                {activeTab === "events" && <EventsTab />}
                {activeTab === "alerts" && <AlertsTab />}
                {activeTab === "settings" && <SettingsTab />}
              </motion.div>
            </AnimatePresence>
          </main>
        </ScrollArea>
      </div>
    </div>
  )
}

"use client"

import { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  ArrowDownRight,
  DollarSign,
  Shield,
  Clock,
  RotateCcw,
  Cpu,
  Activity,
  Zap,
  Thermometer,
  Gauge,
} from "lucide-react"
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
} from "@/lib/api"

interface DecisionRow {
  id: number
  rlAction: string
  reduction: number
  costSaved: number
  stabilityScore: number
  timestamp: string
  mode: RuntimeMode
  scenario: SimulationScenario
  siteId: string
  gridStatus: string
}

const runtimeModes: RuntimeMode[] = ["LIVE_EDGE", "SIMULATION", "HYBRID"]
const scenarios: SimulationScenario[] = ["normal", "peak_load", "low_load", "grid_failure"]

export function DecisionsTab() {
  const [liveData, setLiveData] = useState<LiveDashboardResponse | null>(null)
  const [runtimeMode, setRuntimeModeState] = useState<RuntimeMode>("LIVE_EDGE")
  const [scenario, setScenarioState] = useState<SimulationScenario>("normal")
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isModeUpdating, setIsModeUpdating] = useState(false)
  const [isScenarioUpdating, setIsScenarioUpdating] = useState(false)
  const [decisions, setDecisions] = useState<DecisionRow[]>([])
  const [latest, setLatest] = useState<DecisionRow | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [controlStatus, setControlStatus] = useState<string | null>(null)

  const idRef = useRef(0)
  const fetchLockRef = useRef(false)
  const lastDecisionKeyRef = useRef("")

  const fetchLiveData = async (options?: { force?: boolean }) => {
    if (fetchLockRef.current && !options?.force) {
      return
    }

    fetchLockRef.current = true
    setIsRefreshing(true)

    try {
      const payload = await getLiveLaptopDashboard()
      const currentMode = payload.mode ?? "LIVE_EDGE"
      const currentScenario = payload.scenario ?? "normal"
      const mapped = mapDecisionForUi({ decision: payload.decision })
      const siteId = payload.telemetry?.industrial_metrics?.site_id ?? payload.telemetry?.hostname ?? "site-local"
      const gridStatus =
        payload.telemetry?.industrial_metrics?.grid_status ?? payload.telemetry?.grid_status ?? "unknown"

      setLiveData(payload)
      setRuntimeModeState(currentMode)
      setScenarioState(currentScenario)

      const decisionKey = `${payload.decision?.timestamp ?? mapped.timestamp}|${mapped.rlAction}|${currentMode}|${currentScenario}`

      if (decisionKey !== lastDecisionKeyRef.current) {
        idRef.current += 1

        const nextDecision: DecisionRow = {
          id: idRef.current,
          ...mapped,
          mode: currentMode,
          scenario: currentScenario,
          siteId,
          gridStatus,
        }

        setLatest(nextDecision)
        setDecisions((prev) => [nextDecision, ...prev].slice(0, 80))
        lastDecisionKeyRef.current = decisionKey
      }

      setErrorMessage(null)
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Decision stream failed")
    } finally {
      setIsRefreshing(false)
      fetchLockRef.current = false
    }
  }

  useEffect(() => {
    fetchLiveData()
    const interval = setInterval(fetchLiveData, 5000)
    return () => clearInterval(interval)
  }, [])

  const updateMode = async (nextMode: RuntimeMode) => {
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
      setErrorMessage(error instanceof Error ? error.message : "Mode update failed")
      setControlStatus(null)
    } finally {
      setIsModeUpdating(false)
    }
  }

  const updateScenario = async (nextScenario: SimulationScenario) => {
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
      setErrorMessage(error instanceof Error ? error.message : "Scenario update failed")
      setControlStatus(null)
    } finally {
      setIsScenarioUpdating(false)
    }
  }

  const industrial = liveData?.telemetry?.industrial_metrics
  const predictedEnergy = Number(liveData?.decision?.forecast?.predicted_energy_usage ?? 0)
  const highUsageFlag = Boolean(liveData?.decision?.forecast?.high_usage_flag)

  return (
    <div className="grid gap-6 lg:grid-cols-12">
      <ScrollReveal className="lg:col-span-4" delay={0.02}>
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="mb-5 flex items-center gap-2">
            <div className={`size-2 rounded-full ${isRefreshing ? "animate-pulse bg-neon-cyan" : "bg-neon-amber"}`} />
            <h3 className="font-mono text-xs uppercase tracking-widest text-neon-cyan">
              Decision Control Center
            </h3>
          </div>

          <div className="space-y-5">
            <div>
              <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Runtime Mode
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                {runtimeModes.map((mode) => (
                  <button
                    key={mode}
                    onClick={() => updateMode(mode)}
                    disabled={isModeUpdating}
                    className={`rounded-lg border px-2 py-1.5 font-mono text-[10px] uppercase tracking-wider transition-all ${
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
                Scenario Injection
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {scenarios.map((item) => (
                  <button
                    key={item}
                    onClick={() => updateScenario(item)}
                    disabled={isScenarioUpdating}
                    className={`rounded-lg border px-2 py-1.5 font-mono text-[10px] uppercase tracking-wider transition-all ${
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

            <div className="grid grid-cols-2 gap-2">
              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="mb-1 inline-flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                  <Zap className="size-3 text-neon-amber" />
                  Energy
                </div>
                <div className="font-mono text-lg font-bold text-neon-amber">
                  {Math.round(industrial?.energy_usage_kwh ?? 0)}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="mb-1 inline-flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                  <Gauge className="size-3 text-neon-cyan" />
                  Grid
                </div>
                <div className="font-mono text-lg font-bold text-neon-cyan">
                  {Math.round((industrial?.grid_load ?? 0) * 100)}%
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="mb-1 inline-flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                  <Thermometer className="size-3 text-neon-purple" />
                  Thermal
                </div>
                <div className="font-mono text-lg font-bold text-neon-purple">
                  {Math.round(industrial?.thermal_index_c ?? 0)}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="mb-1 inline-flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                  <Activity className="size-3 text-neon-green" />
                  Site
                </div>
                <div className="font-mono text-xs font-bold text-neon-green">
                  {industrial?.site_id ?? "plant-local"}
                </div>
              </div>
            </div>

            {errorMessage && (
              <p className="rounded-lg border border-neon-red/30 bg-neon-red/10 p-2 font-mono text-[10px] text-neon-red">
                {errorMessage}
              </p>
            )}

            {controlStatus && (
              <p className="rounded-lg border border-neon-green/30 bg-neon-green/10 p-2 font-mono text-[10px] text-neon-green">
                {controlStatus}
              </p>
            )}
          </div>
        </div>
      </ScrollReveal>

      <ScrollReveal className="lg:col-span-4" delay={0.08}>
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="mb-5 flex items-center gap-2">
            <Cpu className="size-4 text-neon-purple" />
            <h3 className="font-mono text-xs uppercase tracking-widest text-neon-purple">
              Latest Decision
            </h3>
          </div>

          <AnimatePresence mode="wait">
            {latest ? (
              <motion.div
                key={latest.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-4"
              >
                <div className="rounded-lg border border-neon-cyan/20 bg-neon-cyan/5 p-4">
                  <div className="mb-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    RL Action
                  </div>
                  <div className="font-mono text-2xl font-bold text-neon-cyan">{latest.rlAction}</div>
                  <div className="mt-1 font-mono text-[10px] text-muted-foreground">
                    {latest.siteId} | Grid {latest.gridStatus.toUpperCase()}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-lg border border-border bg-secondary/50 p-3">
                    <div className="mb-2 flex items-center gap-1">
                      <ArrowDownRight className="size-3 text-neon-green" />
                      <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                        Reduction
                      </span>
                    </div>
                    <div className="font-mono text-xl font-bold text-neon-green">{latest.reduction}%</div>
                  </div>

                  <div className="rounded-lg border border-border bg-secondary/50 p-3">
                    <div className="mb-2 flex items-center gap-1">
                      <DollarSign className="size-3 text-neon-amber" />
                      <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                        Cost Saved
                      </span>
                    </div>
                    <div className="font-mono text-xl font-bold text-neon-amber">Rs {latest.costSaved}</div>
                  </div>

                  <div className="rounded-lg border border-border bg-secondary/50 p-3">
                    <div className="mb-2 flex items-center gap-1">
                      <Shield className="size-3 text-neon-cyan" />
                      <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">
                        Stability
                      </span>
                    </div>
                    <div className="font-mono text-xl font-bold text-neon-cyan">{latest.stabilityScore}</div>
                  </div>
                </div>

                <div className="rounded-lg border border-border bg-secondary/40 p-3 font-mono text-[10px] text-muted-foreground">
                  <div className="flex items-center justify-between">
                    <span>Predicted Energy</span>
                    <span className="font-bold text-foreground">{predictedEnergy.toFixed(2)}</span>
                  </div>
                  <div className="mt-1 flex items-center justify-between">
                    <span>High Usage Flag</span>
                    <span className={highUsageFlag ? "font-bold text-neon-red" : "font-bold text-neon-green"}>
                      {highUsageFlag ? "YES" : "NO"}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 font-mono text-[10px] text-muted-foreground">
                  <Clock className="size-3" />
                  Generated at {latest.timestamp} | {latest.mode.replace("_", " ")}
                </div>
              </motion.div>
            ) : (
              <div className="flex min-h-[180px] flex-col items-center justify-center gap-2 text-muted-foreground">
                <div className="relative">
                  <div className="size-12 rounded-full border border-border" />
                  <div className="absolute inset-0 animate-ping rounded-full border border-neon-cyan/20" />
                </div>
                <span className="font-mono text-xs">Waiting for autonomous decision...</span>
              </div>
            )}
          </AnimatePresence>
        </div>
      </ScrollReveal>

      <ScrollReveal className="lg:col-span-4" delay={0.14}>
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center gap-2">
            <RotateCcw className="size-4 text-neon-cyan" />
            <h3 className="font-mono text-xs uppercase tracking-widest text-neon-cyan">
              Decision Timeline
            </h3>
            <span className="ml-auto rounded-md bg-neon-cyan/10 px-2 py-0.5 font-mono text-[10px] font-bold text-neon-cyan">
              {decisions.length}
            </span>
          </div>

          <ScrollArea className="h-[420px]">
            <div className="space-y-2">
              {decisions.length === 0 && (
                <div className="rounded-lg border border-border bg-secondary/30 p-3 font-mono text-[10px] text-muted-foreground">
                  Timeline starts after first live decision tick.
                </div>
              )}

              {decisions.map((d, i) => (
                <motion.div
                  key={d.id}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className={`rounded-lg border p-3 transition-colors ${
                    latest?.id === d.id
                      ? "border-neon-cyan/30 bg-neon-cyan/5"
                      : "border-border bg-secondary/30 hover:bg-secondary/50"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[11px] font-bold text-neon-cyan">{d.rlAction}</span>
                    <span className="font-mono text-[9px] text-muted-foreground">{d.timestamp}</span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-3 font-mono text-[10px]">
                    <span className="text-neon-green">-{d.reduction}%</span>
                    <span className="text-neon-amber">Rs {d.costSaved}</span>
                    <span className="text-muted-foreground">{d.siteId}</span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-2 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                    <span className="rounded bg-secondary px-1.5 py-0.5">{d.mode.replace("_", " ")}</span>
                    <span className="rounded bg-secondary px-1.5 py-0.5">{d.scenario.replace("_", " ")}</span>
                    <span className="rounded bg-secondary px-1.5 py-0.5">grid {d.gridStatus}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </ScrollReveal>
    </div>
  )
}

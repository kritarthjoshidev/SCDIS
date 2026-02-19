"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import {
  Brain,
  Zap,
  TrendingUp,
  Clock,
  BarChart3,
} from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ScrollReveal } from "@/components/ui/scroll-reveal"
import {
  exportAiModelWeights,
  getAiModelLogs,
  retrainAiModels,
  type AiModelLogSource,
  type ExportModelTarget,
} from "@/lib/api"

interface AIModel {
  id: string
  name: string
  type: string
  version: string
  accuracy: number
  latency: number
  status: "active" | "training" | "standby"
  lastTrained: string
  decisionsToday: number
  description: string
}

const models: AIModel[] = [
  {
    id: "rl-agent",
    name: "RL Decision Agent",
    type: "Reinforcement Learning",
    version: "v7.2.1",
    accuracy: 97.2,
    latency: 12,
    status: "active",
    lastTrained: "2 hours ago",
    decisionsToday: 1247,
    description: "Primary decision engine for energy optimization and grid balancing actions.",
  },
  {
    id: "anomaly-det",
    name: "Anomaly Detector",
    type: "Autoencoder",
    version: "v3.8.0",
    accuracy: 94.6,
    latency: 8,
    status: "active",
    lastTrained: "6 hours ago",
    decisionsToday: 3421,
    description: "Real-time anomaly detection across sensor telemetry and event streams.",
  },
  {
    id: "forecaster",
    name: "Load Forecaster",
    type: "Transformer",
    version: "v5.1.3",
    accuracy: 91.8,
    latency: 45,
    status: "training",
    lastTrained: "Training now...",
    decisionsToday: 856,
    description: "Predicts future grid load and energy demand across all 6 zones.",
  },
  {
    id: "self-evolve",
    name: "Self-Evolution Engine",
    type: "Genetic Algorithm",
    version: "GEN-7",
    accuracy: 88.4,
    latency: 200,
    status: "active",
    lastTrained: "12 hours ago",
    decisionsToday: 34,
    description: "Meta-optimization layer that evolves the architecture of all sub-models.",
  },
  {
    id: "failover",
    name: "Failover Predictor",
    type: "Random Forest",
    version: "v2.4.0",
    accuracy: 96.1,
    latency: 5,
    status: "standby",
    lastTrained: "1 day ago",
    decisionsToday: 0,
    description: "Predicts node failures and proactively triggers backup activations.",
  },
  {
    id: "thermal",
    name: "Thermal Optimizer",
    type: "Deep Q-Network",
    version: "v4.0.2",
    accuracy: 93.7,
    latency: 18,
    status: "active",
    lastTrained: "4 hours ago",
    decisionsToday: 672,
    description: "Controls cooling and thermal management across data center zones.",
  },
]

const statusConfig = {
  active: { color: "text-neon-green", bg: "bg-neon-green/10", border: "border-neon-green/30", label: "ACTIVE" },
  training: { color: "text-neon-amber", bg: "bg-neon-amber/10", border: "border-neon-amber/30", label: "TRAINING" },
  standby: { color: "text-muted-foreground", bg: "bg-secondary", border: "border-border", label: "STANDBY" },
}

export function AIModelsTab() {
  const [selectedModel, setSelectedModel] = useState<AIModel>(models[0])
  const [accuracies, setAccuracies] = useState<Record<string, number>>(() =>
    Object.fromEntries(models.map((m) => [m.id, m.accuracy]))
  )
  const [isRetraining, setIsRetraining] = useState(false)
  const [isLogLoading, setIsLogLoading] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [logSource, setLogSource] = useState<AiModelLogSource>("application")
  const [logLines, setLogLines] = useState<string[]>([])
  const [showLogs, setShowLogs] = useState(false)
  const [actionStatus, setActionStatus] = useState<{ tone: "success" | "error" | "info"; message: string } | null>(
    null
  )

  useEffect(() => {
    const interval = setInterval(() => {
      setAccuracies((prev) => {
        const updated = { ...prev }
        for (const key of Object.keys(updated)) {
          updated[key] = Math.max(85, Math.min(99.5, updated[key] + (Math.random() - 0.45) * 0.5))
          updated[key] = parseFloat(updated[key].toFixed(1))
        }
        return updated
      })
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const resolveWeightTarget = (model: AIModel): ExportModelTarget => {
    if (model.id === "anomaly-det") {
      return "anomaly"
    }
    return "forecast"
  }

  const handleRetrain = async () => {
    if (isRetraining) {
      return
    }

    setIsRetraining(true)
    setActionStatus({ tone: "info", message: "Retraining pipeline started..." })

    try {
      const response = await retrainAiModels()
      const status = String(response.status ?? "completed")

      if (status === "failed") {
        setActionStatus({ tone: "error", message: "Retraining failed. Check error logs." })
      } else if (status === "skipped") {
        setActionStatus({ tone: "info", message: "Retraining skipped: dataset not available." })
      } else {
        setActionStatus({ tone: "success", message: "Retraining completed successfully." })
      }
    } catch (error) {
      setActionStatus({
        tone: "error",
        message: error instanceof Error ? error.message : "Retraining request failed",
      })
    } finally {
      setIsRetraining(false)
    }
  }

  const handleViewLogs = async () => {
    if (isLogLoading) {
      return
    }

    setIsLogLoading(true)
    setActionStatus({ tone: "info", message: "Fetching latest logs..." })

    try {
      const response = await getAiModelLogs(logSource, 180)
      setLogLines(response.lines)
      setShowLogs(true)
      setActionStatus({ tone: "success", message: `Loaded ${response.line_count} lines from ${response.source}.` })
    } catch (error) {
      setActionStatus({
        tone: "error",
        message: error instanceof Error ? error.message : "Unable to fetch logs",
      })
    } finally {
      setIsLogLoading(false)
    }
  }

  const handleExportWeights = async () => {
    if (isExporting) {
      return
    }

    const target = resolveWeightTarget(selectedModel)
    setIsExporting(true)
    setActionStatus({ tone: "info", message: `Exporting ${target} model weights...` })

    try {
      const blob = await exportAiModelWeights(target)
      const downloadUrl = window.URL.createObjectURL(blob)
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      const anchor = document.createElement("a")
      anchor.href = downloadUrl
      anchor.download = `${target}_model_weights_${timestamp}.pkl`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.URL.revokeObjectURL(downloadUrl)

      setActionStatus({ tone: "success", message: `${target} model weights exported.` })
    } catch (error) {
      setActionStatus({
        tone: "error",
        message: error instanceof Error ? error.message : "Weight export failed",
      })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-12">
      {/* Model List */}
      <ScrollReveal className="space-y-3 lg:col-span-5" delay={0.02}>
        <div className="mb-4 flex items-center gap-2">
          <Brain className="size-4 text-neon-purple" />
          <h3 className="font-mono text-xs uppercase tracking-widest text-neon-purple">
            Deployed Models
          </h3>
          <span className="ml-auto rounded-md bg-neon-purple/10 px-2 py-0.5 font-mono text-[10px] font-bold text-neon-purple">
            {models.length}
          </span>
        </div>

        {models.map((model, i) => {
          const st = statusConfig[model.status]
          const isSelected = selectedModel.id === model.id
          return (
            <motion.button
              key={model.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              onClick={() => setSelectedModel(model)}
              className={`w-full rounded-xl border p-4 text-left transition-all ${
                isSelected
                  ? "border-neon-cyan/30 bg-neon-cyan/5"
                  : "border-border bg-card hover:border-neon-cyan/20"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-mono text-sm font-bold text-foreground">{model.name}</div>
                  <div className="mt-0.5 font-mono text-[10px] text-muted-foreground">{model.type}</div>
                </div>
                <div className={`rounded-md border px-2 py-0.5 font-mono text-[9px] font-bold ${st.color} ${st.bg} ${st.border}`}>
                  {st.label}
                </div>
              </div>
              <div className="mt-3 flex items-center gap-4 font-mono text-[10px]">
                <span className="text-neon-cyan">{model.version}</span>
                <span className="text-neon-green">{accuracies[model.id]}%</span>
                <span className="text-muted-foreground">{model.latency}ms</span>
              </div>
            </motion.button>
          )
        })}
      </ScrollReveal>

      {/* Model Details */}
      <ScrollReveal className="lg:col-span-7" delay={0.08}>
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <h2 className="font-mono text-lg font-bold text-foreground">{selectedModel.name}</h2>
              <p className="mt-1 font-mono text-xs text-muted-foreground">{selectedModel.description}</p>
            </div>
            <div className={`rounded-md border px-2.5 py-1 font-mono text-[10px] font-bold ${statusConfig[selectedModel.status].color} ${statusConfig[selectedModel.status].bg} ${statusConfig[selectedModel.status].border}`}>
              {statusConfig[selectedModel.status].label}
            </div>
          </div>

          <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="rounded-lg border border-border bg-secondary/50 p-4">
              <div className="mb-2 flex items-center gap-1.5">
                <TrendingUp className="size-3 text-neon-green" />
                <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">Accuracy</span>
              </div>
              <div className="font-mono text-2xl font-bold text-neon-green">{accuracies[selectedModel.id]}%</div>
            </div>
            <div className="rounded-lg border border-border bg-secondary/50 p-4">
              <div className="mb-2 flex items-center gap-1.5">
                <Zap className="size-3 text-neon-amber" />
                <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">Latency</span>
              </div>
              <div className="font-mono text-2xl font-bold text-neon-amber">{selectedModel.latency}ms</div>
            </div>
            <div className="rounded-lg border border-border bg-secondary/50 p-4">
              <div className="mb-2 flex items-center gap-1.5">
                <BarChart3 className="size-3 text-neon-cyan" />
                <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">Decisions</span>
              </div>
              <div className="font-mono text-2xl font-bold text-neon-cyan">{selectedModel.decisionsToday.toLocaleString()}</div>
            </div>
            <div className="rounded-lg border border-border bg-secondary/50 p-4">
              <div className="mb-2 flex items-center gap-1.5">
                <Clock className="size-3 text-muted-foreground" />
                <span className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">Trained</span>
              </div>
              <div className="font-mono text-sm font-bold text-foreground">{selectedModel.lastTrained}</div>
            </div>
          </div>

          {/* Model Architecture */}
          <div className="mb-6 rounded-lg border border-border bg-secondary/30 p-4">
            <h4 className="mb-3 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Model Architecture
            </h4>
            <div className="flex flex-wrap items-center gap-2">
              {["Input Layer", "Feature Extraction", "Hidden Layers", "Decision Head", "Output"].map(
                (layer, i) => (
                  <div key={layer} className="flex items-center gap-2">
                    <div className="rounded-lg border border-neon-cyan/20 bg-neon-cyan/5 px-3 py-1.5 font-mono text-[10px] text-neon-cyan">
                      {layer}
                    </div>
                    {i < 4 && (
                      <div className="font-mono text-xs text-muted-foreground">{"->"}</div>
                    )}
                  </div>
                )
              )}
            </div>
          </div>

          {/* Performance bars */}
          <div className="space-y-3">
            <h4 className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Performance Metrics
            </h4>
            {[
              { label: "Precision", value: 96.3, color: "bg-neon-cyan" },
              { label: "Recall", value: 94.1, color: "bg-neon-purple" },
              { label: "F1 Score", value: 95.2, color: "bg-neon-green" },
              { label: "Inference Speed", value: 98.7, color: "bg-neon-amber" },
            ].map((metric) => (
              <div key={metric.label}>
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-mono text-[11px] text-foreground">{metric.label}</span>
                  <span className="font-mono text-[11px] font-bold text-foreground">{metric.value}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                  <motion.div
                    className={`h-full rounded-full ${metric.color}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${metric.value}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Action buttons */}
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={handleRetrain}
              disabled={isRetraining}
              className="rounded-lg border border-neon-cyan bg-neon-cyan/10 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-neon-cyan transition-colors hover:bg-neon-cyan/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isRetraining ? "Retraining..." : "Retrain Model"}
            </button>
            <button
              onClick={handleViewLogs}
              disabled={isLogLoading}
              className="rounded-lg border border-neon-purple bg-neon-purple/10 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-neon-purple transition-colors hover:bg-neon-purple/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLogLoading ? "Loading Logs..." : "View Logs"}
            </button>
            <button
              onClick={handleExportWeights}
              disabled={isExporting}
              className="rounded-lg border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isExporting ? "Exporting..." : "Export Weights"}
            </button>
            <select
              value={logSource}
              onChange={(event) => setLogSource(event.target.value as AiModelLogSource)}
              className="rounded-lg border border-border bg-background px-3 py-2 font-mono text-[11px] text-muted-foreground focus:border-neon-cyan focus:outline-none"
            >
              <option value="application">Application Logs</option>
              <option value="errors">Error Logs</option>
            </select>
          </div>

          {actionStatus && (
            <div
              className={`mt-4 rounded-lg border p-3 font-mono text-[11px] ${
                actionStatus.tone === "error"
                  ? "border-neon-red/30 bg-neon-red/10 text-neon-red"
                  : actionStatus.tone === "success"
                    ? "border-neon-green/30 bg-neon-green/10 text-neon-green"
                    : "border-neon-cyan/30 bg-neon-cyan/10 text-neon-cyan"
              }`}
            >
              {actionStatus.message}
            </div>
          )}

          {showLogs && (
            <div className="mt-4 rounded-lg border border-border bg-secondary/20 p-3">
              <div className="mb-2 flex items-center justify-between">
                <h5 className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  {logSource} log stream
                </h5>
                <span className="font-mono text-[10px] text-muted-foreground">{logLines.length} lines</span>
              </div>
              <ScrollArea className="h-[220px] rounded-md border border-border/60 bg-background p-2">
                <pre className="whitespace-pre-wrap font-mono text-[10px] leading-5 text-foreground">
                  {logLines.length > 0 ? logLines.join("\n") : "No logs available."}
                </pre>
              </ScrollArea>
            </div>
          )}

          <div className="mt-3 font-mono text-[10px] text-muted-foreground">
            Export target: {resolveWeightTarget(selectedModel)} weights
          </div>
        </div>
      </ScrollReveal>
    </div>
  )
}

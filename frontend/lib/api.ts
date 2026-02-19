const PRIMARY_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
const API_FALLBACK_CANDIDATES = Array.from(
  new Set([PRIMARY_API_BASE_URL, "http://localhost:8010", "http://127.0.0.1:8010"])
)

let activeApiBaseUrl = PRIMARY_API_BASE_URL

export interface TelemetryInput {
  energy: number
  temperature: number
  gridLoad: number
  location: string
}

interface BackendDecisionPayload {
  timestamp?: string
  rl_action?: string
  optimized_decision?: {
    recommended_reduction?: number
    cost_saving_estimate?: number
    stability_score?: number
  }
}

export interface GenerateDecisionResponse {
  status?: string
  decision?: BackendDecisionPayload
}

export interface UiDecision {
  rlAction: string
  reduction: number
  costSaved: number
  stabilityScore: number
  timestamp: string
}

export interface SystemStatusResponse {
  timestamp?: string
  components?: Record<string, unknown>
}

export interface LiveTelemetry {
  timestamp: string
  hostname: string
  platform: string
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  battery_percent: number | null
  power_plugged: boolean | null
  process_count: number
}

export interface LiveHistoryPoint {
  timestamp: string
  time: string
  optimization: number
  energy: number
}

export interface LiveEvent {
  id: number
  type: "INFO" | "WARN" | "ERROR" | "SUCCESS"
  message: string
  time: string
}

export interface LiveAlert {
  id: number
  severity: "warning" | "critical"
  title: string
  message: string
  time: string
}

export interface RuntimeHealthItem {
  name: string
  value: number
}

export type RuntimeMode = "LIVE_EDGE" | "SIMULATION" | "HYBRID"
export type SimulationScenario = "normal" | "peak_load" | "low_load" | "grid_failure"

export interface IndustrialMetrics {
  site_id: string
  energy_usage_kwh: number
  thermal_index_c: number
  grid_load: number
  grid_status: string
  fault_flag: boolean
}

export interface LiveDashboardResponse {
  status: string
  mode: RuntimeMode
  scenario?: SimulationScenario
  timestamp: string
  telemetry: LiveTelemetry & {
    scan_mode?: RuntimeMode
    scenario?: SimulationScenario
    fault_flag?: boolean
    grid_status?: string
    industrial_metrics?: IndustrialMetrics
  }
  decision: BackendDecisionPayload
  runtime_health: RuntimeHealthItem[]
  history: LiveHistoryPoint[]
  events: LiveEvent[]
  alerts: LiveAlert[]
  service_health?: {
    running: boolean
    scan_interval_seconds: number
    auto_apply_power_profile: boolean
    runtime_mode?: RuntimeMode
    scenario?: SimulationScenario
    supported_modes?: RuntimeMode[]
    supported_scenarios?: SimulationScenario[]
    latest_timestamp?: string
    last_scan_error?: string | null
  }
}

export interface RuntimeControlResponse {
  status: string
  mode?: RuntimeMode
  scenario?: SimulationScenario
  cycles?: number
  timestamp: string
}

export interface AiModelRetrainResponse {
  status: string
  result?: Record<string, unknown>
  timestamp: string
}

export type AiModelLogSource = "application" | "errors"

export interface AiModelLogsResponse {
  status: string
  source: AiModelLogSource
  path: string
  line_count: number
  lines: string[]
  timestamp: string
}

export type ExportModelTarget = "forecast" | "anomaly"

const locationToBuildingId: Record<string, number> = {
  Mumbai: 1,
  Delhi: 2,
  Bangalore: 3,
  Chennai: 4,
  Kolkata: 5,
  Hyderabad: 6,
}

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }
  const requestInit = {
    ...init,
    headers,
  }

  const triedBases = new Set<string>()
  const candidateBases = [activeApiBaseUrl, ...API_FALLBACK_CANDIDATES.filter((base) => base !== activeApiBaseUrl)]
  let lastError: Error | null = null

  for (const baseUrl of candidateBases) {
    if (triedBases.has(baseUrl)) {
      continue
    }
    triedBases.add(baseUrl)

    try {
      const response = await fetch(`${baseUrl}${path}`, requestInit)
      if (!response.ok) {
        const message = await response.text()
        const responseError = new Error(`API ${response.status}: ${message || "request failed"}`)

        // If endpoint isn't available on current server, try next candidate.
        if (response.status === 404) {
          lastError = responseError
          continue
        }

        throw responseError
      }

      activeApiBaseUrl = baseUrl
      return response.json() as Promise<T>
    } catch (error) {
      lastError = error instanceof Error ? error : new Error("request failed")
    }
  }

  throw lastError ?? new Error("request failed")
}

function toSafeNumber(value: unknown, fallback = 0): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function toDisplayTime(timestamp?: string): string {
  if (!timestamp) {
    return new Date().toLocaleTimeString("en-IN", { hour12: false })
  }

  const parsedDate = new Date(timestamp)
  if (Number.isNaN(parsedDate.getTime())) {
    return new Date().toLocaleTimeString("en-IN", { hour12: false })
  }

  return parsedDate.toLocaleTimeString("en-IN", { hour12: false })
}

function toDecisionPayload(payload: TelemetryInput) {
  const now = new Date()
  const occupancy = Math.max(1, Math.round((payload.gridLoad / 100) * 1000))

  return {
    building_id: locationToBuildingId[payload.location] ?? 0,
    current_load: payload.energy,
    energy_usage_kwh: payload.energy,
    temperature: payload.temperature,
    humidity: 50,
    occupancy,
    day_of_week: now.getDay(),
    hour: now.getHours(),
    grid_load: payload.gridLoad,
    location: payload.location,
    state: payload.gridLoad >= 85 ? "high_load" : "normal",
  }
}

export function mapDecisionForUi(response: GenerateDecisionResponse): UiDecision {
  const decision = response.decision ?? {}
  const optimizedDecision = decision.optimized_decision ?? {}

  return {
    rlAction: String(decision.rl_action ?? "unknown_action"),
    reduction: Math.max(0, Math.round(toSafeNumber(optimizedDecision.recommended_reduction))),
    costSaved: Number(toSafeNumber(optimizedDecision.cost_saving_estimate).toFixed(2)),
    stabilityScore: Number(toSafeNumber(optimizedDecision.stability_score).toFixed(2)),
    timestamp: toDisplayTime(decision.timestamp),
  }
}

export async function generateDecision(payload: TelemetryInput): Promise<GenerateDecisionResponse> {
  return apiRequest<GenerateDecisionResponse>("/decision/generate", {
    method: "POST",
    body: JSON.stringify(toDecisionPayload(payload)),
  })
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  return apiRequest<SystemStatusResponse>("/autonomous-ai/status")
}

export async function runFullCycle(): Promise<Record<string, unknown>> {
  return apiRequest<Record<string, unknown>>("/autonomous-ai/run-full-cycle", {
    method: "POST",
  })
}

export async function getLiveLaptopDashboard(): Promise<LiveDashboardResponse> {
  return apiRequest<LiveDashboardResponse>("/monitoring/laptop/live-dashboard")
}

export async function setAutoApplyPowerProfile(enabled: boolean): Promise<Record<string, unknown>> {
  return apiRequest<Record<string, unknown>>("/monitoring/laptop/auto-apply", {
    method: "POST",
    body: JSON.stringify({ enabled }),
  })
}

export async function setRuntimeMode(mode: RuntimeMode): Promise<RuntimeControlResponse> {
  return apiRequest<RuntimeControlResponse>("/monitoring/laptop/mode", {
    method: "POST",
    body: JSON.stringify({ mode }),
  })
}

export async function setSimulationScenario(
  scenario: SimulationScenario,
  cycles = 12
): Promise<RuntimeControlResponse> {
  return apiRequest<RuntimeControlResponse>("/monitoring/laptop/scenario", {
    method: "POST",
    body: JSON.stringify({ scenario, cycles }),
  })
}

export async function retrainAiModels(): Promise<AiModelRetrainResponse> {
  return apiRequest<AiModelRetrainResponse>("/monitoring/ai-models/retrain", {
    method: "POST",
  })
}

export async function getAiModelLogs(
  source: AiModelLogSource = "application",
  lines = 150
): Promise<AiModelLogsResponse> {
  const params = new URLSearchParams({
    source,
    lines: String(Math.max(20, Math.min(lines, 1000))),
  })

  return apiRequest<AiModelLogsResponse>(`/monitoring/ai-models/logs?${params.toString()}`)
}

export async function exportAiModelWeights(model: ExportModelTarget = "forecast"): Promise<Blob> {
  const path = `/monitoring/ai-models/export-weights?model=${encodeURIComponent(model)}`
  const candidateBases = [activeApiBaseUrl, ...API_FALLBACK_CANDIDATES.filter((base) => base !== activeApiBaseUrl)]
  const triedBases = new Set<string>()
  let lastError: Error | null = null

  for (const baseUrl of candidateBases) {
    if (triedBases.has(baseUrl)) {
      continue
    }
    triedBases.add(baseUrl)

    try {
      const response = await fetch(`${baseUrl}${path}`)
      if (!response.ok) {
        const message = await response.text()
        const responseError = new Error(`API ${response.status}: ${message || "request failed"}`)
        if (response.status === 404) {
          lastError = responseError
          continue
        }
        throw responseError
      }

      activeApiBaseUrl = baseUrl
      return response.blob()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error("request failed")
    }
  }

  throw lastError ?? new Error("request failed")
}

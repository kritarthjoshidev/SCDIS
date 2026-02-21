"use client"

import { useEffect, useMemo, useState } from "react"

interface BatteryManagerLike extends EventTarget {
  level: number
  charging: boolean
}

interface NavigatorWithEdgeSignals extends Navigator {
  deviceMemory?: number
  connection?: {
    effectiveType?: string
  }
  userAgentData?: {
    platform?: string
  }
  getBattery?: () => Promise<BatteryManagerLike>
}

export interface ClientEdgeProfile {
  edgeId: string
  edgeLabel: string
  platform: string
  cpuCores: number | null
  memoryGB: number | null
  networkType: string | null
  batteryPercent: number | null
  powerPlugged: boolean | null
}

const EDGE_ID_STORAGE_KEY = "scdis_edge_id"

function createEdgeId(): string {
  try {
    const bytes = new Uint8Array(6)
    window.crypto.getRandomValues(bytes)
    return Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("")
  } catch {
    return Math.random().toString(16).slice(2, 14)
  }
}

function readOrCreateEdgeId(): string {
  try {
    const existing = window.localStorage.getItem(EDGE_ID_STORAGE_KEY)
    if (existing && existing.trim()) {
      return existing.trim()
    }
    const created = createEdgeId()
    window.localStorage.setItem(EDGE_ID_STORAGE_KEY, created)
    return created
  } catch {
    return createEdgeId()
  }
}

export function useClientEdgeProfile(): ClientEdgeProfile | null {
  const [profile, setProfile] = useState<ClientEdgeProfile | null>(null)

  useEffect(() => {
    if (typeof window === "undefined") {
      return
    }

    const nav = navigator as NavigatorWithEdgeSignals
    const edgeId = readOrCreateEdgeId()
    const platform = nav.userAgentData?.platform ?? nav.platform ?? "Browser"
    const cpuCores = Number.isFinite(nav.hardwareConcurrency) ? nav.hardwareConcurrency : null
    const memoryGB = typeof nav.deviceMemory === "number" ? nav.deviceMemory : null
    const networkType = nav.connection?.effectiveType ?? null

    setProfile({
      edgeId,
      edgeLabel: `edge-${edgeId.slice(-6)}`,
      platform,
      cpuCores,
      memoryGB,
      networkType,
      batteryPercent: null,
      powerPlugged: null,
    })

    let batteryRef: BatteryManagerLike | null = null
    let active = true

    const applyBattery = (battery: BatteryManagerLike) => {
      if (!active) {
        return
      }
      const nextBatteryPercent = Math.round(Math.max(0, Math.min(100, battery.level * 100)))
      const nextPowerPlugged = Boolean(battery.charging)
      setProfile((current) =>
        current
          ? {
              ...current,
              batteryPercent: nextBatteryPercent,
              powerPlugged: nextPowerPlugged,
            }
          : current
      )
    }

    const onBatteryChanged = () => {
      if (batteryRef) {
        applyBattery(batteryRef)
      }
    }

    if (typeof nav.getBattery === "function") {
      nav
        .getBattery()
        .then((battery) => {
          if (!active) {
            return
          }
          batteryRef = battery
          applyBattery(battery)
          battery.addEventListener("levelchange", onBatteryChanged)
          battery.addEventListener("chargingchange", onBatteryChanged)
        })
        .catch(() => {
          // Battery API is optional and can be blocked by browser privacy settings.
        })
    }

    return () => {
      active = false
      if (batteryRef) {
        batteryRef.removeEventListener("levelchange", onBatteryChanged)
        batteryRef.removeEventListener("chargingchange", onBatteryChanged)
      }
    }
  }, [])

  return useMemo(() => profile, [profile])
}

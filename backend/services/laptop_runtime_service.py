"""
Laptop Runtime Service

Continuously scans host machine telemetry and produces real-time
optimization signals for dashboard consumption.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import random
import socket
import subprocess
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional

from ai_engine.decision import DecisionEngine

logger = logging.getLogger(__name__)

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None


VALID_RUNTIME_MODES = {"LIVE_EDGE", "SIMULATION", "HYBRID"}
VALID_SCENARIOS = {"normal", "peak_load", "low_load", "grid_failure"}


class LaptopRuntimeService:
    def __init__(self, scan_interval_seconds: int = 5):
        self.scan_interval_seconds = scan_interval_seconds
        self._lock = threading.Lock()
        self._scan_iteration_lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._history: Deque[Dict[str, Any]] = deque(maxlen=720)
        self._events: Deque[Dict[str, Any]] = deque(maxlen=500)
        self._alerts: Deque[Dict[str, Any]] = deque(maxlen=200)

        self._latest_snapshot: Dict[str, Any] = {}
        self._latest_decision: Dict[str, Any] = {}
        self._latest_runtime_health: List[Dict[str, Any]] = []
        self._last_scan_error: Optional[str] = None
        self._previous_snapshot: Optional[Dict[str, Any]] = None

        self._auto_apply_power_profile = True
        self._last_applied_profile: Optional[str] = None
        self._last_applied_ts: float = 0

        self._decision_engine = DecisionEngine()
        self._runtime_mode = "LIVE_EDGE"
        self._scenario = "normal"
        self._scenario_cycles_left = 0
        self._rng = random.Random()
        self._sim_state: Dict[str, Any] = {
            "cpu_percent": 38.0,
            "memory_percent": 52.0,
            "disk_percent": 48.0,
            "battery_percent": 78.0,
            "power_plugged": False,
            "process_count": 190,
        }

    def start(self):
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()
        logger.info("Laptop runtime service started")

    def stop(self):
        self._running = False
        logger.info("Laptop runtime service stopped")

    def set_auto_apply(self, enabled: bool):
        self._auto_apply_power_profile = enabled

    def set_mode(self, mode: str):
        normalized = str(mode).strip().upper()
        if normalized not in VALID_RUNTIME_MODES:
            raise ValueError(f"Unsupported runtime mode: {mode}")

        with self._lock:
            self._runtime_mode = normalized
            self._events.append(
                {
                    "id": int(time.time() * 1000),
                    "type": "INFO",
                    "message": f"runtime_mode_changed {normalized}",
                    "time": datetime.utcnow().strftime("%H:%M:%S"),
                }
            )
        self.scan_now()

    def set_scenario(self, scenario: str, cycles: int = 12):
        normalized = str(scenario).strip().lower()
        if normalized not in VALID_SCENARIOS:
            raise ValueError(f"Unsupported scenario: {scenario}")

        cycles = max(0, min(int(cycles), 240))
        with self._lock:
            self._scenario = normalized
            self._scenario_cycles_left = 0 if normalized == "normal" else max(1, cycles)
            self._events.append(
                {
                    "id": int(time.time() * 1000),
                    "type": "WARN" if normalized != "normal" else "INFO",
                    "message": f"scenario_set {normalized}",
                    "time": datetime.utcnow().strftime("%H:%M:%S"),
                }
            )
        self.scan_now()

    def scan_now(self):
        with self._scan_iteration_lock:
            try:
                self._scan_iteration()
            except Exception as exc:  # pragma: no cover
                logger.exception("Laptop scan iteration failed")
                with self._lock:
                    self._last_scan_error = str(exc)

    def health_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "scan_interval_seconds": self.scan_interval_seconds,
                "last_scan_error": self._last_scan_error,
                "auto_apply_power_profile": self._auto_apply_power_profile,
                "runtime_mode": self._runtime_mode,
                "scenario": self._scenario,
                "scenario_cycles_left": self._scenario_cycles_left,
                "latest_timestamp": self._latest_snapshot.get("timestamp"),
            }

    def latest_payload(self, history_limit: int = 30, event_limit: int = 30, alert_limit: int = 10) -> Dict[str, Any]:
        with self._lock:
            service_health = {
                "running": self._running,
                "scan_interval_seconds": self.scan_interval_seconds,
                "last_scan_error": self._last_scan_error,
                "auto_apply_power_profile": self._auto_apply_power_profile,
                "runtime_mode": self._runtime_mode,
                "scenario": self._scenario,
                "supported_modes": sorted(VALID_RUNTIME_MODES),
                "supported_scenarios": sorted(VALID_SCENARIOS),
                "latest_timestamp": self._latest_snapshot.get("timestamp"),
            }
            return {
                "status": "ok",
                "mode": self._runtime_mode,
                "scenario": self._scenario,
                "timestamp": datetime.utcnow().isoformat(),
                "telemetry": dict(self._latest_snapshot),
                "decision": dict(self._latest_decision),
                "runtime_health": list(self._latest_runtime_health),
                "history": list(self._history)[-history_limit:],
                "events": list(self._events)[-event_limit:],
                "alerts": list(self._alerts)[-alert_limit:],
                "service_health": service_health,
            }

    def _scan_loop(self):
        while self._running:
            self.scan_now()
            time.sleep(self.scan_interval_seconds)

    def _scan_iteration(self):
        with self._lock:
            mode = self._runtime_mode
            scenario = self._scenario

        edge_snapshot = self._collect_snapshot()
        simulation_snapshot = self._collect_simulated_snapshot()

        if mode == "SIMULATION":
            snapshot = simulation_snapshot
        elif mode == "HYBRID":
            snapshot = self._blend_snapshots(edge_snapshot, simulation_snapshot)
        else:
            snapshot = edge_snapshot

        if scenario != "normal":
            snapshot = self._apply_scenario(snapshot, scenario)
            with self._lock:
                if self._scenario_cycles_left > 0:
                    self._scenario_cycles_left -= 1
                if self._scenario_cycles_left == 0:
                    self._scenario = "normal"
                    self._events.append(
                        {
                            "id": int(time.time() * 1000),
                            "type": "INFO",
                            "message": "scenario_completed normal",
                            "time": datetime.utcnow().strftime("%H:%M:%S"),
                        }
                    )
                    scenario = "normal"
        else:
            snapshot["fault_flag"] = False
            snapshot["grid_status"] = "healthy"

        snapshot["scan_mode"] = mode
        snapshot["scenario"] = scenario
        snapshot["industrial_metrics"] = self._to_industrial_metrics(snapshot)

        decision_input = self._to_decision_payload(snapshot)
        decision = self._decision_engine.generate_decision(decision_input)
        score = self._compute_optimization_score(snapshot)
        action = self._pick_power_profile(snapshot)
        if mode == "SIMULATION":
            applied_action = {"applied": False, "reason": "simulation_mode", "requested_profile": action}
        else:
            applied_action = self._apply_power_profile(action)
        runtime_health = self._build_runtime_health(snapshot, decision)

        record = {
            "timestamp": snapshot["timestamp"],
            "time": self._to_local_time(snapshot["timestamp"]),
            "optimization": score,
            "energy": round(snapshot.get("cpu_percent", 0), 2),
        }

        self._push_events_and_alerts(snapshot, score, action, applied_action)

        with self._lock:
            self._latest_snapshot = snapshot
            self._latest_decision = decision
            self._latest_runtime_health = runtime_health
            self._history.append(record)
            self._last_scan_error = None
            self._previous_snapshot = snapshot

    def _to_local_time(self, timestamp: str) -> str:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.utcnow()
        return dt.strftime("%H:%M:%S")

    def _collect_snapshot(self) -> Dict[str, Any]:
        if psutil is not None:
            return self._collect_with_psutil()

        if platform.system().lower().startswith("win"):
            return self._collect_windows_snapshot()

        return self._collect_fallback_snapshot()

    def _collect_with_psutil(self) -> Dict[str, Any]:
        battery = None
        try:
            battery = psutil.sensors_battery()
        except Exception:
            battery = None

        disk_root = "C:\\" if platform.system().lower().startswith("win") else "/"
        disk_usage = psutil.disk_usage(disk_root)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "cpu_percent": round(float(psutil.cpu_percent(interval=0.2)), 2),
            "memory_percent": round(float(psutil.virtual_memory().percent), 2),
            "disk_percent": round(float(disk_usage.percent), 2),
            "battery_percent": None if battery is None else round(float(battery.percent), 2),
            "power_plugged": None if battery is None else bool(battery.power_plugged),
            "process_count": len(psutil.pids()),
        }

    def _collect_windows_snapshot(self) -> Dict[str, Any]:
        script = r"""
$os = Get-CimInstance Win32_OperatingSystem
$cpuLoad = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" | Select-Object -First 1
$battery = Get-CimInstance Win32_Battery | Select-Object -First 1
$processCount = (Get-Process | Measure-Object).Count

$diskPercent = 0
if ($disk -and $disk.Size -gt 0) {
  $diskPercent = (($disk.Size - $disk.FreeSpace) / $disk.Size) * 100
}

$memoryPercent = 0
if ($os -and $os.TotalVisibleMemorySize -gt 0) {
  $memoryPercent = (($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100
}

$batteryPercent = $null
$powerPlugged = $null
if ($battery) {
  $batteryPercent = [double]$battery.EstimatedChargeRemaining
  $powerPlugged = @('2','6','7','8','9') -contains [string]$battery.BatteryStatus
}

[PSCustomObject]@{
  cpu_percent = [math]::Round([double]$cpuLoad, 2)
  memory_percent = [math]::Round([double]$memoryPercent, 2)
  disk_percent = [math]::Round([double]$diskPercent, 2)
  battery_percent = if($batteryPercent -eq $null){$null}else{[math]::Round($batteryPercent, 2)}
  power_plugged = $powerPlugged
  process_count = [int]$processCount
} | ConvertTo-Json -Compress
"""

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "Windows telemetry command failed")

        payload = json.loads(completed.stdout.strip())

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "cpu_percent": round(float(payload.get("cpu_percent", 0.0)), 2),
            "memory_percent": round(float(payload.get("memory_percent", 0.0)), 2),
            "disk_percent": round(float(payload.get("disk_percent", 0.0)), 2),
            "battery_percent": payload.get("battery_percent"),
            "power_plugged": payload.get("power_plugged"),
            "process_count": int(payload.get("process_count", 0)),
        }

    def _collect_fallback_snapshot(self) -> Dict[str, Any]:
        load = 0.0
        try:
            if hasattr(os, "getloadavg"):
                load = os.getloadavg()[0] * 25.0
        except Exception:
            load = 0.0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "cpu_percent": round(float(max(0.0, min(load, 100.0))), 2),
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "battery_percent": None,
            "power_plugged": None,
            "process_count": 0,
        }

    def _collect_simulated_snapshot(self) -> Dict[str, Any]:
        def bounded(value: float, delta: float, low: float, high: float) -> float:
            next_value = value + self._rng.uniform(-delta, delta)
            return max(low, min(high, next_value))

        self._sim_state["cpu_percent"] = bounded(float(self._sim_state["cpu_percent"]), 7.0, 8.0, 96.0)
        self._sim_state["memory_percent"] = bounded(float(self._sim_state["memory_percent"]), 4.0, 20.0, 96.0)
        self._sim_state["disk_percent"] = bounded(float(self._sim_state["disk_percent"]), 1.2, 20.0, 98.0)
        self._sim_state["process_count"] = int(
            max(40, min(600, int(self._sim_state["process_count"]) + self._rng.randint(-8, 12)))
        )

        battery = self._sim_state.get("battery_percent")
        plugged = bool(self._sim_state.get("power_plugged"))
        if battery is not None:
            if plugged:
                battery = min(100.0, float(battery) + self._rng.uniform(0.1, 0.7))
                if battery >= 96 and self._rng.random() < 0.2:
                    plugged = False
            else:
                battery = max(8.0, float(battery) - self._rng.uniform(0.2, 0.9))
                if battery <= 18 and self._rng.random() < 0.35:
                    plugged = True

            self._sim_state["battery_percent"] = round(float(battery), 2)
            self._sim_state["power_plugged"] = plugged

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": "digital-twin-edge",
            "platform": "Industrial Digital Twin",
            "cpu_percent": round(float(self._sim_state["cpu_percent"]), 2),
            "memory_percent": round(float(self._sim_state["memory_percent"]), 2),
            "disk_percent": round(float(self._sim_state["disk_percent"]), 2),
            "battery_percent": self._sim_state.get("battery_percent"),
            "power_plugged": self._sim_state.get("power_plugged"),
            "process_count": int(self._sim_state["process_count"]),
            "fault_flag": False,
            "grid_status": "healthy",
        }

    def _blend_snapshots(self, edge_snapshot: Dict[str, Any], simulation_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        def blend_number(edge_value: Any, sim_value: Any, edge_weight: float = 0.65) -> float:
            e = float(edge_value if edge_value is not None else sim_value if sim_value is not None else 0.0)
            s = float(sim_value if sim_value is not None else edge_value if edge_value is not None else 0.0)
            return e * edge_weight + s * (1.0 - edge_weight)

        battery_value = edge_snapshot.get("battery_percent")
        if battery_value is None:
            battery_value = simulation_snapshot.get("battery_percent")

        power_plugged = edge_snapshot.get("power_plugged")
        if power_plugged is None:
            power_plugged = simulation_snapshot.get("power_plugged")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": edge_snapshot.get("hostname", simulation_snapshot.get("hostname", "edge-hybrid")),
            "platform": f"Hybrid ({edge_snapshot.get('platform', 'edge')} + simulation)",
            "cpu_percent": round(blend_number(edge_snapshot.get("cpu_percent"), simulation_snapshot.get("cpu_percent")), 2),
            "memory_percent": round(
                blend_number(edge_snapshot.get("memory_percent"), simulation_snapshot.get("memory_percent")), 2
            ),
            "disk_percent": round(blend_number(edge_snapshot.get("disk_percent"), simulation_snapshot.get("disk_percent")), 2),
            "battery_percent": battery_value,
            "power_plugged": power_plugged,
            "process_count": int(
                round(blend_number(edge_snapshot.get("process_count"), simulation_snapshot.get("process_count")))
            ),
            "fault_flag": bool(edge_snapshot.get("fault_flag") or simulation_snapshot.get("fault_flag")),
            "grid_status": edge_snapshot.get("grid_status") or simulation_snapshot.get("grid_status") or "healthy",
        }

    def _apply_scenario(self, snapshot: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        scenario_snapshot = dict(snapshot)

        if scenario == "peak_load":
            scenario_snapshot["cpu_percent"] = max(92.0, float(scenario_snapshot.get("cpu_percent", 0.0)))
            scenario_snapshot["memory_percent"] = max(88.0, float(scenario_snapshot.get("memory_percent", 0.0)))
            scenario_snapshot["disk_percent"] = max(78.0, float(scenario_snapshot.get("disk_percent", 0.0)))
            scenario_snapshot["process_count"] = max(450, int(scenario_snapshot.get("process_count", 0)))
            scenario_snapshot["fault_flag"] = False
            scenario_snapshot["grid_status"] = "stressed"
            return scenario_snapshot

        if scenario == "low_load":
            scenario_snapshot["cpu_percent"] = min(18.0, float(scenario_snapshot.get("cpu_percent", 0.0)))
            scenario_snapshot["memory_percent"] = min(40.0, float(scenario_snapshot.get("memory_percent", 0.0)))
            scenario_snapshot["disk_percent"] = float(scenario_snapshot.get("disk_percent", 0.0))
            scenario_snapshot["process_count"] = max(30, min(120, int(scenario_snapshot.get("process_count", 0))))
            scenario_snapshot["fault_flag"] = False
            scenario_snapshot["grid_status"] = "relaxed"
            return scenario_snapshot

        if scenario == "grid_failure":
            scenario_snapshot["cpu_percent"] = max(72.0, float(scenario_snapshot.get("cpu_percent", 0.0)))
            scenario_snapshot["memory_percent"] = max(70.0, float(scenario_snapshot.get("memory_percent", 0.0)))
            scenario_snapshot["fault_flag"] = True
            scenario_snapshot["grid_status"] = "down"
            return scenario_snapshot

        scenario_snapshot["fault_flag"] = False
        scenario_snapshot["grid_status"] = "healthy"
        return scenario_snapshot

    def _to_industrial_metrics(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        cpu = float(snapshot.get("cpu_percent", 0.0))
        memory = float(snapshot.get("memory_percent", 0.0))
        disk = float(snapshot.get("disk_percent", 0.0))
        fault_flag = bool(snapshot.get("fault_flag", False))

        energy_usage_kwh = max(5.0, round(cpu * 0.85 + memory * 0.45 + disk * 0.25, 2))
        thermal_index_c = round(24.0 + cpu * 0.36 + (9.0 if fault_flag else 0.0), 2)
        grid_load = round(min(0.99, max(0.05, (cpu * 0.75 + memory * 0.25) / 100.0)), 2)

        hostname = str(snapshot.get("hostname", "edge-node"))
        site_id = f"plant-{(abs(hash(hostname)) % 7) + 1}"

        return {
            "site_id": site_id,
            "energy_usage_kwh": energy_usage_kwh,
            "thermal_index_c": thermal_index_c,
            "grid_load": grid_load,
            "grid_status": snapshot.get("grid_status", "healthy"),
            "fault_flag": fault_flag,
        }

    def _to_decision_payload(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.utcnow()
        industrial = snapshot.get("industrial_metrics", {})

        cpu = float(snapshot.get("cpu_percent", 0.0))
        memory = float(snapshot.get("memory_percent", 0.0))
        process_count = int(snapshot.get("process_count", 0))

        derived_temperature = float(industrial.get("thermal_index_c", max(25.0, min(85.0, 30.0 + cpu * 0.45))))
        derived_humidity = max(30.0, min(85.0, 35.0 + memory * 0.35))
        energy_kwh = float(industrial.get("energy_usage_kwh", max(1.0, round((cpu * 0.55) + (memory * 0.25), 2))))
        fault_flag = bool(snapshot.get("fault_flag", False))
        grid_status = str(snapshot.get("grid_status", "healthy"))

        state = "normal"
        if fault_flag or grid_status == "down":
            state = "grid_failure"
        elif cpu >= 85:
            state = "high_load"

        return {
            "building_id": 1,
            "temperature": round(derived_temperature, 2),
            "humidity": round(derived_humidity, 2),
            "occupancy": max(1, process_count),
            "day_of_week": now.weekday(),
            "hour": now.hour,
            "current_load": round(float(industrial.get("grid_load", cpu / 100.0)) * 100.0, 2),
            "energy_usage_kwh": energy_kwh,
            "state": state,
            "location": industrial.get("site_id", snapshot.get("hostname", "local-machine")),
            "fault_flag": fault_flag,
            "grid_status": grid_status,
        }

    def _compute_optimization_score(self, snapshot: Dict[str, Any]) -> float:
        industrial = snapshot.get("industrial_metrics", {})
        cpu = float(snapshot.get("cpu_percent", 0.0))
        memory = float(snapshot.get("memory_percent", 0.0))
        disk = float(snapshot.get("disk_percent", 0.0))
        grid_load = float(industrial.get("grid_load", min(1.0, max(0.0, cpu / 100.0))))
        fault_penalty = 25.0 if industrial.get("fault_flag") else 0.0
        battery = snapshot.get("battery_percent")

        battery_penalty = 0.0
        if isinstance(battery, (int, float)):
            battery_penalty = max(0.0, 100.0 - float(battery))

        score = 100.0 - (
            cpu * 0.3
            + memory * 0.25
            + disk * 0.1
            + (grid_load * 100.0) * 0.25
            + battery_penalty * 0.1
            + fault_penalty
        )
        return round(max(5.0, min(100.0, score)), 2)

    def _build_runtime_health(self, snapshot: Dict[str, Any], decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        industrial = snapshot.get("industrial_metrics", {})
        cpu = float(snapshot.get("cpu_percent", 0.0))
        memory = float(snapshot.get("memory_percent", 0.0))
        disk = float(snapshot.get("disk_percent", 0.0))
        battery = snapshot.get("battery_percent")
        grid_load = float(industrial.get("grid_load", min(1.0, max(0.0, cpu / 100.0))))
        grid_resilience = max(0.0, min(100.0, 100.0 - grid_load * 100.0))
        if industrial.get("fault_flag"):
            grid_resilience = max(0.0, grid_resilience - 35.0)

        stability = 90.0
        try:
            stability = float(
                decision.get("optimized_decision", {}).get("stability_score", 0.9) * 100
            )
        except Exception:
            stability = 90.0

        power_health = 100.0
        if isinstance(battery, (int, float)):
            power_health = float(battery)

        return [
            {"name": "CPU Headroom", "value": round(max(0.0, 100.0 - cpu), 2)},
            {"name": "Memory Headroom", "value": round(max(0.0, 100.0 - memory), 2)},
            {"name": "Grid Resilience", "value": round(grid_resilience, 2)},
            {"name": "Power Health", "value": round(max(0.0, min(100.0, power_health)), 2)},
            {"name": "Decision Stability", "value": round(max(0.0, min(100.0, stability)), 2)},
        ]

    def _pick_power_profile(self, snapshot: Dict[str, Any]) -> Optional[str]:
        cpu = float(snapshot.get("cpu_percent", 0.0))
        battery = snapshot.get("battery_percent")
        plugged = snapshot.get("power_plugged")
        if snapshot.get("fault_flag"):
            return "high_performance"

        if isinstance(battery, (int, float)) and not plugged and float(battery) <= 25:
            return "power_saver"
        if plugged and cpu >= 85:
            return "high_performance"
        return "balanced"

    def _apply_power_profile(self, profile: Optional[str]) -> Dict[str, Any]:
        if not profile:
            return {"applied": False}

        if not self._auto_apply_power_profile:
            return {"applied": False, "reason": "auto_apply_disabled", "requested_profile": profile}

        if not platform.system().lower().startswith("win"):
            return {"applied": False, "reason": "unsupported_platform", "requested_profile": profile}

        now = time.time()
        if self._last_applied_profile == profile and now - self._last_applied_ts < 120:
            return {"applied": False, "reason": "cooldown", "requested_profile": profile}

        profile_map = {
            "power_saver": "SCHEME_MAX",
            "balanced": "SCHEME_BALANCED",
            "high_performance": "SCHEME_MIN",
        }
        scheme = profile_map.get(profile)
        if not scheme:
            return {"applied": False, "reason": "unknown_profile", "requested_profile": profile}

        completed = subprocess.run(
            ["powercfg", "/SETACTIVE", scheme],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )

        if completed.returncode != 0:
            return {
                "applied": False,
                "reason": completed.stderr.strip() or "powercfg_failed",
                "requested_profile": profile,
            }

        self._last_applied_profile = profile
        self._last_applied_ts = now
        return {"applied": True, "profile": profile}

    def _push_events_and_alerts(
        self,
        snapshot: Dict[str, Any],
        score: float,
        action: Optional[str],
        applied_action: Dict[str, Any],
    ):
        timestamp = snapshot["timestamp"]
        time_label = self._to_local_time(timestamp)
        cpu = float(snapshot.get("cpu_percent", 0.0))
        memory = float(snapshot.get("memory_percent", 0.0))
        disk = float(snapshot.get("disk_percent", 0.0))
        mode = str(snapshot.get("scan_mode", "LIVE_EDGE"))
        scenario = str(snapshot.get("scenario", "normal"))
        industrial = snapshot.get("industrial_metrics", {})
        grid_load = float(industrial.get("grid_load", min(1.0, max(0.0, cpu / 100.0))))
        battery = snapshot.get("battery_percent")

        events_to_add: List[Dict[str, Any]] = [
            {
                "id": int(time.time() * 1000),
                "type": "INFO",
                "message": (
                    f"scan_complete mode={mode} scenario={scenario} cpu={cpu:.1f}% mem={memory:.1f}% grid={grid_load:.2f} score={score:.1f}"
                ),
                "time": time_label,
            }
        ]

        alerts_to_add: List[Dict[str, Any]] = []
        prev = self._previous_snapshot or {}

        if cpu >= 90 and float(prev.get("cpu_percent", 0.0)) < 90:
            alerts_to_add.append(
                {
                    "id": int(time.time() * 1000) + 1,
                    "severity": "critical",
                    "title": "CPU Pressure Critical",
                    "message": f"CPU usage reached {cpu:.1f}%",
                    "time": time_label,
                }
            )
            events_to_add.append(
                {
                    "id": int(time.time() * 1000) + 2,
                    "type": "ERROR",
                    "message": f"cpu_critical threshold_crossed {cpu:.1f}%",
                    "time": time_label,
                }
            )

        if memory >= 90 and float(prev.get("memory_percent", 0.0)) < 90:
            alerts_to_add.append(
                {
                    "id": int(time.time() * 1000) + 3,
                    "severity": "warning",
                    "title": "Memory Pressure High",
                    "message": f"Memory usage reached {memory:.1f}%",
                    "time": time_label,
                }
            )

        if isinstance(battery, (int, float)) and battery <= 20:
            alerts_to_add.append(
                {
                    "id": int(time.time() * 1000) + 4,
                    "severity": "warning",
                    "title": "Low Battery Detected",
                    "message": f"Battery at {float(battery):.1f}%",
                    "time": time_label,
                }
            )

        if industrial.get("fault_flag"):
            alerts_to_add.append(
                {
                    "id": int(time.time() * 1000) + 7,
                    "severity": "critical",
                    "title": "Grid Failure Simulation Active",
                    "message": "Grid status is DOWN - failover path engaged",
                    "time": time_label,
                }
            )
            events_to_add.append(
                {
                    "id": int(time.time() * 1000) + 8,
                    "type": "ERROR",
                    "message": "grid_failure detected; failover policy recommended",
                    "time": time_label,
                }
            )

        if applied_action.get("applied"):
            events_to_add.append(
                {
                    "id": int(time.time() * 1000) + 5,
                    "type": "SUCCESS",
                    "message": f"power_profile_applied {applied_action.get('profile')}",
                    "time": time_label,
                }
            )
        elif action:
            events_to_add.append(
                {
                    "id": int(time.time() * 1000) + 6,
                    "type": "WARN",
                    "message": f"power_profile_not_applied {action} ({applied_action.get('reason', 'n/a')})",
                    "time": time_label,
                }
            )

        with self._lock:
            for event in events_to_add:
                self._events.append(event)
            for alert in alerts_to_add:
                self._alerts.append(alert)


laptop_runtime_service = LaptopRuntimeService()

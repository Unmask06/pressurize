import axios from "axios";
import { reactive, ref } from "vue";
import type { components } from "./schema";

// Base URL: localhost for dev, api.xergiz.com for production
const API_BASE_URL = import.meta.env.DEV
  ? "http://localhost:8000"
  : "https://api.xergiz.com/pressurize";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Unit System Management
export type UnitSystem = string;
const currentUnitSystem = ref<UnitSystem>("imperial");

export interface UnitConfig {
  systems: string[];
  dimensions: Record<string, Record<string, string>>;
}

export const unitConfig = reactive<UnitConfig>({
  systems: ["imperial"],
  dimensions: {},
});

export function setUnitSystem(system: UnitSystem) {
  currentUnitSystem.value = system;
  // Update default header for axios requests
  apiClient.defaults.headers.common["x-unit-system"] = system;
}

export function getUnitSystem(): UnitSystem {
  return currentUnitSystem.value;
}

export async function fetchUnitConfig(): Promise<UnitConfig> {
  try {
    console.log("Fetching unit config from:", `${API_BASE_URL}/units/config`);
    const response = await apiClient.get<UnitConfig>("/units/config");
    console.log("Unit config response:", response.data);
    console.log("Systems:", response.data.systems);
    console.log("Dimensions keys:", Object.keys(response.data.dimensions));
    console.log(
      "Sample dimension (pressure):",
      response.data.dimensions["pressure"],
    );

    unitConfig.systems = response.data.systems;
    unitConfig.dimensions = response.data.dimensions;

    console.log("unitConfig after assignment:", {
      systems: unitConfig.systems,
      dimensionKeys: Object.keys(unitConfig.dimensions),
    });

    return response.data;
  } catch (error) {
    console.error("Error fetching unit config:", error);
    throw error;
  }
}

/**
 * Get unit string for a dimension in the current system.
 */
export function getUnit(dimension: string): string {
  if (dimension == null) {
    console.warn(`getUnit called with a null or undefined dimension.`);
    return "?";
  }
  const system = currentUnitSystem.value;
  // Normalize: lowercase, trim, and convert underscores to spaces
  // This handles variations like "Volumetric Flow Rate" and "volumetric_flowrate"
  const dimKey = dimension.toLowerCase().trim().replace(/_/g, " ");

  if (!unitConfig.dimensions[dimKey]) {
    console.warn(`Dimension not found: "${dimension}" (key: "${dimKey}")`);
    console.warn(
      `Available dimensions: "${Object.keys(unitConfig.dimensions).join(", ")}"`,
    );
    return "?";
  }

  const unit = unitConfig.dimensions[dimKey][system];
  if (!unit) {
    console.warn(
      `Unit not found for dimension: "${dimKey}", system: "${system}"`,
    );
    return "?";
  }

  return unit;
}

// Initialize with default header
apiClient.defaults.headers.common["x-unit-system"] = currentUnitSystem.value;

// Streaming message types for Server-Sent Events
export interface StreamingChunk {
  type: "chunk";
  rows: SimulationRow[];
  total_rows: number;
}

export interface StreamingComplete {
  type: "complete";
  peak_flow: number;
  final_pressure: number;
  equilibrium_time: number;
  total_mass: number;
  completed: boolean;
}

export interface StreamingError {
  type: "error";
  message: string;
}

// Type aliases for API schema types
export type SimulationRow = components["schemas"]["SimulationResultPoint"];
export type SimulationRequest = components["schemas"]["SimulationRequest"];
export type PropertiesRequest = components["schemas"]["PropertiesRequest"];
export type PropertiesResponse = components["schemas"]["PropertiesResponse"];

export type StreamingMessage =
  | StreamingChunk
  | StreamingComplete
  | StreamingError;

export interface StreamCallbacks {
  onChunk: (rows: SimulationRow[], totalRows: number) => void;
  onComplete: (kpis: Omit<StreamingComplete, "type">) => void;
  onError: (message: string) => void;
}

/**
 * Stream simulation results using Server-Sent Events.
 * Results arrive in 100-row batches for progressive chart updates.
 */
export async function streamSimulation(
  params: Record<string, unknown>,
  callbacks: StreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/simulate/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-unit-system": currentUnitSystem.value,
    },
    body: JSON.stringify(params),
    signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || ""; // Keep incomplete message in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.slice(6);
          try {
            const msg: StreamingMessage = JSON.parse(jsonStr);
            if (msg.type === "chunk") {
              callbacks.onChunk(msg.rows, msg.total_rows);
            } else if (msg.type === "complete") {
              callbacks.onComplete({
                peak_flow: msg.peak_flow,
                final_pressure: msg.final_pressure,
                equilibrium_time: msg.equilibrium_time,
                total_mass: msg.total_mass,
                completed: msg.completed,
              });
            } else if (msg.type === "error") {
              callbacks.onError(msg.message);
            }
          } catch (e) {
            console.error("Failed to parse SSE message:", e);
          }
        }
      }
    }
  } catch (e: any) {
    // Re-throw AbortError so the caller can detect cancellation
    if (e.name === "AbortError") {
      throw e;
    }
    console.error("Stream reading error:", e);
    throw e;
  } finally {
    reader.releaseLock();
  }
}

export default apiClient;

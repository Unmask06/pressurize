import Dexie, { type Table } from "dexie";

/**
 * Simulation history entry stored in IndexedDB.
 * Contains all simulation parameters and metadata.
 */
export interface SimulationHistoryEntry {
  id?: number;
  timestamp: number;
  params: {
    mode: string;
    p_up: number;
    upstream_volume: number;
    upstream_temp: number;
    p_down_init: number;
    downstream_volume: number;
    downstream_temp: number;
    valve_id: number;
    opening_time: number;
    molar_mass: number;
    z_factor: number;
    k_ratio: number;
    discharge_coeff: number;
    valve_action: string;
    opening_mode: string;
    k_curve: number;
    dt: number;
    property_mode: string;
    composition?: string;
  };
  label?: string;
}

/**
 * Dexie database for simulation history.
 */
class SimulationHistoryDatabase extends Dexie {
  history!: Table<SimulationHistoryEntry, number>;

  constructor() {
    super("SimulationHistoryDB");
    this.version(1).stores({
      history: "++id, timestamp",
    });
  }
}

const db = new SimulationHistoryDatabase();

/**
 * Save a simulation to history.
 * Automatically keeps only the last 10 simulations.
 */
export async function saveSimulation(
  params: Record<string, any>,
  label?: string,
): Promise<void> {
  try {
    // Add new entry
    await db.history.add({
      timestamp: Date.now(),
      params: {
        mode: params.mode,
        p_up: params.p_up,
        upstream_volume: params.upstream_volume,
        upstream_temp: params.upstream_temp,
        p_down_init: params.p_down_init,
        downstream_volume: params.downstream_volume,
        downstream_temp: params.downstream_temp,
        valve_id: params.valve_id,
        opening_time: params.opening_time,
        molar_mass: params.molar_mass,
        z_factor: params.z_factor,
        k_ratio: params.k_ratio,
        discharge_coeff: params.discharge_coeff,
        valve_action: params.valve_action,
        opening_mode: params.opening_mode,
        k_curve: params.k_curve,
        dt: params.dt,
        property_mode: params.property_mode,
        composition: params.composition,
      },
      label,
    });

    // Keep only last 10 entries
    const allEntries = await db.history
      .orderBy("timestamp")
      .reverse()
      .toArray();

    if (allEntries.length > 10) {
      const toDelete = allEntries.slice(10);
      const idsToDelete = toDelete
        .map((entry) => entry.id)
        .filter((id): id is number => id !== undefined);
      await db.history.bulkDelete(idsToDelete);
    }
  } catch (error) {
    console.error("Failed to save simulation to history:", error);
    throw error;
  }
}

/**
 * Get all simulation history, ordered by timestamp (newest first).
 */
export async function getSimulationHistory(): Promise<
  SimulationHistoryEntry[]
> {
  try {
    return await db.history.orderBy("timestamp").reverse().toArray();
  } catch (error) {
    console.error("Failed to get simulation history:", error);
    return [];
  }
}

/**
 * Delete a single simulation from history.
 */
export async function deleteSimulation(id: number): Promise<void> {
  try {
    await db.history.delete(id);
  } catch (error) {
    console.error("Failed to delete simulation from history:", error);
    throw error;
  }
}

/**
 * Clear all simulation history.
 */
export async function clearHistory(): Promise<void> {
  try {
    await db.history.clear();
  } catch (error) {
    console.error("Failed to clear simulation history:", error);
    throw error;
  }
}

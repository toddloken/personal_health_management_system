/**
 * @fileoverview
 *
 * App component types
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import { DatabaseDataProcessor } from '../services/DatabaseDataProcessor';
import { ApiClient } from '../api/ApiClient';

export interface AppState {
  activeTab: string;
  apiClient: ApiClient;
  dataProcessor: DatabaseDataProcessor | null;
}

export interface DatabaseRecord {
  date: string;
  dynamic_recovery?: number | null;
  heart_rate?: number | null;
  heart_rate_variability?: number | null;
  id?: number;
  movement?: number | null;
  raw_notes?: string | null;
  resting_heart_rate?: number | null;
  sleep_debt?: number | null;
  sleep_index?: number | null;
  steps?: number | null;
  stress_rhythm?: number | null;
  ud_a?: number | null;
  ud_mj?: number | null;
  ud_narc?: number | null;
  ud_sd?: number | null;
  ud_t?: number | null;
  vo2_max?: number | null;
  [key: string]: string | number | boolean | null | undefined;
}

export interface DateRange {
  endDate: string;
  startDate: string;
}

export interface InputMode {
  mode: 'daily' | 'weekly';
}

export interface TabConfig {
  component: React.ComponentType;
  id: string;
  label: string;
}

export interface TabDefinition {
  component: React.ComponentType<any>;
  id: string;
  label: string;
  requiresProcessor: boolean;
}

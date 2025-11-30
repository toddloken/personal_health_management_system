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
  dynamic_recovery?: number;
  heart_rate?: number;
  heart_rate_variability?: number;
  id?: number;
  movement?: number;
  raw_notes?: string;
  resting_heart_rate?: number;
  sleep_debt?: number;
  sleep_index?: number;
  steps?: number;
  stress_rhythm?: number;
  ud_a?: number;
  ud_mj?: number;
  ud_narc?: number;
  ud_sd?: number;
  ud_t?: number;
  vo2_max?: number;
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

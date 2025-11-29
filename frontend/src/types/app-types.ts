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

export interface AppState {
  activeTab: string;
  dataProcessor: DatabaseDataProcessor | null;
}

export interface DatabaseRecord {
  id?: number;
  date: string;
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
  component: React.ComponentType<{ dataProcessor?: DatabaseDataProcessor }>;
  id: string;
  label: string;
  requiresProcessor: boolean;
}

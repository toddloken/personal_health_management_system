/**
 * @fileoverview
 *
 * Core application types and interfaces
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

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

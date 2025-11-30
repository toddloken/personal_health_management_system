/**
 * @fileoverview
 *
 * Input tab component types and interfaces
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import { ApiClient } from '../api/ApiClient';

export interface InputTabProps {
  apiClient: ApiClient;
}

export interface InputTabState {
  date: string;
  dynamic_recovery: string;
  errorMessage: string;
  heart_rate: string;
  heart_rate_variability: string;
  isSubmitting: boolean;
  movement: string;
  raw_notes: string;
  resting_heart_rate: string;
  sleep_debt: string;
  sleep_index: string;
  steps: string;
  stress_rhythm: string;
  successMessage: string;
  ud_a: string;
  ud_mj: string;
  ud_narc: string;
  ud_sd: string;
  ud_t: string;
  vo2_max: string;
}

export interface PersonalDataRecord {
  date: string;
  dynamic_recovery?: number | null;
  heart_rate?: number | null;
  heart_rate_variability?: number | null;
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
}
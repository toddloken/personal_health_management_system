/**
 * @fileoverview
 *
 * Output tab component types
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import { DatabaseRecord } from './app-types.ts';
import {ApiClient} from "../api/ApiClient.ts";

export interface OutputTabProps {
  apiClient: ApiClient;
}

export interface OutputTabState {
  endDate: string;
  records: DatabaseRecord[];
  selectedStatsColumns: Set<string>;
  sortColumn: string | null;
  sortDirection: 'asc' | 'desc';
  startDate: string;
}
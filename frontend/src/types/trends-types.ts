/**
 * @fileoverview
 *
 * Trends tab component types
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import { DatabaseDataProcessor } from '../services/DatabaseDataProcessor';

export interface TrendsTabProps {
  dataProcessor?: DatabaseDataProcessor;
}

export interface TrendsTabState {
  count: number;
  loaded: boolean;
}

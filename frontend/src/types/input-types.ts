/**
 * @fileoverview
 *
 * Input tab component types
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import { DatabaseDataProcessor } from '../services/DatabaseDataProcessor';

export interface InputTabProps {
  dataProcessor?: DatabaseDataProcessor;
}

export interface InputTabState {
  date: string;
  mode: 'daily' | 'weekly';
}

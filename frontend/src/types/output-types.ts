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

import { DatabaseDataProcessor } from '../services/DatabaseDataProcessor';
import { DatabaseRecord } from '../types/app-types';

export interface OutputTabProps {
  dataProcessor?: DatabaseDataProcessor;
}

export interface OutputTabState {
  endDate: string;
  records: DatabaseRecord[];
  startDate: string;
}

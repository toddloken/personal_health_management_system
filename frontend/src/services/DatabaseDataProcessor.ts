/**
 * @fileoverview
 *
 * Database data processor service layer
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import { ApiClient } from '../api/ApiClient';
import { DatabaseRecord, DateRange } from '../types/app-types';

export class DatabaseDataProcessor {
  private apiClient: ApiClient;
  private tableName: string;

  constructor(apiClient: ApiClient, tableName: string = 'personal_data') {
    this.apiClient = apiClient;
    this.tableName = tableName;
  }

  async createRecord(record: DatabaseRecord): Promise<boolean> {
    const response = await this.apiClient.create(this.tableName, record);
    return response.success;
  }

  async deleteRecord(criteria: Record<string, unknown>): Promise<boolean> {
    const response = await this.apiClient.delete(this.tableName, criteria);
    return response.success;
  }

  async getRecordsByDateRange(dateRange: DateRange): Promise<DatabaseRecord[]> {
    const criteria = {
      date: {
        gte: dateRange.startDate,
        lte: dateRange.endDate,
      },
    };

    const response = await this.apiClient.read({
      table_name: this.tableName,
      criteria,
    });

    return response.success ? response.data : [];
  }

  async readRecords(criteria?: Record<string, unknown>, limit?: number): Promise<DatabaseRecord[]> {
    const response = await this.apiClient.read({
      table_name: this.tableName,
      criteria,
      limit,
    });

    return response.success ? response.data : [];
  }

  async updateRecord(data: DatabaseRecord, criteria: Record<string, unknown>): Promise<boolean> {
    const response = await this.apiClient.update(this.tableName, data, criteria);
    return response.success;
  }
}

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
import { DateRangeRequest } from '../types/api-types';
import { DatabaseRecord } from '../types/app-types';

export class DatabaseDataProcessor {
  private apiClient: ApiClient;
  private readonly tableName: string;

  constructor(apiClient: ApiClient, tableName: string = 'personal_data') {
    this.apiClient = apiClient;
    this.tableName = tableName;
  }

  public async createRecord(record: DatabaseRecord): Promise<boolean> {
    const response = await this.apiClient.create(this.tableName, record);
    return response.success;
  }

  public async deleteRecord(criteria: Record<string, unknown>): Promise<boolean> {
    const response = await this.apiClient.delete(this.tableName, criteria);
    return response.success;
  }

  public async getRecordsByDateRange(params: {
    endDate: string;
    startDate: string;
  }): Promise<DatabaseRecord[]> {
    const request: DateRangeRequest = {
      end_date: params.endDate,
      start_date: params.startDate,
      table_name: this.tableName,
    };

    const response = await this.apiClient.queryData(request);

    if (!response.success || !response.data) {
      console.error('Failed to fetch records:', response.error);
      return [];
    }

    return response.data.data as DatabaseRecord[];
  }

  public async readRecords(criteria?: Record<string, unknown>, limit?: number): Promise<DatabaseRecord[]> {
    const response = await this.apiClient.read({
      table_name: this.tableName,
      criteria,
      limit,
    });

    return response.success ? response.data : [];
  }

  public async updateRecord(data: DatabaseRecord, criteria: Record<string, unknown>): Promise<boolean> {
    const response = await this.apiClient.update(this.tableName, data, criteria);
    return response.success;
  }
}
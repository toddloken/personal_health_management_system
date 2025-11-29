/**
 * @fileoverview
 *
 * API client for database operations
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import {ApiConfig, ApiResponse, DataQueryResponse, DateRangeRequest, QueryParams} from '../types/api-types';
import { DatabaseRecord } from '../types/app-types';

export class ApiClient {
  private config: ApiConfig;

  constructor(config: ApiConfig) {
    this.config = config;
  }

  public async create(tableName: string, data: DatabaseRecord): Promise<ApiResponse<boolean>> {
    return this.request('/api/create', 'POST', { table_name: tableName, data });
  }

  public async delete(tableName: string, criteria: Record<string, unknown>): Promise<ApiResponse<boolean>> {
    return this.request('/api/delete', 'POST', { table_name: tableName, criteria });
  }

  public async queryData(params: DateRangeRequest): Promise<ApiResponse<DataQueryResponse>> {
    return this.request<DataQueryResponse>('/api/data/query', 'POST', {
      table_name: params.table_name || 'personal_data',
      start_date: params.start_date,
      end_date: params.end_date,
    });
  }

  public async read(params: QueryParams): Promise<ApiResponse<DatabaseRecord[]>> {
    return this.request('/api/read', 'POST', params);
  }

  private async request<T>(endpoint: string, method: string, body?: Record<string, unknown>): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      const data = await response.json();
      return {
        success: response.ok,
        data,
        error: response.ok ? undefined : data.message || 'Request failed',
      };
    } catch (error) {
      return {
        success: false,
        data: {} as T,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  public async update(tableName: string, data: DatabaseRecord, criteria: Record<string, unknown>): Promise<ApiResponse<boolean>> {
    return this.request('/api/update', 'POST', { table_name: tableName, data, criteria });
  }
}

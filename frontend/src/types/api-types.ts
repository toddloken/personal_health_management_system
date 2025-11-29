/**
 * @fileoverview
 *
 * API client types and interfaces
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  success: boolean;
}

export interface QueryParams extends Record<string, unknown> {
  columns?: string[];
  criteria?: Record<string, unknown>;
  limit?: number;
  table_name?: string;
}

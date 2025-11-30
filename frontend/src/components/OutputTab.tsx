/**
 * @fileoverview
 *
 * Output tab component with date range filtering
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { DatabaseRecord } from '../types/app-types';
import {OutputTabProps, OutputTabState} from "../types/output-types.ts";

export class OutputTab extends React.Component<OutputTabProps, OutputTabState> {
  constructor(props: OutputTabProps) {
    super(props);
    const today = new Date().toISOString().split('T')[0];
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    this.state = {
      endDate: today,
      records: [],
      selectedStatsColumns: new Set(),
      sortColumn: null,
      sortDirection: 'asc',
      startDate: weekAgo,
    };
  }

  private calculateStats(columnName: string): { avg: number; stdDev: number; min: number; max: number } | null {
    const values = this.state.records
        .map(r => r[columnName])
        .filter(v => typeof v === 'number') as number[];

    if (values.length === 0) return null;

    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    const squaredDiffs = values.map(val => Math.pow(val - avg, 2));
    const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / values.length;
    const stdDev = Math.sqrt(variance);

    return { avg, stdDev, min, max };
  }

  private columnDisplayNames: Record<string, string> = {
    pdate: 'Date',
    sleep_index: 'Sleep Index',
    sleep_debt: 'Sleep Debt (Minutes)',
    dynamic_recovery: 'Dynamic Recovery',
    movement: 'Movement Index',
    steps: 'Steps',
    stress_rhythm: 'Stress Rhythm',
    heart_rate: 'Daily Heart Rate',
    heart_rate_variability: 'Heart Rate Variability',
    resting_heart_rate: 'Resting Heart Rate',
    vo2_max: 'VO2 Max',
    ud_t: 'Travel',
    ud_a: 'A',
    ud_mj: 'MJ',
    ud_sd: 'SD',
    ud_narc: 'Pain',
    raw_notes: 'Notes'
  };

  public async componentDidMount(): Promise<void> {
    await this.loadData();
  }

  private getDisplayName(columnName: string): string {
    return this.columnDisplayNames[columnName] || columnName;
  }

  public handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    this.setState({ endDate: e.target.value });
  };

  public handleFilter = async (): Promise<void> => {
    await this.loadData();
  };

  public handleSort = (column: string): void => {
    const { sortColumn, sortDirection } = this.state;
    const newDirection = sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';

    this.setState({
      sortColumn: column,
      sortDirection: newDirection,
    }, () => {
      this.sortRecords();
    });
  };

  public handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    this.setState({ startDate: e.target.value });
  };

  public async loadData(): Promise<void> {
    const result = await this.props.apiClient.queryData({
      table_name: 'personal_data',
      start_date: this.state.startDate,
      end_date: this.state.endDate,
    });

    if (result.success && result.data.data) {
      this.setState({ records: result.data.data as DatabaseRecord[] }, () => {
        this.updateStatsColumns();
      });
    } else {
      console.error('Failed to load data:', result.error);
      this.setState({ records: [] });
    }
  }

  public render(): React.ReactNode {
    const { records, selectedStatsColumns } = this.state;
    const columns = records.length > 0 ? Object.keys(records[0]) : [];

    return (
        <div className="output-container">
          <h1>Daily Output</h1>
          <div className="filter-controls">
            <div className="date-filter">
              <label htmlFor="startDate">Start Date:</label>
              <input
                  type="date"
                  id="startDate"
                  value={this.state.startDate}
                  onChange={this.handleStartDateChange}
              />
            </div>
            <div className="date-filter">
              <label htmlFor="endDate">End Date:</label>
              <input
                  type="date"
                  id="endDate"
                  value={this.state.endDate}
                  onChange={this.handleEndDateChange}
              />
            </div>
            <button onClick={this.handleFilter}>Filter</button>
          </div>

          <div className="records-table">
            {records.length > 0 ? (
                <table>
                  <thead>
                  <tr>
                    {columns.map((col) => (
                        <th
                            key={col}
                            onClick={() => this.handleSort(col)}
                            style={{ cursor: 'pointer' }}
                        >
                          {this.getDisplayName(col)}
                          {this.state.sortColumn === col && (
                              <span>{this.state.sortDirection === 'asc' ? ' ▲' : ' ▼'}</span>
                          )}
                        </th>
                    ))}
                  </tr>
                  </thead>
                  <tbody>
                  {records.map((record, index) => (
                      <tr key={index}>
                        {columns.map((col) => (
                            <td key={col}>{String(record[col] ?? '')}</td>
                        ))}
                      </tr>
                  ))}
                  </tbody>
                </table>
            ) : (
                <p>No records found for the selected date range.</p>
            )}
          </div>

          {selectedStatsColumns.size > 0 && (
              <div className="statistics-section" style={{ marginTop: '2rem' }}>
                <h2>Column Statistics</h2>
                <table>
                  <thead>
                  <tr>
                    {columns.map((col, index) => (
                        <th key={col}>
                          {index === 0 ? 'Metric' : this.getDisplayName(col)}
                        </th>
                    ))}
                  </tr>
                  </thead>
                  <tbody>
                  <tr>
                    <td style={{ fontWeight: 'bold', background: '#f5f5f5' }}>Average</td>
                    {columns.slice(1).map((col) => {
                      if (!selectedStatsColumns.has(col)) {
                        return <td key={col}></td>;
                      }
                      const stats = this.calculateStats(col);
                      return <td key={col}>{stats ? stats.avg.toFixed(2) : 'N/A'}</td>;
                    })}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 'bold', background: '#f5f5f5' }}>Stand Devn</td>
                    {columns.slice(1).map((col) => {
                      if (!selectedStatsColumns.has(col)) {
                        return <td key={col}></td>;
                      }
                      const stats = this.calculateStats(col);
                      return <td key={col}>{stats ? stats.stdDev.toFixed(2) : 'N/A'}</td>;
                    })}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 'bold', background: '#f5f5f5' }}>Min</td>
                    {columns.slice(1).map((col) => {
                      if (!selectedStatsColumns.has(col)) {
                        return <td key={col}></td>;
                      }
                      const stats = this.calculateStats(col);
                      return <td key={col}>{stats ? stats.min.toFixed(2) : 'N/A'}</td>;
                    })}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 'bold', background: '#f5f5f5' }}>Max</td>
                    {columns.slice(1).map((col) => {
                      if (!selectedStatsColumns.has(col)) {
                        return <td key={col}></td>;
                      }
                      const stats = this.calculateStats(col);
                      return <td key={col}>{stats ? stats.max.toFixed(2) : 'N/A'}</td>;
                    })}
                  </tr>
                  </tbody>
                </table>
              </div>
          )}
        </div>
    );
  }

  private sortRecords(): void {
    const { records, sortColumn, sortDirection } = this.state;
    if (!sortColumn) return;

    const sortedRecords = [...records].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      const comparison = aVal < bVal ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });

    this.setState({ records: sortedRecords });
  }

  private updateStatsColumns(): void {
    if (this.state.records.length === 0) return;

    const columns = Object.keys(this.state.records[0]);
    const statsColumns = columns.filter(col =>
        col !== 'date' && col !== 'notes'
    );

    this.setState({ selectedStatsColumns: new Set(statsColumns) });
  }

}
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
import { ApiClient } from '../api/ApiClient';
import { DatabaseRecord } from '../types/app-types';

interface OutputTabProps {
  apiClient: ApiClient;
}

interface OutputTabState {
  endDate: string;
  records: DatabaseRecord[];
  startDate: string;
}

export class OutputTab extends React.Component<OutputTabProps, OutputTabState> {
  constructor(props: OutputTabProps) {
    super(props);
    const today = new Date().toISOString().split('T')[0];
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    this.state = {
      endDate: today,
      records: [],
      startDate: weekAgo,
    };
  }

  public async componentDidMount(): Promise<void> {
    await this.loadData();
  }

  public handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    this.setState({ endDate: e.target.value });
  };

  public handleFilter = async (): Promise<void> => {
    await this.loadData();
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
      this.setState({ records: result.data.data as DatabaseRecord[] });
    } else {
      console.error('Failed to load data:', result.error);
      this.setState({ records: [] });
    }
  }

  public render(): React.ReactNode {
    const { records } = this.state;
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
                        <th key={col}>{col}</th>
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
        </div>
    );
  }
}
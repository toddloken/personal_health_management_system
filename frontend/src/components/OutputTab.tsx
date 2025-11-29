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
import { OutputTabProps, OutputTabState } from '../types/output-types';

export class OutputTab extends React.Component<OutputTabProps, OutputTabState> {
  constructor(props: OutputTabProps) {
    super(props);
    const today = new Date().toISOString().split('T')[0];
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    this.state = {
      startDate: weekAgo,
      endDate: today,
      records: [],
    };
  }

  public async componentDidMount(): Promise<void> {
    await this.loadData();
  }

  public handleFilter = async (): Promise<void> => {
    await this.loadData();
  };

  public async loadData(): Promise<void> {
    if (!this.props.dataProcessor) {
      return;
    }
    const records = await this.props.dataProcessor.getRecordsByDateRange({
      startDate: this.state.startDate,
      endDate: this.state.endDate,
    });
    this.setState({ records });
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
                  onChange={(e) => this.setState({ startDate: e.target.value })}
              />
            </div>
            <div className="date-filter">
              <label htmlFor="endDate">End Date:</label>
              <input
                  type="date"
                  id="endDate"
                  value={this.state.endDate}
                  onChange={(e) => this.setState({ endDate: e.target.value })}
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

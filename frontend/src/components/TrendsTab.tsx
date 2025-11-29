/**
 * @fileoverview
 *
 * Basic trends and insights tab component
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { TrendsTabProps, TrendsTabState } from '../types/trends-types';

export class TrendsTab extends React.Component<TrendsTabProps, TrendsTabState> {
  constructor(props: TrendsTabProps) {
    super(props);
    this.state = {
      count: 0,
      loaded: false,
    };
  }

  public async componentDidMount(): Promise<void> {
    await this.loadMetrics();
  }

  public async loadMetrics(): Promise<void> {
    if (!this.props.dataProcessor) {
      return;
    }
    const records = await this.props.dataProcessor.readRecords();
    this.setState({
      count: records.length,
      loaded: true,
    });
  }

  public render(): React.ReactNode {
    return (
      <div className="trends-container">
        <h1>Basic Trends and Insights</h1>
        {this.state.loaded ? (
          <div className="metrics">
            <div className="metric">
              <span className="metric-label">Total Records:</span>
              <span className="metric-value">{this.state.count}</span>
            </div>
          </div>
        ) : (
          <p>Loading...</p>
        )}
      </div>
    );
  }
}

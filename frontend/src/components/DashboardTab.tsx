/**
 * @fileoverview
 *
 * Dashboard tab component
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { DatabaseDataProcessor } from '../services/DatabaseDataProcessor';

export class DashboardTab extends React.Component<{ dataProcessor?: DatabaseDataProcessor }> {
  public render(): React.ReactNode {
    return (
      <div className="dashboard-container">
        <h1>Dashboard</h1>
        <div className="dashboard-content">
          <p>Welcome to PythonPHMS - Public Health Management System</p>
        </div>
      </div>
    );
  }
}

/**
 * @fileoverview
 *
 * Settings tab component
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { SettingsTabState } from '../types/settings-types';
import { DatabaseDataProcessor } from '../services/DatabaseDataProcessor';

export class SettingsTab extends React.Component<{ dataProcessor?: DatabaseDataProcessor }, SettingsTabState> {
  constructor(props: { dataProcessor?: DatabaseDataProcessor }) {
    super(props);
    this.state = {
      apiUrl: 'http://localhost:8000',
      tableName: 'personal_data',
    };
  }

  handleSave = (): void => {
    localStorage.setItem('apiUrl', this.state.apiUrl);
    localStorage.setItem('tableName', this.state.tableName);
  };

  render(): React.ReactNode {
    return (
      <div className="settings-container">
        <h1>Settings</h1>
        <div className="settings-form">
          <div className="form-group">
            <label htmlFor="apiUrl">API URL:</label>
            <input
              type="text"
              id="apiUrl"
              value={this.state.apiUrl}
              onChange={(e) => this.setState({ apiUrl: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="tableName">Table Name:</label>
            <input
              type="text"
              id="tableName"
              value={this.state.tableName}
              onChange={(e) => this.setState({ tableName: e.target.value })}
            />
          </div>
          <button onClick={this.handleSave}>Save Settings</button>
        </div>
      </div>
    );
  }
}

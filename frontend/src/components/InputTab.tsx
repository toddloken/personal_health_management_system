/**
 * @fileoverview
 *
 * Input tab component for daily or weekly data entry
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { InputTabProps, InputTabState } from '../types/input-types';
import {DatabaseRecord} from "../types/app-types.ts";

export class InputTab extends React.Component<InputTabProps, InputTabState> {
  constructor(props: InputTabProps) {
    super(props);
    this.state = {
      mode: 'daily',
      date: new Date().toISOString().split('T')[0],
    };
  }

  public handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    this.setState({ mode: e.target.value as 'daily' | 'weekly' });
  };

  public handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!this.props.dataProcessor) {
      return;
    }
    const formData = new FormData(e.currentTarget);
    const record: DatabaseRecord = {
      date: this.state.date,
      mode: this.state.mode,
    };

    formData.forEach((value, key) => {
      record[key] = value.toString();
    });

    await this.props.dataProcessor.createRecord(record);
  };

  public render(): React.ReactNode {
    return (
      <div className="input-container">
        <h1>Input Data</h1>
        <div className="mode-selector">
          <label htmlFor="mode">Mode:</label>
          <select id="mode" value={this.state.mode} onChange={this.handleModeChange}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>
        <form onSubmit={this.handleSubmit}>
          <div className="form-group">
            <label htmlFor="date">Date:</label>
            <input
              type="date"
              id="date"
              value={this.state.date}
              onChange={(e) => this.setState({ date: e.target.value })}
              required
            />
          </div>
          <button type="submit">Submit</button>
        </form>
      </div>
    );
  }
}

/**
 * @fileoverview
 *
 * Input tab component for data entry
 *
 * Provides form interface for entering personal health data into the database.
 * Uses ApiClient for backend communication and follows class-based React patterns.
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { InputTabProps, InputTabState, PersonalDataRecord } from '../types/input-types';
import '../styles/InputTab.css';

export class InputTab extends React.Component<InputTabProps, InputTabState> {
  private readonly columnDisplayNames: Record<string, string> = {
    date: 'Date',
    dynamic_recovery: 'Dynamic Recovery',
    heart_rate: 'Heart Rate',
    heart_rate_variability: 'Heart Rate Variability',
    movement: 'Movement',
    raw_notes: 'Raw Notes',
    resting_heart_rate: 'Resting Heart Rate',
    sleep_debt: 'Sleep Debt',
    sleep_index: 'Sleep Index',
    steps: 'Steps',
    stress_rhythm: 'Stress Rhythm',
    ud_a: 'UD A',
    ud_mj: 'UD MJ',
    ud_narc: 'UD Narc',
    ud_sd: 'UD SD',
    ud_t: 'UD T',
    vo2_max: 'VO2 Max',
  };

  constructor(props: InputTabProps) {
    super(props);
    this.state = this.getInitialState();
  }

  private buildRecordFromState(): PersonalDataRecord {
    const parseNumber = (value: string): number | null => {
      const trimmed = value.trim();
      if (trimmed === '') return null;
      const parsed = parseFloat(trimmed);
      return isNaN(parsed) ? null : parsed;
    };

    return {
      date: this.state.date,
      dynamic_recovery: parseNumber(this.state.dynamic_recovery),
      heart_rate: parseNumber(this.state.heart_rate),
      heart_rate_variability: parseNumber(this.state.heart_rate_variability),
      movement: parseNumber(this.state.movement),
      raw_notes: this.state.raw_notes.trim() || null,
      resting_heart_rate: parseNumber(this.state.resting_heart_rate),
      sleep_debt: parseNumber(this.state.sleep_debt),
      sleep_index: parseNumber(this.state.sleep_index),
      steps: parseNumber(this.state.steps),
      stress_rhythm: parseNumber(this.state.stress_rhythm),
      ud_a: parseNumber(this.state.ud_a),
      ud_mj: parseNumber(this.state.ud_mj),
      ud_narc: parseNumber(this.state.ud_narc),
      ud_sd: parseNumber(this.state.ud_sd),
      ud_t: parseNumber(this.state.ud_t),
      vo2_max: parseNumber(this.state.vo2_max),
    };
  }

  private clearMessages(): void {
    this.setState({
      errorMessage: '',
      successMessage: '',
    });
  }

  private formatDateForInput(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private getInitialState(): InputTabState {
    return {
      date: this.formatDateForInput(new Date()),
      dynamic_recovery: '',
      errorMessage: '',
      heart_rate: '',
      heart_rate_variability: '',
      isSubmitting: false,
      movement: '',
      raw_notes: '',
      resting_heart_rate: '',
      sleep_debt: '',
      sleep_index: '',
      steps: '',
      stress_rhythm: '',
      successMessage: '',
      ud_a: '',
      ud_mj: '',
      ud_narc: '',
      ud_sd: '',
      ud_t: '',
      vo2_max: '',
    };
  }

  private handleClear = (): void => {
    this.setState(this.getInitialState());
  };

  private handleInputChange = (
      event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ): void => {
    const { name, value } = event.target;
    this.clearMessages();

    this.setState((prevState) => ({
      ...prevState,
      [name]: value
    }));
  };

  private handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    this.clearMessages();

    if (!this.state.date) {
      this.setState({ errorMessage: 'Date is required' });
      return;
    }

    this.setState({ isSubmitting: true });

    try {
      const record = this.buildRecordFromState();
      const response = await this.props.apiClient.create('personal_data', record as any);

      if (response.success) {
        this.setState({
          errorMessage: '',
          isSubmitting: false,
          successMessage: 'Data saved successfully!',
        });
        setTimeout(() => this.handleClear(), 2000);
      } else {
        this.setState({
          errorMessage: response.error || 'Failed to save data',
          isSubmitting: false,
          successMessage: '',
        });
      }
    } catch (error) {
      this.setState({
        errorMessage: error instanceof Error ? error.message : 'An unexpected error occurred',
        isSubmitting: false,
        successMessage: '',
      });
    }
  };

  public render(): React.ReactNode {
    return (
        <div className="input-tab">
          <h2>Data Input</h2>

          {this.state.successMessage && (
              <div className="message success-message">{this.state.successMessage}</div>
          )}

          {this.state.errorMessage && (
              <div className="message error-message">{this.state.errorMessage}</div>
          )}

          <form onSubmit={this.handleSubmit} className="input-form">
            <div className="form-section">
              <h3>Required</h3>
              <div className="form-group">
                <label htmlFor="date">{this.columnDisplayNames.date}*</label>
                <input
                    type="date"
                    id="date"
                    name="date"
                    value={this.state.date}
                    onChange={this.handleInputChange}
                    required
                    disabled={this.state.isSubmitting}
                />
              </div>
            </div>

            <div className="form-section">
              <h3>Sleep Metrics</h3>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="sleep_index">{this.columnDisplayNames.sleep_index}</label>
                  <input
                      type="number"
                      id="sleep_index"
                      name="sleep_index"
                      value={this.state.sleep_index}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="sleep_debt">{this.columnDisplayNames.sleep_debt}</label>
                  <input
                      type="number"
                      id="sleep_debt"
                      name="sleep_debt"
                      value={this.state.sleep_debt}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Recovery & Movement</h3>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="dynamic_recovery">{this.columnDisplayNames.dynamic_recovery}</label>
                  <input
                      type="number"
                      id="dynamic_recovery"
                      name="dynamic_recovery"
                      value={this.state.dynamic_recovery}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="movement">{this.columnDisplayNames.movement}</label>
                  <input
                      type="number"
                      id="movement"
                      name="movement"
                      value={this.state.movement}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="steps">{this.columnDisplayNames.steps}</label>
                  <input
                      type="number"
                      id="steps"
                      name="steps"
                      value={this.state.steps}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Heart Metrics</h3>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="heart_rate">{this.columnDisplayNames.heart_rate}</label>
                  <input
                      type="number"
                      id="heart_rate"
                      name="heart_rate"
                      value={this.state.heart_rate}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="heart_rate_variability">
                    {this.columnDisplayNames.heart_rate_variability}
                  </label>
                  <input
                      type="number"
                      id="heart_rate_variability"
                      name="heart_rate_variability"
                      value={this.state.heart_rate_variability}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="resting_heart_rate">
                    {this.columnDisplayNames.resting_heart_rate}
                  </label>
                  <input
                      type="number"
                      id="resting_heart_rate"
                      name="resting_heart_rate"
                      value={this.state.resting_heart_rate}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Other Metrics</h3>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="stress_rhythm">{this.columnDisplayNames.stress_rhythm}</label>
                  <input
                      type="number"
                      id="stress_rhythm"
                      name="stress_rhythm"
                      value={this.state.stress_rhythm}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="vo2_max">{this.columnDisplayNames.vo2_max}</label>
                  <input
                      type="number"
                      id="vo2_max"
                      name="vo2_max"
                      value={this.state.vo2_max}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>UD Metrics</h3>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="ud_t">{this.columnDisplayNames.ud_t}</label>
                  <input
                      type="number"
                      id="ud_t"
                      name="ud_t"
                      value={this.state.ud_t}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="ud_a">{this.columnDisplayNames.ud_a}</label>
                  <input
                      type="number"
                      id="ud_a"
                      name="ud_a"
                      value={this.state.ud_a}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="ud_mj">{this.columnDisplayNames.ud_mj}</label>
                  <input
                      type="number"
                      id="ud_mj"
                      name="ud_mj"
                      value={this.state.ud_mj}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="ud_sd">{this.columnDisplayNames.ud_sd}</label>
                  <input
                      type="number"
                      id="ud_sd"
                      name="ud_sd"
                      value={this.state.ud_sd}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="ud_narc">{this.columnDisplayNames.ud_narc}</label>
                  <input
                      type="number"
                      id="ud_narc"
                      name="ud_narc"
                      value={this.state.ud_narc}
                      onChange={this.handleInputChange}
                      disabled={this.state.isSubmitting}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Notes</h3>
              <div className="form-group">
                <label htmlFor="raw_notes">{this.columnDisplayNames.raw_notes}</label>
                <textarea
                    id="raw_notes"
                    name="raw_notes"
                    value={this.state.raw_notes}
                    onChange={this.handleInputChange}
                    rows={4}
                    disabled={this.state.isSubmitting}
                />
              </div>
            </div>

            <div className="form-actions">
              <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={this.state.isSubmitting}
              >
                {this.state.isSubmitting ? 'Saving...' : 'Save Data'}
              </button>
              <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={this.handleClear}
                  disabled={this.state.isSubmitting}
              >
                Clear Form
              </button>
            </div>
          </form>
        </div>
    );
  }
}
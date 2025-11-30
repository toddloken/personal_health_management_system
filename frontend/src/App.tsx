/**
 * @fileoverview
 *
 * Main application component
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { AppState, TabDefinition } from './types/app-types';
import { ApiClient } from './api/ApiClient';
import { DatabaseDataProcessor } from './services/DatabaseDataProcessor';
import { DashboardTab } from './components/DashboardTab';
import { InputTab } from './components/InputTab';
import { LlmInsightsTab } from './components/LlmInsightsTab';
import { OutputTab } from './components/OutputTab';
import { SettingsTab } from './components/SettingsTab';
import { TabNavigation } from './components/TabNavigation';
import { TrendsTab } from './components/TrendsTab';
import './styles/App.css';

export class App extends React.Component<Record<string, never>, AppState> {
  private tabs: TabDefinition[];

  constructor(props: Record<string, never>) {
    super(props);

    const apiClient = new ApiClient({
      baseUrl: 'http://localhost:8000',
      timeout: 30000,
    });

    const dataProcessor = new DatabaseDataProcessor(apiClient, 'personal_data');

    this.tabs = [
      { id: 'dashboard', label: 'Dashboard', component: DashboardTab, requiresProcessor: false },
      { id: 'input', label: 'Input', component: InputTab, requiresProcessor: false },
      { id: 'output', label: 'Output', component: OutputTab, requiresProcessor: false },
      { id: 'trends', label: 'Basic Trends and Insights', component: TrendsTab, requiresProcessor: true },
      { id: 'llm', label: 'LLM Insights', component: LlmInsightsTab, requiresProcessor: false },
      { id: 'settings', label: 'Settings', component: SettingsTab, requiresProcessor: false },
    ];

    this.state = {
      activeTab: 'dashboard',
      apiClient,
      dataProcessor,
    };
  }

  public handleTabChange = (tabId: string): void => {
    this.setState({ activeTab: tabId });
  };

  public renderActiveTab(): React.ReactNode {
    const activeTabDef = this.tabs.find((t) => t.id === this.state.activeTab);
    if (!activeTabDef) {
      return <div>Tab not found</div>;
    }

    const Component = activeTabDef.component;

    if (activeTabDef.id === 'input') {
      return <Component apiClient={this.state.apiClient} />;
    }

    if (activeTabDef.id === 'output') {
      return <Component apiClient={this.state.apiClient} />;
    }

    if (activeTabDef.requiresProcessor && this.state.dataProcessor) {
      return <Component dataProcessor={this.state.dataProcessor} />;
    }

    return <Component />;
  }

  public render(): React.ReactNode {
    return (
        <div className="app">
          <header className="app-header">
            <h1>Todd's Personal Health Management System</h1>
          </header>
          <TabNavigation
              tabs={this.tabs.map((t) => ({ id: t.id, label: t.label }))}
              activeTab={this.state.activeTab}
              onTabChange={this.handleTabChange}
          />
          <main className="app-content">{this.renderActiveTab()}</main>
        </div>
    );
  }
}

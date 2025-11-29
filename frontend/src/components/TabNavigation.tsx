/**
 * @fileoverview
 *
 * Tab navigation component
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

import React from 'react';
import { TabNavigationProps } from '../types/tab-navigation-types';

export class TabNavigation extends React.Component<TabNavigationProps> {
  handleClick = (tabId: string): void => {
    this.props.onTabChange(tabId);
  };

  render(): React.ReactNode {
    return (
      <nav className="tab-navigation">
        {this.props.tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${this.props.activeTab === tab.id ? 'active' : ''}`}
            onClick={() => this.handleClick(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    );
  }
}

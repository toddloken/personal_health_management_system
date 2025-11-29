/**
 * @fileoverview
 *
 * Tab navigation component types
 *
 *
 * @author tjl
 * @version 1.0.0
 * @since November 2025
 */

export interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
  tabs: Array<{ id: string; label: string }>;
}

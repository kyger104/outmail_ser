import type { GlobalThemeOverrides } from 'naive-ui'

const fontFamily = "Inter, Aptos, 'Segoe UI Variable', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"

export const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily,
    primaryColor: '#2563eb',
    primaryColorHover: '#1d4ed8',
    primaryColorPressed: '#1e40af',
    primaryColorSuppl: '#2563eb',
    successColor: '#059669',
    warningColor: '#d97706',
    errorColor: '#dc2626',
    infoColor: '#0891b2',
    bodyColor: '#f4f7fb',
    cardColor: '#ffffff',
    modalColor: '#ffffff',
    popoverColor: '#ffffff',
    tableColor: '#ffffff',
    tableHeaderColor: '#f1f5f9',
    borderColor: '#dbe4ee',
    dividerColor: '#e2e8f0',
    textColor1: '#0f172a',
    textColor2: '#334155',
    textColor3: '#64748b',
    borderRadius: '10px'
  },
  Button: {
    borderRadiusMedium: '10px',
    borderRadiusLarge: '10px',
    textColorPrimary: '#ffffff',
    textColorHoverPrimary: '#ffffff',
    textColorPressedPrimary: '#ffffff'
  },
  Card: {
    borderRadius: '14px',
    color: '#ffffff',
    colorEmbedded: '#f8fafc',
    borderColor: '#dbe4ee'
  },
  Input: {
    color: '#ffffff',
    colorFocus: '#ffffff',
    border: '1px solid #c5d1df',
    borderFocus: '1px solid #2563eb',
    boxShadowFocus: '0 0 0 3px rgba(37, 99, 235, 0.18)'
  },
  DataTable: {
    thColor: '#f1f5f9',
    tdColor: '#ffffff',
    tdColorHover: '#eff6ff',
    borderColor: '#e2e8f0'
  }
}

export const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily,
    primaryColor: '#60a5fa',
    primaryColorHover: '#93c5fd',
    primaryColorPressed: '#3b82f6',
    primaryColorSuppl: '#60a5fa',
    successColor: '#34d399',
    warningColor: '#fbbf24',
    errorColor: '#f87171',
    infoColor: '#22d3ee',
    bodyColor: '#0f172a',
    cardColor: '#111827',
    modalColor: '#111827',
    popoverColor: '#111827',
    tableColor: '#111827',
    tableHeaderColor: '#1e293b',
    borderColor: '#334155',
    dividerColor: '#263449',
    textColor1: '#f8fafc',
    textColor2: '#cbd5e1',
    textColor3: '#94a3b8',
    borderRadius: '10px'
  },
  Button: {
    borderRadiusMedium: '10px',
    borderRadiusLarge: '10px',
    textColorPrimary: '#08111f',
    textColorHoverPrimary: '#08111f',
    textColorPressedPrimary: '#08111f'
  },
  Card: {
    borderRadius: '14px',
    color: '#111827',
    colorEmbedded: '#1e293b',
    borderColor: '#334155'
  },
  Input: {
    color: '#111827',
    colorFocus: '#111827',
    border: '1px solid #334155',
    borderFocus: '1px solid #60a5fa',
    boxShadowFocus: '0 0 0 3px rgba(96, 165, 250, 0.16)'
  },
  DataTable: {
    thColor: '#1e293b',
    tdColor: '#111827',
    tdColorHover: 'rgba(96, 165, 250, 0.1)',
    borderColor: '#263449'
  }
}

import type { GlobalThemeOverrides } from 'naive-ui'

const fontFamily = "Inter, Aptos, 'Segoe UI Variable', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"

export const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily,
    primaryColor: '#0f9f86',
    primaryColorHover: '#0d8a75',
    primaryColorPressed: '#0a6f60',
    primaryColorSuppl: '#0f9f86',
    bodyColor: '#f6f8f7',
    cardColor: '#ffffff',
    modalColor: '#ffffff',
    popoverColor: '#ffffff',
    tableColor: '#ffffff',
    tableHeaderColor: '#f1f5f4',
    borderColor: '#d9e3df',
    dividerColor: '#e5ece9',
    textColor1: '#10231f',
    textColor2: '#3d5450',
    textColor3: '#6b817c',
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
    colorEmbedded: '#f7faf8',
    borderColor: '#d9e3df'
  },
  Input: {
    color: '#ffffff',
    colorFocus: '#ffffff',
    border: '1px solid #d3dfda',
    borderFocus: '1px solid #0f9f86',
    boxShadowFocus: '0 0 0 3px rgba(15, 159, 134, 0.14)'
  },
  DataTable: {
    thColor: '#f1f5f4',
    tdColor: '#ffffff',
    tdColorHover: '#f3faf7',
    borderColor: '#e2ebe7'
  }
}

export const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily,
    primaryColor: '#2dd4bf',
    primaryColorHover: '#5eead4',
    primaryColorPressed: '#14b8a6',
    primaryColorSuppl: '#2dd4bf',
    bodyColor: '#0e1413',
    cardColor: '#151d1b',
    modalColor: '#151d1b',
    popoverColor: '#151d1b',
    tableColor: '#151d1b',
    tableHeaderColor: '#1b2623',
    borderColor: '#2b3c37',
    dividerColor: '#22322e',
    textColor1: '#effaf7',
    textColor2: '#c2d7d2',
    textColor3: '#85a09a',
    borderRadius: '10px'
  },
  Button: {
    borderRadiusMedium: '10px',
    borderRadiusLarge: '10px',
    textColorPrimary: '#06211d',
    textColorHoverPrimary: '#06211d',
    textColorPressedPrimary: '#06211d'
  },
  Card: {
    borderRadius: '14px',
    color: '#151d1b',
    colorEmbedded: '#1b2623',
    borderColor: '#2b3c37'
  },
  Input: {
    color: '#111a18',
    colorFocus: '#111a18',
    border: '1px solid #2b3c37',
    borderFocus: '1px solid #2dd4bf',
    boxShadowFocus: '0 0 0 3px rgba(45, 212, 191, 0.16)'
  },
  DataTable: {
    thColor: '#1b2623',
    tdColor: '#151d1b',
    tdColorHover: 'rgba(45, 212, 191, 0.08)',
    borderColor: '#263833'
  }
}

import type { GlobalThemeOverrides } from 'naive-ui'

export const themeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily: "Aptos, 'Segoe UI Variable', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
    primaryColor: '#46c2ff',
    primaryColorHover: '#76d3ff',
    primaryColorPressed: '#1b9fff',
    primaryColorSuppl: '#46c2ff',
    bodyColor: '#08111a',
    cardColor: '#101b29',
    modalColor: '#101b29',
    popoverColor: '#101b29',
    tableColor: '#101b29',
    tableHeaderColor: '#142234',
    borderColor: '#22344a',
    dividerColor: '#1b2b3d',
    textColor1: '#ecf6ff',
    textColor2: '#b7ccdf',
    textColor3: '#7d95aa',
    borderRadius: '14px'
  },
  Button: {
    borderRadiusMedium: '14px',
    borderRadiusLarge: '14px',
    textColorPrimary: '#03101b',
    textColorHoverPrimary: '#03101b',
    textColorPressedPrimary: '#03101b'
  },
  Card: {
    borderRadius: '22px',
    color: '#101b29',
    colorEmbedded: '#142234',
    borderColor: '#22344a'
  },
  Input: {
    color: '#0c1724',
    colorFocus: '#0c1724',
    border: '1px solid #22344a',
    borderFocus: '1px solid #46c2ff',
    boxShadowFocus: '0 0 0 3px rgba(70, 194, 255, 0.14)'
  },
  DataTable: {
    thColor: '#142234',
    tdColor: '#101b29',
    tdColorHover: 'rgba(70, 194, 255, 0.08)',
    borderColor: '#22344a'
  }
}

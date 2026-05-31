# IMAP 邮件托管系统 - UI/UX 全面改进提示词

## 项目背景

当前项目是一个 IMAP 邮件托管系统，使用 FastAPI (后端) + Vue 3 + Naive UI (前端)。目前功能可用但 UI/UX 较为粗糙，需要参考同类项目 InboxHub 进行全面改进。

**当前项目路径：** `D:\DevSpace\H01_hotmail_reg\imap`  
**参考项目路径：** `D:\DevSpace\H01_hotmail_reg\InboxHub`

---

## 一、核心问题分析

### 当前项目的主要问题

1. **视觉设计粗糙**
   - 缺少统一的设计系统和主题配置
   - 没有暗色主题支持
   - 颜色、圆角、间距不统一
   - 缺少视觉层次和呼吸感

2. **交互体验不佳**
   - 页面布局简单，缺少导航结构
   - 没有加载状态、空状态、错误状态的优雅处理
   - 缺少操作反馈（成功/失败提示不够明显）
   - 表单交互体验差

3. **功能展示不清晰**
   - 邮箱列表展示信息不够丰富
   - 邮件详情页面排版混乱
   - 缺少筛选、搜索、分页等基础功能
   - 没有统计数据展示

4. **代码组织混乱**
   - 缺少组件化拆分
   - 样式散落在各处，没有统一管理
   - 缺少工具函数和公共逻辑抽取

---

## 二、参考 InboxHub 的优秀设计

### InboxHub 的设计亮点

1. **专业的暗色主题**
   ```typescript
   // 完整的主题配置系统
   const themeOverrides: GlobalThemeOverrides = {
     common: {
       primaryColor: '#46c2ff',      // 主色调：科技蓝
       bodyColor: '#08111a',          // 深色背景
       cardColor: '#101b29',          // 卡片背景
       borderColor: '#22344a',        // 边框颜色
       // ... 完整的颜色系统
     }
   }
   ```

2. **精致的视觉效果**
   - 渐变背景 + 网格纹理
   - 毛玻璃效果（backdrop-filter）
   - 柔和的阴影和圆角
   - 统一的间距系统

3. **清晰的信息架构**
   - 侧边栏导航 + 主内容区
   - 卡片式布局，信息分组清晰
   - 表格/列表展示数据丰富
   - 统计数据可视化

4. **流畅的交互体验**
   - 加载骨架屏
   - 操作确认对话框
   - 实时搜索和筛选
   - WebSocket 实时推送

---

## 三、详细改进任务清单

### 任务 1：建立设计系统

**目标：** 创建统一的主题配置和设计规范

**具体要求：**

1. **创建主题配置文件** `frontend/src/theme.ts`
   ```typescript
   import type { GlobalThemeOverrides } from 'naive-ui'
   
   export const themeOverrides: GlobalThemeOverrides = {
     common: {
       fontFamily: 'Aptos, Segoe UI Variable, Segoe UI, sans-serif',
       primaryColor: '#46c2ff',
       primaryColorHover: '#76d3ff',
       primaryColorPressed: '#1b9fff',
       bodyColor: '#08111a',
       cardColor: '#101b29',
       borderColor: '#22344a',
       textColor1: '#ecf6ff',
       textColor2: '#b7ccdf',
       textColor3: '#7d95aa'
     },
     Button: {
       borderRadiusMedium: '14px',
       colorPrimary: '#46c2ff',
       textColorPrimary: '#03101b'
     },
     Input: {
       color: '#0c1724',
       border: '1px solid #22344a',
       borderFocus: '1px solid #46c2ff',
       boxShadowFocus: '0 0 0 3px rgba(70, 194, 255, 0.14)'
     },
     Card: {
       color: '#101b29',
       borderColor: '#22344a'
     }
   }
   ```

2. **创建全局样式文件** `frontend/src/style.css`
   - 参考 InboxHub 的 CSS 变量系统
   - 添加渐变背景和网格纹理
   - 统一滚动条样式
   - 定义间距、圆角、阴影等设计 token

3. **更新 App.vue**
   ```vue
   <template>
     <n-config-provider 
       :theme="darkTheme" 
       :theme-overrides="themeOverrides"
       :locale="zhCN" 
       :date-locale="dateZhCN"
     >
       <n-message-provider>
         <n-dialog-provider>
           <router-view />
         </n-dialog-provider>
       </n-message-provider>
     </n-config-provider>
   </template>
   
   <script setup lang="ts">
   import { darkTheme, zhCN, dateZhCN } from 'naive-ui'
   import { themeOverrides } from './theme'
   </script>
   ```

---

### 任务 2：重构页面布局

**目标：** 建立清晰的导航结构和页面布局

**具体要求：**

1. **创建主布局组件** `frontend/src/layout/MainLayout.vue`
   - 顶部导航栏（Logo + 用户信息 + 退出按钮）
   - 侧边栏导航（收件箱、管理后台、API Keys、设置）
   - 主内容区（router-view）
   - 响应式设计（移动端折叠侧边栏）

2. **侧边栏导航项**
   ```
   📧 收件箱 (/inbox)
   ⚙️ 管理后台 (/admin)
   🔑 API Keys (/api-keys)
   📊 统计数据 (/stats)
   ⚙️ 系统设置 (/settings)
   ```

3. **布局结构**
   ```
   ┌─────────────────────────────────────┐
   │  Header (Logo + User + Actions)     │
   ├──────┬──────────────────────────────┤
   │      │                              │
   │ Side │   Main Content Area          │
   │ bar  │   (router-view)              │
   │      │                              │
   │      │                              │
   └──────┴──────────────────────────────┘
   ```

---

### 任务 3：改进管理后台页面 (Admin.vue)

**目标：** 打造专业的邮箱管理界面

**具体要求：**

1. **顶部统计卡片**
   ```
   ┌──────────┬──────────┬──────────┬──────────┐
   │ 总邮箱数 │ 活跃邮箱 │ 今日同步 │ 错误邮箱 │
   │   128    │   115    │   1,234  │    3     │
   └──────────┴──────────┴──────────┴──────────┘
   ```

2. **操作区域优化**
   - 批量导入：使用抽屉（Drawer）而不是直接展示在页面上
   - 添加单个邮箱：使用模态框（Modal）
   - 批量操作：选择多个邮箱后显示批量删除按钮

3. **邮箱列表表格优化**
   - 添加搜索框（实时搜索邮箱）
   - 添加筛选器（按状态筛选：全部/活跃/错误）
   - 表格列优化：
     ```
     [✓] | ID | 邮箱地址 | 状态 | 邮件数 | 最后同步 | 创建时间 | 操作
     ```
   - 状态使用彩色标签（Tag）
   - 操作列：复制链接、同步、编辑、删除

4. **空状态设计**
   - 当没有邮箱时，显示友好的空状态插图
   - 提供"导入邮箱"按钮引导用户

5. **加载状态**
   - 表格加载时显示骨架屏（Skeleton）
   - 操作按钮添加 loading 状态

---

### 任务 4：改进收件箱页面 (Inbox.vue)

**目标：** 打造类似邮件客户端的阅读体验

**具体要求：**

1. **三栏布局**
   ```
   ┌────────┬─────────────┬──────────────────┐
   │        │  邮件列表   │                  │
   │ 文件夹 │  (摘要)     │   邮件详情       │
   │        │             │   (HTML渲染)     │
   │        │             │                  │
   └────────┴─────────────┴──────────────────┘
   ```

2. **邮件列表优化**
   - 未读邮件加粗显示
   - 显示发件人头像（使用邮箱生成头像）
   - 显示邮件摘要（前100字符）
   - 显示附件图标
   - 时间显示优化（今天显示时间，昨天显示"昨天"，更早显示日期）

3. **邮件详情优化**
   - 顶部显示：发件人、收件人、时间、主题
   - HTML 邮件渲染优化（样式隔离）
   - 附件列表展示
   - 操作按钮：标记已读/未读、删除、回复（如果支持）

4. **搜索和筛选**
   - 顶部搜索框（搜索主题、发件人、内容）
   - 筛选器：全部/未读/已读/有附件

---

### 任务 5：创建 API Keys 管理页面

**目标：** 独立的 API Key 管理界面

**具体要求：**

1. **页面结构**
   - 顶部说明：API Key 的用途和使用方法
   - 创建按钮：打开模态框创建新 Key
   - Key 列表表格

2. **表格列**
   ```
   名称 | Key (部分隐藏) | 权限 | 创建时间 | 最后使用 | 状态 | 操作
   ```

3. **创建 Key 模态框**
   - 输入名称
   - 选择权限（只读/读写）
   - 设置过期时间（可选）
   - 创建后显示完整 Key（只显示一次，提示复制）

4. **操作**
   - 复制 Key
   - 禁用/启用
   - 删除（需要确认）

---

### 任务 6：添加统计数据页面

**目标：** 可视化展示系统运行数据

**具体要求：**

1. **统计卡片**
   - 总邮箱数、总邮件数、今日新邮件、同步成功率

2. **图表展示**（使用 ECharts 或 Chart.js）
   - 邮件接收趋势（折线图，最近7天）
   - 邮箱状态分布（饼图）
   - 邮件来源分布（柱状图）

3. **活动日志**
   - 最近的同步记录
   - 最近的错误日志

---

### 任务 7：组件化和代码优化

**目标：** 提高代码可维护性

**具体要求：**

1. **创建公共组件**
   - `StatCard.vue` - 统计卡片组件
   - `EmailList.vue` - 邮件列表组件
   - `EmailDetail.vue` - 邮件详情组件
   - `MailboxTable.vue` - 邮箱表格组件
   - `EmptyState.vue` - 空状态组件
   - `LoadingSkeleton.vue` - 加载骨架屏组件

2. **创建工具函数** `frontend/src/utils/`
   - `formatDate.ts` - 日期格式化
   - `formatEmail.ts` - 邮箱格式化
   - `generateAvatar.ts` - 生成头像
   - `copyToClipboard.ts` - 复制到剪贴板

3. **创建 Composables** `frontend/src/composables/`
   - `useMailbox.ts` - 邮箱管理逻辑
   - `useEmail.ts` - 邮件管理逻辑
   - `useAuth.ts` - 认证逻辑

---

### 任务 8：添加动画和过渡效果

**目标：** 提升交互流畅度

**具体要求：**

1. **页面切换动画**
   ```vue
   <router-view v-slot="{ Component }">
     <transition name="fade" mode="out-in">
       <component :is="Component" />
     </transition>
   </router-view>
   ```

2. **列表项动画**
   - 使用 `<transition-group>` 为列表添加进入/离开动画

3. **加载动画**
   - 按钮点击后显示 loading 状态
   - 数据加载时显示骨架屏

4. **微交互**
   - 按钮 hover 效果
   - 卡片 hover 阴影变化
   - 输入框 focus 效果

---

### 任务 9：响应式设计

**目标：** 适配移动端和平板

**具体要求：**

1. **断点设计**
   - 移动端：< 768px
   - 平板：768px - 1024px
   - 桌面：> 1024px

2. **移动端适配**
   - 侧边栏改为抽屉（Drawer）
   - 表格改为卡片列表
   - 三栏布局改为单栏（可切换）

3. **触摸优化**
   - 增大点击区域
   - 支持滑动操作

---

### 任务 10：性能优化

**目标：** 提升加载速度和运行性能

**具体要求：**

1. **代码分割**
   - 路由懒加载
   - 组件懒加载

2. **虚拟滚动**
   - 邮件列表使用虚拟滚动（当邮件数量 > 100 时）

3. **图片优化**
   - 邮件中的图片懒加载
   - 使用 WebP 格式

4. **缓存策略**
   - API 响应缓存
   - 静态资源缓存

---

## 四、技术栈和依赖

### 需要安装的额外依赖

```bash
cd frontend

# 图表库（可选）
npm install echarts vue-echarts

# 日期处理
npm install date-fns

# 图标库（如果需要更多图标）
npm install @vicons/ionicons5

# 虚拟滚动（如果需要）
npm install vueuc
```

---

## 五、实施步骤建议

### 第一阶段：基础设施（1-2天）
1. 建立设计系统（主题配置、全局样式）
2. 创建主布局组件
3. 配置路由和导航

### 第二阶段：核心页面改进（3-4天）
1. 重构管理后台页面
2. 重构收件箱页面
3. 创建 API Keys 页面

### 第三阶段：增强功能（2-3天）
1. 添加统计数据页面
2. 添加搜索和筛选功能
3. 优化表单和交互

### 第四阶段：优化和完善（2-3天）
1. 组件化拆分
2. 添加动画效果
3. 响应式适配
4. 性能优化

---

## 六、验收标准

### 视觉设计
- [ ] 统一的暗色主题
- [ ] 清晰的视觉层次
- [ ] 一致的颜色、圆角、间距
- [ ] 精致的阴影和渐变效果

### 交互体验
- [ ] 流畅的页面切换
- [ ] 明确的加载状态
- [ ] 友好的空状态和错误提示
- [ ] 快速的操作反馈

### 功能完整性
- [ ] 所有原有功能正常工作
- [ ] 新增搜索、筛选、统计功能
- [ ] 支持批量操作
- [ ] 响应式适配完成

### 代码质量
- [ ] 组件化拆分合理
- [ ] 代码结构清晰
- [ ] 有适当的注释
- [ ] 无明显性能问题

---

## 七、参考资源

### 设计参考
- InboxHub 项目：`D:\DevSpace\H01_hotmail_reg\InboxHub`
- Naive UI 官方文档：https://www.naiveui.com/
- Tailwind CSS 颜色系统：https://tailwindcss.com/docs/customizing-colors

### 技术文档
- Vue 3 文档：https://vuejs.org/
- Vue Router 文档：https://router.vuejs.org/
- Naive UI 组件库：https://www.naiveui.com/

---

## 八、注意事项

1. **保持功能完整性**
   - 改进 UI 的同时，确保所有原有功能正常工作
   - 不要删除或破坏现有的 API 调用逻辑

2. **渐进式改进**
   - 可以分阶段实施，每个阶段都要确保项目可运行
   - 每完成一个大功能就提交一次 Git

3. **性能优先**
   - 不要为了视觉效果牺牲性能
   - 大列表必须使用虚拟滚动或分页

4. **可访问性**
   - 确保键盘导航可用
   - 颜色对比度符合 WCAG 标准
   - 为图标添加 aria-label

5. **浏览器兼容性**
   - 测试 Chrome、Firefox、Safari、Edge
   - 确保移动端浏览器正常工作

---

## 九、交付物

1. **代码**
   - 完整的前端代码（frontend 目录）
   - 更新后的 README.md

2. **文档**
   - UI 组件使用说明
   - 主题定制指南
   - 部署更新说明

3. **演示**
   - 部署到测试服务器
   - 提供演示视频或截图

---

## 十、联系方式

如有疑问，请参考：
- 当前项目：`D:\DevSpace\H01_hotmail_reg\imap`
- 参考项目：`D:\DevSpace\H01_hotmail_reg\InboxHub`
- Git 仓库：已提交最新修复（commit: 86b03ca）

---

**最后更新：** 2026-05-31  
**版本：** v1.0

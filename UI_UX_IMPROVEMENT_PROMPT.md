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

### 重点参考文件

- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\layout\MainLayout.vue`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\style.css`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\router\index.ts`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\utils\api.ts`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\views\Dashboard.vue`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\views\ApiKeys.vue`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\views\OutlookImport.vue`
- `D:\DevSpace\H01_hotmail_reg\InboxHub\frontend\src\views\DomainBatch.vue`

### InboxHub 可参考的功能矩阵

> 参考时不要简单复制业务字段，需要结合 `imap` 当前后端接口、JWT 邮箱访问方式和 IMAP 托管模型做适配。能直接复用的优先复用交互模式、状态管理方式、页面结构和错误处理策略。

| InboxHub 功能 | 可迁移到 imap 的方向 | 备注 |
| --- | --- | --- |
| `MainLayout.vue` 工作区框架 | 建立固定侧边栏 + 顶部面包屑 + 主内容区 | 支持桌面折叠侧边栏、移动端抽屉导航、当前路由高亮 |
| `Dashboard.vue` 概览页 | 增加系统总览、最近邮箱、最近邮件、快捷入口 | 当前 `imap` 只有 Admin/Inbox，需要补一个 Dashboard 作为后台首页 |
| 侧边栏树 `sidebar-tree` | 邮箱状态分组、域名/邮箱类型分组、标签分组 | 如果后端暂无树接口，前端先由邮箱列表聚合 |
| 分组创建弹窗 | 邮箱标签/分组管理 | 可先实现前端筛选和展示，后端支持后再保存 |
| 批量生成域名邮箱 | 可作为后续扩展页面，不作为首批必做 | `imap` 当前是托管已有邮箱，不要强行创建域名邮箱 |
| Outlook 批量导入 | 强化当前批量导入体验 | 支持多分隔符、行级解析、错误行跳过、导入报告、成功结果复制 |
| 账号列表批量操作 | 邮箱批量导出链接、批量删除、批量同步、批量分组 | 操作前必须有确认，执行后刷新列表和统计 |
| API Key 管理 | 独立 API Key 页面 | 展示速率限制、每日额度、已用次数、总请求数、状态、复制/显示/删除 |
| 统一 axios 封装 | 增强 `frontend/src/utils/api.ts` | 统一超时、错误消息、401 处理、响应解包、请求 header |
| 登录会话守卫 | 增加管理员登录/会话状态 | 如果当前项目没有登录接口，先保留路由守卫结构并标记待接入 |
| 本地配置缓存 | 导入表单、筛选条件、侧边栏状态持久化 | 使用 localStorage 保存非敏感 UI 状态，禁止保存 API Key 明文和邮箱令牌 |
| 复制/导出工具 | 邮箱链接、账号数据、API Key 一键复制 | 所有复制操作使用统一反馈，失败时提示浏览器权限问题 |

### 产品级补齐目标

1. **从两个页面升级为后台工作区**
   - 当前 `main.ts` 直接挂载 `/inbox` 和 `/admin`，需要改成 `MainLayout` 子路由模式。
   - `/` 默认进入 Dashboard，`/inbox` 保留 JWT 邮箱阅读场景，`/admin` 进入邮箱托管管理。
   - 后台页面与公开邮箱访问页面要区分：公开 `Inbox.vue?jwt=...` 不应暴露管理员导航。

2. **从单一表格升级为可运营列表**
   - 邮箱列表支持搜索、状态筛选、分页、选中、批量操作、导出。
   - 列表行要包含可复制访问链接、同步状态、最近同步时间、错误摘要、邮件数量。
   - 详情或展开区域展示最近邮件样本，便于快速判断邮箱是否正常。

3. **从简单导入升级为批处理工作流**
   - 导入前：多行解析、格式预览、行号错误提示、重复邮箱提示。
   - 导入中：进度、loading、禁用重复提交。
   - 导入后：成功/失败统计、失败原因列表、成功链接批量复制或导出 CSV。

4. **从被动查看升级为状态监控**
   - Dashboard 展示总邮箱数、活跃邮箱、错误邮箱、总邮件数、今日新邮件、最近同步时间。
   - 增加最近错误、最近导入、最近同步活动流。
   - 对同步失败、JWT 过期、IMAP 登录失败等状态给出明确恢复路径。

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
   - 顶部导航栏（Logo + 面包屑 + 后端连接状态 + 快捷操作 + 用户信息/退出按钮）
   - 侧边栏导航（Dashboard、邮箱管理、公开收件箱、API Keys、统计数据、设置）
   - 主内容区（router-view）
   - 响应式设计（桌面端可折叠侧边栏、移动端抽屉导航）
   - 记住侧边栏折叠状态和展开分组状态

2. **侧边栏导航项**
   ```
   Dashboard (/)
   Mailboxes 邮箱管理 (/admin)
   Inbox 公开收件箱 (/inbox)
   API Keys (/api-keys)
   Stats 统计数据 (/stats)
   Import 批量导入 (/import)
   Settings 系统设置 (/settings)
   ```

   图标要求：
   - 使用 `lucide-vue-next`，不要使用 emoji 作为结构性图标。
   - 每个图标按钮必须有 `title` 或 `aria-label`。
   - 折叠状态下只显示图标和计数，hover/focus 显示可读提示。

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

4. **路由结构**
   - 新建 `frontend/src/router/index.ts`，不要继续把路由写在 `main.ts`。
   - 后台路由使用 `MainLayout`：
     ```typescript
     {
       path: '/',
       component: MainLayout,
       children: [
         { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
         { path: 'admin', name: 'Admin', component: () => import('../views/Admin.vue') },
         { path: 'api-keys', name: 'ApiKeys', component: () => import('../views/ApiKeys.vue') },
         { path: 'stats', name: 'Stats', component: () => import('../views/Stats.vue') },
         { path: 'import', name: 'Import', component: () => import('../views/Import.vue') },
         { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue') }
       ]
     }
     ```
   - 公开收件箱可根据实际访问模型选择：
     - 如果 `/inbox?jwt=...` 是公开访问页面，则放在 layout 外，避免暴露后台导航。
     - 如果管理员也需要查看邮箱客户端，则新增 `/mail-client` 放在 layout 内。

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

6. **参考 InboxHub 补齐批量操作**
   - 选中邮箱后显示固定的批量操作条：已选数量、复制链接、导出 CSV、批量同步、批量删除、移动分组。
   - 支持“导出当前筛选结果”和“导出选中项”两种模式。
   - 删除、批量删除、批量同步失败重试必须使用确认弹窗和结果反馈。
   - 批量导出格式至少包含：`email, status, last_sync, access_link`。

7. **邮箱分组/标签**
   - 支持按状态自动分组：全部、活跃、错误、未同步。
   - 支持按导入批次或自定义标签分组；如果后端暂不支持保存标签，则先保留 UI 和前端筛选结构。
   - 侧边栏展示分组计数，参考 InboxHub 的可展开分组树。

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

5. **验证码/关键内容提取**
   - 自动识别邮件摘要中的验证码、确认码、OTP、登录链接。
   - 在邮件列表和详情头部显示“复制验证码”快捷按钮。
   - 支持按验证码邮件筛选：全部邮件 / 含验证码 / 含链接 / 含附件。
   - 识别失败时不影响原文阅读。

6. **安全渲染与隔离**
   - 继续使用 DOMPurify 清洗 HTML。
   - HTML 邮件内容放入隔离容器，限制外部样式污染页面。
   - 邮件内图片默认懒加载，外链图片加载失败时显示占位。
   - 链接默认 `target="_blank"`，补齐 `rel="noopener noreferrer"`。

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
   - 显示/隐藏完整 Key
   - 禁用/启用
   - 删除（需要确认）

5. **参考 InboxHub 的用量展示**
   - 卡片或表格展示：速率限制、每日限额、今日已用、历史总请求、创建时间、最后使用时间。
   - 每日用量用进度条展示；达到 80% 后显示 warning 状态，达到 100% 显示 danger 状态。
   - 支持按状态筛选：全部 / 启用 / 禁用 / 即将过期。
   - 删除操作必须二次确认，复制完整 Key 后显示安全提示。

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

4. **健康状态面板**
   - 后端连接状态、数据库连接状态、定时同步任务状态。
   - 最近一次同步成功时间、最近一次失败时间、失败原因摘要。
   - JWT 访问链接生成状态和过期策略提示。

5. **快捷入口**
   - 导入邮箱
   - 查看错误邮箱
   - 创建 API Key
   - 导出全部访问链接

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

### 任务 11：新增 Dashboard 控制台首页

**目标：** 参考 InboxHub 的 `Dashboard.vue`，把后台入口从单一列表升级为总览工作台。

**具体要求：**

1. **首页信息架构**
   - 顶部 hero 区：页面标题、系统说明、后端连接状态、刷新按钮、导入邮箱快捷按钮。
   - 指标卡片：总邮箱数、活跃邮箱、错误邮箱、总邮件数、今日新邮件、同步成功率。
   - 两栏布局：左侧账号/邮箱结构，右侧快捷入口和系统状态。

2. **最近数据预览**
   - 最近导入的邮箱 5 条。
   - 最近收到的邮件 5 条。
   - 最近同步失败 5 条。
   - 每条支持跳转到对应邮箱或错误详情。

3. **空状态和降级**
   - 没有邮箱时，引导用户进入批量导入。
   - 统计接口缺失时，可先从现有列表接口聚合基础指标。
   - 所有卡片保留 skeleton/loading/error 三种状态。

---

### 任务 12：新增批量导入工作流页面

**目标：** 把 Admin.vue 里的简单 textarea 导入拆成独立的 `Import.vue` 页面，参考 InboxHub 的 `OutlookImport.vue` 做成可靠的批处理工具。

**具体要求：**

1. **输入与解析**
   - 支持格式：`email:imap_token`、`email----imap_token`、`email|imap_token`。
   - 支持自动识别分隔符，也允许用户手动选择。
   - 输入区显示行数、有效行数、错误行数。
   - 错误行展示行号、原始内容、错误原因。

2. **导入配置**
   - 分组/标签（可选）。
   - 是否覆盖已存在邮箱。
   - 是否导入后立即同步。
   - 是否生成访问链接并在结果中展示。

3. **执行报告**
   - 成功、失败、跳过、已存在数量统计。
   - 成功项可复制：邮箱、访问链接、邮箱+链接。
   - 失败项保留错误原因并支持重新导入失败项。
   - 支持导出 CSV。

4. **体验要求**
   - 支持一键粘贴剪贴板。
   - 导入过程中禁用重复提交。
   - 大批量导入时显示进度或分批执行提示。
   - 表单配置可保存到 localStorage，但不能保存邮箱令牌明文。

---

### 任务 13：完善统一 API 层和错误处理

**目标：** 参考 InboxHub 的 `frontend/src/utils/api.ts`，提升所有页面的 API 调用一致性。

**具体要求：**

1. **Axios 实例**
   - 统一 `baseURL`、`timeout`、请求头、响应解包。
   - 兼容后端返回：直接数据、`{success, data}`、`{detail}`、`{error: {message}}`。
   - 所有错误转换成统一结构：`message`、`status`、`code`、`raw`。

2. **认证和会话**
   - 如果接入管理员登录，则使用 `X-Admin-Session` 或 Bearer Token。
   - 401 自动清理会话并跳转登录页。
   - 登录接口自身的 401 由登录页面处理，不做全局跳转循环。

3. **前端调用规范**
   - 页面组件不直接拼接重复错误消息逻辑。
   - 请求 loading、空状态、错误状态必须独立维护。
   - 所有 destructive API 调用必须在 UI 层确认。

---

### 任务 14：新增设置页面 (Settings.vue)

**目标：** 集中管理前端偏好和系统参数，避免配置散落在页面里。

**具体要求：**

1. **界面偏好**
   - 主题模式：跟随系统 / 暗色 / 亮色（首版可默认暗色，保留控件）。
   - 每页条数默认值：20 / 50 / 100。
   - 是否默认自动刷新。
   - 邮件列表预览长度。

2. **邮箱访问设置**
   - 访问链接有效期说明。
   - JWT 过期提示文案。
   - 默认复制格式：链接 / CSV / 邮箱+链接。

3. **开发/诊断信息**
   - 前端版本、后端地址、构建时间。
   - 一键复制诊断信息。
   - 清理本地 UI 缓存。

---

### 任务 15：补齐管理员登录与权限入口

**目标：** 如果后端已有或计划提供管理员会话，参考 InboxHub 的登录守卫完善后台安全边界。

**具体要求：**

1. **登录页**
   - `frontend/src/views/Login.vue`。
   - 支持密码登录；如果后端支持 2FA，则预留二步验证状态。
   - 登录成功后写入会话并跳转 Dashboard。

2. **路由守卫**
   - 后台路由需要登录。
   - 公开 `/inbox?jwt=...` 不需要管理员登录。
   - 未登录访问后台时跳转 `/login`，并保留 redirect。

3. **权限降级**
   - 如果当前后端没有登录接口，不要阻塞 UI 改造。
   - 先实现路由结构和会话工具，默认关闭守卫或用配置开关控制。

---

### 任务 16：补齐可复用业务工具

**目标：** 将邮箱管理、复制、导出、日期展示、验证码提取等逻辑抽成公共工具，减少页面内重复代码。

**具体要求：**

1. **工具函数**
   - `extractCode.ts`：从主题、摘要、正文中提取验证码。
   - `exportCsv.ts`：安全生成 CSV 并下载。
   - `copyToClipboard.ts`：统一复制和错误处理。
   - `formatDate.ts`：相对时间、完整时间、短日期。
   - `mailboxLink.ts`：生成和格式化访问链接。

2. **Composables**
   - `useAsyncState.ts`：统一 loading/error/data。
   - `usePagination.ts`：分页状态和参数。
   - `useMailboxList.ts`：邮箱列表查询、筛选、刷新、批量选择。
   - `useLocalPreference.ts`：本地 UI 偏好持久化。

3. **组件**
   - `ConfirmDialog.vue`：统一危险操作确认。
   - `SelectionToolbar.vue`：批量选择操作条。
   - `SearchFilterBar.vue`：搜索和筛选工具条。
   - `StatusBadge.vue`：统一状态标签。
   - `CopyButton.vue`：复制按钮和反馈。

---

## 四、技术栈和依赖

### 需要安装的额外依赖

```bash
cd frontend

# 图表库（可选）
npm install echarts vue-echarts

# 日期处理
npm install date-fns

# 图标库（优先使用 lucide，参考 InboxHub）
npm install lucide-vue-next

# 虚拟滚动（如果需要）
npm install vueuc

# HTML 清洗（当前 Inbox.vue 已使用，确保依赖存在）
npm install dompurify
npm install -D @types/dompurify

# CSV/文件导出可优先手写轻量工具，不强制引入大型库
```

### 依赖原则

1. 优先复用现有依赖：Vue 3、Vue Router、Naive UI、Axios、date-fns、DOMPurify。
2. 图标统一使用 `lucide-vue-next`，不要同时混用多个图标体系。
3. 图表库只在 Stats/Dashboard 确认需要后安装；首版可以先用指标卡片和列表完成。
4. 虚拟滚动只在邮件或邮箱列表超过 100 条且实际卡顿时启用。

---

## 五、实施步骤建议

### 第一阶段：基础设施（1-2天）
1. 建立设计系统（主题配置、全局样式）
2. 创建主布局组件
3. 配置路由和导航
4. 拆出 `router/index.ts`
5. 增强 `utils/api.ts`
6. 接入 lucide 图标和统一按钮/卡片样式

### 第二阶段：后台工作区（2-3天）
1. 新增 Dashboard 页面
2. 重构 MainLayout 的侧边栏、顶部栏、面包屑
3. 增加状态分组、快捷入口、最近数据预览
4. 完成移动端抽屉导航和桌面折叠状态记忆

### 第三阶段：核心业务页面（3-4天）
1. 重构管理后台页面
2. 重构公开收件箱页面
3. 创建批量导入页面
4. 创建 API Keys 页面
5. 补齐搜索、筛选、分页、批量选择

### 第四阶段：增强功能（2-3天）
1. 添加统计数据页面
2. 添加设置页面
3. 添加验证码提取和复制
4. 添加活动日志和错误恢复提示

### 第五阶段：优化和完善（2-3天）
1. 组件化拆分
2. 添加动画效果
3. 响应式适配
4. 性能优化
5. 完成可访问性检查和浏览器验证

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
- [ ] 危险操作都有二次确认
- [ ] 复制、导出、同步、导入都有成功/失败反馈

### 功能完整性
- [ ] 所有原有功能正常工作
- [ ] 新增搜索、筛选、统计功能
- [ ] 支持批量操作
- [ ] 响应式适配完成
- [ ] Dashboard 可展示关键指标和最近活动
- [ ] 批量导入支持行级解析和执行报告
- [ ] API Key 页面支持创建、复制、隐藏/显示、删除、用量展示
- [ ] 公开收件箱 JWT 访问不受后台登录守卫影响
- [ ] 邮件详情 HTML 渲染经过 DOMPurify 清洗

### 代码质量
- [ ] 组件化拆分合理
- [ ] 代码结构清晰
- [ ] 有适当的注释
- [ ] 无明显性能问题
- [ ] 路由配置从 `main.ts` 拆出到 `router/index.ts`
- [ ] API 错误处理集中在 `utils/api.ts`
- [ ] 重复复制/导出/日期逻辑已抽成工具函数

### 可访问性和响应式
- [ ] 所有 icon-only 按钮有 `aria-label` 或 `title`
- [ ] 键盘 Tab 顺序符合视觉顺序
- [ ] 移动端无横向滚动
- [ ] 触摸目标不小于 44px
- [ ] 文本对比度符合 WCAG AA

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

6. **不要盲目复制 InboxHub**
   - InboxHub 的域名邮箱批量生成、Outlook refresh_token 导入等功能只能作为交互参考。
   - `imap` 首要目标是 IMAP 邮箱托管、JWT 访问链接、邮件读取和管理后台。
   - 后端接口缺失时，前端可以预留入口，但必须标注“待后端支持”，不要做假成功。

7. **公开页面和后台页面隔离**
   - `/inbox?jwt=...` 是公开访问场景时，不显示后台侧边栏、API Key、设置等入口。
   - 后台工作区需要登录或预留登录守卫。
   - JWT 过期、无效、缺失时给出清晰错误状态和联系管理员提示。

8. **敏感信息处理**
   - API Key 完整值只在创建后或用户主动显示时展示。
   - 邮箱令牌、IMAP token、API Key 不写入 localStorage。
   - 导出 CSV 时避免默认导出敏感令牌，除非用户明确选择。

---

## 九、交付物

1. **代码**
   - 完整的前端代码（frontend 目录）
   - 更新后的 README.md
   - 新增/更新路由、布局、页面、公共组件、工具函数

2. **文档**
   - UI 组件使用说明
   - 主题定制指南
   - 部署更新说明
   - API 缺口清单：哪些功能已接后端、哪些是预留入口

3. **演示**
   - 部署到测试服务器
   - 提供演示视频或截图
   - 至少包含桌面端和移动端截图
   - 至少包含 Dashboard、Admin、Inbox、Import、API Keys 五个核心页面

---

## 十、联系方式

如有疑问，请参考：
- 当前项目：`D:\DevSpace\H01_hotmail_reg\imap`
- 参考项目：`D:\DevSpace\H01_hotmail_reg\InboxHub`
- Git 仓库：已提交最新修复（commit: 86b03ca）

---

**最后更新：** 2026-05-31  
**版本：** v1.1

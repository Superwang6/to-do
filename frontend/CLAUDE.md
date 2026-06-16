# Frontend Instructions

本文件为 Claude Code 在 `frontend/` 目录中工作时提供前端专属指导。根目录 `CLAUDE.md` 中的项目总览、跨端 API 约定和开发流水线仍然适用。

## 前端概览

前端使用 uni-app（Vue 3）+ Vite + SCSS。用户通过待办列表、语音创建页、聊天/智能创建页来创建和管理待办事项。当前项目主要通过 HBuilderX 运行/构建，npm 仅用于依赖管理。

## 目录结构

```text
frontend/
├── pages/
│   ├── index/               # 主待办列表
│   ├── voice/               # 语音创建页面
│   ├── chat/                # 聊天/智能创建页面
│   └── ...
├── api/                     # API 客户端封装
├── utils/                   # 前端工具函数
├── static/                  # 静态资源
├── App.vue
├── main.js
├── uni.scss                 # 设计系统变量
├── pages.json               # 路由与导航配置
├── index.html
└── vite.config.js
```

## 开发顺序

前端功能开发优先按以下顺序：

```text
api 封装 → 页面状态 → UI/交互 → 样式布局 → 联调
```

涉及后端接口时，先确认根目录 `CLAUDE.md` 中的 API 契约，再修改 `frontend/api/`。

## API 封装规则

- 所有后端接口调用应优先封装在 `frontend/api/` 中。
- API method、path、request body、response 字段必须与后端 router/schema 保持一致。
- 后端路由变更时，必须同步更新前端 API 封装和页面调用点。
- 项目后端仅使用 GET 和 POST：不要在前端新增 PUT / DELETE 请求。
- 列表接口使用 `POST /list`，详情接口使用 `GET /detail/{id}`。

## 页面与状态

页面实现应覆盖以下状态：

- 加载状态
- 空状态
- 成功状态
- 错误状态
- 用户输入非法或为空的状态
- 网络异常状态

交互完成后应给用户明确反馈，例如提示、刷新列表、跳转或按钮状态变化。

## 布局模式

本项目包含 `.claude/skills/uni-app-layout/` 技能，用于避免 uni-app 页面滚动条和溢出问题。创建新页面、修改页面布局、修复滚动问题时必须遵守以下规则。

### 核心规则

1. 页面根元素使用 `height: 100vh` + `overflow: hidden`，不要使用 `min-height` 代替。
2. 带 `flex: 1` 的 `scroll-view` 必须同时设置 `height: 0`。
3. Flex 子元素需要设置 `width: 100%` + `box-sizing: border-box`。
4. 不要在父元素和子元素上嵌套设置横向 padding。
5. 消息气泡、卡片等内容容器需要设置 `max-width` 和 `word-break`，防止长文本撑破布局。
6. 使用 `navigationStyle: "custom"` 时，需要处理状态栏高度。
7. 底部输入栏需要考虑 `safe-area-inset-bottom`。
8. `index.html` 入口的 `src` 路径必须与实际文件位置一致。

### 推荐页面结构

```html
<template>
  <view class="page">
    <view class="header">...</view>
    <scroll-view class="scroll" scroll-y>
      <view class="list">...</view>
    </scroll-view>
    <view class="bottom-bar">...</view>
  </view>
</template>
```

```scss
.page {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.scroll {
  flex: 1;
  height: 0;
  overflow: hidden;
}

.list,
.bottom-bar {
  width: 100%;
  box-sizing: border-box;
}
```

## 设计系统

设计变量定义于 `frontend/uni.scss`：

- 暖奶油色背景：`#F8F6F3`
- 陶土红主色：`#C0544A`
- 常用变量：`$bg-page`、`$primary`、`$text-primary`、`$shadow-sm` 等
- 使用 `rpx` 单位进行响应式尺寸设置。
- 使用 `$transition-spring` 实现交互动效。

新增样式时优先复用 `uni.scss` 变量，避免散落硬编码颜色和阴影。

## 测试与验证

当前前端通过 HBuilderX 运行/构建，项目没有暴露 `npm run build` / `npm run dev` 脚本。HBuilderX 配置位于 `.hbuilderx/launch.json`，当前运行目标为 `uni-app:app-android`；开发模式 App 端产物通常输出到 `unpackage/dist/dev/app-plus/`。

前端改动后，根据范围优先使用 HBuilderX 验证：

```text
运行 → 运行到手机或模拟器 → 运行到 Android App 基座
```

涉及打包发布时使用 HBuilderX 的发行入口，例如：

```text
发行 → 原生 App-云打包 / 本地打包
```

不要默认假设 `npm run build` / `npm run dev` 可用；如果需要命令行构建，必须先确认项目是否已改造成 CLI 标准结构，或已补齐对应 scripts。当前根目录式 uni-app 结构下，直接运行 Vite/uni CLI 可能会查找 `src/manifest.json` 并失败。

如果无法运行 HBuilderX 或当前环境不适合运行，最终回复中必须说明原因。

手动验证至少覆盖：

- 页面能正常进入
- 主流程可完成
- 加载/空/错误状态可见
- API 请求路径和字段正确
- 无横向滚动、无异常页面级滚动
- 聊天/列表类页面滚动区域正常

## 禁止事项

- 不要绕过 `frontend/api/` 直接在页面里散落接口路径。
- 不要新增 PUT / DELETE 请求。
- 不要使用 `min-height: 100vh` 作为页面根布局的主要高度控制。
- 不要让 `scroll-view` 在 flex 布局中缺少 `height: 0`。
- 不要在父子元素中重复叠加横向 padding 导致溢出。
- 不要引入与 `uni.scss` 设计系统明显冲突的颜色和阴影。

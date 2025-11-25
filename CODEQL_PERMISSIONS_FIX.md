# CodeQL 权限配置修复报告

## 问题描述

GitHub Actions 工作流 `.github/workflows/docker-build.yml` 在上传 Trivy 安全扫描结果到 GitHub Security 时遇到权限错误。

### 错误信息
```
Resource not accessible by integration
```

### 根本原因
`build-and-test` 作业使用 `github/codeql-action/upload-sarif@v3` 上传 SARIF 格式的安全扫描结果，但该作业的 `permissions` 配置中缺少 `security-events: write` 权限。

## 解决方案

### 修改内容

在 `.github/workflows/docker-build.yml` 文件的第 29 行添加了 `security-events: write` 权限：

**修改前：**
```yaml
permissions:
  contents: read
  packages: write
```

**修改后：**
```yaml
permissions:
  contents: read
  packages: write
  security-events: write
```

### 权限说明

- **`contents: read`**: 允许工作流读取仓库内容
- **`packages: write`**: 允许工作流推送 Docker 镜像到 GitHub Container Registry
- **`security-events: write`**: 允许工作流上传安全扫描结果到 GitHub Security 标签页（**新增**）

## 影响范围

### 修改的文件
- `.github/workflows/docker-build.yml`

### 受影响的作业
- `build-and-test` 作业中的以下步骤：
  - **镜像安全扫描** (第 90-96 行): 使用 Trivy 扫描 Docker 镜像
  - **上传扫描结果到 GitHub Security** (第 98-102 行): 上传 SARIF 结果

### 触发条件
- 只在非 Pull Request 事件中执行（`if: github.event_name != 'pull_request'`）
- 包括：
  - `push` 到 `main`、`develop` 或 `feat/**` 分支
  - 推送标签（`v*`）
  - 手动触发（`workflow_dispatch`）

## 验证方法

### 1. 本地验证
工作流配置文件的 YAML 语法正确，权限配置符合 GitHub Actions 规范。

### 2. 线上验证
在工作流下次运行时，验证以下内容：

1. **工作流成功执行**
   - 访问 Actions 标签页
   - 查看最新的 Docker 构建工作流
   - 确认所有步骤都成功完成

2. **扫描结果上传成功**
   - 查看 "上传扫描结果到 GitHub Security" 步骤
   - 确认没有权限相关的错误信息

3. **Security 标签页有扫描结果**
   - 访问仓库的 Security → Code scanning 标签页
   - 查看是否显示 Trivy 的扫描结果
   - 确认扫描时间和发现的问题

## 最佳实践

### GitHub Actions 权限原则
1. **最小权限原则**: 只授予作业完成任务所需的最小权限
2. **显式声明**: 明确声明所需的所有权限
3. **作业级权限**: 在作业级别而非工作流级别声明权限（更精细的控制）

### CodeQL/SARIF 上传要求
上传 SARIF 格式的安全扫描结果（包括 CodeQL、Trivy、Snyk 等）必须具备以下权限：
- `security-events: write` - 上传扫描结果
- `contents: read` - 读取仓库内容以关联代码位置

### Fork PR 的安全考虑
当前配置已通过 `if: github.event_name != 'pull_request'` 条件跳过 PR 事件，这样可以：
- 避免 fork 的 PR 访问敏感 token 和权限
- 防止恶意 PR 滥用 GitHub Security 功能
- 保持主分支和标签的安全扫描完整性

## 参考资料

- [GitHub Actions: Permissions for the GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [Uploading a SARIF file to GitHub](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github)
- [CodeQL Action: upload-sarif](https://github.com/github/codeql-action#upload-sarif)
- [Trivy Action](https://github.com/aquasecurity/trivy-action)

## 更新日期
2024-11-25

## 相关问题
- Issue: CodeQL Action 无权访问 GitHub API 端点
- Error: `Resource not accessible by integration`
- Solution: 添加 `security-events: write` 权限

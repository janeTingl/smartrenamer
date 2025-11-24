# GitHub Actions 升级说明

## 升级日期
2024-11-24

## 升级内容

### 🎯 主要目标：Artifact Actions v3 → v4

#### 升级原因
- GitHub 宣布 upload-artifact 和 download-artifact v3 版本即将弃用
- v4 提供更好的性能和功能
- 消除 CI/CD 中的弃用警告

#### 变更详情

**upload-artifact@v3 → v4**（3 处）
- Windows 构建产物上传
- macOS 构建产物上传  
- Linux 构建产物上传

**download-artifact@v3 → v4**（1 处）
- Release 创建时下载所有平台产物

### 🔧 附加升级

**setup-python@v4 → v5**（3 处）
- 改进的缓存机制
- 更快的环境设置
- 支持更多 Python 版本

**codeql-action/upload-sarif@v2 → v3**（1 处）
- 改进的安全扫描集成
- 更好的 SARIF 支持

## 兼容性确认

### ✅ v4 Artifact 兼容性检查

1. **命名唯一性** - 已确认
   - `windows-build`
   - `macos-x86_64-build`
   - `macos-arm64-build`
   - `linux-build`
   - 每个 artifact 名称唯一，无冲突

2. **下载配置** - 已适配
   - 使用 `path: artifacts` 参数
   - 所有 artifacts 下载到各自子目录
   - `find` 命令收集文件兼容 v4 结构

3. **保留期** - 保持不变
   - `retention-days: 7`
   - 符合 v4 要求

## 测试建议

### 快速验证
```bash
# 1. 创建测试 PR（自动触发 docker-build）
git checkout -b test-actions-upgrade
git push origin test-actions-upgrade

# 2. 手动触发构建（可选）
# GitHub Actions → 构建跨平台发布包 → Run workflow
```

### 完整测试
```bash
# 创建测试标签（触发完整发布流程）
git tag v0.6.1-test
git push origin v0.6.1-test

# 验证点：
# - Windows/macOS/Linux 构建成功
# - Artifacts 正确上传
# - Release 创建成功
# - 所有文件正确收集
```

## 预期结果

- ✅ 无弃用警告
- ✅ 构建速度提升
- ✅ Artifact 传输更快
- ✅ 所有工作流正常运行

## 回滚指令

如遇问题，可快速回滚：

```yaml
# 在相应文件中替换：
upload-artifact@v4 → @v3
download-artifact@v4 → @v3
setup-python@v5 → @v4
codeql-action/upload-sarif@v3 → @v2
```

## 相关文档

项目根目录：
- `GITHUB_ACTIONS_UPGRADE.md` - 详细升级报告
- `UPGRADE_SUMMARY.md` - 升级总结
- `CHANGELOG.md` - 已更新

官方文档：
- [upload-artifact v4 迁移指南](https://github.com/actions/upload-artifact/blob/main/docs/MIGRATION.md)
- [download-artifact v4 迁移指南](https://github.com/actions/download-artifact/blob/main/docs/MIGRATION.md)

---

**维护人员注意：**
本次升级已经过语法验证和兼容性检查，可以安全合并。建议在合并后创建测试 tag 进行完整验证。

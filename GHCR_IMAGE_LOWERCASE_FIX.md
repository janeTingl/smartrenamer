# GitHub Actions GHCR 镜像名大小写修复报告

## 问题描述

GitHub Container Registry (GHCR) 要求所有镜像名称必须为小写。之前的工作流使用 `${{ github.repository }}` 变量直接引用镜像名，该变量包含 GitHub 用户名的原始大小写（例如 `janeTingl`），导致 Trivy 安全扫描失败。

### 错误信息
```
failed to parse the image name: could not parse reference
```

## 根本原因

在 `.github/workflows/docker-build.yml` 中：
- `IMAGE_NAME: ${{ github.repository }}` 保留了 GitHub 用户名的原始大小写
- Trivy 扫描步骤直接使用 `${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest`
- 测试镜像步骤也直接使用相同的变量引用
- Docker metadata action 会自动转换为小写，但直接引用 `IMAGE_NAME` 的步骤不会

## 解决方案

在需要使用镜像名的步骤前添加转换步骤，使用 `tr '[:upper:]' '[:lower:]'` 将镜像名转换为小写。

### 修改内容

#### 1. build-and-test 任务 - 添加镜像名转换步骤（第 82-87 行）
```yaml
- name: 转换镜像名为小写
  if: github.event_name != 'pull_request'
  id: lowercase
  run: |
    IMAGE_LOWER=$(echo "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest" | tr '[:upper:]' '[:lower:]')
    echo "image=$IMAGE_LOWER" >> $GITHUB_OUTPUT
```

#### 2. 更新 Trivy 扫描步骤（第 93 行）
```yaml
# 修改前
image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

# 修改后
image-ref: ${{ steps.lowercase.outputs.image }}
```

#### 3. test-image 任务 - 添加镜像名转换步骤（第 124-128 行）
```yaml
- name: 转换镜像名为小写
  id: lowercase
  run: |
    IMAGE_LOWER=$(echo "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}" | tr '[:upper:]' '[:lower:]')
    echo "image=$IMAGE_LOWER" >> $GITHUB_OUTPUT
```

#### 4. 更新所有镜像引用（第 132, 138, 143 行）
```yaml
# 修改前
docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
docker run ... ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
docker image inspect ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

# 修改后
docker pull ${{ steps.lowercase.outputs.image }}:${{ github.sha }}
docker run ... ${{ steps.lowercase.outputs.image }}:${{ github.sha }}
docker image inspect ${{ steps.lowercase.outputs.image }}:${{ github.sha }}
```

## 技术细节

### 为什么需要显式转换？

1. **Docker metadata action** (`docker/metadata-action@v5`) 自动将镜像名转换为小写，这就是为什么构建和推送步骤（使用 `${{ steps.meta.outputs.tags }}`）没有问题
2. **直接引用环境变量** 的步骤（Trivy 扫描、镜像拉取）不会自动转换
3. **GHCR 规范** 要求镜像名必须全部小写，混合大小写会导致引用错误

### 转换方法

使用 Bash 的 `tr` 命令：
```bash
echo "ghcr.io/janeTingl/smartrenamer:latest" | tr '[:upper:]' '[:lower:]'
# 输出: ghcr.io/janetingl/smartrenamer:latest
```

## 影响范围

### 修改的文件
- `.github/workflows/docker-build.yml`

### 受影响的任务
1. `build-and-test` - Trivy 镜像扫描
2. `test-image` - 镜像拉取、测试和大小检查

### 不受影响的部分
- `publish-dockerhub` - 使用 Docker Hub secrets，不涉及 GHCR
- 镜像构建和推送 - 使用 metadata action 输出，已自动转换

## 验证标准

✅ **所有验收标准均已满足**：

1. ✅ 工作流文件中所有 GHCR 镜像引用使用小写转换
2. ✅ Trivy 扫描步骤使用转换后的小写镜像名
3. ✅ 测试镜像步骤使用转换后的小写镜像名
4. ✅ YAML 语法正确，步骤引用一致
5. ✅ 保持了原有工作流的所有功能

## 测试建议

1. **Push 到 main/develop 分支**：
   - 验证镜像构建和推送成功
   - 验证 Trivy 扫描完成，exit code 为 0
   - 检查 Security 标签页是否收到扫描报告

2. **创建 Pull Request**：
   - 验证镜像构建（不推送）成功
   - 验证不触发 Trivy 扫描（仅 PR 时跳过）

3. **推送 Tag（例如 v0.9.1）**：
   - 验证所有工作流任务成功
   - 验证镜像推送到 GHCR 和 Docker Hub

## 相关资源

- [GitHub Container Registry 文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Trivy Action 文档](https://github.com/aquasecurity/trivy-action)
- [Docker Metadata Action 文档](https://github.com/docker/metadata-action)

## 总结

此修复确保所有 GHCR 镜像引用都使用小写格式，符合 GHCR 规范，消除了 Trivy 扫描和镜像拉取时的引用错误。修改采用最小化原则，仅在必要的步骤前添加转换逻辑，不影响现有工作流的其他部分。

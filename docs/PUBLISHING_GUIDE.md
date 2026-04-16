# Selfclaw 发布指南

本文档描述如何将Selfclaw发布到NPM和PyPI。

## 发布前准备

### 1. 准备工作

#### 1.1 账号准备
- [ ] 注册PyPI账号：https://pypi.org/account/register/
- [ ] 注册NPM账号：https://www.npmjs.com/signup
- [ ] 配置PyPI API Token
- [ ] 配置NPM认证

#### 1.2 测试环境
- [ ] 确保所有测试通过
- [ ] 验证包结构完整
- [ ] 测试CLI命令正常工作
- [ ] 验证文档完整

### 2. 包发布步骤

#### 2.1 发布到PyPI

```bash
# 安装发布工具
pip install build twine

# 构建包
cd package
python -m build

# 检查包
twine check dist/*

# 上传到PyPI（测试）
twine upload --repository testpypi dist/*

# 上传到PyPI（正式）
twine upload dist/*
```

#### 2.2 发布到NPM

```bash
# 登录NPM
npm login

# 构建包（如有需要）
npm run build

# 发布包（测试）
npm publish --dry-run

# 发布包（正式）
npm publish
```

### 3. 发布后验证

#### 3.1 PyPI验证
```bash
# 从PyPI安装
pip install selfclaw

# 测试安装
selfclaw --version

# 测试功能
selfclaw --help
```

#### 3.2 NPM验证
```bash
# 从NPM安装
npm install -g selfclaw

# 测试安装
selfclaw --version

# 测试功能
selfclaw --help
```

## 包体积优化

### 当前包大小
- Python包：~10MB（不含后端和前端源码）
- NPM包：~5MB（仅CLI工具）

### 优化措施
1. 精简依赖：只包含必要的依赖包
2. 使用MANIFEST.in排除不必要的文件
3. 分离后端和前端为可选依赖
4. 使用wheel格式提供二进制包

## 发布检查清单

### 代码质量
- [ ] 所有代码通过语法检查
- [ ] 没有明显的bug
- [ ] 遵循代码风格规范

### 文档完整性
- [ ] README.md完整
- [ ] API文档齐全
- [ ] 安装说明清晰
- [ ] 使用示例可用

### 测试覆盖
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] CLI功能测试通过
- [ ] 跨平台测试（Windows/Linux/macOS）

### 安全检查
- [ ] 没有硬编码敏感信息
- [ ] 依赖包安全性检查
- [ ] 许可证信息正确

## 版本管理

### 版本号规则
- 遵循语义化版本（Semantic Versioning）
- 格式：主版本.次版本.修订版本（MAJOR.MINOR.PATCH）
- 示例：1.0.0, 1.0.1, 1.1.0, 2.0.0

### 发布频率
- 主版本：重大功能变更或不兼容更新
- 次版本：新功能或重要改进
- 修订版本：bug修复或小改进

## 发布流程

### 开发阶段
1. 在develop分支开发新功能
2. 编写测试和文档
3. 提交代码并创建PR

### 测试阶段
1. 合并到main分支
2. 进行全面测试
3. 更新版本号
5. 创建发布说明

### 发布阶段
1. 构建发布包
2. 测试发布包
3. 发布到PyPI和NPM
4. 验证安装
5. 更新文档

## 故障排查

### PyPI发布失败
- 检查包名是否已存在
- 验证API Token是否正确
- 检查包文件是否有效

### NPM发布失败
- 检查包名是否已存在
- 验证登录状态
- 检查package.json格式

## 参考资源

- PyPI发布文档：https://packaging.python.org/tutorials/packaging-projects/
- NPM发布文档：https://docs.npmjs.com/cli/v7/commands/npm-publish
- 语义化版本：https://semver.org/lang/zh-CN/

---

最后更新：2026-04-16
版本：1.0.0
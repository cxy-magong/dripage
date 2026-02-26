# Dripage 文件清理指南

## 📌 可以删除的文件/目录

### 运行时生成（必须删除或忽略）

```
✅ 可以删除：
├── __pycache__/              # Python 字节码缓存
├── dripage.egg-info/         # Python 包信息（构建生成）
├── .venv/                    # 虚拟环境（已忽略）
├── output/                   # 输出目录（运行时生成）
├── test_project/             # 测试项目（临时）
└── config/__pycache__/       # 字节码缓存
```

### 配置文件（根据情况）

```
⚠️  需要判断：
├── .env                      # 本地环境变量（包含敏感信息，不要提交）
├── config/dripage_session.yaml  # 会话配置（用户级别，不应提交）
└── config/dripage_default.yaml  # 默认配置（可以考虑提交，作为团队默认值）
```

---

## 📦 可以提交的文件/目录

### 新增的实现文件

```
✅ 应该提交：
├── cli_config.py             # 配置管理核心逻辑（已修改）
├── cli.py                    # CLI 入口（已修改）
├── IMPLEMENTATION_SUMMARY.md  # 实现文档
├── .dripage.example          # 项目配置示例
└── CONFIG_CLEANUP.md         # 本文档
```

### 配置示例和文档

```
✅ 可以提交（建议）：
├── .dripage.example          # 项目配置模板（✅ 新增，强烈推荐提交）
├── config/browsers.yaml      # 浏览器配置（如果团队共用）
├── config/browser/*.ini      # 浏览器 INI 配置（如果团队共用）
└── docs/*                   # 文档
```

---

## 🚫 不应提交的文件/目录（已在 .gitignore 中）

```
❌ 不要提交（已忽略）：
├── .venv/
├── __pycache__/
├── output/
├── *.py[oc]
├── build/
├── dist/
├── wheels/
├── *.egg-info
├── *.log
├── .env
└── worktrees
```

---

## 🔍 需要额外处理的文件

### 1. 用户级配置（不应提交）

```
~/.dripage/
  └── current_app            # 用户级配置（不应提交）
```

**处理方式：**
- 在 `.gitignore` 中添加：`~/.dripage/`
- 如果提交了，使用 `git rm --cached` 移除

---

### 2. 运行时生成的配置文件

```
config/dripage_session.yaml  # 会话配置（运行时生成）
```

**处理方式：**
- 添加到 `.gitignore`
- 不应提交

---

### 3. 项目级配置示例

```
.dripage/example             # 配置示例（可以提交）
.dripage/config             # 实际配置（不应提交）
```

**处理方式：**
- 提交 `.dripage/example`
- 在 `.gitignore` 中添加：`.dripage/config`
- 用户复制 `example` 为 `config`

---

## 📝 推荐的 .gitignore 更新

```gitignore
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv
output/
*.log
worktrees

# Environment variables
.env

# 运行时配置
config/dripage_session.yaml
config/__pycache__/

# 用户配置（项目级）
.dripage/config
~/.dripage/

# 临时文件
test_project/
*.tmp
*.bak
```

---

## 🎯 立即可以删除的文件

```bash
# 删除临时测试项目
rm -rf test_project/

# 删除缓存
rm -rf __pycache__/
rm -rf dripage.egg-info/

# 删除运行时配置（可选）
rm config/dripage_session.yaml
```

---

## 📋 提交清单

### 需要提交的新文件

```
✅ 必须提交：
├── cli_config.py             # 已修改
├── cli.py                    # 已修改
├── IMPLEMENTATION_SUMMARY.md  # 新增文档
├── .dripage.example          # 新增配置示例
└── CONFIG_CLEANUP.md         # 本文档
```

### 可选提交的文件

```
⭕ 可选提交：
├── config/dripage_default.yaml  # 团队默认配置
├── config/browsers.yaml         # 如果团队共用
└── README.md                  # 更新使用说明
```

### 不应提交的文件

```
❌ 不要提交：
├── .env
├── config/dripage_session.yaml
├── .dripage/config（实际配置）
└── test_project/
```

---

## 🚀 快速清理命令

```bash
# 1. 删除临时文件
rm -rf test_project/ __pycache__/ dripage.egg-info/

# 2. 提交代码
git add cli_config.py cli.py IMPLEMENTATION_SUMMARY.md .dripage.example
git commit -m "feat: implement multi-level configuration system"

# 3. 更新 .gitignore
git add .gitignore
git commit -m "chore: update gitignore for runtime files"
```

---

## ⚡ 总结

| 类型 | 文件/目录 | 操作 |
|------|-----------|------|
| ✅ 提交 | `cli_config.py`, `cli.py` | Git add & commit |
| ✅ 提交 | `IMPLEMENTATION_SUMMARY.md` | Git add & commit |
| ✅ 提交 | `.dripage.example` | Git add & commit |
| ⭕ 可选 | `config/dripage_default.yaml` | 团队默认值 |
| ❌ 删除 | `test_project/` | `rm -rf` |
| ❌ 删除 | `__pycache__/` | `rm -rf` |
| ❌ 忽略 | `.env` | 已在 .gitignore |
| ❌ 忽略 | `config/dripage_session.yaml` | 添加到 .gitignore |

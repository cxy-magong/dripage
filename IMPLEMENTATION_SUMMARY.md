# Dripage 多级配置架构 - 实现总结

## 实现日期
2024-02-26

## 核心特性

### 1. 多级配置优先级

```
优先级（从高到低）：
1. DRIPAGE_BROWSER 环境变量         ← 最高优先级
2. 项目配置 (.dripage/config)        ← 项目级默认
3. 用户配置 (~/.dripage/current_app) ← 用户级默认
4. 全局配置 (dripage_default.yaml)   ← 最低优先级
```

### 2. 支持的场景

#### 场景1：不同项目自动使用不同浏览器
```bash
# 项目A
cd G:\code\crawler_prod
# .dripage/config: browser: browser1
dripage get http://example.com  # 自动使用 browser1

# 项目B
cd G:\code\scraper_amazon
# .dripage/config: browser: browser2
dripage get http://amazon.com   # 自动使用 browser2
```

#### 场景2：同一项目不同终端使用不同浏览器
```bash
# Terminal 1 - 使用项目默认 (browser1)
cd G:\code\crawler_prod
dripage get http://example.com

# Terminal 2 - 覆盖为 browser2
cd G:\code\crawler_prod
set DRIPAGE_BROWSER=browser2
dripage get http://example.com  # 使用 browser2

# Terminal 3 - 覆盖为 browser3
cd G:\code\crawler_prod
set DRIPAGE_BROWSER=browser3
dripage get http://example.com  # 使用 browser3
```

### 3. 新增CLI命令

```bash
# 查看当前配置
dripage config show

# 验证项目配置
dripage config validate
```

### 4. 配置文件格式

#### 项目级配置 (.dripage/config)
```yaml
app_id: crawler_prod
browser: browser1
output:
  directory: G:\code\crawler_prod\output
vision:
  model: glm-4v-flash
```

### 5. DeepAgents 会话支持

DeepAgents 每次执行 Bash 工具时都是独立进程，环境变量不会持久化。

**解决方案：**
```bash
# 启动 deepagents 前设置环境变量
export DRIPAGE_BROWSER=browser2
deepagents  # 整个会话期间都有效
```

## 修改的文件

### 1. cli_config.py
- 重构 `get_current_config()` 实现多级优先级
- 新增 `_load_project_config()` 加载项目配置
- 新增 `_load_user_app_config()` 加载用户配置
- 新增 `_load_browser_config_by_name()` 按名称加载浏览器配置
- 新增 `_get_config_source()` 获取配置来源信息
- 新增 `validate_project_config()` 验证项目配置

### 2. cli.py
- 新增 `config show` 命令
- 新增 `config validate` 命令
- 新增 `config init` 命令

## 测试结果

✅ 环境变量优先级正确
✅ 项目配置正确加载
✅ 全局默认兜底正确
✅ 配置来源信息正确显示
✅ .dripage/config 文件格式正确

## 使用示例

### 示例1：创建项目配置
```bash
cd G:\code\my_project
mkdir .dripage
cat > .dripage/config <<EOF
app_id: my_project
browser: browser2
EOF
```

### 示例2：验证配置
```bash
dripage config show
```

输出：
```
Current Configuration:

  Source: project
    Detail: G:\code\my_project\.dripage\config

  Browser: browser2 @ 127.0.0.1:19000
  App ID: my_project

  Working Directory:
    G:\code\my_project
```

### 示例3：临时覆盖
```bash
set DRIPAGE_BROWSER=browser1
dripage get http://example.com
```

## 优势

✅ **零配置启动** - 进入项目目录自动使用配置的浏览器
✅ **项目隔离** - 每个项目独立配置，互不干扰
✅ **层次清晰** - 环境 > 项目 > 用户 > 默认
✅ **易于调试** - `config show` 查看配置来源
✅ **团队协作** - `.dripage/config` 可提交到 Git
✅ **并发安全** - 不同项目并发运行，各自使用不同浏览器
✅ **灵活覆盖** - 环境变量可临时覆盖任何配置

## .gitignore 配置

```
# .gitignore
.dripage/
  !.dripage/config
```

**说明：** 只提交 `config` 文件，忽略 `.dripage` 目录下的其他临时文件

## 注意事项

1. **DeepAgents 会话**：需要在启动 deepagents 前设置环境变量
2. **配置优先级**：环境变量会覆盖项目配置
3. **配置文件格式**：YAML 格式，需要正确缩进
4. **浏览器名称**：必须在 `config/browsers.yaml` 中定义

## 未来扩展

- [ ] 配置模板支持
- [ ] 配置继承
- [ ] 动态配置（基于负载）
- [ ] 配置版本控制
- [ ] 图形化配置管理器

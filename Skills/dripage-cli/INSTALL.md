# Dripage CLI Skill 安装说明

## 当前安装方式

已使用 **Windows Junction 目录链接**，将 opencode 技能目录链接到项目源代码：

- **源目录**: `G:\code\agent-use\dripage\Skills\dripage-cli`
- **链接位置**: `C:\Users\mg\.config\opencode\skills\dripage-cli`
- **链接类型**: Junction（无需管理员权限）

## 优势

✅ **自动同步** - 修改源目录中的文件会立即反映到 opencode
✅ **无需重复安装** - 一次安装，永久生效
✅ **无需管理员权限** - Junction 不需要提升权限
✅ **节省磁盘空间** - 不会复制文件

## 验证链接

```bash
# 查看链接类型和目标
powershell -Command "Get-Item 'C:\Users\mg\.config\opencode\skills\dripage-cli' | Select-Object LinkType, Target"
```

预期输出：
```
LinkType Target
-------- ------
Junction {G:\code\agent-use\dripage\Skills\dripage-cli}
```

## 更新技能

修改 `Skills/dripage-cli/` 目录下的任何文件后，会自动同步到 opencode，无需额外操作。

### 示例

```bash
# 修改源文件
vim Skills/dripage-cli/SKILL.md

# 自动生效，无需重新安装！
# opencode 中看到的会是最新版本
```

## 重新安装（如果链接损坏）

如果链接损坏或需要重新安装，运行：

```bash
# Windows
install_skill.bat

# 或手动创建链接
powershell -Command "Remove-Item -Path 'C:\Users\mg\.config\opencode\skills\dripage-cli' -Recurse -Force"
powershell -Command "New-Item -ItemType Junction -Path 'C:\Users\mg\.config\opencode\skills\dripage-cli' -Target 'G:\code\agent-use\dripage\Skills\dripage-cli'"
```

## 删除链接

如果需要移除技能安装：

```bash
# 删除链接（不会删除源文件）
powershell -Command "Remove-Item -Path 'C:\Users\mg\.config\opencode\skills\dripage-cli' -Recurse -Force"
```

## 注意事项

⚠️ **不要手动删除链接目录中的文件** - 这会删除源文件
⚠️ **不要在链接目录中编辑文件** - 虽然可以，但建议在源目录编辑
⚠️ **Junction 限制** - 只能在本地文件系统上使用，不支持网络驱动器

## Windows 文件系统链接类型

| 类型 | 说明 | 是否需要管理员 | 适用场景 |
|------|------|----------------|----------|
| **Junction** | 目录硬链接（用于本例） | ❌ 否 | 本地目录链接 |
| Symbolic Link | 软链接 | ✅ 是 | 文件和目录 |
| Hard Link | 文件硬链接 | ❌ 否 | 文件（不能用于目录） |

本技能使用 **Junction**，因为：
- 不需要管理员权限
- 适合本地目录链接
- 性能好，透明度高

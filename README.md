# Clawd Plana Theme

Plana desk-pet theme for [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk).

这是一个可直接移植到 Clawd on Desk 的 Plana 桌宠主题包。仓库包含运行时主题文件、构建参考资料和 QA 预览图。

## 这是什么

- 主题名称：`Clawd Plana`
- 主题目录：`clawd-plana`
- 运行格式：Clawd on Desk `theme.json` + APNG 动画资源
- 画布尺寸：`266x200`
- 动画资源：34 个 APNG 文件
- 当前版本：`1.1.3`
- 动画帧率：50 ms/frame，约 20 fps
- Windows 安装目标：`%APPDATA%\clawd-on-desk\themes\clawd-plana`

可直接移植的主题文件在：

```text
themes/
  clawd-plana/
    theme.json
    assets/
      *.apng
```

## 如何移植到 Clawd on Desk

1. 关闭 Clawd on Desk，或准备在复制后重启它。
2. 将本仓库的 `themes/clawd-plana` 复制到 Clawd on Desk 用户主题目录：

```powershell
$repoTheme = ".\themes\clawd-plana"
$target = "$env:APPDATA\clawd-on-desk\themes\clawd-plana"
New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
if (Test-Path $target) { Remove-Item $target -Recurse -Force }
Copy-Item $repoTheme $target -Recurse
```

3. 重新打开 Clawd on Desk。
4. 进入 `Settings... -> Theme`。
5. 选择 `Clawd Plana`。

不要覆盖应用安装目录里的内置 Clawd 主题。本主题应作为额外的用户主题安装。

## 仓库结构

```text
themes/clawd-plana/
  可直接复制到 Clawd on Desk 用户主题目录的运行时主题。

docs/qa/
  浅色和深色背景的视觉检查图。

docs/source-generated/
  早期生成中间图和动作条，仅保留作参考。

docs/source-original/
  原 Codex pet 元数据和参考 spritesheet。

tools/build_clawd_plana.py
  本地资产流水线的重建脚本，仅作复现参考。
```

## 重建说明

移植安装不需要 Python，也不需要运行构建脚本。Clawd on Desk 只需要 `themes/clawd-plana/theme.json` 和 `themes/clawd-plana/assets`。

`tools/build_clawd_plana.py` 包含原工作机上的本地路径假设，主要用于记录生成方式；如果在其他机器上重建，需要先调整脚本中的源路径。

## 质量目标

当前版本按接近内置 Clawd 主题的体验整理：

- APNG 输出约 20 fps。
- 动作数量和帧数高于初版。
- 工作动作按稳定角色高度重建，降低人物模型忽大忽小的问题。
- 工作动作使用稳定角色层和固定道具层合成，降低电脑、箱子、扫帚等道具忽远忽近的问题。
- 跑步派生动作已替换为站立任务动作，避免角色前后冲刺造成忽大忽小。
- 帧间过渡使用光流中间帧，减少关键姿势硬切。
- 清理绿幕边缘，减少绿色溢色。
- `docs/qa/dark-contact-sheet.png` 用于检查深色背景下的边缘质量。
- `docs/qa/working-motion-strip.png` 用于检查工作动作的衔接和模型稳定性。
- `docs/qa/all-motion-strip.png` 用于检查全量动作的抽帧连续性。

## Credits / 说明

- Clawd on Desk: https://github.com/rullerzhou-afk/clawd-on-desk
- Plana / Blue Archive belongs to its respective rights holders.

This is an unofficial fan-made theme and is not affiliated with, endorsed by, or sponsored by the Clawd on Desk project or the Blue Archive rights holders.

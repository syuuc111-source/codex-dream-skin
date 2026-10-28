# Codex Dream Skin 中文覆盖包

Windows Codex 皮肤技能的中文说明和 UI 元数据。

这是独立公开仓库，只包含 **codex-dream-skin**。完整技能说明见 [overlays/codex-dream-skin/SKILL.md](overlays/codex-dream-skin/SKILL.md)。

## 获取仓库

需要 Git 和 PowerShell。

```powershell
git clone https://github.com/syuuc111-source/codex-dream-skin.git
cd codex-dream-skin
```

## 安装中文覆盖包

这是单技能的中文覆盖包，必须和固定版本上游完整技能合成。以下命令下载上游，在临时目录合成后安装；已有安装会拒绝覆盖。它不运行 Blender 或皮肤安装器。

```powershell
$name = 'codex-dream-skin'
$deps = Get-Content -LiteralPath '.\dependencies.json' -Raw | ConvertFrom-Json
$spec = $deps.$name
$stageRoot = Join-Path ([IO.Path]::GetTempPath()) ('codex-skill-' + [guid]::NewGuid().ToString('N'))
$checkout = Join-Path $stageRoot 'source'
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$skillRoot = Join-Path $codexRoot 'skills'
$destination = Join-Path $skillRoot $name
if (Test-Path -LiteralPath $destination) { throw "请先备份并移走已有技能：$destination" }
New-Item -ItemType Directory -Force -Path $stageRoot,$skillRoot | Out-Null
git clone --filter=blob:none --no-checkout $spec.url $checkout
if ($LASTEXITCODE -ne 0) { throw 'clone 失败' }
git -C $checkout checkout --detach $spec.commit
if ($LASTEXITCODE -ne 0) { throw 'checkout 失败' }
$upstreamSkill = Join-Path $checkout (Split-Path $spec.entry -Parent)
$merged = Join-Path $stageRoot $name
Copy-Item -LiteralPath $upstreamSkill -Destination $merged -Recurse
Get-ChildItem -LiteralPath (Join-Path '.\overlays' $name) -Force | Copy-Item -Destination $merged -Recurse -Force
Copy-Item -LiteralPath (Join-Path '.\licenses' ($name + '.txt')) -Destination (Join-Path $merged 'LICENSE.txt')
Copy-Item -LiteralPath $merged -Destination $destination -Recurse
```

应用皮肤可能关闭或重启 Codex；在明确请求应用时再按上游技能执行。

## 使用

客户端重新加载技能或新建会话后：

```text
$codex-dream-skin 检查 Windows 环境，说明应用与恢复皮肤的步骤。
```

## 检查

需要 Python 3.9+。

```powershell
python scripts/validate.py
```

校验覆盖文件头、来源清单、文档链接和机器专用路径；实际领域运行需对应的软件与数据。本次拆分没有执行建模、渲染、皮肤应用或收费 API。

## 许可与来源

[MIT](LICENSE) · [第三方声明](THIRD_PARTY.md)。来源及安装依赖独立保留，不把上游项目称作原创。

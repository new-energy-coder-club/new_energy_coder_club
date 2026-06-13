---
name: agentic-loop
description: 管理 Claude Code Agentic Loop 防护。控制每次对话的工具调用上限（默认25次）与连续重复命令检测（默认5次）。用户说"loop上限""循环次数""agentic loop""防止循环""重复调用"时使用。
---

# Agentic Loop 防护管理

用途：读取或修改 `~/.claude/settings.json` 中的 Agentic Loop 防护钩子，支持查看状态、调整阈值、启用/禁用、重置计数。

## 用法

```
/agentic-loop [子命令] [参数]
```

子命令省略时默认执行 `status`。

## 子命令

### status（默认）

查看当前配置状态。

读取 `~/.claude/settings.json`，检查 `hooks.UserPromptSubmit` 和 `hooks.PreToolUse` 是否存在，提取当前阈值并展示：

- Loop 防护是否启用
- 工具调用总上限（max）
- 连续重复检测阈值（repeat）
- 临时计数文件路径示例

### set

调整阈值，至少提供一个参数：

- `--max <N>`：工具调用总上限（正整数，建议 10–100）
- `--repeat <N>`：连续相同命令阈值（正整数，建议 3–10）

执行步骤：
1. 读取 `~/.claude/settings.json`
2. 在 `PreToolUse` hook 的 command 字符串中，将 `s.count>当前值` 替换为 `s.count><N>`，将 `s.repeat>=当前值` 替换为 `s.repeat>= <N>`
3. 写回文件
4. 输出修改前后对比

示例：
```
/agentic-loop set --max 40 --repeat 3
```

### disable

临时禁用 Loop 防护（不删除，仅注释掉 hooks）。

执行步骤：
1. 读取 `~/.claude/settings.json`
2. 将 `hooks` 对象整体移动到 `_hooks_disabled`（重命名字段）
3. 写回文件
4. 提示"已禁用，使用 /agentic-loop enable 恢复"

### enable

恢复已禁用的 Loop 防护。

执行步骤：
1. 读取 `~/.claude/settings.json`
2. 将 `_hooks_disabled` 重命名回 `hooks`
3. 写回文件
4. 提示"已恢复，当前阈值为 max=N repeat=N"

### install

在当前 `~/.claude/settings.json` 中安装完整的 Agentic Loop 防护钩子（适合首次配置或钩子丢失时）。

执行步骤：
1. 读取 `~/.claude/settings.json`（不存在则创建 `{}`）
2. 检查 `hooks` 是否已存在，若已存在则询问用户是否覆盖
3. 写入以下两个钩子（保留文件其他字段）：

**UserPromptSubmit**（重置计数器）：
```
node -e "let b='';process.stdin.on('data',c=>b+=c);process.stdin.on('end',()=>{let d={};try{d=JSON.parse(b);}catch(e){}const sid=d.session_id||'default';const f=(process.env.TEMP||'C:/Users/29711/AppData/Local/Temp').replace(/\\\\/g,'/')+'/claude-loop-'+sid+'.json';require('fs').writeFileSync(f,JSON.stringify({count:0,last_sig:'',repeat:0}));});"
```

**PreToolUse**（计数 + 双重阻断）：
```
node -e "let b='';process.stdin.on('data',c=>b+=c);process.stdin.on('end',()=>{const fs=require('fs');let d={};try{d=JSON.parse(b);}catch(e){}const sid=d.session_id||'default';const tmp=(process.env.TEMP||'C:/Users/29711/AppData/Local/Temp').replace(/\\\\/g,'/');const f=tmp+'/claude-loop-'+sid+'.json';let s={count:0,last_sig:'',repeat:0};try{s=JSON.parse(fs.readFileSync(f,'utf8'));}catch(e){}const sig=(d.tool_name||'')+'|'+(d.tool_input?JSON.stringify(d.tool_input):'');if(sig===s.last_sig){s.repeat++;}else{s.repeat=1;s.last_sig=sig;}s.count++;fs.writeFileSync(f,JSON.stringify(s));if(s.count>25){console.log(JSON.stringify({continue:false,stopReason:'已达到 Agentic Loop 上限（25次工具调用），请重新提问'}));}else if(s.repeat>=5){console.log(JSON.stringify({continue:false,stopReason:'检测到重复调用（连续'+s.repeat+'次相同命令），已自动停止，请调整思路后重新提问'}));}});"
```

4. 提示"安装成功，重启 Claude Code 生效"

### reset `<session_id>`

手动清零指定 session 的计数器（调试用）。

执行步骤：
1. 构造文件路径：`$TEMP/claude-loop-<session_id>.json`
2. 写入 `{"count":0,"last_sig":"","repeat":0}`
3. 输出确认

## 规则

- 所有操作必须先读取文件再写入，禁止整体替换
- 写入前验证 JSON 合法性（用 `node -e "JSON.parse(...)"` 验证）
- 路径中的反斜杠统一转为正斜杠
- 阈值修改只替换 command 字符串中的数字，不重写整个 hooks 结构
- 操作完成后输出简洁的前/后对比，不要冗余说明

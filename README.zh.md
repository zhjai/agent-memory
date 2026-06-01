# agent-memory

<p align="center">
  <img src="assets/banner.svg" alt="agent-memory — 面向 AI agent 的治理层记忆，一道按权限隔离的信任边界，而非检索引擎" width="100%">
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>中文</strong>
</p>

<p align="center">
  <img alt="skill" src="https://img.shields.io/badge/agent--skill-agent--memory-1f6feb">
  <img alt="version" src="https://img.shields.io/badge/version-0.1.0-informational">
  <img alt="works with" src="https://img.shields.io/badge/Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20any%20agent-444">
  <img alt="no backend" src="https://img.shields.io/badge/no%20vector%2Fgraph-files%20only-2ea043">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-yellow"></a>
</p>

> **面向 AI agent 的治理层记忆（governance-layer memory）** —— 三个按权限隔离的层，让 agent 能把规则、状态、lesson（经验）跨任务带下去，却**无法改写自己的权限来源**。它不是检索引擎，而是一道信任边界。可在**任何**任务、**任何** agent（Claude Code、Codex 等）上**独立**使用。

主流 agent 记忆产品（Mem0、Zep、Letta、LangMem）优化的是**检索质量** —— 向量 / 图 / 时序召回 —— 并默认 agent 是配合的。`agent-memory` 解决的是另一个、通常被忽略的问题：**目标驱动的 agent 会悄悄降级或改写挡在它"宣布任务完成"路上的"记忆"。** 它的核心是**谁能写什么**，而不是怎么嵌入。

纯文件 + 一次权限切分。Agent 无关、可移植、零检索依赖。**可以单独使用** —— 你不需要任何"完成度校验"机制，就能享受到跨运行携带规则 / 状态 / lesson 的好处。

## 它防的那个失败（30 秒）

一个目标驱动的 agent 在任务中途，发现某条稳定规则碍事，就"更新"了它 —— 或者提拔了一条对自己有利、却削弱了未来检查的 lesson。在普通记忆里（一切皆可写），这会悄无声息地成功。

```
有了 agent-memory（control/ 只读，lessons 需评审）：
  agent 改 control/rules.md             → 拒绝（只读挂载）
  agent 写 approved_lessons/            → 拒绝（只有 candidate_lessons/ 可写）
  候选 lesson "下次跳过 case 检查"          → 保持 PENDING；永远不会作为权威自动生效
```

agent 可以记录*提案*，但无法改写自己的权限来源，也无法自我批准一条 lesson。`control/` 是信任边界；`state/` 只是它的草稿纸。见 [`examples/`](examples/)。

## 三个层（按权限划分，而非按内容）

```
🔒 control/   对 worker 只读（由人 / CI 维护）
   rules.md                 agent 必须遵守、不能编辑的稳定规则
   approved_lessons/        已评审、已提拔的 lesson
     index.yaml             摘要优先的索引

✍️ state/     worker 可写，但不是真相来源
   tasks/<task_id>/
     run_state.yaml         任务检查点（是"信念"，不是真相）—— 不是跨任务知识
     decision_log.md        任务过程中的决策 / 风险
     candidate_lessons.md   新观察到的 lesson，PENDING 待评审（不能自我批准）
```

**不变量（invariants）：**
- Worker **不能写 `control/`** —— 把它挂成 `read_only`（Claude Code 子 agent 记忆 / Managed Agents 记忆库在文件系统层面区分 read_only 与 read_write，直接用它，别自己造）。
- `state/` 是**工作记忆，不是真相**（`run_state` = "agent 认为自己做了什么"）。
- 新 lesson 进 `candidate_lessons.md`；**提拔到 `approved_lessons/` 是一次需评审的动作 —— worker 只能提案，永不自我批准。**
- 提拔**不能削弱强制力** —— 完成度的真相来源（[`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) 里的 gate、manifest、verifier prompt）不在 lesson 提拔可触达的范围内。

## 独立使用（任何任务，不只长任务）

你不需要 gate 或长任务机制：
1. `resume-context` 在开始时读 `control/rules.md`（如项目命名约定）。
2. 过程中把决策写进 `state/.../decision_log.md`。
3. 收尾时，`lesson-promote` 把值得留的 lesson 归档进 `candidate_lessons.md`。

**安装足迹可证明是独立的：** 把 `agent-memory` 装进一个全新项目，**不会带进任何 gate 文件、gate 配置或完成度机制** —— 只有三个层 + 两个 skill。

## Skills（流程，不是权威）

- [`resume-context`](skills/resume-context/SKILL.md) —— 在开始 / 恢复时加载 control + 任务 state；浮出活跃约束 + 相关 lesson。
- [`lesson-promote`](skills/lesson-promote/SKILL.md) —— 把观察变成提拔*提案*（worker 只提案）。

## 对比主流记忆库

我们刻意**不提供向量 / 图后端**（Mem0 被记录的弱点：多存储复杂度、schema 设计、图功能收费、厂商锁定）。lesson 用摘要优先的 frontmatter + 一个索引；只有当召回量真的需要时，再加检索。我们的价值是**治理 / 权限边界**，而非检索 —— 恰恰是主流记忆库省略掉的那一块。

## 与 agent-completion-gate 搭配

对于**长任务 / 高风险**任务，加上 [`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) —— 一个 fail-closed 的完成度 gate + 四态状态机，它读取本工具的只读 `control/`（规则 + 已批准的 lesson）作为它必须遵守的策略层，同时自带它自己受保护的检查规格。**agent-memory 是地基，可独立站立；那个 kit 是叠在上面的可选强制层。**

## 安装

```bash
npx skills add zhjai/agent-memory -g -a claude-code   # Claude Code
npx skills add zhjai/agent-memory -g -a codex          # Codex
# … 或任何其他 Agent-Skills 宿主 —— 它就是纯文件 + 一次权限切分，无厂商锁定
```

## 状态

`v0.1.0` 预览版。MIT 许可。可移植、agent 无关、基于文件、可独立使用。

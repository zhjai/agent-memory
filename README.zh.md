# agent-lessonbook

<p align="center">
  <img src="assets/banner.svg" alt="agent-lessonbook —— 给 AI 编程 agent 用的受控记忆：记录纠正与跑偏教训，但 worker 不能把自己的笔记升级成权威" width="100%">
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>中文</strong>
</p>

<p align="center">
  <img alt="version" src="https://img.shields.io/badge/version-0.3.0-informational">
  <img alt="works with" src="https://img.shields.io/badge/Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20any%20agent-444">
  <img alt="no backend" src="https://img.shields.io/badge/no%20vector%2Fgraph-files%20only-2ea043">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-yellow"></a>
</p>

> **给 AI 编程 agent 用的受控记忆。** 在长任务里记录用户的纠正、任务约束和跑偏教训——但不让 worker 把自己的笔记升级成项目权威。
>
> *项目往后要带着走的、经过评审的纠正、约束与教训——不是教程，也不是聊天记录。*

AI 编程 agent 本来就有记忆。这工具盯的是一个更窄的失败：**任务进行到一半，你纠正了 agent、或补充了一条要求——结果这条要么转头就被忘了，要么没经任何评审就悄悄变成了往后的"权威"。**

- 你说*"其实图表标题里得带上 run name"*——agent 这次照做了，下个 session 又忘了。
- agent 跑偏了，把眼前的 bug 修了，却没记下*为什么*跑偏——于是下一轮又犯。
- 更糟的是：agent 嫌某条稳定规则碍事，悄悄把它改了，而没有任何东西拦住它。

`agent-lessonbook` 就是为这些时刻准备的一个**项目本地评审队列**。worker 可以记下澄清的约束、纠正、跑偏笔记，也可以*提议* lesson。但它**不能批准自己的笔记，也不能改写项目权威**——提拔是一步人工评审。全是能像代码一样 diff、review 的纯文本文件。没有向量库、没有图数据库、没有后端。

> `agent-lessonbook` 不保证 agent 能自己可靠地发现跑偏；它是在用户、某个 verifier、一个失败的检查、或一次具体的自我观察**把跑偏暴露出来**时，把它记下来。

## 它在整条链路里的位置

你不是拿它替换现有记忆——而是在上面加一道评审边界。

- **内置 agent 记忆**（Claude Code、Codex、Copilot）：擅长召回、偏好、项目上下文。
- **记忆引擎**（Mem0、Zep、Letta、LangMem）：擅长检索、图记忆、个性化、规模化。
- **agent-lessonbook**：决定*哪些*记下来的纠正和 lesson 有资格影响未来行为——先评审，再授权。

> 大多数 memory 工具回答的是*"怎么存、怎么搜上下文?"*；`agent-lessonbook` 回答的是*"哪些记忆有资格影响未来 agent 行为?"*

## 它记什么（以及不记什么）

它只记**有证据支撑**、该带着走、且不该让 worker 自己说了算的东西——五类：

1. **用户纠正 / 验收偏好** —— "其实图表标题里得带上 run name"。
2. **跑偏根因** —— *为什么*走错了，好让下一轮别再犯。
3. **negative constraint** —— 从一次错误里学到的"以后绝不做 X"。
4. **被失败证明的 repo 坑** —— "跑测试 A 不带环境 B，会给你假的安全感"。
5. **影响权威的架构约束** —— "approved lessons 住在 `control/`，worker 不能往那写"。

它刻意**不**管这些：怎么跑测试 / 怎么验证（→ README、Makefile、CI）、项目惯例与环境配置（→ `CLAUDE.md` / `AGENTS.md` / lockfile）、任务状态与待决问题（→ `run_state.yaml`，不需评审）、你个人的输出风格（→ 内置 agent 记忆）。把日志压到高信号、值得评审的证据上，正是它的意义——一个什么都记的噪音日志会把它毁掉。

## 权限模型（谁能写什么）

```
🔒 control/   对 worker 只读（由人 / CI 维护）
   rules.md                 agent 必须遵守、不能编辑的稳定规则
   approved_lessons/        已评审、已提拔的 lesson
     index.yaml             摘要优先的索引

✍️ state/     worker 可写，但不是真相来源
   tasks/<task_id>/
     run_state.yaml         任务检查点 + 当前活跃约束（是"信念"，不是真相）
     correction_journal.md  随手记下的澄清要求 + 跑偏笔记
     candidate_lessons.md   提议的 lesson，PENDING 待人工评审（不能自我批准）
```

**不变量（invariants）：**
- Worker **不能写 `control/`** —— 把它挂成 `read_only`（Claude Code 子 agent 记忆 / Managed Agents 记忆库在文件系统层面区分 read_only 与 read_write，直接用它，别自己造）。
- `state/` 是**工作记忆，不是真相**（`run_state` = "agent 认为自己做了什么"）。
- 新 lesson 进 `candidate_lessons.md`；**提拔到 `approved_lessons/` 是一次需评审的动作 —— worker 只能提案，永不自我批准。** 提拔是人工的 git 操作，不是 worker 能触发的东西。

## Skills（流程，不是权威）

三个 skill，全是 worker 侧的流程——没有一个能授予权威：

- [`resume-context`](skills/resume-context/SKILL.md) —— 开始 / 恢复时，读 `control/` 的规则 + 已批准 lesson + 任务 state，浮出这一轮的**活跃约束**。
- [`correction-capture`](skills/correction-capture/SKILL.md) —— 当用户中途纠正 / 澄清，*或者*跑偏被暴露（被用户、一个检查、或一次具体的自我观察）时，记进 `state/.../correction_journal.md`：本该怎样、实际怎样、大概原因、怎么预防。
- [`lesson-propose`](skills/lesson-propose/SKILL.md) —— 收尾时把日志整理成*候选* lesson 供评审，按目标层级分类。**只提案，绝不提拔。**

提拔（候选 → `approved_lessons/` 或 `rules.md`）刻意**不做成 skill**——它是 git 里的一步人工评审，这样 worker 永远没法靠调工具够到权威。

## 快速上手

```bash
npx skills add zhjai/agent-lessonbook -g -a claude-code   # 也可 -a codex、cursor…… 任何宿主
```

长任务里的典型循环：

1. **开始：** `resume-context` 加载规则 + 已批准 lesson + 上次的任务 state，并列出活跃约束。
2. **任务中：** 你说*"其实导出必须带上 month 列"* → `correction-capture` 把它写进日志，并加进本轮的活跃约束，免得三步之后又忘。
3. **暴露跑偏：** 某个检查失败 / 你指出漏了东西 → `correction-capture` 记下原因 + 下次怎么避免。
4. **收尾：** `lesson-propose` 把值得留的整理进 `candidate_lessons.md`。
5. **你来评审** 这些候选，把好的提拔进 `control/`（一次普通的 git commit）。到这一步它们才算权威。

全是文件——像改任何东西一样 `git diff` 你的 `state/` 和 `control/`。没有后端要跑。

## 与 agent-completion-gate 搭配

`agent-lessonbook` 在干活**过程中**记录过程教训。[`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) 是另一个独立工具，管**收尾时的验收**（agent 不能自己宣布任务完成）。两者**相互独立**——gate 运行时不读这个 lessonbook。唯一的联系是人来牵线：你在这儿评审出的一条反复出现的 lesson，可能促使*你*去给 gate 的受保护 manifest 加一条检查。

## 状态

`v0.3.0` 预览版。MIT。可移植、agent 无关、基于文件、可独立使用。（由 `agent-memory` 改名而来。）

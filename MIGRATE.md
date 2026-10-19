# 换机 / 双机同步手册

> 本项目的全部内容（规则文档、92 篇文章、项目记忆）已在 git 私有仓库中。
> 换一台电脑只需要：clone 仓库 → 拷技能 → 重建定时任务 → 重新授权邮箱。

- **远端**：`git@github.com:hutaoer/black-ai-wechat-workflow.git`
- **最后一次同步基准**：见 `git log -1`

---

## 一、新机落地（一次性）

### 1. 克隆仓库

建议**沿用同一路径**，可免去后面改定时任务路径的麻烦：

```bash
mkdir -p ~/Sites/github && cd ~/Sites/github
git clone git@github.com:hutaoer/black-ai-wechat-workflow.git
git config core.quotepath false    # 让中文目录名正常显示，不加会显示八进制转义
```

若新机路径**确实不同**，记下实际路径，第 3 步要用。

### 2. 拷贝用户级技能

老机器上打包，拷到新机：

```bash
# 老机器
rsync -av --exclude '.DS_Store' ~/.workbuddy/skills/ /Volumes/<U盘>/skills-bak/
# 新机器
rsync -av /Volumes/<U盘>/skills-bak/ ~/.workbuddy/skills/
```

目前是 3 个：`grill-me`、`totorosir-workbuddy-score`、`workbuddy-reward-helper`。

### 3. 重建定时任务

定时任务**不随 git 走**，必须在新机手动重建。

直接把下面这段发给新机上的 WorkBuddy 即可（注意替换两处路径占位符）：

```
创建一个定时任务，配置如下：
- 名称：公众号每日选题推送
- 频率：每天 09:00（FREQ=DAILY;BYHOUR=9;BYMINUTE=0）
- 工作目录：<新机项目绝对路径>
- 状态：ACTIVE
- prompt：见下方

prompt 全文：
执行公众号每日文章工作流的第一阶段——热点选题，并把结果邮件推送给作者。工作目录 <新机项目绝对路径>。

步骤：
1) 阅读 <新机项目绝对路径>/.workbuddy/memory/automations/ 下本任务的 memory.md，避免重复推送近几日已推送过的旧话题。
2) 联网搜索今日新闻热点，只关注社会民生类话题（住房、就业、收入、教育、养老、医疗、消费、物价等）。
3) 按 WORKFLOW.md 中的选题权重打分（作者经历可关联+2、能算账+2、有逆主流判断空间+2、热度高+1），选出3个候选话题。
4) 每个候选附：话题一句话概述、建议切入角度、可用的数据锚点（需真实可查、注明来源与日期）。
5) 推送给用户并明确等待用户拍板，不要自行选题直接写稿。
6) 发送邮件：使用 Agent Mail 工具 mcp__agent-mail__SendMessage，收件人固定为 hutao06051@126.com（作者本人邮箱，已明确授权每日接收，发信时传 skip_confirmation: true 以免卡在确认环节，不得向其他任何地址发信）。主题格式「【公众号选题】M月D日 3个候选选题」，正文用 HTML，完整包含3个候选的概述／切入角度／数据锚点（含来源与日期），末尾附一句「请回复圈定哪个话题，我再进入成稿环节」。若发送失败，在正文回复中说明失败原因，不要静默跳过。

红线：不选纯娱乐八卦、刑事案件细节消费、无法核实的传言。

用户圈定某个话题后（本轮或后续对话中），严格按 STYLE_GUIDE.md 写1000字以内Markdown初稿：开头用时间场景/具体物件/直接抛事实切入，核心论证链为"数据→算账→个人经历佐证→审慎判断"，禁用清单中的AI味表达一律不用，逐条跑风格指南第九节自检清单，批现象不碰制度，成稿保存到 posts/YYYYMMDD-标题/index.md 并附上"本稿的三个关键判断"交付用户修改。
```

**两个坑**：
- 原任务 prompt 里硬编码的是 `/Users/heizi/...`，换机路径一变就必须替换，否则读不到记忆文件、成稿存错地方。
- 原 prompt 里写的是固定任务 ID 的 memory 路径（`automation-1791091700033`）。新机重建后 ID 会变，所以上面改成了"本任务的 memory.md"——**照抄这段，不要照抄老 prompt**。

### 4. 重新授权邮箱

在新机对话里连接一次 Agent Mail 连接器即可，登录态不随文件走。

---

## 二、双机日常协同

唯一的纪律：**换机前 push，落座后 pull**。

```bash
# 离开这台机器前
git add -A && git commit -m "sync: 简述改了什么" && git push

# 打开另一台机器，开工前
git pull
```

忘了 pull 就写，两边会产生分叉，届时 `git pull` 报冲突需手动解（文章文件冲突通常是两篇不同文件，很少真冲突；真冲突多半在 STYLE_GUIDE.md 这类共同维护的文件上）。

---

## 三、双机同时开着的注意事项

**两台机器都启用定时任务，每天 9 点会各跑一次，你会收到两封重复选题邮件。**

选一个：
- 只留常用那台 ACTIVE，另一台 PAUSED
- 或把其中一台改到 9:30，错开

另外，项目记忆 `.workbuddy/memory/` 是入库的，所以 A 机的记忆 pull 到 B 机后能接上；但它也意味着**记忆文件同样受 push/pull 纪律约束**——别把没 push 的记忆留在另一台机器上。

---

## 四、不要做的事

- **不要用 iCloud / 坚果云 / Dropbox 同步这个目录**。云盘和 `.git` 混用，两台同时写会产生冲突副本，有丢提交的风险。要"自动"就走 git（手动 push/pull），要"实时"就用单向拷贝。
- **不要把 `.workbuddy/` 加进 `.gitignore`**。里面是项目记忆和定时任务日志，换机同步全靠它。
- 仓库是**私有**的，里面是未发布草稿，别改成 public，也别用公共仓库镜像。

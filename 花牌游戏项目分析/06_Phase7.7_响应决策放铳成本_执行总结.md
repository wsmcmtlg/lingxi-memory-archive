# Phase 7.7 响应决策放铳成本优化 — 执行总结

> 日期：2026-09-02 | 状态：方案已确认，待执行 | 关联文档：04_AI决策系统.md（7.7 节执行后补写）

## 一、目标

在 AI 的碰/扎/招/吃四类响应决策中引入**放铳成本**评估：响应动作会让响应者获得出牌权并被迫立即打出一张牌，若此时手中无安全牌可打，响应反而制造放铳给危险家的机会，比不响应更糟。这是"两害相权取其轻"思想从出牌侧（Phase 7）向响应侧的延伸。

## 二、现状问题（已核实）

| 响应类型 | 触发时机 | 响应后动作 | 现有决策是否考虑放铳 |
|---------|---------|-----------|---------------------|
| 碰（pen） | 旁家出牌后 | 立即 `aiPickDiscard` 出一张（L3319） | 否，只看自身收益 |
| 招（zhao） | 旁家出牌后 | 招后摸牌顶，立即出一张（L3384） | 否 |
| 吃（chi） | 旁家出牌后（仅听牌旁家） | 立即出一张（L8587） | 否 |
| 扎（zha） | 自己回合摸牌后 | 扎后摸牌底，再出一张（opponentAutoPlay 内） | 否 |

## 三、设计决策（用户已确认）

1. **触发条件**：任一家旁家 `_aiEstimateOpponentHu(pi).estPoints >= 3.5` 时启用放铳成本检查（与止损模式 oppThreat 同阈值）；无危险家时保持现有积极响应，不误伤正常碰/扎/招/吃。
2. **影响方式**：响应后最安全可打牌的放铳风险 > 安全阈值 → 一票否决；否则把该风险 × 扣益系数从响应收益中扣除。

## 四、实现要点

### 4.1 新增函数

- `_aiGetResponseThreat()`：返回 `{hasThreat, maxOppHu, threatPi}`，复用 `_aiHuEstCache`，无新增性能开销。
- `_aiForcedDiscardRisk(simHand, responderIdx)`：遍历响应后手中可打牌（计数≤3），对每张按 getRiskCost 归一化公式（conf × scarcity × handPressure × passDiscount × estPoints，除以 `3.0*(e1+e2)` 固定基准）计算对**非响应者旁家**的风险，返回最安全牌 `{minRisk, safestChar}`。关键点：**排除响应者自己**（自己不会胡自己打出的牌），故不复用 getRiskCost 原函数。

### 4.2 参数

- `RESP_SAFE_LINE = 0.25`：minRisk > 0.25 判定"无安全牌可打"
- `RESP_RISK_WEIGHT = 30`：扣益系数（与 L3 中 riskCost*30 一致）

### 4.3 四类响应集成差异

| 类型 | 基准 | 处理方式 |
|------|------|---------|
| 碰 | 不碰不出牌 | minRisk>0.25 否决；否则 benefit -= minRisk×30 |
| 招 | 不招不出牌 | 同上（招后摸牌保守按不摸评估） |
| 吃 | 不吃不出牌 | 同上，扣益权重减半为 15（听牌冲刺，避免过度抑制） |
| 扎 | **不扎也要出牌** | 放铳成本 = 扎后风险 − 不扎风险（增量），仅增量>0 时扣 ×15，不一票否决 |

## 五、执行清单

1. 实现 `_aiGetResponseThreat` 与 `_aiForcedDiscardRisk`（插入 Phase 7.6 之后）
2. 碰牌集成：`_aiPenBenefit` 返回加 reject 标记 + 扣益；`_aiDecidePen` 处理 reject
3. 招牌集成：`_aiDecideZhao` 加扣益与否决
4. 吃牌集成：`_aiCheckOpponentChi` 返回 null 时并入放铳否决（权重 15）
5. 扎牌集成：`_aiDecideZha` 计算增量成本（权重 15），保留现有 P3 听牌影响检查
6. 编写 `test_ai_response_risk.js`（场景 A-F），接入 `run_all.sh`
7. 浏览器实测三场景 + 性能
8. git commit + PAT 推送 + GitHub Pages 在线版验证
9. 文档 04_AI决策系统.md 第 7.7 节 + 记忆同步

## 六、单测设计（test_ai_response_risk.js）

| 场景 | 验证点 |
|------|--------|
| A | 无危险家 → hasThreat=false，不扣益 |
| B | 有危险家 + 碰后手中有安全牌 → minRisk 低，扣少量 |
| C | 有危险家 + 碰后手中全危险 → reject=true 一票否决 |
| D | 排除自己：responderIdx=1 时风险只算 pi=2 |
| E | 扎牌增量：扎后风险>不扎扣益；否则不扣 |
| F | 安全阈值边界：0.24 放行、0.26 否决 |

## 七、验证与交付

- 回归：run_all.sh 由 9 项增至 10 项，全部通过
- 浏览器实测：危险家+无安全牌 → `_aiDecidePen` 返回 false（对照有安全牌 true）；验证排除自己逻辑；性能新增 <2ms
- 推送：commit message 含 "Phase 7.7 响应决策放铳成本"；在线版验证新函数出现次数

## 八、风险与说明

- 保守设计：阈值仅在危险家存在时启用，避免常态下 AI 不敢响应
- 吃牌扣益减半，避免削弱 Phase 6 听牌旁家吃牌能力
- 不碰拦截价值（碰掉危险家需要的牌）本次不纳入：胡牌优先于碰牌，危险家能胡就直接胡了，拦截价值有限
- 真人玩家（playerIdx=0）听牌未建模，与 Phase 7 一致（getRiskCost 体系只覆盖两家旁家 AI）

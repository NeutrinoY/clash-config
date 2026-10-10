# 双供应商最小增量配置

本目录是根目录 `Custom_Clash.ini` 的独立多供应商版本。**根目录原文件不变，Nikki 私有 Mixin 不变。**

## 设计

- `Premium`：日常主力（目前可由跑路云代测，以后换 MESL）；全部原有国家组、自动组和现有业务组的直接节点仅来自该来源。
- `Bulk`：廉价大流量辅助；只进入 `📦 大流量下载`（手动组，含 Bulk 的具体节点及 Premium 备用）和 `📦 大流量自动`（仅 Bulk 节点测速）。下载规则自动指向前者，其余业务沿用旧分流。
- 私有美国 ISP 节点及 `🛫 ISP前置` 继续由 Nikki Mixin 添加。Mixin 的前置规则优先于转换出的规则，适合保留身份敏感例外。**不要在两个位置定义同名策略组。**

## 接入步骤（占位示例，禁止把真实 URL 推送到公开仓库）

先获得两条**可由 Mihomo 原生 proxy-provider 解析的 Clash/Mihomo YAML** 订阅链接。原始节点列表或 Base64 订阅不一定能被 Provider 直接读取，须在 Nikki 中核验实际 Provider 更新是否成功。

```text
provider:Premium,tag:Premium,https://example.com/premium-clash.yaml|provider:Bulk,tag:Bulk,https://example.com/bulk-clash.yaml
```

把整个字符串进行 URL 编码，作为 SubConverter-Extended 的 `url=`；使用 `target=clash`，将 `config=` 指向：

```text
https://raw.githubusercontent.com/NeutrinoY/clash-config/main/multi-provider/Custom_Clash_Multi.ini
```

**必须保留固定标签 `Premium`、`Bulk`（区分大小写）。** 不要只拼两个未标记的 URL，也不要以节点名称或订阅源的排序替代标签。转换器支持来源标签 `tag:`、Provider 名称 `provider:` 和 `!!GROUP=` 筛选。

正式切换前，在生成的 YAML 核实：

1. `proxy-providers` 下有两个来源，能成功更新、都有节点；若原始链接格式不兼容，请优先改用机场的 Clash/Mihomo YAML 订阅。
2. `♻️ 自动选择`、六个国家组和旧业务组的直接节点只来自 Premium；`📦 大流量自动` 和 `📦 大流量下载` 的 Bulk 部分只来自 Bulk。
3. `📦 大流量下载` 手动组默认选中 `📦 大流量自动`（或手动指定 Bulk 节点），而非误选 Premium 备用。
4. Nikki Mixin 的 ISP 节点和 `🤖 AI服务` 等引用仍有效，且没有重复组名。
5. 用 Mihomo 连接日志检查下方三类测试下载实际命中的规则和出口；不满足要求时先回退旧配置。

## 下载规则维护

`rules/Bulk_Download.yaml` 是目前的精选列表：PyPI wheel 文件域名、PyTorch 下载域名、NVIDIA 下载域名。规则位于原始的部分直连规则**之后**、海外业务规则**之前**，因此已命中的前置直连与 Nikki 更高优先级例外不被覆盖。

增补规则时仅添加经过连接日志验证的**下载专用主机**；不要直接加入整个 `github.com`、`api.github.com`、`nvidia.com`、`huggingface.co` 等混合用途域名。

GitHub API 的共享 IP 限额和登录、鉴权相关请求继续使用现有业务/ISP 出口。npm 的 `registry.npmjs.org` 同时承担元数据、包获取和可能的认证操作，Hugging Face 下载可能使用签名 URL，暂不整体交给 Bulk；待实测后再分别补充精确规则。**Mihomo 依据域名等规则识别，不会自动根据下载字节数切换出口。**

更改规则文件后，等 Rule Provider 更新（当前配置 28800 秒间隔）或手动刷新 Provider；必要时重新生成配置并检查连接日志。

## 安全与回退

本目录禁止提交带 token 的订阅 URL、ISP 凭据或转换结果。公开转换服务也可能记录订阅 URL；敏感场景应自行部署转换器。

当前提交只涉及 GitHub 中的静态文件，**未更新 Nikki、未使用真实订阅执行端到端验证**。旧版链接仍指向根目录 `Custom_Clash.ini`，需要回退时恢复旧链接即可。

参考：[SubConverter-Extended 来源标签](https://github.com/Aethersailor/SubConverter-Extended/wiki/Feature-Parameters) · [官方订阅说明](https://github.com/Aethersailor/SubConverter-Extended/wiki/Remote-Subscriptions) · [Mihomo Proxy Groups](https://wiki.metacubex.one/en/config/proxy-groups/)

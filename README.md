# clash-config

宿舍路由器（OpenWrt + nikki/mihomo）用的订阅转换模板。配合 [SubConverter-Extended](https://github.com/Aethersailor/SubConverter-Extended) 的 Mihomo Provider 模式使用：后端只生成策略组和规则，节点由 mihomo 自己从机场拉取，订阅内容不经过后端。

`Custom_Clash.ini` 由 `build.py` 从上游 [Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) 的默认模板 `cfg/Custom_Clash.ini` 生成，**不要手改**。要改什么，改 `build.py`。

## 相对上游的改动

只改策略组，规则集和顺序完全沿用上游，规则内容跟着上游一起更新。

| 补丁 | 改动 | 为什么 |
|---|---|---|
| **P0 ISP 出口** | `🤖 ChatGPT`、`🤖 AI服务` 最前面加 `🇺🇸 美国ISP出口`（默认选中它）；`🚀 手动选择` 里把它放在 `♻️ 自动选择` 后面 | AI 必须用干净的美国静态 IP。`🚀 手动选择` 是大部分境外流量的出口，默认走自动选择；需要时一键切到 ISP，就能让所有流量都走美国静态 IP。ISP 出口本身由环境层（nikki Mixin / Verge 脚本）定义。这几个组是 `select`：ISP 挂了不会自己跳到别的节点（fail-closed），要换出口时手动切。 |
| **P1 聚类组** | 六个地区组换成聚类组：`🇭🇰 香港v6`（只有香港、日本、新加坡有）和 `🇭🇰 香港自动`，都是 url-test，只装倍率 ≤1x 的节点，挑最快的（v6 组只装名字带 v6 的）。香港另有 `🇭🇰 香港GIA`：只装 GIA 节点、不限倍率，卡的时候手动切过去兜底。地区组这一层 select 删掉，其他组里引用地区组的地方直接列出它的聚类组。`♻️ 自动选择` 也只装 ≤1x 的节点 | 自动组的本质就是把节点聚成一类；所有要选的地方直接列聚类组和单个节点，不用先选地区再进去选。以前 url-test 只看延迟，会自动选到 4～6 倍的 GIA，现在高倍率节点只能手动点。v6 线路便宜（0.4～0.5x），又走 IPv6 入口，所以单独成一类。分类只有这一套，环境层（如 nikki 的 ISP 前置）直接引用这些组，不另建。 |
| **P2 Premium / Bulk 分开** | 地区组、业务组里的「全部节点」只取 `Premium`。Bulk 只进 `📦 大流量下载`（select）：默认 `📦 0.01倍`，其次 `📦 0.1倍`（都是 url-test），后面是 `🚀 手动选择` 和全部 Bulk 节点。信息条目（剩余流量、套餐到期等）排除在外 | Bulk 的 IP 脏，只适合下载，不能混进日常分流。节点都不限速，优先用最便宜的。组在面板上是平铺显示的，所以只按倍率分两档，不再按地区细分。 |

倍率从节点名里的 `[x]` 读取，没写的按 1x。判断 >1x 的正则：`\[(?:[2-9]|[1-9]\d|1\.0*[1-9])`。

`build.py` 会检查每个补丁的命中次数，上游模板结构变了会直接报错，不会悄悄生成错的模板。

## 重新生成

```sh
uv run build.py            # 从上游 main 拉取并生成
uv run build.py path.ini   # 用本地的上游模板文件
```

## 订阅链接

```
https://<SCE 后端>/sub?target=clash&emoji=true&add_emoji=true
  &url=provider:Premium,tag:Premium,<跑路云 nodelist 订阅>|provider:Bulk,tag:Bulk,<赔钱机场订阅>
  &config=https://raw.githubusercontent.com/NeutrinoY/clash-config/<提交号>/Custom_Clash.ini
```

（`url` 和 `config` 需要 URL 编码。订阅链接里有 token，不要写进这个仓库。）

`config` 固定指向某一次提交，不用 `main`：SCE 后端会按地址缓存模板，用 `main` 时推送以后很久都拿不到新版本，加查询参数也绕不过去。地址一变，后端必然重新拉取，跑的是哪个版本也一目了然。改模板以后，把订阅链接里的提交号换成新的。节点不受影响：Provider 模式下，节点由 mihomo 直接从机场拉。

## 已知问题

- **空组会变成直连**：mihomo 给没有成员的组塞一个 `COMPATIBLE`，它本质是 DIRECT。如果 Premium 订阅拉取失败，地区组会变成直连。mihomo 支持 `empty-fallback: REJECT`，打算在环境层处理。上游模板也有同样的问题。
- **还没有下载分流规则**：`📦 大流量下载` 组已经有了，但还没有规则指向它。下载 / 直连规则需要单独测试后再加。

## 验证记录

2026-10-24：上游模板 → `build.py` → 本机 SCE v1.10.5 生成 → 路由器 mihomo 加载并拉取两个订阅。`⚡` 组里 >1x 的节点 0 个；香港 GIA 只出现在 `🇭🇰 香港节点`（8 个）；Bulk 节点没有混进任何 Premium 组；`🚀 手动选择`、`🤖 AI服务` 默认是 ISP 出口。

2026-10-24（`6d0548f`）：地区 select 去掉后一共 43 个组；`🚀 手动选择` 依次是 自动选择 → ISP → 10 个聚类组 → 单个节点；AI 出口 `161.77.142.144`（US）。

2026-10-24（`a9a0b91`）：asailor 后端生成 → 路由器 nikki 加载。Premium 105 个、Bulk 70 个节点；v6 组：香港 4 个、日本 6 个、新加坡 3 个；地区自动组：香港 15、日本 17、台湾 21、新加坡 7、美国 6、韩国 3；Bulk：0.01倍 5 个、0.1倍 30 个；`🚀 手动选择` 默认 `♻️ 自动选择`，AI 组默认 ISP。

# clash-config

宿舍路由器（OpenWrt + nikki/mihomo）用的订阅转换模板。配合 [SubConverter-Extended](https://github.com/Aethersailor/SubConverter-Extended) 的 Mihomo Provider 模式使用：后端只生成策略组和规则，节点由 mihomo 自己从机场拉取，订阅内容不经过后端。

`Custom_Clash.ini` 由 `build.py` 从上游 [Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) 的默认模板 `cfg/Custom_Clash.ini` 生成，**不要手改**。要改什么，改 `build.py`。

## 相对上游的改动

只改策略组，规则集和顺序完全沿用上游，规则内容跟着上游一起更新。

| 补丁 | 改动 | 为什么 |
|---|---|---|
| **P0 ISP 出口** | `🚀 手动选择`、`🤖 ChatGPT`、`🤖 AI服务` 最前面加 `🇺🇸 美国ISP出口`（默认选中它） | AI 必须用干净的美国静态 IP；同时随时可以让所有流量都走它。ISP 出口本身由环境层（nikki Mixin / Verge 脚本）定义。这几个组是 `select`：ISP 挂了不会自己跳到别的节点（fail-closed），要换出口时手动切。 |
| **P1 倍率分档** | 六个地区组从「url-test 全部节点」改成 `select`：默认是 `⚡ X自动`，后面列出该地区全部节点。`⚡ X自动` 和 `♻️ 自动选择` 只装倍率 ≤1x 的节点 | 以前 url-test 只看延迟，会自动选到 4～6 倍的 GIA。现在高倍率节点只能手动选。主人按地区切换，组内能不能连上交给健康检查。 |
| **P2 Premium / Bulk 分开** | 地区组、业务组里的「全部节点」只取 `Premium`。Bulk 只进 `📦 大流量下载`（select），默认 `📦 低倍率`（fallback：`📦 0.01倍` → `📦 0.1倍`），另有 `📦 大流量自动` 和日本 / 新加坡 / 美国 / 台湾四个地区子组，每档、每个地区都能单独选。信息条目（剩余流量、套餐到期等）排除在外 | Bulk 的 IP 脏，只适合下载，不能混进日常分流。节点都不限速，优先用最便宜的。Bulk 没有节点的地区不建组，因为空组会变成直连。 |

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
  &config=https://raw.githubusercontent.com/NeutrinoY/clash-config/main/Custom_Clash.ini
```

（`url` 和 `config` 需要 URL 编码。订阅链接里有 token，不要写进这个仓库。）

## 已知问题

- **空组会变成直连**：mihomo 给没有成员的组塞一个 `COMPATIBLE`，它本质是 DIRECT。如果 Premium 订阅拉取失败，地区组会变成直连。mihomo 支持 `empty-fallback: REJECT`，打算在环境层处理。上游模板也有同样的问题。
- **还没有下载分流规则**：`📦 大流量下载` 组已经有了，但还没有规则指向它。下载 / 直连规则需要单独测试后再加。

## 验证记录

2026-10-24：上游模板 → `build.py` → 本机 SCE v1.10.5 生成 → 路由器 mihomo 加载并拉取两个订阅。`⚡` 组里 >1x 的节点 0 个；香港 GIA 只出现在 `🇭🇰 香港节点`（8 个）；Bulk 节点没有混进任何 Premium 组；`🚀 手动选择`、`🤖 AI服务` 默认是 ISP 出口。

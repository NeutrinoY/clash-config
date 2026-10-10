# 双提供商运行模板

本目录是根目录 `Custom_Clash.ini` 的独立双提供商版本，供 SubConverter-Extended 生成 Mihomo/Nikki 配置。根目录旧模板保持不变。

## 提供商与现有分组

- `Premium`：现有主提供商（当前 NLoli 原始订阅，用户现有主力来源）。日常手动、自动、国家及业务组的直接节点只来自该来源。
- `Bulk`：赔钱机场辅助来源，只进入 `📦 大流量下载` 和 `📦 大流量自动`。大流量下载默认首先提供 Bulk 自动组，可手动选择 Bulk 具体节点或主提供商备用。
- 国内及适合直连的下载命中 `🎯 全球直连`；其他公共大文件命中大流量下载组；其余业务沿用现有分类。

用户仍可手动选择香港、日本、新加坡、台湾或其他节点。提供商来源隔离不规定地区，也不新增亚洲策略组。

美国 ISP 节点及 `🛫 ISP前置` 由 Nikki 私有 Mixin 添加。现有身份敏感和日本地区例外保留；Mixin 前置规则优先。模板引用 `🇺🇸 美国ISP出口`，因此生成结果应搭配已有 Mixin 使用，不能在两个位置重复定义同名组或节点。

## 双订阅转换

两条来源都应返回 Mihomo 可读取的 YAML。示例使用占位地址：

```text
provider:Premium,tag:Premium,https://example.com/premium-meta.yaml|provider:Bulk,tag:Bulk,https://example.com/bulk-meta.yaml
```

把整个来源字符串 URL 编码后作为 SubConverter-Extended 的 `url=`，使用 `target=clash`，`config=` 指向：

```text
https://raw.githubusercontent.com/NeutrinoY/clash-config/main/multi-provider/Custom_Clash_Multi.ini
```

保留固定的 `provider:` 名称和 `tag:` 标签 `Premium`、`Bulk`（区分大小写），模板用 `!!GROUP=^Premium$!!` 和 `!!GROUP=^Bulk$!!` 筛选来源，不按订阅排序或节点地区猜测。

当前两来源格式核查：

- NLoli 的 `subType=meta&protocol=anytls` 返回 Mihomo YAML，可作 Premium Provider。
- 赔钱机场原链接返回 Base64 节点列表；使用该来源的 `flag=meta` 格式作为 Bulk Provider。
- 不使用该来源的 `flag=clash` 格式：本次仅返回少量 SS 节点，会缺失大量 VLESS/Hysteria2 节点。

使用完整配置转换路径，不加 `list=true`。远程订阅由客户端更新；转换成功仍需核验实际 Provider 更新与节点连接。真实订阅 URL、token、ISP 凭据和生成结果只保存在用户本地，不提交仓库。

## 文件域名规则

- `rules/Download_Direct.yaml`：28 条后缀规则，覆盖 HF 文件 CDN、ModelScope、PyTorch、npm、Node、Anaconda、VS Code、NVIDIA/AMD/Intel 驱动、CUDA、Ollama/Civitai 专用文件存储和国内镜像。NVIDIA 驱动最终重定向域、AMD Adrenalin 和 Intel Arc 大型驱动均已按真实下载测试。
- `rules/Bulk_Download.yaml`：23 条后缀规则，覆盖 PyPI、Rust、GitHub 文件、Docker Layer、GHCR Blob、YouTube 视频分段、Proxmox ISO、Go Modules、Maven、JetBrains、NuGet、Discord 媒体等。YouTube `googlevideo.com` 和各宽泛 YouTube 规则之间按本模板的先命中顺序由 Bulk 接管。用户截图中的 `raw.kiko-play-niptan.one` 音频文件主机也列为 Bulk 候选；因 URL 截断，尚无同文件速度测试。

规则结合真实下载结果与平台分发架构，采用平台专用域名的 `DOMAIN-SUFFIX` 匹配，不要求各地区子域逐个测速。

HF 的 `cdn.hf.co` 覆盖 AWS/GCP 美国、欧洲、亚洲文件 CDN；官方 LFS 和 Xet 传输端点另列后缀。不把整个 `hf.co` 当文件域名，因为其中还有 Hub/协议接口。主站、GitHub API 等保留现有业务分类。

共享 R2 等存储只添加已识别的平台专用主机；不加入整个 `cloudflarestorage.com`、`amazonaws.com`、`cloudfront.net` 或 `storage.googleapis.com`。其他动态终点后续按平台用途补充。

npm、NuGet、GHCR 等存在元数据、包文件或认证同域的情况，本模板按整域选定出口；HTTPS 域名规则不能按 URL 路径自动拆开。固定来源需求可通过用户 Mixin 前置例外处理。

## 规则优先级

1. Nikki Mixin 的身份、地区及用户例外。
2. 私有地址与域名直连。
3. `Download_Direct` 文件直连。
4. 原 Aethersailor 补充直连规则。
5. `Bulk_Download` 大流量出口。
6. 原补充代理与 AI、GitHub、社交媒体等业务分类。
7. 国内及最终兜底。

文件规则位于宽泛业务分类之前，避免模型文件误入 ISP、GitHub Release 误入日常出口。驱动域名仅按 NVIDIA、AMD、Intel 实际文件域处理，不把厂商门户或通用 CDN 一并改道。

规则文件改动由 Rule Provider 更新或手动刷新生效；规则引用和组结构变动需要重新转换配置。当前两个文件规则的更新间隔为 28800 秒。

## 导入检查与回退

核对生成结果：有 `Premium`、`Bulk` 两个 Provider；主力组只引用 Premium；两个大流量组的直接来源只引用 Bulk；Nikki Mixin 的 ISP 及前置引用有效，无重复组名。

用真实连接核对 DIRECT、Bulk 和身份例外。`url-test` 的 204 测速选择可达/低延迟节点，不代表持续下载最快。两来源节点是否适合具体服务还受实际节点连接、配额和地区影响。

回退可恢复指向根目录旧 `Custom_Clash.ini` 的转换链接。仓库更新不会自动切换路由器订阅，运行配置由用户导入。

参考：[SubConverter-Extended 来源参数](https://github.com/Aethersailor/SubConverter-Extended/wiki/Feature-Parameters) · [远程 Provider](https://github.com/Aethersailor/SubConverter-Extended/wiki/Remote-Subscriptions) · [HF 官方域名清单](https://huggingface.co/.well-known/meta.json)

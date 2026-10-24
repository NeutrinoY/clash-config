"""从上游 Custom_OpenClash_Rules 的默认模板生成本仓库的 Custom_Clash.ini。

用法：uv run build.py [上游模板的路径或 URL]
不带参数时取上游 main 分支。每个补丁都会检查命中次数，上游结构变了就直接报错，不悄悄生成错的模板。
"""

import sys
import urllib.request
from pathlib import Path

UPSTREAM = "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/main/cfg/Custom_Clash.ini"
OUT = Path(__file__).with_name("Custom_Clash.ini")

PREFIX = "custom_proxy_group="
ISP = "[]🇺🇸 美国ISP出口"  # 由环境层（nikki Mixin / Verge 脚本）定义
PREMIUM = "!!GROUP=^Premium$!!"
BULK = "!!GROUP=^Bulk$!!"
TEST = ["https://www.gstatic.com/generate_204", "300,,50"]

# Premium（跑路云）节点名里的倍率标记 [x]：x > 1 的节点不进任何自动组，只能手动选。没写倍率的按 1x。
OVER_1X = r"\[(?:[2-9]|[1-9]\d|1\.0*[1-9])"
# Bulk（赔钱机场）的倍率写法是「-0.1倍」「-0.01倍」。只按这两档分组：组在面板上是平铺的，多一个组就多一张卡片
BULK_TIERS = [("📦 0.01倍", r"0\.01倍"), ("📦 0.1倍", r"0\.1倍")]
# 订阅里混着的信息条目，不是节点
NOT_NODE = r"(?!.*(?:剩余流量|套餐到期|官网|过期时间))"

ISP_FIRST = {"🤖 ChatGPT", "🤖 AI服务"}  # AI 默认走 ISP
MANUAL = "🚀 手动选择"  # ISP 放在 ♻️ 自动选择 后面：随时能切，但默认不走
AUTO = "♻️ 自动选择"


def load(src: str) -> list[str]:
    if src.startswith(("http://", "https://")):
        with urllib.request.urlopen(src, timeout=30) as r:
            text = r.read().decode("utf-8")
    else:
        text = Path(src).read_text(encoding="utf-8")
    return text.splitlines()


def auto_name(region_group: str) -> str:
    # "🇭🇰 香港节点" → "⚡ 香港自动"
    return "⚡ " + region_group.split(" ", 1)[1].removesuffix("节点") + "自动"


def bulk_groups() -> list[str]:
    tiers = [name for name, _ in BULK_TIERS]
    groups = [
        ["📦 大流量下载", "select", *[f"[]{t}" for t in tiers], f"[]{MANUAL}", f"{BULK}^{NOT_NODE}.*$"],
        *[[name, "url-test", f"{BULK}^{NOT_NODE}(?=.*{pat}).*$", *TEST] for name, pat in BULK_TIERS],
    ]
    return [PREFIX + "`".join(g) for g in groups]


def patch(lines: list[str]) -> list[str]:
    out: list[str] = []
    hits = {"P0": 0, "P1": 0, "P1-auto": 0, "P2-premium": 0, "P2-bulk": 0}

    for line in lines:
        if not line.startswith(PREFIX):
            out.append(line)
            continue
        f = line[len(PREFIX):].split("`")
        name, kind = f[0], f[1]

        # P1：地区组 = select（⚡X自动 + 该地区全部 Premium 节点）；⚡X自动 只装 ≤1x 的节点
        if kind == "url-test" and name.endswith("节点"):
            region = f[2]
            auto = auto_name(name)
            out.append(PREFIX + "`".join([name, "select", f"[]{auto}", PREMIUM + region]))
            out.append(PREFIX + "`".join([auto, "url-test", f"{PREMIUM}^(?=.*{region})(?!.*{OVER_1X}).*$", *f[3:]]))
            hits["P1"] += 1
            continue

        if name == AUTO and kind == "url-test":
            f[2] = f"{PREMIUM}^(?!.*{OVER_1X}).*$"
            out.append(PREFIX + "`".join(f))
            hits["P1-auto"] += 1
            # P2：Bulk 节点只进大流量下载组
            out.extend(bulk_groups())
            hits["P2-bulk"] += 1
            continue

        # P2：业务组里的「全部节点」只取 Premium
        if ".*" in f[2:]:
            f = [PREMIUM + ".*" if m == ".*" else m for m in f]
            hits["P2-premium"] += 1

        # P0：随时能让流量走美国静态 IP
        if name in ISP_FIRST:
            f.insert(2, ISP)
            hits["P0"] += 1
        elif name == MANUAL:
            f.insert(f.index(f"[]{AUTO}") + 1, ISP)
            hits["P0"] += 1

        out.append(PREFIX + "`".join(f))

    expect = {"P0": len(ISP_FIRST) + 1, "P1": 6, "P1-auto": 1, "P2-bulk": 1}
    bad = {k: (hits[k], v) for k, v in expect.items() if hits[k] != v}
    if bad or hits["P2-premium"] == 0:
        sys.exit(f"上游模板结构变了，补丁命中次数不对（实际, 期望）：{bad or hits}")
    return out


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else UPSTREAM
    header = [
        "; 由 build.py 从上游 Custom_OpenClash_Rules/cfg/Custom_Clash.ini 生成，不要手改。",
        "; 相对上游的改动见 README.md。",
    ]
    OUT.write_text("\n".join(header + patch(load(src))) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

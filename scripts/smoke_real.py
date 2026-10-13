"""开发用冒烟脚本：在真实机器上跑扫描，打印脱敏摘要（不输出密码明文）。

用法：py scripts/smoke_real.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wifi_pass_viewer.scanner import WindowsWifiScanner


def mask_ssid(s: str) -> str:
    if len(s) <= 2:
        return (s[:1] + "*") if s else s
    return s[0] + "*" * (len(s) - 2) + s[-1]


def main() -> None:
    result = WindowsWifiScanner().scan()
    with_pw = [n for n in result.networks if n.has_password]
    print(f"networks: {len(result.networks)}")
    print(f"connected_available: {result.connected_available}")
    print(f"note: {result.note}")
    print(f"with password: {len(with_pw)} | without: {len(result.networks) - len(with_pw)}")
    for n in result.networks[:8]:
        pw = f"len={len(n.password)}" if n.password else "-"
        print(
            f"  {mask_ssid(n.ssid):24} auth={n.authentication} "
            f"cipher={n.cipher} pw:{pw} conn={n.connected} note={n.note}"
        )


if __name__ == "__main__":
    main()

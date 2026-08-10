#!/usr/bin/env python3
"""Extract domains from URLs and append them to my-direct.txt."""

from __future__ import annotations

import argparse
import ipaddress
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


RULE_FILE = Path(__file__).resolve().parents[1] / "my-direct.txt"
LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def extract_domain(value: str) -> str | None:
    """Return a normalized domain from a URL/domain string, or None."""
    candidate = value.strip()
    if not candidate or any(character.isspace() for character in candidate):
        return None

    if "://" in candidate:
        parsed = urlsplit(candidate)
        if parsed.scheme.lower() not in {"http", "https"}:
            return None
    else:
        if "@" in candidate:
            return None
        parsed = urlsplit(f"//{candidate}")

    try:
        host = parsed.hostname
        parsed.port
    except ValueError:
        return None

    if not host:
        return None

    host = host.rstrip(".").lower()
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        return None

    try:
        normalized = host.encode("idna").decode("ascii")
    except UnicodeError:
        return None

    if len(normalized) > 253 or "." not in normalized:
        return None

    labels = normalized.split(".")
    if any(not LABEL_PATTERN.fullmatch(label) for label in labels):
        return None

    return normalized


def unique(items: list[str]) -> list[str]:
    """Deduplicate strings while preserving their first-seen order."""
    return list(dict.fromkeys(items))


def load_existing_rules() -> list[str]:
    """Load, normalize and deduplicate all existing valid rules."""
    if not RULE_FILE.exists():
        return []

    rules: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        RULE_FILE.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        if not line.strip():
            continue
        domain = extract_domain(line)
        if domain is None:
            raise ValueError(
                f"{RULE_FILE} 第 {line_number} 行不是有效的纯域名；为避免删除原规则，已停止更新。"
            )
        if domain not in seen:
            seen.add(domain)
            rules.append(domain)
    return rules


def collect_inputs(arguments: argparse.Namespace) -> list[str]:
    """Collect inputs from arguments, files, or standard input."""
    values: list[str] = []
    for value in arguments.inputs:
        values.extend(value.splitlines())

    for input_file in arguments.file:
        try:
            values.extend(input_file.read_text(encoding="utf-8-sig").splitlines())
        except OSError as error:
            raise ValueError(f"无法读取输入文件 {input_file}: {error}") from error

    if not values and not arguments.file:
        if sys.stdin.isatty():
            print("请逐行粘贴网址或域名；Windows 下按 Ctrl+Z 后回车结束输入。")
        values.extend(sys.stdin.read().splitlines())

    return values


def print_group(title: str, domains: list[str]) -> None:
    """Print a labeled domain list."""
    print(f"{title}：")
    if not domains:
        print("  无")
        return
    for domain in domains:
        print(f"  - {domain}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从网址中提取域名，并追加到 my-direct.txt。"
    )
    parser.add_argument("inputs", nargs="*", help="一个或多个网址/域名")
    parser.add_argument(
        "-f",
        "--file",
        action="append",
        default=[],
        type=Path,
        help="从 UTF-8 文本文件逐行读取网址/域名；可重复使用",
    )
    arguments = parser.parse_args()

    try:
        rules = load_existing_rules()
        raw_inputs = collect_inputs(arguments)
    except ValueError as error:
        parser.error(str(error))

    known = set(rules)
    added: list[str] = []
    already_present: list[str] = []
    invalid_count = 0

    for raw_input in raw_inputs:
        domain = extract_domain(raw_input)
        if domain is None:
            if raw_input.strip():
                invalid_count += 1
            continue
        if domain in known:
            already_present.append(domain)
            continue
        known.add(domain)
        rules.append(domain)
        added.append(domain)

    output = "".join(f"{domain}\n" for domain in rules)
    RULE_FILE.write_text(output, encoding="utf-8", newline="\n")

    print_group("本次新增", unique(added))
    print_group("已经存在", unique(already_present))
    print(f"已忽略错误输入：{invalid_count} 条")
    print(f"当前规则数量：{len(rules)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

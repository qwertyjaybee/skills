#!/usr/bin/env python3
"""
Uploads a generated Markdown task description to a Jira issue via the Jira REST API.
Can read credentials from:
1. Custom config path specified by --config
2. Environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
3. JSON config files:
   - ~/.gemini/config/jira.json
   - /opt/core-aairi/.agents/automation/jira-description/jira_config.json
   - ~/.jira_config.json
   - ~/.gemini/config/mcp_config.json (parsing mcpServers.jira.env)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("❌ Error: 'requests' package is required. Install it using: pip install requests", file=sys.stderr)
    sys.exit(1)


def markdown_to_jira_wiki(text: str) -> str:
    """
    Converts standard Markdown text into Jira Wiki Markup.
    This ensures Jira Cloud and Server properly render:
    - Headings (h1. to h6. instead of '#' being treated as numbered lists)
    - Bold (*text* instead of '**text**')
    - Italic (_text_)
    - Inline code ({{code}} instead of `code`)
    - Code blocks ({code:lang} instead of ```lang)
    - Tables (|| Header || and | Cell | without separator dashes)
    - Bullet lists (* and ** instead of -)
    - Numbered lists (# and ## instead of 1.)
    - Blockquotes (bq. text instead of > text)
    - Horizontal rules (---- instead of ---)
    - Links ([text|url] instead of [text](url))
    """
    lines = text.split('\n')
    output = []
    in_code_block = False
    code_lang = ''
    code_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block fence
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lang = stripped[3:].strip()
                code_lines = []
            else:
                in_code_block = False
                if code_lang:
                    output.append(f'{{code:{code_lang}}}')
                else:
                    output.append('{code}')
                output.extend(code_lines)
                output.append('{code}')
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Check if table row
        if stripped.startswith('|') and stripped.endswith('|'):
            # Check if this line is a markdown separator row (e.g. |:---|:---| or |---|---|)
            if re.match(r'^\|(\s*:?-+:?\s*\|)+\s*$', stripped):
                # Skip markdown separator row completely
                i += 1
                continue

            # Check if this is a header row (the next line is a separator row)
            is_header = False
            if i + 1 < len(lines):
                next_stripped = lines[i + 1].strip()
                if re.match(r'^\|(\s*:?-+:?\s*\|)+\s*$', next_stripped):
                    is_header = True

            cells = [c.strip() for c in stripped[1:-1].split('|')]
            if is_header:
                output.append('|| ' + ' || '.join(cells) + ' ||')
            else:
                output.append('| ' + ' | '.join(cells) + ' |')
            i += 1
            continue

        # Headings: # -> h1., ## -> h2., etc.
        m_heading = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m_heading:
            level = len(m_heading.group(1))
            heading_text = m_heading.group(2)
            output.append(f'h{level}. {heading_text}')
            i += 1
            continue

        # Horizontal rules: ---, ***, ___
        if re.match(r'^(?:---|\*\*\*|___)\s*$', stripped):
            output.append('----')
            i += 1
            continue

        # Blockquote: > text -> bq. text
        m_bq = re.match(r'^>\s?(.*)$', line)
        if m_bq:
            output.append(f'bq. {m_bq.group(1)}')
            i += 1
            continue

        # Unordered list items (- item or * item)
        m_bullet = re.match(r'^(\s*)[-*]\s+(.*)$', line)
        if m_bullet:
            indent = len(m_bullet.group(1))
            depth = (indent // 2) + 1
            bullet_prefix = '*' * depth
            output.append(f'{bullet_prefix} {m_bullet.group(2)}')
            i += 1
            continue

        # Ordered list items (1. item)
        m_num = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
        if m_num:
            indent = len(m_num.group(1))
            depth = (indent // 2) + 1
            num_prefix = '#' * depth
            output.append(f'{num_prefix} {m_num.group(2)}')
            i += 1
            continue

        output.append(line)
        i += 1

    result = '\n'.join(output)

    # Protect code blocks from inline replacements using tokens without markdown or underscore chars
    code_blocks = []
    def save_cb(m):
        code_blocks.append(m.group(0))
        return f"ZZZJIRACODEBLOCK{len(code_blocks)-1}ZZZ"

    result = re.sub(r'\{code(?::\w+)?\}.*?\{code\}', save_cb, result, flags=re.DOTALL)
    result = re.sub(r'\{noformat\}.*?\{noformat\}', save_cb, result, flags=re.DOTALL)

    # 1. Inline code: `code` -> {{code}}
    result = re.sub(r'(?<!`)`([^`\n]+)`(?!`)', r'{{\1}}', result)

    # 2. Bold: **text** or __text__ -> *text*
    result = re.sub(r'\*\*(.+?)\*\*', r'*\1*', result)
    result = re.sub(r'__(.+?)__', r'*\1*', result)

    # 3. Links: [text](url) -> [text|url]
    result = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[\1|\2]', result)

    # Restore protected code blocks
    for idx, cb in enumerate(code_blocks):
        result = result.replace(f"ZZZJIRACODEBLOCK{idx}ZZZ", cb)

    return result


def find_config_file(custom_path: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Look for configuration credentials in priority order."""
    search_paths = []
    if custom_path:
        search_paths.append(Path(custom_path).expanduser())

    search_paths.extend([
        Path("~/.gemini/config/jira.json").expanduser(),
        Path("/opt/core-aairi/.agents/automation/jira-description/jira_config.json"),
        Path(__file__).resolve().parent.parent / "jira_config.json",
        Path("~/.jira_config.json").expanduser(),
        Path("~/.config/jira/config.json").expanduser(),
        Path("~/.gemini/config/mcp_config.json").expanduser(),
    ])

    for path in search_paths:
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Case 1: Direct JSON config with jira_url, jira_email, jira_api_token
                url = data.get("jira_url") or data.get("JIRA_URL") or data.get("url")
                email = data.get("jira_email") or data.get("JIRA_EMAIL") or data.get("email") or data.get("username")
                token = data.get("jira_api_token") or data.get("JIRA_API_TOKEN") or data.get("api_token") or data.get("token")

                if url and email and token:
                    return {"url": str(url).strip(), "email": str(email).strip(), "token": str(token).strip()}

                # Case 2: MCP config style (mcpServers.jira.env)
                if "mcpServers" in data and "jira" in data["mcpServers"]:
                    env_dict = data["mcpServers"]["jira"].get("env", {})
                    url = env_dict.get("JIRA_URL")
                    email = env_dict.get("JIRA_EMAIL")
                    token = env_dict.get("JIRA_API_TOKEN")
                    if url and email and token:
                        return {"url": str(url).strip(), "email": str(email).strip(), "token": str(token).strip()}

            except Exception as e:
                # Silently skip malformed config files and proceed to next source
                continue

    return None


def resolve_credentials(custom_config: Optional[str] = None) -> Tuple[str, str, str]:
    """Resolve Jira credentials from config file or environment variables."""
    # 1. Check custom config or standard config files
    cfg = find_config_file(custom_config)
    url = cfg.get("url") if cfg else None
    email = cfg.get("email") if cfg else None
    token = cfg.get("token") if cfg else None

    # 2. Environment variables override / fill in missing values
    url = os.environ.get("JIRA_URL") or os.environ.get("JIRA_BASE_URL") or url
    email = os.environ.get("JIRA_EMAIL") or os.environ.get("JIRA_USER") or os.environ.get("JIRA_USERNAME") or email
    token = os.environ.get("JIRA_API_TOKEN") or os.environ.get("JIRA_TOKEN") or os.environ.get("JIRA_PASSWORD") or token

    if not url or not email or not token:
        print("❌ Error: Missing Jira configuration credentials.\n", file=sys.stderr)
        print("Please configure your Jira credentials using one of the following methods:\n", file=sys.stderr)
        print("Option 1: Create a JSON config file at:", file=sys.stderr)
        print("  /opt/core-aairi/.agents/automation/jira-description/jira_config.json", file=sys.stderr)
        print("  or ~/.gemini/config/jira.json", file=sys.stderr)
        print("  Content:", file=sys.stderr)
        print("  {", file=sys.stderr)
        print('    "jira_url": "https://your-company.atlassian.net",', file=sys.stderr)
        print('    "jira_email": "your-email@company.com",', file=sys.stderr)
        print('    "jira_api_token": "your_jira_api_token"', file=sys.stderr)
        print("  }\n", file=sys.stderr)
        print("Option 2: Set environment variables:", file=sys.stderr)
        print('  export JIRA_URL="https://your-company.atlassian.net"', file=sys.stderr)
        print('  export JIRA_EMAIL="your-email@company.com"', file=sys.stderr)
        print('  export JIRA_API_TOKEN="your_jira_api_token"\n', file=sys.stderr)
        sys.exit(1)

    return url.rstrip("/"), email, token


def upload_description(issue_key: str, description_text: str, url: str, email: str, token: str, dry_run: bool = False) -> bool:
    """Send PUT request to Jira REST API v2 issue endpoint to update the description field."""
    api_endpoint = f"{url}/rest/api/2/issue/{issue_key}"

    payload = {
        "fields": {
            "description": description_text
        }
    }

    if dry_run:
        print(f"🔍 Dry run mode enabled. Target URL: {api_endpoint}")
        print(f"👤 Auth Email: {email}")
        print(f"📝 Description length: {len(description_text)} characters")
        print("\n--- Payload Preview ---")
        print(json.dumps(payload, indent=2)[:500] + "... (truncated)")
        return True

    print(f"🚀 Uploading description to Jira issue {issue_key}...")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.put(
            api_endpoint,
            auth=HTTPBasicAuth(email, token),
            headers=headers,
            json=payload,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Network or connection error: {e}", file=sys.stderr)
        return False

    if response.status_code in (200, 204):
        issue_browse_url = f"{url}/browse/{issue_key}"
        print(f"✅ Successfully updated Jira issue: {issue_key}")
        print(f"🔗 Issue URL: {issue_browse_url}")
        return True

    print(f"❌ Failed to update Jira issue. HTTP Status: {response.status_code}", file=sys.stderr)
    try:
        error_data = response.json()
        if "errorMessages" in error_data and error_data["errorMessages"]:
            print(f"  Messages: {', '.join(error_data['errorMessages'])}", file=sys.stderr)
        if "errors" in error_data and error_data["errors"]:
            print(f"  Field Errors: {json.dumps(error_data['errors'], indent=2)}", file=sys.stderr)
    except Exception:
        print(f"  Raw response: {response.text}", file=sys.stderr)

    if response.status_code in (401, 403):
        print("\n💡 Troubleshooting: Check that your JIRA_EMAIL and JIRA_API_TOKEN are correct and that you have edit permissions on this issue.", file=sys.stderr)
    elif response.status_code == 404:
        print(f"\n💡 Troubleshooting: Issue '{issue_key}' was not found. Please verify the issue key.", file=sys.stderr)

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload a generated task description to Jira using the Jira REST API."
    )
    parser.add_argument(
        "--issue", "-i",
        required=True,
        help="The Jira issue key (e.g. AIRI-284)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f",
        help="Path to the Markdown file containing the task description."
    )
    group.add_argument(
        "--text", "-t",
        help="Description text string to upload directly."
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to a custom JSON configuration file containing Jira credentials."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate credentials and preview payload without executing the API request."
    )
    parser.add_argument(
        "--no-convert",
        action="store_true",
        help="Skip automatic Markdown-to-Jira Wiki conversion and upload raw text as-is."
    )

    args = parser.parse_args()

    # Read description text
    if args.file:
        file_path = Path(args.file).expanduser()
        if not file_path.is_file():
            print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            description = f.read().strip()
    else:
        description = args.text.strip()

    if not description:
        print("❌ Error: Description content cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Convert standard Markdown to Jira Wiki Markup so Jira natively
    # formats headings (H1-H6), bold, italics, tables, and bullet lists
    # instead of treating markdown '#' as numbered lists ("1. a. i.").
    if not args.no_convert:
        description = markdown_to_jira_wiki(description)

    # Resolve credentials
    jira_url, jira_email, jira_token = resolve_credentials(args.config)

    # Perform upload
    success = upload_description(
        issue_key=args.issue,
        description_text=description,
        url=jira_url,
        email=jira_email,
        token=jira_token,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


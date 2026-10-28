"""Validate the redistributable skill bundle using only Python's standard library."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    deps = json.loads((ROOT / "dependencies.json").read_text(encoding="utf-8"))
    skills = sorted((ROOT / "skills").iterdir()) if (ROOT / "skills").exists() else []
    overlays = sorted((ROOT / "overlays").iterdir()) if (ROOT / "overlays").exists() else []
    for skill in skills + overlays:
        entry = skill / "SKILL.md"
        if not entry.is_file():
            errors.append(f"Missing entry: {skill.name}")
            continue
        text = entry.read_text(encoding="utf-8")
        header = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not header:
            errors.append(f"Invalid frontmatter: {skill.name}")
            continue
        fields = dict(re.findall(r"^(name|description):\s*(.+)$", header[1], re.M))
        if fields.get("name") != skill.name or not fields.get("description"):
            errors.append(f"Invalid name/description: {skill.name}")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", skill.name):
            errors.append(f"Invalid skill directory: {skill.name}")
        if skill.name != "image-to-bimbase" and skill.name not in deps:
            errors.append(f"Missing dependency: {skill.name}")

    for name, dep in deps.items():
        if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+", dep["url"]):
            errors.append(f"Unexpected dependency URL: {name}")
        if not re.fullmatch(r"[0-9a-f]{40}", dep["commit"]):
            errors.append(f"Unpinned dependency: {name}")
        if not (ROOT / "licenses" / (name + ".txt")).is_file():
            errors.append(f"Missing license: {name}")

    count = 0
    for file in ROOT.rglob("*"):
        rel = file.relative_to(ROOT)
        if not file.is_file() or any(p in {".git", "__pycache__"} for p in rel.parts):
            continue
        count += 1
        if file.name.startswith(".env") or file.suffix.lower() in {".pem", ".key", ".pfx"}:
            errors.append(f"Sensitive file type: {rel}")
        text = file.read_text(encoding="utf-8-sig")
        for pattern in [r"[A-Za-z]:[\\/]Users[\\/](?!Public\b|<)[^\s`\\/]+",
                        r"gh[pousr]_[A-Za-z0-9]{30,}",
                        r"github_pat_[A-Za-z0-9_]{30,}",
                        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]:
            if re.search(pattern, text):
                errors.append(f"Potential private data: {rel}")
                break
        if file.suffix == ".md" and "overlays" not in rel.parts:
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if re.match(r"[a-zA-Z]+:|#", link):
                    continue
                target = unquote(link.split("#", 1)[0])
                if target and not (file.parent / target).exists():
                    errors.append(f"Broken link in {rel}: {target}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(skills)} skills, {len(overlays)} overlays, {len(deps)} pinned dependencies, {count} files")
    print("Runtime workflows and upstream software were not executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

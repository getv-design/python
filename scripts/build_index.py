"""Build the package index (PEP 503, the "simple" API pip and uv read) from this repository's releases.

Reads the releases as `gh api --paginate repos/<repo>/releases` prints them (a JSON array, or
several concatenated when paginated) on stdin, and writes the index to the folder named by
the first argument:

    <out>/simple/index.html                      every project
    <out>/simple/<project>/index.html            every file of one project, linked to its
                                                 release download, with its sha256

Each file's project is read from its name (`getv_design_author-0.1.0-....whl` is
`getv-design-author`). The release body says which Pythons it is for, on a line
`requires-python: >=3.10`, and every file of that release carries it as
`data-requires-python`. The index is rebuilt whole from the releases every time, so running
it twice gives the same pages.

    gh api --paginate repos/getv-design/python/releases | python scripts/build_index.py site
"""

import html
import json
import re
import sys
from pathlib import Path


def normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def project_of(filename: str) -> str | None:
    if filename.endswith(".whl"):
        return normalise(filename.split("-", 1)[0])
    match = re.match(r"^(.+?)-\d[^-]*\.tar\.gz$", filename)
    return normalise(match.group(1)) if match else None


def read_releases(text: str) -> list[dict]:
    releases, decoder, at = [], json.JSONDecoder(), 0
    text = text.strip()
    while at < len(text):
        page, end = decoder.raw_decode(text, at)
        releases.extend(page if isinstance(page, list) else [page])
        at = end
        while at < len(text) and text[at].isspace():
            at += 1
    return releases


def page(title: str, links: list[str]) -> str:
    body = "\n".join(f"    {link}<br>" for link in links)
    return (
        "<!DOCTYPE html>\n<html>\n  <head>\n"
        '    <meta name="pypi:repository-version" content="1.0">\n'
        f"    <title>{html.escape(title)}</title>\n  </head>\n  <body>\n"
        f"    <h1>{html.escape(title)}</h1>\n{body}\n  </body>\n</html>\n"
    )


def build(releases: list[dict], out: Path) -> dict[str, list[str]]:
    files: dict[str, list[tuple[str, str]]] = {}
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        requires = re.search(r"^requires-python:\s*(\S+)\s*$", release.get("body") or "", re.M)
        for asset in release.get("assets", []):
            name = asset["name"]
            project = project_of(name)
            digest = asset.get("digest") or ""
            if project is None or not digest.startswith("sha256:"):
                continue
            href = f"{asset['browser_download_url']}#sha256={digest.removeprefix('sha256:')}"
            attrs = f'href="{html.escape(href)}"'
            if requires:
                attrs += f' data-requires-python="{html.escape(requires.group(1))}"'
            files.setdefault(project, []).append((name, f"<a {attrs}>{html.escape(name)}</a>"))

    simple = out / "simple"
    simple.mkdir(parents=True, exist_ok=True)
    for project, links in files.items():
        (simple / project).mkdir(exist_ok=True)
        ordered = [link for _, link in sorted(links)]
        (simple / project / "index.html").write_text(page(f"Links for {project}", ordered))
    projects = [f'<a href="{p}/">{html.escape(p)}</a>' for p in sorted(files)]
    (simple / "index.html").write_text(page("Simple index", projects))
    (out / ".nojekyll").write_text("")
    return {project: [name for name, _ in sorted(links)] for project, links in files.items()}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: build_index.py <out folder>  (releases JSON on stdin)")
    built = build(read_releases(sys.stdin.read()), Path(sys.argv[1]))
    for project, names in built.items():
        print(f"{project}: {len(names)} files")

# vDesign Python packages

A package index for vDesign's Python packages, served at
**https://getv-design.github.io/python/simple/**. The packages are built and tested
elsewhere and released here; this repository holds no source.

| Package              | Import               | What it is                                                                                                              |
| -------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `getv-design-author` | `getv_design.author` | vDesign's tools and skill for your own agent: read and edit `.vd` designs in your own store, with LangChain, the OpenAI Agents SDK or Pydantic AI. [Docs](https://getv.design/docs/author/) |

Wheels for Python 3.10 and later on Linux (x86_64 and arm64, glibc and musl), macOS
(Intel and Apple silicon) and Windows (x64).

## Install

### uv (recommended)

Name the index for this package only, so uv never takes it from anywhere else:

```toml
# pyproject.toml
[[tool.uv.index]]
name = "getv-design"
url = "https://getv-design.github.io/python/simple/"
explicit = true

[tool.uv.sources]
getv-design-author = { index = "getv-design" }
```

```sh
uv add "getv-design-author[langchain]" langchain     # or [openai-agents], [pydantic-ai]
```

The extras bring each library's tool layer: `[langchain]` installs `langchain-core`, so add
`langchain` for its `create_agent`; `[pydantic-ai]` needs Python 3.11 or later, as
Pydantic AI does.

### pip

```sh
pip install --extra-index-url https://getv-design.github.io/python/simple/ "getv-design-author[langchain]==0.1.0" langchain
```

`--extra-index-url` also looks on PyPI, and pip takes the highest version it finds
anywhere. Until `getv-design-author` is published on PyPI by vDesign, prefer the uv setup
above, or pin the version you expect (`getv-design-author==0.1.0`).

In `requirements.txt`:

```
--extra-index-url https://getv-design.github.io/python/simple/
getv-design-author[langchain]==0.1.0
```

## Releases

Every version is a [release](https://github.com/getv-design/python/releases) here with
its wheels attached; the index links to those files with their sha256.

## Licence

Free to use under the vDesign Author Licence ([`LICENSE`](LICENSE)); the vDesign skill
the package carries is CC BY 4.0.

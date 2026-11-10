# training

Endurance training skills. Each skill keeps the athlete's data in a private folder outside this repository and reaches it through a `state/` link, so the data is never committed. State starts empty and is written only by the skill's own procedures (see `skills/cycling/references/state.md`).

| Skill | Use it for |
|---|---|
| `cycling` | Three procedures for one road cyclist: a plan interview (screening, measured anchors, evidence-graded plan), a review after every logged session (compliance, internal vs external load, decoupling, wellness, optional HRV), and adaptation when the rider raises illness, missed training, travel, heat, injury or life stress. Every number comes from the bundled scripts or from `state/`, and every recommendation is explained with its evidence. |

## Setup

The athlete's data lives in a private folder outside this repository (`<private-folder>` below, readable only by you). Link it into the skill once per clone:

```bash
ln -s <private-folder>/training/cycling/state plugins/training/skills/cycling/state
```

The link is ignored by git. To use the skill in claude.ai, build an upload. Uploads leave `state/` out unless you add `--with-state`, which sends your health and training data to your claude.ai account:

```bash
scripts/package_skill.sh --with-state plugins/training/skills/cycling
```

## Tests

The self-tests run from the skill folder (`python3 scripts/cyclingcalc.py selftest`, `python3 scripts/search_sim.py selftest`). The full suites live outside the skill, in `tests/cycling/`, and need `numpy` and `pyyaml`:

```bash
uv run --no-project --with numpy --with pyyaml python plugins/training/tests/cycling/test_compute.py
uv run --no-project --with numpy --with pyyaml python plugins/training/tests/cycling/test_verifier.py
```

License: MIT

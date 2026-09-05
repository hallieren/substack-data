"""Shadow rung, offline form: pico's proposed fix lined up against the
maintainers' merged fix, entry by entry. Zero model calls.

Writes analysis/shadow.md with one row per fix case (reference verdict,
files pico touched vs files the human touched, sizes, pico's own summary)
and a three-way column left for the human reading: pico wrong / human wrong /
both right (different route). Also dumps analysis/shadow/<id>.md with both
patches and pico's final report for that reading.

Usage: python shadow.py runs/replay
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "harness"))
from traces import final_text, load_traj  # noqa: E402
from select_traffic import is_test  # noqa: E402

DIFF = re.compile(r"^diff --git a/(\S+) b/(\S+)", re.M)


def files(patch):
    return sorted({m.group(2) for m in DIFF.finditer(patch)})


def lines_changed(patch):
    return sum(1 for l in patch.splitlines() if (l.startswith("+") or l.startswith("-"))
               and not l.startswith(("+++", "---")))


def main(run_dir):
    run_dir = Path(run_dir)
    out_dir = HERE / "analysis" / "shadow"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = ["# Shadow comparison: pico vs the merged human fix", "",
            "Three-way column is filled by hand after reading analysis/shadow/<id>.md.", "",
            "| case | ref | pico files | human files | overlap | pico ± | human ± | pico says | three-way |",
            "|---|---|---|---|---|---|---|---|---|"]
    for d in sorted((HERE / "cases").iterdir()):
        meta_p = d / "meta.json"
        if not meta_p.exists():
            continue
        meta = json.loads(meta_p.read_text())
        key = f"{meta['id']}-r1"
        wp = run_dir / "world" / f"{key}.json"
        if not wp.exists():
            continue
        world = json.loads(wp.read_text())
        traj = load_traj(run_dir / "trajs" / f"{key}.traj.json")
        ref = json.loads((d / "reference.json").read_text())
        human = (d / "fix.patch").read_text()
        pf = [f for f in files(world["patch"]) if not is_test(f)]
        hf = [f for f in files(human) if not is_test(f)]
        overlap = sorted(set(pf) & set(hf))
        f2p = ref.get("f2p", [])
        green = sum(world.get("ref_results", {}).get(t) == "PASSED" for t in f2p)
        refcol = f"{green}/{len(f2p)}" if f2p else "no-fix"
        report = final_text(traj).strip().replace("\n", " ")
        rows.append(f"| {meta['id']} | {refcol} | {len(pf)} | {len(hf)} | {len(overlap)} | "
                    f"{lines_changed(world['patch'])} | {lines_changed(human)} | {report[:90]} |  |")
        (out_dir / f"{meta['id']}.md").write_text(
            f"# {meta['id']} — {meta['url']}\n\n## reference\n\nF2P: {f2p}\n\n"
            f"pico's F2P results: { {t: world.get('ref_results', {}).get(t) for t in f2p} }\n\n"
            f"## pico's final report\n\n{final_text(traj)}\n\n## pico's patch\n\n```diff\n{world['patch']}\n```\n\n"
            f"## human fix (merged PR #{meta['pr']})\n\n```diff\n{human}\n```\n"
            + ((d / "ruling.md").exists() and f"\n## maintainers' ruling\n\n{(d / 'ruling.md').read_text()}\n" or ""))
    (HERE / "analysis" / "shadow.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "runs" / "replay")

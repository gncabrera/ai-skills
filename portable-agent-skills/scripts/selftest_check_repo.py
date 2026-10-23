#!/usr/bin/env python3
"""Self-test for check_repo.py — the gate has to prove it still tells the truth.

Builds throwaway skill repos under /tmp with 11 planted defects and 6
false-positive traps, then asserts the checker reports exactly the first set.
Run it after editing check_repo.py:

    python3 selftest_check_repo.py

Secrets and token-shaped strings in the fixture are built at runtime on purpose:
a literal one in this file gets redacted by tooling that writes or displays it,
which would silently turn the token trap into a no-op.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKER = Path(__file__).resolve().parent / "check_repo.py"
FENCE = "```"


def skill(name, desc="Does a thing for a stranger, useful when needed.", body=""):
    return f"---\nname: {name}\ndescription: \"{desc}\"\n---\n\n# {name}\n\n{body}\n"


def build(root: Path, denylist: Path):
    (root / "good").mkdir(parents=True)
    (root / "good" / "SKILL.md").write_text(skill("good"), encoding="utf-8")

    (root / "namewrong").mkdir()
    (root / "namewrong" / "SKILL.md").write_text(skill("other-name"), encoding="utf-8")

    (root / "crlf").mkdir()
    (root / "crlf" / "SKILL.md").write_bytes(skill("crlf").replace("\n", "\r\n").encode())

    fake_token = "ghp_" + "A" * 32
    # Planted shapes are assembled at runtime on purpose: this file is scanned by
    # check_repo.py like any other, and a literal address would fail the repo that
    # ships it. Same trap for the checker, no literal in the source.
    leaky_home = "/home/" + "alguien/repo"
    leaky_mail = "alguien" + "@" + "empresa.com"
    leaky_ip = "192." + "168.1.50"
    (root / "leaky").mkdir()
    (root / "leaky" / "SKILL.md").write_text(
        skill("leaky", body=(
            f"Run it on {leaky_home} and mail {leaky_mail}.\n"
            f"Host is {leaky_ip}, token {fake_token}.\n"
            "Vendor AcmeCorp ships the widget.\n"
            "Safe placeholders: /home/<user>/repo and user@example.com.\n"
        )), encoding="utf-8")

    (root / "big").mkdir()
    (root / "big" / "SKILL.md").write_text(skill("big", body="x " * 12000), encoding="utf-8")

    (root / "descbig").mkdir()
    (root / "descbig" / "SKILL.md").write_text(
        skill("descbig", desc="y" * 1200), encoding="utf-8")

    (root / "README.md").write_text(
        "# fake skills\n\n## Skills\n\n| Skill | What it does |\n|-------|--------------|\n"
        "| [`good`](good/SKILL.md) | the clean one |\n\n"
        "Broken relative link whose path starts with h: [notes](handbook/notes.md)\n"
        f"{FENCE}\nIllustrative only: [Source A](url-a) and [Source B](url-b)\n{FENCE}\n"
        "Inline example too: `[x](url-c)`\n",
        encoding="utf-8")

    denylist.write_text("# private terms, one per line\nAcmeCorp\n", encoding="utf-8")


def run(repo, denylist):
    proc = subprocess.run([sys.executable, str(CHECKER), str(repo), "--denylist", str(denylist)],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout


def main():
    failures = []
    tmp = Path(tempfile.mkdtemp(prefix="skills-selftest-"))
    try:
        repo = tmp / "repo"
        repo.mkdir()
        denylist = tmp / "denylist.txt"
        build(repo, denylist)
        code, out = run(repo, denylist)
        print(out)

        def want(label, needle):
            if needle not in out:
                failures.append(f"MISSING {label}: {needle!r}")

        def forbid(label, needle):
            if needle in out:
                failures.append(f"FALSE POSITIVE {label}: {needle!r}")

        if code != 1:
            failures.append(f"expected exit 1, got {code}")
        for label, needle in [
            ("name mismatch", "other-name"),
            ("crlf", "crlf/SKILL.md has CRLF"),
            ("readme row", "leaky is not in the README"),
            ("broken h-link", "handbook/notes.md does not resolve"),
            ("home path", "PRIVATE_PATH"),
            ("email", "PRIVATE_EMAIL"),
            ("private ip", "PRIVATE_IP"),
            ("token", "TOKEN"),
            ("denylist", "DENYLIST"),
            ("desc length", "DESC_LEN"),
            ("body size warn", "BODY_SIZE"),
        ]:
            want(label, needle)
        for label, needle in [
            ("fenced link", "url-a"),
            ("fenced link", "url-b"),
            ("inline code link", "url-c"),
            ("placeholder home path", "/home/<user>/"),
            ("placeholder email", "example.com"),
            ("clean skill", "FAIL good"),
        ]:
            forbid(label, needle)

        # the exception file silences one tag and only that one
        (repo / ".skillchecks-ignore").write_text("descbig:DESC_LEN  # planted on purpose\n",
                                                  encoding="utf-8")
        code2, out2 = run(repo, denylist)
        if "ignoring 1 exception(s)" not in out2:
            failures.append("ignore file was not read")
        if "DESC_LEN" in out2:
            failures.append("ignored DESC_LEN still reported")
        if "descbig is not in the README" not in out2:
            failures.append("ignore file silenced an unrelated tag (README_ROW vanished)")
        if "PRIVATE_PATH" not in out2 or code2 != 1:
            failures.append("ignore file silenced more than the targeted tag")

        # a clean repo exits 0
        clean = tmp / "clean"
        (clean / "good").mkdir(parents=True)
        (clean / "good" / "SKILL.md").write_text(skill("good"), encoding="utf-8")
        (clean / "README.md").write_text(
            "## Skills\n\n| Skill | What it does |\n|-------|--------------|\n"
            "| [`good`](good/SKILL.md) | clean |\n", encoding="utf-8")
        code3, out3 = run(clean, denylist)
        print(out3)
        if code3 != 0:
            failures.append(f"clean repo should exit 0, got {code3}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("\nSELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print("SELFTEST PASSED — 11 planted defects reported, 6 false-positive traps clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

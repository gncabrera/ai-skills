---
name: troubleshooting
description: >-
  Troubleshoot a live incident: read the runbook first, mitigate before
  diagnosing, run a 60-second sanity checklist, gather evidence for one
  hypothesis at a time, and walk a layer stack from application down to hardware.
  Use when a service is down, degraded, unreachable, throwing errors, or behaving
  differently after a change — and when someone says "it stopped working",
  "debug this", "triage this", or "why is X failing".
license: MIT
---

# Troubleshooting

## The two rules that decide the outcome

1. **Mitigate before you diagnose.** If users are affected, restore service with
   the cheapest reversible workaround first. A root cause found in 40 minutes
   while the service is down is worth less than a restart in 40 seconds followed
   by a proper diagnosis.
2. **One change at a time.** Two changes at once means you no longer know which
   one fixed it — or which one broke something else. Observe, verify, then act.

Everything below is the discipline that makes those two rules work.

**When to use:** a service is down or degraded; a request fails; a job that used
to run doesn't; something changed after a deploy, upgrade, reboot or restore; a
symptom appears with no obvious cause.

**Don't use for:** writing the incident write-up after the fact (that's a
postmortem); planned maintenance; reviewing code (that's a code review); a
question about how something works.

## Phase 0 — Pre-flight

Before touching anything, spend two minutes reading.

1. **Find the existing documentation.** A runbook for this service, a README, an
   architecture note, a previous incident. Most recurring failures are already
   written down somewhere, including the fix.
2. **Rubber-duck the symptom.** State out loud: what the user sees, what should
   happen instead, when it last worked, what changed since. Half the time the
   answer surfaces here.
3. **Read the architecture**, at least the path the request takes: client →
   proxy/DNS → host → runtime → service → storage. You need to know which hop
   you are about to test.
4. **Confirm you have credentials and access** — and never print secret values
   while checking. Verify presence, not content:

   ```bash
   test -n "$SERVICE_TOKEN" && echo "token present" || echo "token MISSING"
   ```

5. **Load the service's own operational notes** if they exist: its health check,
   its restart procedure, its known failure modes. A generic checklist applied to
   an unfamiliar service is slower than that service's own runbook.

## Phase 1 — Define the problem

Write down, in one line each:

- **Symptom** — what is observed, not what you think causes it.
- **Impact** — who or what is affected, and how badly. This drives urgency.
- **Scope** — one service, one host, one user, or everything.
- **Last known good** — when it worked, and what happened in between.

Then look at **what changed**, because that is the highest-yield question in the
whole process:

```bash
git log --oneline -20          # recent commits in the service's config repo
git status --short             # uncommitted local edits
git diff HEAD~1 -- <config>    # what the last change actually touched
```

Also check for changes that aren't in git: automatic updates, a reboot, a
certificate renewal, a full disk, a rotated credential, an expiring token.

## Phase 2 — Stop the bleeding

Restore service with the cheapest reversible action that fits the failure:

1. Restart the process or container.
2. Recreate it (down + up) if a restart isn't enough.
3. Roll back the last config change.
4. Fail over to a replica or a previous version.
5. Accept a degraded state deliberately — document it and schedule the real fix.

Say what you did and what it changed. Then continue to Phase 3: **the service
being up is not the incident being closed.**

## Phase 3 — The 60-second sanity checklist

Cheap checks first. Each failure is a direct clue, and most incidents are caught
here.

```bash
# 1. Is the process/container actually running?
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -i <service>
systemctl is-active <unit>

# 2. Are things in a restart loop?
docker ps --format '{{.Names}} {{.Status}}' | grep -v 'Up'

# 3. Is storage full? Local AND network mounts.
df -h / /var /mnt/<data> 2>/dev/null

# 4. Are the expected mounts present?
mount | grep -E 'nfs|cifs|/mnt'

# 5. Does DNS resolve?
dig +short <service>.<domain>
cat /etc/resolv.conf

# 6. Does the service answer on its own address and port?
curl -sI --max-time 5 http://<host>:<port>/health | head -3
ss -lntp | grep -E ':(80|443|<port>)'

# 7. Is the host reachable, and does it still have its address?
ping -c 2 -W 2 <host>
ip -brief addr show

# 8. Did scheduled jobs fail recently?
#    Check the scheduler's own log/state for the last 24h of failures.

# 9. Any hardware-level complaints?
dmesg -T | tail -40
```

If a check fails, start there. If all pass, the problem is above or below this
layer — go to Phase 4.

## Phase 4 — Rank hypotheses

List 3–7 candidates ordered by probability × cheapness to test. Typical order for
a containerised service:

| Rank | Cause | Quick check |
|------|-------|-------------|
| 1 | Process down or crash-looping | `docker ps`, `docker logs` |
| 2 | Bad config change | `git log`, `git diff` |
| 3 | Disk or inode exhaustion | `df -h`, `df -i` |
| 4 | Storage mount stale or missing | `mount`, `df -h` |
| 5 | Credential or token expired | app logs, 401/403 in logs |
| 6 | Network path broken (DNS, proxy, firewall) | `dig`, `curl -I`, `ss` |
| 7 | Permission/ownership change | `ls -ln <datadir>` |
| 8 | Resource exhaustion (RAM, CPU, fd, connections) | `free -h`, `uptime`, `ulimit` |
| 9 | Hardware failure | `dmesg`, `smartctl -a` |

State the leading hypothesis and the check that would falsify it. Then run that
one check.

## Phase 5 — Gather evidence

Every command should test one hypothesis. Do not run a wall of diagnostics and
read the output for vibes.

```bash
# Runtime
docker ps -a --filter name=<service>
docker logs --tail 200 --timestamps <container>
docker inspect <container> --format '{{json .Mounts}}'

# systemd
systemctl status <unit> --no-pager
journalctl -u <unit> --since "15 min ago" --no-pager

# Network
ip -brief addr
ip route show default
ss -lntp
ip neigh

# Storage
df -h; df -i; lsblk; mount

# DNS
dig +short <host>; dig +short <host> @<dns-server>
```

Read errors before reading status: a container that is "Up" can still be failing
every request, and a healthcheck can be lying if it checks the wrong thing.

**When the host answers but the VM/guest doesn't**, capture packets on the
hypervisor side to find out whether the guest is alive:

```bash
timeout 10 tcpdump -ni <vm-interface> -c 40
```

Signals worth knowing: traffic only from the guest's own bridge means the OS is
running but its address config may be gone; ARP requests arriving with no reply
means the address isn't bound; total silence means the kernel is likely hung —
reboot rather than keep poking.

## Phase 6 — Decision tree for the usual suspects

**Container won't start.** Logs first. Port conflict → `ss -lntp | grep <port>`.
Missing env or auth error → credential check. Bad volume path → `ls -ln` the
mount. Image pull failure → re-pull.

**Service resolves but doesn't answer.** Resolve from two places (client and
host). Right address but no response → proxy/firewall. Proxy 502 → the upstream
behind it is down. Wrong address → stale DNS or proxy entry, usually after a
migration.

**Mount hangs / files vanish.** Check for uninterruptible-sleep processes
**before** unmounting:

```bash
ps -eo stat,pid,cmd | awk '$1 ~ /D/'
```

If any exist, a normal `umount` will hang too. Use a lazy unmount
(`umount -l <mountpoint>`), then remount. If the remount also hangs, the server
side is unresponsive — reboot the client, not the server, and fix the mount
options after. Note that `mount -o remount` does **not** apply new NFS timing
options; those are read at mount time only, so it's `fstab` + remount.

**Full disk.** `df -h` then `df -i`. Deleted-but-open files are the classic case —
a process holding a removed file keeps the space:

```bash
lsof +L1 | head
```

**Slow instead of down.** Compare against a baseline: is it CPU, I/O wait,
network latency, or a lock? `iostat -x 1`, `vmstat 1`, and the app's own timing
logs answer different questions — pick one.

**Everything is broken at once.** Suspect a shared dependency: DNS, the proxy,
the storage export, the container runtime, the hypervisor, or a host reboot.
Prefer one root cause over many coincidental failures.

## Phase 7 — Walk the layers

Start at the layer where the symptom appears, then go **down** until you find the
break. Don't skip a layer without evidence.

```
1. Client          → browser devtools, curl from the client itself
2. Application     → app logs, app health endpoint
3. Runtime         → container/process state, compose/systemd config
4. Reverse proxy   → proxy config, upstream address, TLS certificate
5. Host OS         → systemd, journal, disk, memory, limits
6. Storage         → mounts, exports, free space, inodes
7. DNS             → resolution, zone/records, cache
8. Network         → link, routes, firewall, VPN
9. Power / hardware→ uptime, dmesg, SMART
```

## Phase 8 — Iterate, then stop

After each new piece of evidence: eliminate what's impossible, re-rank the rest,
state the current leading theory, propose the next single check. Never re-run a
check you've already ruled out.

**If three fix attempts fail, stop fixing and question the model.** Three
failures usually mean the hypothesis is wrong, not that the fourth variant will
work. Re-read the architecture, and consider that the symptom is downstream of
something you haven't looked at.

**Exit criteria — it is fine to stop here:**

- [ ] The service works, confirmed from the user's vantage point (not just "the
      process is up").
- [ ] Root cause identified with reasonable confidence, or explicitly deferred.
- [ ] The fix is applied and verified.
- [ ] The workaround and its limits are written down.
- [ ] If 30+ minutes pass with no progress: escalate, roll back, or accept the
      workaround — and say so.

## Phase 9 — Close the loop

The incident is only finished when it can't silently repeat.

- **Postmortem** if there was downtime, data loss, or more than a restart's worth
  of manual work. Use the `postmortem` skill; the timeline you built here feeds
  straight into it.
- **A check that would have caught it** — a health check, a monitor with a
  shorter interval, a pre-flight guard in the script that broke, an alert that
  fires only on failure.
- **Documentation** — new runbook, or fix the existing one that was wrong.
- **A one-line incident log**, if you keep one, so trends become visible:

  ```
  date	service	symptom	root_cause	fix	duration_min	confidence
  ```

- **Memory of the fix**: if the diagnosis took three or more non-obvious steps,
  it belongs in a skill or a runbook, not in this conversation.

## Explain the root cause like an engineer

When you're confident, summarise in four lines:

```
Root cause: <what actually broke>
Evidence:   <the observation that proved it>
Confidence: low | medium | high
Rejected:   <the hypotheses you eliminated, and why>
```

That format is what makes the next incident faster — for you and for whoever
inherits the system.

## Pitfalls

1. **Stopping at the restart.** A restart that fixes the symptom hides the cause.
   The same failure returns, usually at the worst hour. Always continue to Phase 3.
2. **Skipping the sanity checklist.** It is cheap and catches most incidents.
   Jumping from "it's broken" to a clever theory is how you spend an hour on the
   wrong layer.
3. **Changing two things at once.** You lose the ability to attribute the fix —
   and you may have introduced a second fault you'll discover later.
4. **Trusting a healthcheck.** A check that returns 200 while the database is
   unreachable is worse than no check. Verify from the user's vantage point.
5. **Unmounting while processes are stuck.** `umount` hangs on D-state
   processes; use `umount -l`, and expect a reboot if the server side is gone.
6. **Deleting before capturing evidence.** Logs, `dmesg`, config diffs and the
   current state are the diagnosis. Recreating a container "clean" destroys them.
   Copy them out first.
7. **Assuming the change you know about is the change that broke it.** Check
   automatic updates, expiries and reboots too.
8. **Diagnosing on the wrong host.** Confirm the service actually runs where you
   are looking before reading empty logs.
9. **Going destructive to save time.** Delete/recreate/prune when you're out of
   ideas converts a service outage into a data loss incident. Always warn before
   anything irreversible, and back up first.
10. **Never declaring victory.** Troubleshooting with no exit criteria runs until
    someone gives up. Fix, verify, document, stop.

## Verification

- [ ] Symptom reproduced or observed directly — not inferred from a description
- [ ] Documentation/runbook for the service read before changing anything
- [ ] Mitigation applied and its effect confirmed (if users were affected)
- [ ] Sanity checklist run, results recorded
- [ ] Every change made one at a time, with its effect observed
- [ ] Root cause stated with evidence and confidence, or explicitly deferred
- [ ] Fix verified from the user's vantage point
- [ ] Prevention recorded: postmortem, monitor, runbook, or skill

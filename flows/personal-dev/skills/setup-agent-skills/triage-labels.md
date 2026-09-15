# Triage Labels

The **triage axis** governs getting an issue *ready to build* — it is one of several label namespaces
in the pipeline. This file maps the triage roles to the actual strings in this repo's tracker; the
full label state machine (kind / triage / stage / needs:human / blocked) is in
[dev-flow-provisioning.md](./dev-flow-provisioning.md).

| Default label | Label in our tracker | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate this issue |
| `needs-info`   | `needs-info`   | Waiting on reporter for more information |

The single exit out of triage into the build machine is **`needs-triage → stage:ready`**. Two roles
from the old vocabulary are gone:

- **`ready-for-agent` is deleted** — it *was* `stage:ready` under another name.
- **`ready-for-human` became the modifier `needs:human`** — it answers *who executes*, not *where it
  is*, so it is no longer a triage state.
- **`wontfix`** is not a label — close the issue with a reason.

Edit the right-hand column to match whatever vocabulary you actually use. When a skill mentions a
triage role, use the corresponding string here.

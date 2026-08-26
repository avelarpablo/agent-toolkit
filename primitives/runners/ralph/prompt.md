# ralph — generic implementation loop

> **This prompt is a placeholder.** The previous contents were the *Discount Genie*
> workspace prompt (hard-coded repo, Klaviyo OAuth section) and moved to
> [`flows/shopstack/runners/ralph-dg/prompt-dg-workspace.md`](../../../flows/shopstack/runners/ralph-dg/prompt-dg-workspace.md)
> where the flow that owns it lives.
>
> Writing the generic, flow-agnostic prompt is **build item 2.1** (dev loop). It must:
>
> - name no repository, no stage label, and no branch convention beyond
>   "you are on a non-protected branch"
> - implement the slice's checkbox plan with unit/integration TDD plus the inline Codex gate
> - **stop at dev-done** — never close the issue, never write labels; the orchestrator owns
>   every transition
> - respect a hard iteration cap and report what it could not finish
>
> Until 2.1 lands, a project supplies its own prompt via its flow's runner.

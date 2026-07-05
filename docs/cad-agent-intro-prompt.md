# CAD Agent Intro Prompt

Use this from the `cnc-workshop-tools` repo when starting a CAD-focused session
or spawning the custom CAD agent.

```text
Spawn the cad-agent custom agent.

Read docs/ai-cad-stack.md first, then read docs/router-capacity.md and any
project-specific docs that apply. Work as the CAD / physical-engineering agent:
geometry, validation, CNC, composites, moulds, fixtures, workshop process, and
physical coupon planning.

Use $cad-geometry-validation for measurable geometry checks and
$cad-manufacturability-review before making fabrication recommendations.

Task:
[replace this line with the actual CAD/manufacturing job]
```

For a standalone CAD thread where spawning is not available, paste the same text
minus the first line and ask Codex to follow it directly.

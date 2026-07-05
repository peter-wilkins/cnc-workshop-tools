# AI CAD Stack

This is the first pass at a CAD/manufacturing agent stack, analogous to the
software-agent stack: specs, executable artifacts, deterministic checks, visual
review, then human sign-off.

## Current Take

Use a dedicated CAD / physical-engineering agent for serious CAD work.

Reason:

- CAD work needs its own vocabulary: geometry kernels, toolpaths, stock, fixtures,
  moulds, layup, dust, safety, tolerance, and inspection.
- Codex skills use progressive disclosure, so full skill files are not all loaded
  at once, but the initial skill metadata list still has a context budget and can
  get noisy when many unrelated skills are installed.
- A CAD agent can keep CAD/manufacturing skills visible while disabling or
  ignoring most web/app/backend skills.
- The main software agent can still do repo plumbing, CI, web pages, and scripts.

Practical shape:

- `CAD Agent`: geometry, validation, CAM-adjacent checks, manufacturing reviews.
- `Software Agent`: apps, sites, Android, backend, deployment.
- `Workflow Agent`: handoffs, backlog, cross-project coordination.

Do not make this a rigid wall. Use handoffs when a CAD artifact becomes a web
tool, repo feature, or public site page.

Repo implementation:

- `.codex/agents/cad-agent.toml` defines the project-scoped custom CAD agent.
- `docs/cad-agent-intro-prompt.md` gives the pasteable starter prompt.
- `.agents/skills/cad-geometry-validation/` validates generated CAD geometry.
- `.agents/skills/cad-manufacturability-review/` checks whether the design can
  actually be made safely and cleanly.

## Codex Skill Invocation Controls

Matt Pocock's newer skills distinguish user-invoked and model-invoked skills
with `disable-model-invocation: true`.

Current Codex docs do not describe that frontmatter key as the Codex control.
For Codex, use:

```yaml
# agents/openai.yaml inside a skill folder
policy:
  allow_implicit_invocation: false
```

That keeps explicit `$skill` invocation available while preventing automatic
implicit invocation.

For machine-local disabling, use `~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/absolute/path/to/skill/SKILL.md"
enabled = false
```

For a dedicated CAD subagent, Codex custom agents can also carry `skills.config`
overrides in their agent config.

## Source Pass

### CADSmith

Most important research blueprint.

Pattern:

```text
natural language spec
  -> plan
  -> CadQuery code
  -> execute
  -> OpenCASCADE geometry measurements
  -> visual judge
  -> repair loop
```

Takeaway:

- Do not trust a rendered screenshot alone.
- Measure bounding boxes, volume, validity, and feature positions directly from
  the geometry kernel.
- Use screenshots/renders for holistic visual checks after deterministic checks.

Useful for us:

- ammonite slices: verify slab count, overall dimensions, registration holes.
- foil board generator: verify volume, length, width, rocker, box position.
- fixtures: verify hole positions, symmetry, clearances, stock envelope.

Sources:

- https://arxiv.org/abs/2603.26512
- https://github.com/jabarkle/CADSmith

### Forgent3D

Closest local product/workbench pattern.

It is explicitly built for coding agents generating, rebuilding, previewing, and
revising real local geometry. It also frames web exploration and local desktop
workbench as complementary rather than competing modes.

Takeaway:

- A browser preview loop matters.
- Local files and private geometry matter once a toy model becomes a real project.
- We should inspect whether its runtime/viewer can save us building our own too
  early.

Source:

- https://github.com/forgent3d/forgent3d

### CAD/CAE Copilot

Most ambitious engineering-workbench pattern.

It uses build123d / OpenCASCADE, emits STEP/STL/GLB/source/topology metadata,
keeps artifacts reproducible in a `.aieng` package, and has an MCP interface for
agents.

Takeaway:

- CAD should preserve source, exports, checks, thumbnails, and provenance
  together.
- Stable topology pointers are important for edits and simulation setup.
- CAE should be a separate approval-gated step, not silently implied by CAD
  generation.

Source:

- https://github.com/armpro24-blip/cad-cae-copilot

### CAD Skills / text-to-cad

Closest "Matt Pocock for AI CAD" candidate right now.

It is not one person-as-teacher in the Matt Pocock style, but
`earthtojake/text-to-cad` is the clearest skill-library approach:

- CAD skill: generate/edit models, STEP primary output.
- CAD viewer skill: browser previews for CAD, G-code, and robot files.
- step.parts skill: source off-the-shelf STEP parts.

Takeaway:

- We should study the skill shape before inventing our own.
- Our differentiator is not "make generic CAD"; it is physical manufacturing
  judgement: CNC, composites, moulds, layup, workshop layout, and safety.

Source:

- https://github.com/earthtojake/text-to-cad

### FreeCAD Skills

There are already skills for FreeCAD Python, macros, parametric objects,
mesh-solid conversion, CAM automation, and custom workbenches.

Takeaway:

- Do not start by writing a general FreeCAD skill.
- Borrow the shape if we need FreeCAD-specific automation.
- Keep FreeCAD as an inspection/editing target, not necessarily the first source
  of truth.

Source:

- https://mcpservers.org/agent-skills/github/freecad-scripts

### AgentSCAD

Interesting but lower priority.

It uses OpenSCAD as source of truth, renders to STL/PNG, validates meshes, and
has repair loops. Good for simple 3D-printable parametric parts, less obviously
right for CNC/composites work where STEP/BREP and surfaces matter more.

Source:

- https://github.com/Kevoyuan/AgentSCAD

### Awesome Physical Engineering AI

Use as the periodic radar.

It maps CAD, CAE, CFD, CAM, manufacturing, inspection, materials, digital twins,
and official MCP connectors.

Source:

- https://github.com/010zx00x1/Awesome-Physical-Engineering-AI

### Awesome CAD

Useful background list for open-source CAD projects, kernels, viewers, datasets,
and research.

Source:

- https://github.com/mlightcad/awesome-cad

## Recommended Stack v0

### 1. Source-of-truth geometry

Default:

- CadQuery or build123d for precise parametric solids.
- Python source committed with parameters at the top.
- Export STEP first, STL/GLB/PNG as derived artifacts.

Use Blender when:

- the object is organic, sculptural, visual, or mesh-first.
- examples: ammonites, fossil textures, reaction-diffusion patterns, presentation
  renders.

Use OpenSCAD when:

- the part is simple, printable, and constructive-solid-geometry friendly.
- examples: brackets, holders, simple ducts, jigs.

### 2. Execution harness

Every generated model should have:

- source file
- parameter manifest
- generated STEP/STL/GLB where relevant
- thumbnail/render
- geometry report
- manufacturing report
- provenance record: prompt/spec, generator version, tool versions, commit hash

### 3. Deterministic validation

Start with boring checks:

- execution succeeds
- solid validity
- watertightness where needed
- bounding box
- volume and mass estimate
- named features exist
- hole centers and diameters
- symmetry
- minimum wall thickness
- stock envelope
- tool reach / slab depth constraint
- registration features present when slicing

### 4. Visual review

Use generated renders for:

- shape plausibility
- recognisability
- surface/rib/detail aesthetics
- obvious slicing/glue-up weirdness
- "does this look stupid?" checks

Visual review is useful but second-class evidence. Geometry measurements are the
primary pass/fail signal.

### 5. Manufacturing review

This is where our skills should be strongest.

Checks:

- Can the machine reach it?
- Can it be held down?
- Where does waste go?
- What breaks during machining?
- What needs tabs, ears, registration holes, or fixtures?
- What finishing work remains?
- What PPE/extraction is needed?
- What coupon should be cut first?

### 6. Physical coupons

Software tests are not enough. The physical stack needs coupons:

- shape coupon
- material coupon
- glue-up coupon
- finish coupon
- toolpath air-cut
- scrap-stock cut

Record results back into the project docs.

## First Skills To Build

### Model-invoked skills

These are safe for the agent to reach for automatically.

- `cad-geometry-validation`: inspect generated CAD reports and decide whether
  measurements match the spec.
- `cad-manufacturability-review`: check stock, tool reach, workholding, toolpath
  risk, finishing effort, and physical coupons.
- `cad-visual-review`: compare renders/screenshots with intent and flag obvious
  aesthetic or spatial failures.
- `cad-source-provenance`: make sure generated artifacts include source,
  parameters, tool versions, and commit hash.

### User-invoked skills

These should not auto-trigger unless explicitly requested.

- `grill-cad-brief`: interview the human before modelling.
- `mould-split-review`: choose split lines, flanges, registration, release
  strategy, and layup access.
- `composite-layup-review`: fibre orientation, core, vacuum strategy, peel ply,
  resin estimate, cure cycle.
- `cnc-fixture-review`: design and review fixtures, tabs, dowels, spoilboard
  strategy, and safe first cuts.
- `workshop-process-review`: dust, extraction, PPE, clean/dirty separation,
  neighbour risk, repeatability.

For Codex, user-invoked skills should include:

```yaml
# agents/openai.yaml
policy:
  allow_implicit_invocation: false
```

## "Matt Pocock Of AI CAD"

No single equivalent yet.

Closest current anchors:

- Research blueprint: CADSmith.
- Agent workbench: Forgent3D.
- Engineering workbench: CAD/CAE Copilot.
- Skill-library pattern: earthtojake/text-to-cad.
- Radar list: Awesome Physical Engineering AI.

So for now the strategy is to follow projects, not a guru.

Our opportunity is the layer above generic text-to-CAD:

```text
geometry generation
  -> deterministic checks
  -> manufacturing judgement
  -> physical coupon loop
  -> workshop/process knowledge
```

That is closer to "AI manufacturing discipline" than "AI CAD prompting".

## Next Experiment

Pick one small object and run the whole loop:

1. Generate source-of-truth geometry.
2. Export STEP/STL/PNG.
3. Produce a geometry report.
4. Produce a manufacturability report.
5. Produce a visual review.
6. Decide the first coupon.

Best candidate: a foam-sliced mini ammonite with registration ears.

It exercises organic modelling, slicing, tool reach, glue-up, visual judgement,
and physical coupons without risking expensive stock.

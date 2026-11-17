---
name: write-method-docs
description: Write or revise scientific method documentation with equations, algorithm sketches, and implementation-status notes.
argument-hint: "[topic or target doc path]"
---

# Writing Scientific Method Documentation

Use this skill when writing theory-first scientific documentation for methods,
algorithms, and techniques in this repo.

## Purpose

These documents explain how a method works, why it is used, what equations govern it, how the
algorithm proceeds, and how the package implements it. The main body teaches the method rather
than describing the code.

## When to Use This Skill

Use this skill for:

- New method documentation pages.
- Revisions of existing scientific-method pages.
- Expanding stubs into full equation-and-algorithm references.
- Harmonizing scientific documentation across packages.

Do not use this skill for:

- API-only documentation.
- Quickstart guides or installation docs.
- Changelogs or release notes.
- Pure implementation architecture documents unless explicitly requested.

## Core Principles

- Open with a three- or four-sentence overview of the method and why it matters.
- Put theory first. Explain the method before the package's implementation.
- Include every defining equation: objective, transform, update, eigenvalue problem, projector,
  or recurrence.
- Include an algorithm sketch where it helps. A reader should learn how to carry out the method,
  not only its name.
- Keep implementation status out of the theory. Describe the package's behavior in its own
  section near the end.
- Make every reference in the final section a markdown hyperlink, preferring DOI links.
- Use markdown links rather than raw paths.
- Use Unicode Greek letters and mathematical symbols where they read more clearly.

## Required Structure

Most method documents follow this structure, adapted to the topic:

```md
# <Title>

Introductory paragraph.

## Overview

## Core Theory

## Key Equations

## Algorithm Sketch

## Practical Considerations

## Relationship To Other Methods

## Current Implementation

## References
```

Not every document needs every heading, but each needs these components:

- A clear introduction.
- A theory-focused explanation.
- The central equations.
- An algorithm or pseudocode sketch when relevant.
- Practical limitations or caveats.
- A dedicated near-end implementation section.
- A final references section.

## Header And Style Rules

- H1 and H2 headers use Title Case.
- H3 and deeper headers use sentence case.
- List items generally start with a capital letter.
- Prefer markdown links over inline-code paths.
- Prefer concise, formal scientific prose.
- Keep terminology consistent within a document.

Examples:

```md
# Rational Function Optimization

## Key Equations

### Restricted-step variant
```

## Equations And Algorithms

- Include displayed equations for the core mathematical content.
- Define symbols in nearby prose unless they are standard in context.
- Omit equations that do not help explain the method.
- Include pseudocode or a numbered algorithm sketch when the method involves
  iterative or branching logic.

Good candidates for displayed equations include:

- Objective functions.
- Trust-region constraints.
- Hessian update formulas.
- Coordinate transforms.
- Augmented eigenvalue problems.
- Projection operators.
- Convergence conditions.

Example:

```md
$$
m(s) = g^T s + \frac{1}{2} s^T H s
$$

1. build the local model
2. compute a trial step
3. apply any trust-region restriction
4. evaluate the new point
5. update the model
```

## Current Implementation Section

Place the implementation discussion near the end of the document, after the main
scientific content.

This section should answer:

- Is the method currently implemented?
- Where is it implemented?
- What variant is implemented?
- How does the implementation differ from the canonical literature formulation?
- What is missing, simplified, or future work?

Keep it distinct from the theory. The main body should not become a code tour unless the user
asked for an implementation-focused document.

## References

Every document must end with a `## References` section.

Reference rules:

- Every entry must be a markdown hyperlink.
- Prefer DOI links.
- If a DOI is unavailable, use a stable publisher, manual, or project page.
- List primary literature first, then software or manual references.

Example style:

```md
## References

1. [Bakken, V.; Helgaker, T. The efficient optimization of molecular geometries using redundant internal coordinates. J. Chem. Phys. 117, 9160–9174](https://doi.org/10.1063/1.1515483)
2. [Baker, J.; Kessi, A.; Delley, B. The generation and use of delocalized internal coordinates in geometry optimization. J. Chem. Phys. 105, 192–212](https://doi.org/10.1063/1.471864)
```

## Cross-Linking

- Use descriptive markdown link text.
- Prefer relative links appropriate to the target file location.
- Link related method, usage, or theory pages when they help orient the reader.
- Do not paste raw filenames without link text.

Good:

```md
See [Trust-Region Newton](trust-region-newton.md) and
[Hessian updates](hessian-updates.md).
```

Avoid:

```md
See `docs/step-trust-region-newton.md`.
```

## Workflow

When writing a new scientific method page:

1. Read neighboring pages for structure, terminology, and cross-link conventions.
2. Read source files only as far as needed to establish implementation status.
3. Gather the canonical references and, where useful, a modern supporting one.
4. Draft the theory-first explanation.
5. Add the governing equations.
6. Add an algorithm sketch or pseudocode when relevant.
7. Add a near-end implementation-status section.
8. End with linked references.
9. Verify header capitalization, link formatting, and list capitalization.

## Final Checklist

- H1 and H2 use Title Case.
- H3 and deeper use sentence case.
- List items generally start with a capital letter.
- The main body is theory-first.
- All key equations are included.
- An algorithm sketch is included when relevant.
- The implementation section appears near the end.
- The document finishes with `## References`.
- Every reference is a markdown hyperlink.
- DOI links are used where possible.
- Markdown links are used instead of raw path literals.

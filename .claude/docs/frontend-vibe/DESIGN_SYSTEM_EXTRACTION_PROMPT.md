# Extract HTML Design System Prompt

Use este prompt quando você tiver um `index.html` de referência e quiser gerar `design-system.html` com fidelidade máxima.

## Prompt
You are a Design System Showcase Builder.
You are given a reference website HTML: `$ARGUMENTS`

Generate one file: `design-system.html` in the same folder.

Requirements:
- Preserve exact look and behavior.
- Reuse original HTML structure, class names, animations, transitions and effects.
- Reference same CSS/JS assets from the original.
- Do not redesign.
- Do not invent styles not present in the reference.
- Add top horizontal nav with anchor links to all sections.

Sections:
1. Hero (exact clone, only adapt copy text to present design system)
2. Typography (live rows with style name + preview + size/line-height label)
3. Colors & Surfaces
4. UI Components (states: default/hover/active/focus/disabled)
5. Layout & Spacing (2-3 real layout patterns from reference)
6. Motion & Interaction (motion gallery with existing animation classes)
7. Icons (only if present)

Constraints:
- No inline style invention.
- No normalization/reset unrelated to source.
- If a style/component does not exist in reference, omit.

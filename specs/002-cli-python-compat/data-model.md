# Data Model: CLI Python Version Compatibility

## RenderSourceFormat

The CLI's choice of input kind.

| Member | Value | Selects |
|--------|-------|---------|
| `STU3` | `"STU3"` | `Stu3FhirRenderer` |
| `CCDA` | `"CCDA"` | `CcdaRenderer` |

**Invariants (must hold on Python 3.8 to 3.12):**

- `RenderSourceFormat("CCDA") is RenderSourceFormat.CCDA` (lookup by value).
- `RenderSourceFormat("ccda")` raises `ValueError` (case-sensitive, unchanged).
- `RenderSourceFormat.CCDA == "CCDA"` and `isinstance(RenderSourceFormat.CCDA, str)`.
- `str(RenderSourceFormat.CCDA) == "CCDA"` and `f"{RenderSourceFormat.CCDA}" == "CCDA"`.
- `render_map` has exactly these two keys.

No state transitions. No persistence.

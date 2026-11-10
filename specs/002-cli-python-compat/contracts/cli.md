# Contract: `fhir_converter_cli` / `python -m fhir_converter`

This feature must **not** change this contract. It only makes it available on Python 3.8 to 3.10.

## Arguments

| Argument | Required | Value |
|----------|----------|-------|
| `--from-file <Path>` | one of from-file / from-dir | file to render |
| `--from-dir <Path>` | one of from-file / from-dir | folder to render; wins over `--from-file` |
| `--to-dir <Path>` | yes | output folder (parent must exist) |
| `--template-dir <Path>` | no | user template folder |
| `--template-name <str>` | yes | template to render with |
| `--source-format <RenderSourceFormat>` | yes | `CCDA` or `STU3`, case-sensitive |
| `--continue_on_error` | no | flag |
| `--flatten_to_dir` | no | flag |

## Exit codes

| Code | When |
|------|------|
| 0 | render succeeded; summary prints `RENDER SUCCESS` |
| 1 | render failed; traceback then `RENDER FAILURE` |
| 2 | argument error (argparse usage error), nothing rendered, output folder not created |

## Error message for a bad source format

`argument --source-format: invalid RenderSourceFormat value: '<value>'` on stderr, exit 2.

## Output

One `<input base name>.json` per input file in `--to-dir`.

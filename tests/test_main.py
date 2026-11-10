from json import loads
from pathlib import Path
from typing import List
from unittest import TestCase

import pytest

from fhir_converter.__main__ import (
    RenderSourceFormat,
    get_argparser,
    main,
    parse_args,
    render_map,
)
from fhir_converter.renderers import CcdaRenderer, Stu3FhirRenderer

SAMPLE_CCDA = Path(__file__).parent / "data" / "ccda" / "sample.ccda"


class RenderSourceFormatTest(TestCase):
    def test_lookup_by_value(self) -> None:
        self.assertIs(RenderSourceFormat("CCDA"), RenderSourceFormat.CCDA)
        self.assertIs(RenderSourceFormat("STU3"), RenderSourceFormat.STU3)

    def test_lookup_is_case_sensitive(self) -> None:
        with self.assertRaises(ValueError):
            RenderSourceFormat("ccda")

    def test_is_str(self) -> None:
        self.assertIsInstance(RenderSourceFormat.CCDA, str)
        self.assertEqual(RenderSourceFormat.CCDA, "CCDA")
        self.assertEqual(RenderSourceFormat.STU3, "STU3")

    def test_str_and_format_return_value(self) -> None:
        self.assertEqual(str(RenderSourceFormat.CCDA), "CCDA")
        self.assertEqual(f"{RenderSourceFormat.CCDA}", "CCDA")
        self.assertEqual(str(RenderSourceFormat.STU3), "STU3")
        self.assertEqual(f"{RenderSourceFormat.STU3}", "STU3")

    def test_render_map_keys(self) -> None:
        self.assertEqual(set(render_map), {"STU3", "CCDA"})


def cli_args(to_dir: Path, source_format: str = "CCDA") -> List[str]:
    return [
        "--from-file",
        str(SAMPLE_CCDA),
        "--to-dir",
        str(to_dir),
        "--template-name",
        "CCD",
        "--source-format",
        source_format,
    ]


def test_help_exits_zero(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "--source-format" in capsys.readouterr().out


def test_render_ccda_file(tmp_path: Path) -> None:
    to_dir = tmp_path / "out"
    with pytest.raises(SystemExit) as exc:
        main(cli_args(to_dir))
    assert exc.value.code == 0

    out_file = to_dir / "sample.json"
    assert out_file.is_file()
    assert loads(out_file.read_text(encoding="utf-8"))["resourceType"] == "Bundle"


@pytest.mark.parametrize(
    "source_format, renderer",
    [("CCDA", CcdaRenderer), ("STU3", Stu3FhirRenderer)],
)
def test_source_format_selects_renderer(tmp_path: Path, source_format: str, renderer: type) -> None:
    args = parse_args(get_argparser(), cli_args(tmp_path, source_format))
    assert args.source_format is RenderSourceFormat(source_format)
    assert render_map[args.source_format] is renderer


@pytest.mark.parametrize("source_format", ["HL7V2", "ccda"])
def test_invalid_source_format(tmp_path: Path, capsys: pytest.CaptureFixture, source_format: str) -> None:
    to_dir = tmp_path / "out"
    with pytest.raises(SystemExit) as exc:
        main(cli_args(to_dir, source_format))
    assert exc.value.code == 2
    assert f"invalid RenderSourceFormat value: '{source_format}'" in capsys.readouterr().err
    assert not to_dir.exists()


def test_missing_source_format(tmp_path: Path) -> None:
    args = cli_args(tmp_path / "out")[:-2]
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2

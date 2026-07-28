"""Render source files declared by pattern metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError


class RenderError(ValueError):
    """Report an output rendering failure."""


def resolve_output_path(destination_dir: Path, rendered_path: str) -> Path:
    """Resolve a rendered output path under the current directory."""
    output = Path(rendered_path)
    if output.is_absolute():
        return output
    return destination_dir / output


def render_outputs(
    pattern_dir: Path,
    meta: dict[str, Any],
    context: dict[str, Any],
    destination_dir: Path,
    force: bool = False,
) -> list[Path]:
    """Render and overwrite all outputs declared by the pattern."""
    templates_dir = pattern_dir / "templates"
    environment = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    generated: list[Path] = []

    try:
        for output in meta["outputs"]:
            if not isinstance(output, dict):
                raise RenderError("cada saída de meta.yaml deve ser um mapeamento")

            template_name = output.get("template")
            output_template = output.get("output_path")
            if not isinstance(template_name, str) or not isinstance(
                output_template, str
            ):
                raise RenderError(
                    "cada saída precisa de 'template' e 'output_path'"
                )

            rendered_path = environment.from_string(output_template).render(
                **context
            )
            destination = resolve_output_path(destination_dir, rendered_path)
            source = environment.get_template(template_name).render(**context)

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(source, encoding="utf-8")
            generated.append(destination)
    except (OSError, TemplateError, KeyError) as error:
        raise RenderError(f"falha ao gerar arquivos: {error}") from error

    return generated

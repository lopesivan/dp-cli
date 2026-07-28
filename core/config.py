"""Read, create, and update generator YAML configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, StrictUndefined, TemplateError


class ConfigError(ValueError):
    """Report an invalid generator configuration."""


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from a file."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConfigError(f"não foi possível ler {path.name}: {error}") from error
    except yaml.YAMLError as error:
        raise ConfigError(f"YAML inválido em {path.name}: {error}") from error

    if not isinstance(data, dict):
        raise ConfigError(f"{path.name} deve conter um mapeamento YAML")
    return data


def load_meta(path: Path) -> dict[str, Any]:
    """Load and minimally validate a pattern metadata file."""
    meta = load_yaml(path)
    fields = meta.get("fields")
    outputs = meta.get("outputs")
    if not isinstance(fields, list):
        raise ConfigError(f"{path.name}: 'fields' deve ser uma lista")
    if not isinstance(outputs, list) or not outputs:
        raise ConfigError(f"{path.name}: 'outputs' deve ser uma lista não vazia")

    for field in fields:
        if not isinstance(field, dict) or not isinstance(field.get("name"), str):
            raise ConfigError(f"{path.name}: cada campo precisa de um nome")
        if "default" not in field:
            raise ConfigError(
                f"{path.name}: campo '{field['name']}' não possui default"
            )

    for output in outputs:
        if (
            not isinstance(output, dict)
            or not isinstance(output.get("template"), str)
            or not isinstance(output.get("output_path"), str)
        ):
            raise ConfigError(
                f"{path.name}: cada saída precisa de template e output_path"
            )
    return meta


def load_config(path: Path) -> dict[str, Any]:
    """Load key.yaml."""
    return load_yaml(path)


def field_defaults(meta: dict[str, Any]) -> dict[str, Any]:
    """Return the default value for every declared field."""
    defaults: dict[str, Any] = {}
    for field in meta["fields"]:
        defaults[field["name"]] = field["default"]
    return defaults


def yaml_value(value: Any) -> str:
    """Serialize one value as compact YAML."""
    serialized = yaml.safe_dump(
        value,
        default_flow_style=True,
        allow_unicode=True,
        sort_keys=False,
    ).strip()
    if serialized.endswith("\n..."):
        return serialized[:-4]
    return serialized


def create_config(
    template_path: Path,
    destination: Path,
    meta: dict[str, Any],
    language: str,
    pattern: str,
) -> None:
    """Render a new editable key.yaml file."""
    if not template_path.is_file():
        raise ConfigError(f"template de configuração ausente: {template_path.name}")

    context = field_defaults(meta)
    context.update({"language": language, "pattern": pattern})
    environment = Environment(
        autoescape=False,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    environment.filters["yaml_value"] = yaml_value

    try:
        rendered = environment.from_string(
            template_path.read_text(encoding="utf-8")
        ).render(**context)
    except OSError as error:
        raise ConfigError(
            f"não foi possível ler {template_path.name}: {error}"
        ) from error
    except TemplateError as error:
        raise ConfigError(
            f"falha ao gerar key.yaml a partir de {template_path.name}: {error}"
        ) from error

    destination.write_text(rendered, encoding="utf-8")


def merge_missing_defaults(
    config: dict[str, Any],
    meta: dict[str, Any],
    language: str,
    pattern: str,
) -> tuple[dict[str, Any], list[str]]:
    """Fill missing required values with metadata defaults."""
    merged = dict(config)
    missing: list[str] = []
    identity_defaults = {"pattern": pattern, "language": language}

    for name, default in identity_defaults.items():
        if name not in merged:
            merged[name] = default
            missing.append(name)

    for field in meta["fields"]:
        name = field["name"]
        required = bool(field.get("required", True))
        if required and (name not in merged or merged[name] is None):
            merged[name] = field["default"]
            missing.append(name)

    return merged, missing


def save_config(path: Path, config: dict[str, Any]) -> None:
    """Write a normalized YAML configuration."""
    try:
        content = yaml.safe_dump(
            config,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        raise ConfigError(f"não foi possível atualizar {path.name}: {error}") from error

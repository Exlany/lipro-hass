"""Architecture policy checker for plane/root/surface/authority enforcement."""

from __future__ import annotations

import argparse
from itertools import pairwise
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.lib.architecture_policy import (
        ArchitecturePolicyRule,
        load_policy_text,
        load_structural_rules,
        load_targeted_bans,
        policy_root,
        resolve_policy_paths,
    )
    from scripts.lib.ast_guard_utils import (
        extract_all,
        extract_property_names,
        extract_top_level_bindings,
        find_forbidden_imports,
    )
elif __package__ in {None, ""}:
    from lib.architecture_policy import (
        ArchitecturePolicyRule,
        load_policy_text,
        load_structural_rules,
        load_targeted_bans,
        policy_root,
        resolve_policy_paths,
    )
    from lib.ast_guard_utils import (
        extract_all,
        extract_property_names,
        extract_top_level_bindings,
        find_forbidden_imports,
    )
else:
    from scripts.lib.architecture_policy import (
        ArchitecturePolicyRule,
        load_policy_text,
        load_structural_rules,
        load_targeted_bans,
        policy_root,
        resolve_policy_paths,
    )
    from scripts.lib.ast_guard_utils import (
        extract_all,
        extract_property_names,
        extract_top_level_bindings,
        find_forbidden_imports,
    )

_EXPECTED_STRUCTURAL_RULE_IDS = {
    "ENF-IMP-ENTITY-PROTOCOL-INTERNALS",
    "ENF-IMP-CONTROL-NO-BYPASS",
    "ENF-IMP-BOUNDARY-LOCALITY",
    "ENF-GOV-DEPENDENCY-POLICY-REF",
    "ENF-GOV-PUBLIC-SURFACE-POLICY-REF",
    "ENF-GOV-AUTHORITY-POLICY-REF",
    "ENF-GOV-VERIFICATION-POLICY-REF",
    "ENF-GOV-CI-FAIL-FAST",
    "ENF-GOV-RELEASE-CI-REUSE",
    "ENF-IMP-API-LEGACY-SPINE-LOCALITY",
    "ENF-IMP-MQTT-TRANSPORT-LOCALITY",
    "ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT",
    "ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW",
    "ENF-IMP-HEADLESS-PROOF-LOCALITY",
    "ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR",
    "ENF-IMP-ASSURANCE-NO-PRODUCTION-BACKFLOW",
}
_DOC_REQUIRED_TOKENS = {
    Path("AGENTS.md"): ("Phase 5 已关闭 coordinator 私有 auth seam", ".planning/codebase/*.md"),
    Path("docs/developer_architecture.md"): ("协作图谱身份", ".planning/codebase/*.md", "派生视图"),
}
_DOC_FORBIDDEN_TOKENS = {
    Path("AGENTS.md"): ("仍有 coordinator 私有 auth seam",),
    Path(".planning/codebase/STRUCTURE.md"): ("runtime-auth seam",),
    Path(".planning/codebase/ARCHITECTURE.md"): ("runtime-auth seam：`custom_components/lipro/services/execution.py`",),
    Path(".planning/reviews/FILE_MATRIX.md"): ("| `custom_components/lipro/services/execution.py` | Control | Phase 5 / 7 | 迁移适配 | runtime-auth seam |",),
}

_EXPECTED_TARGETED_BAN_IDS = {
    "ENF-SURFACE-COORDINATOR-ENTRY",
    "ENF-SURFACE-API-EXPORTS",
    "ENF-SURFACE-PROTOCOL-EXPORTS",
    "ENF-BACKDOOR-COORDINATOR-PROPERTIES",
    "ENF-BACKDOOR-SERVICE-AUTH",
    "ENF-COMPAT-ROOT-NO-LEGACY-CLIENT",
    "ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT",
    "ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS",
    "ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT",
    "ENF-ADAPTER-CONFIG-FLOW-USES-AUTH-PROJECTION",
    "ENF-ADAPTER-ENTRY-AUTH-USES-BOOTSTRAP",
    "ENF-HOSTPROJ-CATEGORIES-NO-HA-PLATFORMS",
    "ENF-HOSTPROJ-CAPABILITY-NO-PLATFORM-FIELD",
    "ENF-HOSTPROJ-DEVICE-VIEWS-NO-PLATFORM-PROJECTION",
    "ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS",
    "ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW",
}


def _relative(path: Path, *, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _validate_policy_inventory(root: Path) -> list[str]:
    errors: list[str] = []
    text = load_policy_text(root)

    if "## Structural Rules" not in text:
        errors.append("ARCHITECTURE_POLICY missing '## Structural Rules' section")
    if "## Targeted Regression Bans" not in text:
        errors.append("ARCHITECTURE_POLICY missing '## Targeted Regression Bans' section")

    structural_rules = load_structural_rules(root)
    targeted_bans = load_targeted_bans(root)

    structural_rule_ids = set(structural_rules)
    targeted_ban_ids = set(targeted_bans)

    if structural_rule_ids != _EXPECTED_STRUCTURAL_RULE_IDS:
        errors.append(
            "ARCHITECTURE_POLICY structural rule set mismatch: "
            f"expected={sorted(_EXPECTED_STRUCTURAL_RULE_IDS)}, actual={sorted(structural_rule_ids)}"
        )
    if targeted_ban_ids != _EXPECTED_TARGETED_BAN_IDS:
        errors.append(
            "ARCHITECTURE_POLICY targeted ban set mismatch: "
            f"expected={sorted(_EXPECTED_TARGETED_BAN_IDS)}, actual={sorted(targeted_ban_ids)}"
        )
    return errors


def _check_import_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    governed_paths, missing_governed = resolve_policy_paths(rule.governed_targets, root=root)
    allowed_paths, missing_allowed = resolve_policy_paths(
        rule.allowed_or_required_signals,
        root=root,
    )
    allowed_path_set = set(allowed_paths)
    disallowed_paths = [path for path in governed_paths if path not in allowed_path_set]

    errors: list[str] = []
    for missing in missing_governed:
        errors.append(f"{rule.rule_id} unresolved governed path pattern: {missing}")
    for missing in missing_allowed:
        errors.append(f"{rule.rule_id} unresolved allowed path pattern: {missing}")

    if errors:
        return errors

    violations = find_forbidden_imports(
        disallowed_paths,
        tuple(rule.forbidden_signals),
        root=root,
    )
    return [f"{rule.rule_id}: {violation}" for violation in violations]


def _check_file_contains_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    if len(rule.governed_targets) != 1:
        return [f"{rule.rule_id}: file_contains mode requires exactly one governed file"]
    file_path = root / rule.governed_targets[0]
    if not file_path.exists():
        return [f"{rule.rule_id}: governed file missing: {_relative(file_path, root=root)}"]
    text = file_path.read_text(encoding="utf-8")
    missing = [signal for signal in rule.allowed_or_required_signals if signal not in text]
    return [
        f"{rule.rule_id}: {_relative(file_path, root=root)} missing required signal '{signal}'"
        for signal in missing
    ]


def _check_ordered_tokens_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    if len(rule.governed_targets) != 1:
        return [f"{rule.rule_id}: ordered_tokens mode requires exactly one governed file"]
    file_path = root / rule.governed_targets[0]
    if not file_path.exists():
        return [f"{rule.rule_id}: governed file missing: {_relative(file_path, root=root)}"]
    text = file_path.read_text(encoding="utf-8")

    positions: list[tuple[str, int]] = []
    for signal in rule.allowed_or_required_signals:
        position = text.find(signal)
        if position < 0:
            return [
                f"{rule.rule_id}: {_relative(file_path, root=root)} missing ordered token '{signal}'"
            ]
        positions.append((signal, position))

    errors: list[str] = []
    for (current_signal, current_position), (_, next_position) in pairwise(positions):
        if current_position > next_position:
            errors.append(
                f"{rule.rule_id}: ordered token '{current_signal}' appears after its successor"
            )
    return errors


def _check_all_exact_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    file_path = root / rule.governed_targets[0]
    actual = set(extract_all(file_path, root=root))
    expected = set(rule.allowed_or_required_signals)
    if actual != expected:
        return [
            f"{rule.rule_id}: {_relative(file_path, root=root)} exports mismatch: expected={sorted(expected)}, actual={sorted(actual)}"
        ]
    return []


def _check_all_contains_disjoint_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    file_path = root / rule.governed_targets[0]
    public_symbols = set(extract_all(file_path, root=root))
    errors: list[str] = []

    missing = sorted(set(rule.allowed_or_required_signals) - public_symbols)
    forbidden = sorted(public_symbols.intersection(rule.forbidden_signals))

    if missing:
        errors.append(
            f"{rule.rule_id}: {_relative(file_path, root=root)} missing required exports: {missing}"
        )
    if forbidden:
        errors.append(
            f"{rule.rule_id}: {_relative(file_path, root=root)} exposes forbidden exports: {forbidden}"
        )
    return errors


def _check_property_contains_disjoint_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    target = rule.governed_targets[0]
    if "::" not in target:
        return [f"{rule.rule_id}: property_contains_disjoint requires '<file>::<Class>' target"]
    relative_path, class_name = target.split("::", maxsplit=1)
    file_path = root / relative_path
    property_names = extract_property_names(file_path, class_name, root=root)

    errors: list[str] = []
    missing = sorted(set(rule.allowed_or_required_signals) - property_names)
    forbidden = sorted(property_names.intersection(rule.forbidden_signals))

    if missing:
        errors.append(f"{rule.rule_id}: {target} missing required properties: {missing}")
    if forbidden:
        errors.append(f"{rule.rule_id}: {target} exposes forbidden properties: {forbidden}")
    return errors


def _check_file_contains_disjoint_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    file_path = root / rule.governed_targets[0]
    text = file_path.read_text(encoding="utf-8")
    errors: list[str] = []

    missing = [signal for signal in rule.allowed_or_required_signals if signal not in text]
    forbidden = [signal for signal in rule.forbidden_signals if signal in text]

    for signal in missing:
        errors.append(
            f"{rule.rule_id}: {_relative(file_path, root=root)} missing required token '{signal}'"
        )
    for signal in forbidden:
        errors.append(
            f"{rule.rule_id}: {_relative(file_path, root=root)} contains forbidden token '{signal}'"
        )
    return errors


def _check_top_level_bindings_disjoint_rule(root: Path, rule: ArchitecturePolicyRule) -> list[str]:
    file_path = root / rule.governed_targets[0]
    bindings = set(extract_top_level_bindings(file_path, root=root))
    errors: list[str] = []

    missing = sorted(set(rule.allowed_or_required_signals) - bindings)
    forbidden = sorted(bindings.intersection(rule.forbidden_signals))

    if missing:
        errors.append(
            f"{rule.rule_id}: {_relative(file_path, root=root)} missing required bindings: {missing}"
        )
    if forbidden:
        errors.append(
            f"{rule.rule_id}: {_relative(file_path, root=root)} binds forbidden names: {forbidden}"
        )
    return errors


def validate_structural_rules(root: Path) -> list[str]:
    """Validate import and governance rules declared in `ARCHITECTURE_POLICY.md`."""
    errors: list[str] = []
    for rule in load_structural_rules(root).values():
        if rule.mode == "imports_disjoint":
            errors.extend(_check_import_rule(root, rule))
            continue
        if rule.mode == "file_contains":
            errors.extend(_check_file_contains_rule(root, rule))
            continue
        if rule.mode == "ordered_tokens":
            errors.extend(_check_ordered_tokens_rule(root, rule))
            continue
        errors.append(f"{rule.rule_id}: unsupported structural rule mode '{rule.mode}'")
    return errors


def validate_targeted_bans(root: Path) -> list[str]:
    """Validate focused regression bans derived from the policy baseline."""
    errors: list[str] = []
    for rule in load_targeted_bans(root).values():
        if rule.mode == "all_exact":
            errors.extend(_check_all_exact_rule(root, rule))
            continue
        if rule.mode == "all_contains_disjoint":
            errors.extend(_check_all_contains_disjoint_rule(root, rule))
            continue
        if rule.mode == "property_contains_disjoint":
            errors.extend(_check_property_contains_disjoint_rule(root, rule))
            continue
        if rule.mode == "file_contains_disjoint":
            errors.extend(_check_file_contains_disjoint_rule(root, rule))
            continue
        if rule.mode == "top_level_bindings_disjoint":
            errors.extend(_check_top_level_bindings_disjoint_rule(root, rule))
            continue
        errors.append(f"{rule.rule_id}: unsupported targeted ban mode '{rule.mode}'")
    return errors



def validate_governance_story(root: Path) -> list[str]:
    """Validate cross-doc architecture wording that must not drift back to legacy seams."""
    errors: list[str] = []

    for relative_path, required_tokens in _DOC_REQUIRED_TOKENS.items():
        text = (root / relative_path).read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                errors.append(f"{_relative(root / relative_path, root=root)} missing governance token: {token}")

    for relative_path, forbidden_tokens in _DOC_FORBIDDEN_TOKENS.items():
        text = (root / relative_path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in text:
                errors.append(f"{_relative(root / relative_path, root=root)} still contains forbidden legacy token: {token}")

    return errors

def validate_governance_truth_alignment(root: Path) -> list[str]:
    """Validate derived-collaboration-map wording and closed-seam governance truth."""
    errors: list[str] = []
    agents_text = (root / 'AGENTS.md').read_text(encoding='utf-8')
    public_text = (root / '.planning' / 'baseline' / 'PUBLIC_SURFACES.md').read_text(encoding='utf-8')
    authority_text = (root / '.planning' / 'baseline' / 'AUTHORITY_MATRIX.md').read_text(encoding='utf-8')
    developer_text = (root / 'docs' / 'developer_architecture.md').read_text(encoding='utf-8')

    if '仍有 coordinator 私有 auth seam' in agents_text:
        errors.append('AGENTS.md still describes service execution private auth seam as active')
    if 'derived collaboration maps' not in public_text:
        errors.append('PUBLIC_SURFACES.md missing derived collaboration maps wording')
    if 'derived collaboration maps' not in authority_text:
        errors.append('AUTHORITY_MATRIX.md missing derived collaboration maps row')
    if 'derived collaboration maps / 协作图谱' not in developer_text:
        errors.append('docs/developer_architecture.md missing codebase-map identity note')
    return errors


def run_checks(root: Path | None = None) -> list[str]:
    """Return all architecture-policy drift or violation messages."""
    resolved_root = root or policy_root(Path(__file__))
    errors: list[str] = []
    errors.extend(_validate_policy_inventory(resolved_root))
    errors.extend(validate_structural_rules(resolved_root))
    errors.extend(validate_targeted_bans(resolved_root))
    errors.extend(validate_governance_story(resolved_root))
    errors.extend(validate_governance_truth_alignment(resolved_root))
    return errors


def main() -> int:
    """Run the architecture policy checker CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate architecture policy enforcement")
    parser.add_argument("--report", action="store_true", help="print architecture policy inventory summary")
    args = parser.parse_args()

    root = policy_root(Path(__file__))
    structural_rules = load_structural_rules(root)
    targeted_bans = load_targeted_bans(root)

    if args.report:
        sys.stdout.write(f"structural_rules_total={len(structural_rules)}\n")
        sys.stdout.write(f"targeted_bans_total={len(targeted_bans)}\n")

    if args.check:
        errors = run_checks(root)
        if errors:
            for error in errors:
                sys.stdout.write(f"{error}\n")
            return 1

    if not any((args.check, args.report)):
        parser.print_help()
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

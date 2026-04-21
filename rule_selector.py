"""rule_selector.py: Payload mapping aligned with ai_rule_generator (Azure OpenAI)."""

__author__ = "Praful"
__copyright__ = "Copyright 2026, Prescience Decision Solutions"


from dotenv import load_dotenv

load_dotenv()


def validate_and_normalize_rules(rules: list[dict]) -> list[dict]:
    normalized = []

    for rule in rules:
        has_value = "value" in rule
        has_old = "old_value" in rule
        has_new = "new_value" in rule
        has_mapping = "mapping" in rule and isinstance(rule.get("mapping"), dict)

        if rule.get("name") == "transform_column_values_by_replacing_with_mapping_dictionary" and has_mapping:
            normalized.append(rule)
            continue

        if has_value and (has_old or has_new):
            raise ValueError("Cannot mix delete and replace formats")

        if has_old != has_new:
            raise ValueError("Replace rule must have old_value and new_value")

        if has_old and rule["new_value"] is None:
            raise ValueError("Replacement cannot have null new_value")

        normalized.append(rule)

    return normalized
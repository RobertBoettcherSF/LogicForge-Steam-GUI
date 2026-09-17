"""MENU themes — richer grouping for the Logic Forge shell picker."""
from __future__ import annotations

THEMES: dict[str, list[str]] = {
    "Attention & Control": [
        "go_nogo", "stop_hold", "timed_choice_rt", "visual_search",
        "scan_count", "ufo_count", "falling_catch", "novelty_check",
        "conflict_label",
    ],
    "Working Memory": [
        "recall_span", "spatial_memory", "pair_associate", "info_retain",
        "eyewitness_count", "dictation_echo", "type_copy", "archive_title",
        "sequence_match",
    ],
    "Language": [
        "word_unscramble", "vocabulary_pick", "guess_letters", "morse_decode",
        "letter_index", "alpha_bravo", "wisdom_pick", "color_label",
    ],
    "Number & Quantity": [
        "number_grid", "number_series", "add_check", "product_check",
        "multiply_drill", "sum_digits", "parity_count", "subtract_check",
        "double_half", "min_of_three", "max_of_three", "percent_estimate",
        "quantity_compare", "money_change", "calorie_guess", "round_tens",
    ],
    "Visuospatial": [
        "path_plan", "route_steps", "compass_orient", "geometry_sides",
        "line_measure", "grid_position", "balance_scale", "scale_read",
        "labyrinth_turn", "border_count", "connect_path", "follow_pattern",
        "odd_one_out",
    ],
    "Reasoning & Knowledge": [
        "rule_infer", "category_decide", "compare_items", "concept_match",
        "symbol_code", "element_pick", "geo_pick", "clock_read",
        "calendar_offset",
    ],
}


def theme_for(exercise_id: str) -> str:
    for theme, ids in THEMES.items():
        if exercise_id in ids:
            return theme
    return "Other"


def filter_catalog(catalog: list[dict], theme: str | None) -> list[dict]:
    if not theme or theme == "All":
        return catalog
    return [item for item in catalog if theme_for(item["id"]) == theme]


def theme_names() -> list[str]:
    return ["All", *THEMES.keys()]


def theme_counts(catalog: list[dict]) -> dict[str, int]:
    counts = {name: 0 for name in theme_names() if name != "All"}
    for item in catalog:
        counts[theme_for(item["id"])] = counts.get(theme_for(item["id"]), 0) + 1
    return counts

"""MENU themes — group exercises for the shell picker."""
from __future__ import annotations

# Clean-room theme buckets (not product names).
THEMES: dict[str, list[str]] = {
    "Attention": [
        "go_nogo", "stop_hold", "timed_choice_rt", "visual_search", "scan_count",
        "ufo_count", "falling_catch", "novelty_check",
    ],
    "Memory": [
        "recall_span", "spatial_memory", "pair_associate", "info_retain",
        "eyewitness_count", "dictation_echo", "type_copy", "archive_title",
    ],
    "Language": [
        "word_unscramble", "vocabulary_pick", "guess_letters", "morse_decode",
        "letter_index", "alpha_bravo", "wisdom_pick", "conflict_label",
    ],
    "Number": [
        "number_grid", "number_series", "add_check", "product_check",
        "multiply_drill", "sum_digits", "parity_count", "subtract_check",
        "double_half", "min_of_three", "max_of_three", "percent_estimate",
        "quantity_compare", "money_change", "calorie_guess", "round_tens",
    ],
    "Visuospatial": [
        "path_plan", "route_steps", "compass_orient", "geometry_sides",
        "line_measure", "grid_position", "balance_scale", "scale_read",
        "labyrinth_turn", "border_count", "connect_path", "follow_pattern",
    ],
    "Reasoning": [
        "sequence_match", "rule_infer", "odd_one_out", "category_decide",
        "compare_items", "concept_match", "symbol_code", "color_label",
        "element_pick", "geo_pick", "clock_read", "calendar_offset",
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
    return ["All", *sorted(THEMES.keys()), "Other"]

from scripts.project_types import PROJECT_TYPES, GENERIC_INTERPRETATIONS, GENERIC_RISK_BY_TRIGGER


def get_trigger_key(result, buffer_distances):
    """
    Returns 'Site' if site_intersect is True.
    Returns 'b1', 'b2', or 'b3' for the smallest buffer where within_{X}m is True.
    Returns 'None' if no presence found.
    """
    if result.get("site_intersect"):
        return "Site"
    for i, dist in enumerate(buffer_distances):
        label = ["b1", "b2", "b3"][i]
        if result.get(f"within_{dist}m"):
            return label
    return "None"


def get_layer_interpretation(layer_key, trigger_key, project_type_name, buffer_distances):
    """
    Looks up PROJECT_TYPES[project_type_name]['interpretation_rules'][layer_key][trigger_key].
    Formats {b1}, {b2}, {b3} placeholders with actual buffer distances.
    Falls back to GENERIC_INTERPRETATIONS[trigger_key] if rule not found.
    Returns (risk_level, interpretation_text).
    """
    b1, b2, b3 = str(buffer_distances[0]), str(buffer_distances[1]), str(buffer_distances[2])
    fmt = {"b1": b1, "b2": b2, "b3": b3}

    try:
        rules = PROJECT_TYPES[project_type_name]["interpretation_rules"]
        risk_level, text = rules[layer_key][trigger_key]
        return risk_level, text.format(**fmt)
    except (KeyError, TypeError, AttributeError):
        pass

    risk_level = GENERIC_RISK_BY_TRIGGER[trigger_key]
    text = GENERIC_INTERPRETATIONS[trigger_key]
    return risk_level, text


def get_layer_risk_score(layer_key, trigger_key, project_type_name):
    """
    weight = layer_weights.get(layer_key, 1)
    relevance = {Site: 4, b1: 3, b2: 2, b3: 1, None: 0}
    Returns weight * relevance.
    """
    weight = PROJECT_TYPES[project_type_name]["layer_weights"].get(layer_key, 1)
    relevance = {"Site": 4, "b1": 3, "b2": 2, "b3": 1, "None": 0}[trigger_key]
    return weight * relevance


def score_results(results, project_type_name, buffer_distances):
    """
    For each result adds: trigger_key, layer_score, risk_level, interpretation.
    Groups by theme and calculates theme_rating:
      HIGH  if any layer risk_level == 'HIGH' or theme_score >= 20
      MEDIUM if any layer risk_level == 'MEDIUM' or theme_score >= 10
      LOW   if any features present
      NONE  if no features found
    Returns (scored_results, theme_summary dict with rating/score/key_finding/interpretation per theme).
    """
    scored = []
    for r in results:
        r = dict(r)
        layer_key = r["layer_key"]
        trigger_key = get_trigger_key(r, buffer_distances)
        risk_level, interpretation = get_layer_interpretation(
            layer_key, trigger_key, project_type_name, buffer_distances
        )
        layer_score = get_layer_risk_score(layer_key, trigger_key, project_type_name)
        r["trigger_key"] = trigger_key
        r["layer_score"] = layer_score
        r["risk_level"] = risk_level
        r["interpretation"] = interpretation
        scored.append(r)

    themes = list(dict.fromkeys(r["theme"] for r in scored))
    theme_summary = {}

    for theme in themes:
        theme_results = [r for r in scored if r["theme"] == theme]
        theme_score = sum(r["layer_score"] for r in theme_results)
        risk_levels = [r["risk_level"] for r in theme_results]
        has_features = any(r["present"] for r in theme_results)

        if "HIGH" in risk_levels or theme_score >= 20:
            rating = "HIGH"
        elif "MEDIUM" in risk_levels or theme_score >= 10:
            rating = "MEDIUM"
        elif has_features:
            rating = "LOW"
        else:
            rating = "NONE"

        present_results = [r for r in theme_results if r["present"]]
        if present_results:
            best = max(present_results, key=lambda r: r["layer_score"])
            key_finding = best["layer"]
            key_interpretation = best["interpretation"]
        else:
            key_finding = "No features identified"
            key_interpretation = "No features identified within the screening area"

        theme_summary[theme] = {
            "rating": rating,
            "score": theme_score,
            "key_finding": key_finding,
            "interpretation": key_interpretation,
        }

    return scored, theme_summary

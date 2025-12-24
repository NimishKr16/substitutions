import re
from typing import List, Dict

# ============================================================
# YAGEO SERIES RULE DATABASE
# ============================================================

SERIES_RULES = {

    # ---------------- RESISTORS ----------------
    "RC": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic (embossed) tape",
            "S": "ESD-safe tape"
        },
        "reel_codes": {
            "07": '7" reel',
            "10": '10" reel',
            "13": '13" reel'
        },
        "cross_series": {
            "RT": "Thin-film equivalent",
            "RL": "Current-sense equivalent"
        }
    },

    "RT": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic (embossed) tape"
        },
        "reel_codes": {
            "07": '7" reel',
            "10": '10" reel',
            "13": '13" reel'
        },
        "cross_series": {
            "RC": "Thick-film equivalent"
        }
    },

    "RL": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic (embossed) tape"
        },
        "reel_codes": {
            "07": '7" reel'
        },
        "cross_series": {
            "RC": "Thick-film equivalent"
        }
    },

    "AC": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic tape"
        },
        "reel_codes": {
            "07": '7" reel',
            "13": '13" reel'
        },
        "cross_series": {}
    },

    "NR": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic tape"
        },
        "reel_codes": {
            "07": '7" reel',
            "13": '13" reel'
        },
        "cross_series": {
            "LR": "Metal strip equivalent"
        }
    },

    "LR": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic tape"
        },
        "reel_codes": {
            "07": '7" reel',
            "13": '13" reel'
        },
        "cross_series": {
            "NR": "Metal strip equivalent"
        }
    },

    # ---------------- CAPACITORS ----------------
    "CC": {
        "family": "capacitor",
        "packaging_styles": {
            "R": "Paper tape – 7\"",
            "P": "Paper tape – 13\"",
            "K": "Plastic tape – 7\"",
            "F": "Plastic tape – 13\"",
            "C": "Bulk"
        },
        "cross_series": {
            "CQ": "Automotive grade equivalent"
        }
    },

    "CQ": {
        "family": "capacitor",
        "packaging_styles": {
            "R": "Paper tape – 7\"",
            "P": "Paper tape – 13\"",
            "K": "Plastic tape – 7\"",
            "F": "Plastic tape – 13\""
        },
        "cross_series": {
            "CC": "Commercial grade equivalent"
        }
    },

    # ---------------- INDUCTORS ----------------
    "CL": {
        "family": "inductor",
        "packaging_styles": {
            "T": "Tape & reel",
            "B": "Bulk"
        },
        "cross_series": {}
    }
}


# ============================================================
# SERIES DETECTION
# ============================================================

def detect_series(part_number: str) -> str:
    for series in SERIES_RULES:
        if part_number.startswith(series):
            return series

    # MOV example: 271KD07-TR
    if re.match(r"\d{3}KD\d{2}", part_number):
        return "MOV"

    return "UNKNOWN"


# ============================================================
# MAIN CONTROLLER
# ============================================================

def generate_substitutions(part_number: str) -> Dict:
    series = detect_series(part_number)

    if series == "UNKNOWN":
        return {
            "series": "UNKNOWN",
            "substitutions": []
        }

    family = SERIES_RULES[series]["family"]

    if family == "resistor":
        subs = resistor_substitutions(part_number, series)
    elif family == "capacitor":
        subs = capacitor_substitutions(part_number, series)
    elif family == "inductor":
        subs = inductor_substitutions(part_number)
    elif series == "MOV":
        subs = mov_substitutions(part_number)
    else:
        subs = []

    return {
        "series": series,
        "substitutions": subs
    }


# ============================================================
# RESISTOR SUBSTITUTIONS
# ============================================================

def resistor_substitutions(part_number: str, series: str) -> List[Dict]:
    rules = SERIES_RULES[series]
    output = []

    match = re.match(r"([A-Z]{2})(\d{4})([A-Z])([A-Z])-(\d{2})(.*)", part_number)
    if not match:
        return []

    prefix, size, tol, orig_pack, orig_reel, rest = match.groups()

    # Packaging-only
    for p_code, p_desc in rules["packaging_letters"].items():
        for r_code, r_desc in rules["reel_codes"].items():
            new_pn = f"{prefix}{size}{tol}{p_code}-{r_code}{rest}"

            sub_type = "Original" if (p_code == orig_pack and r_code == orig_reel) \
                       else "Packaging Substitute"

            output.append({
                "part_number": new_pn,
                "type": sub_type,
                "details": f"{p_desc}, {r_desc}"
            })

    # Cross-series electrical equivalents
    for cross, desc in rules["cross_series"].items():
        cross_pn = part_number.replace(prefix, cross, 1)
        output.append({
            "part_number": cross_pn,
            "type": "Electrical Equivalent",
            "details": desc
        })

    return output


# ============================================================
# CAPACITOR SUBSTITUTIONS
# ============================================================

def capacitor_substitutions(part_number: str, series: str) -> List[Dict]:
    rules = SERIES_RULES[series]
    output = []

    base = part_number[:6]
    orig_pack = part_number[6]
    rest = part_number[7:]

    for p_code, p_desc in rules["packaging_styles"].items():
        new_pn = f"{base}{p_code}{rest}"

        sub_type = "Original" if p_code == orig_pack \
                   else "Packaging Substitute"

        output.append({
            "part_number": new_pn,
            "type": sub_type,
            "details": p_desc
        })

    for cross, desc in rules["cross_series"].items():
        cross_pn = part_number.replace(series, cross, 1)
        output.append({
            "part_number": cross_pn,
            "type": "Electrical Equivalent",
            "details": desc
        })

    return output


# ============================================================
# INDUCTOR SUBSTITUTIONS
# ============================================================

def inductor_substitutions(part_number: str) -> List[Dict]:
    output = []

    match = re.match(r"(CL\d{6})([TB])(.*)", part_number)
    if not match:
        return []

    base, orig_pack, rest = match.groups()

    for p_code, p_desc in SERIES_RULES["CL"]["packaging_styles"].items():
        new_pn = f"{base}{p_code}{rest}"

        sub_type = "Original" if p_code == orig_pack \
                   else "Packaging Substitute"

        output.append({
            "part_number": new_pn,
            "type": sub_type,
            "details": p_desc
        })

    return output


# ============================================================
# MOV (VARISTOR) SUBSTITUTIONS
# ============================================================

def mov_substitutions(part_number: str) -> List[Dict]:
    output = []

    if part_number.endswith("-TR"):
        output.append({
            "part_number": part_number,
            "type": "Original",
            "details": "Tape & reel"
        })
        output.append({
            "part_number": part_number.replace("-TR", ""),
            "type": "Packaging Substitute",
            "details": "Bulk / cut tape"
        })
    else:
        output.append({
            "part_number": part_number,
            "type": "Original",
            "details": "Bulk / cut tape"
        })
        output.append({
            "part_number": f"{part_number}-TR",
            "type": "Packaging Substitute",
            "details": "Tape & reel"
        })

    return output





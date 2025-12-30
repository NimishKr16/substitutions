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

    "9C": {
        "family": "resistor",
        "packaging_letters": {
            "R": "Paper tape",
            "K": "Plastic (embossed) tape"
        },
        "reel_codes": {
            "07": '7" reel',
            "13": '13" reel'
        },
        "cross_series": {}
    },

    "AT": {
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
        "cross_series": {}
    },

    "AF": {
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
        "cross_series": {}
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
# NORMALIZER FUNCTION
# ============================================================

def normalize_part_number(part_number: str) -> Dict:
    pn = part_number.strip().upper()

    # Case 1: RC / RT / RL missing packaging letter and reel code
    # Example: RC0402F-475RL
    match_short_rc = re.match(r"(RC|RT|RL)(\d{4})([A-Z])-(\d+)([A-Z]+)", pn)
    if match_short_rc:
        series, size, tol, value, suffix = match_short_rc.groups()
        normalized = f"{series}{size}{tol}R-07{value}{suffix}"
        return {
            "normalized": normalized,
            "status": "NORMALIZED",
            "note": "Packaging letter and reel code were missing. Defaulted to R, 07."
        }

    # Case 2: RC / RT / RL missing reel code only
    # Example: RC0603FR-1K0L
    match_missing_reel = re.match(r"(RC|RT|RL)(\d{4})([A-Z])([A-Z])-(\d+)([A-Z]+)", pn)
    if match_missing_reel:
        series, size, tol, pack, value, suffix = match_missing_reel.groups()
        normalized = f"{series}{size}{tol}{pack}-07{value}{suffix}"
        return {
            "normalized": normalized,
            "status": "NORMALIZED",
            "note": "Reel code missing. Defaulted to 07."
        }

    # Case 3: RC / RT / RL missing dash entirely
    # Example: RC0603FR1K0L
    match_no_dash = re.match(r"(RC|RT|RL)(\d{4})([A-Z])([A-Z])(\d+)([A-Z]+)", pn)
    if match_no_dash:
        series, size, tol, pack, value, suffix = match_no_dash.groups()
        normalized = f"{series}{size}{tol}{pack}-07{value}{suffix}"
        return {
            "normalized": normalized,
            "status": "NORMALIZED",
            "note": "Dash and reel code missing. Defaulted to 07."
        }

    # Case 4: CC / CQ missing packaging style
    # Example: CC0603RX7R104
    match_cc_missing_pack = re.match(r"(CC|CQ)(\d{4})([A-Z0-9]+)", pn)
    if match_cc_missing_pack and len(pn) == 6 + len(match_cc_missing_pack.group(3)):
        series, size, rest = match_cc_missing_pack.groups()
        normalized = f"{series}{size}R{rest}"
        return {
            "normalized": normalized,
            "status": "NORMALIZED",
            "note": "Packaging style missing. Defaulted to R."
        }

    return {
        "normalized": pn,
        "status": "UNCHANGED",
        "note": "Part number already complete or unsupported for normalization."
    }


# ============================================================
# MAIN CONTROLLER
# ============================================================

def generate_substitutions(part_number: str) -> Dict:
    norm = normalize_part_number(part_number)
    part_number = norm["normalized"]
    normalization_note = None if norm["status"] == "UNCHANGED" else norm["note"]

    series = detect_series(part_number)

    # Legacy Philips / Yageo numeric part numbers (e.g. 232270672613L)
    if re.match(r"^23\d+[A-Z]?$", part_number):
        return {
            "series": "LEGACY_PHILIPS_YAGEO",
            "substitutions": [
                {
                    "part_number": part_number,
                    "type": "Legacy Part",
                    "details": "Legacy Philips/Yageo numeric part number. Packaging and electrical substitutions cannot be generated by pattern. Cross-reference to a modern CC/CQ/CL series part number is required before substitution."
                }
            ],
            "normalization": {
                "normalized": part_number,
                "status": "LEGACY",
                "note": "Legacy numeric Yageo/Philips part number detected. Cross-reference required."
            }
        }

    if series == "UNKNOWN":
        return {
            "series": "UNKNOWN",
            "substitutions": [],
            "normalization": norm
        }

    family = SERIES_RULES[series]["family"]

    if family == "resistor":
        subs = resistor_substitutions(part_number, series, normalization_note)
    elif family == "capacitor":
        subs = capacitor_substitutions(part_number, series, normalization_note)
    elif family == "inductor":
        subs = inductor_substitutions(part_number, normalization_note)
    elif series == "MOV":
        subs = mov_substitutions(part_number, normalization_note)
    else:
        subs = []

    return {
        "series": series,
        "substitutions": subs,
        "normalization": norm
    }


# ============================================================
# RESISTOR SUBSTITUTIONS
# ============================================================

def resistor_substitutions(part_number: str, series: str, normalization_note: str = None) -> List[Dict]:
    rules = SERIES_RULES[series]
    output = []

    # Special handling for Yageo 9C automotive resistors (no dash format)
    if series == "9C":
        match_9c = re.match(r"(9C)(\d{4})([A-Z0-9]+)", part_number)
        if not match_9c:
            return []

        prefix, size, rest = match_9c.groups()

        for p_code, p_desc in rules["packaging_letters"].items():
            for r_code, r_desc in rules["reel_codes"].items():
                new_pn = f"{prefix}{size}{rest}"
                output.append({
                    "part_number": new_pn,
                    "type": "Packaging Substitute",
                    "details": f"{p_desc}, {r_desc}" + (f" | NOTE: {normalization_note}" if normalization_note else "")
                })

        return output

    # Special handling for Yageo AT thin-film resistors (no dash format)
    if series == "AT" and "-" not in part_number:
        match_at = re.match(r"(AT)(\d{4})([A-Z0-9]+)", part_number)
        if not match_at:
            return []

        prefix, size, rest = match_at.groups()

        for p_code, p_desc in rules["packaging_letters"].items():
            for r_code, r_desc in rules["reel_codes"].items():
                new_pn = f"{prefix}{size}{rest}"
                output.append({
                    "part_number": new_pn,
                    "type": "Packaging Substitute",
                    "details": f"{p_desc}, {r_desc}" + (f" | NOTE: {normalization_note}" if normalization_note else "")
                })

        return output

    # Special handling for Yageo AF anti-sulfur resistors (no dash format)
    if series == "AF" and "-" not in part_number:
        match_af = re.match(r"(AF)(\d{4})([A-Z0-9]+)", part_number)
        if not match_af:
            return []

        prefix, size, rest = match_af.groups()

        for p_code, p_desc in rules["packaging_letters"].items():
            for r_code, r_desc in rules["reel_codes"].items():
                new_pn = f"{prefix}{size}{rest}"
                output.append({
                    "part_number": new_pn,
                    "type": "Packaging Substitute",
                    "details": f"{p_desc}, {r_desc}" + (f" | NOTE: {normalization_note}" if normalization_note else "")
                })

        return output

    match = re.match(r"([A-Z0-9]{2})(\d{4})([A-Z])([A-Z])-(\d{2})(.*)", part_number)
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
                "details": f"{p_desc}, {r_desc}" + (f" | NOTE: {normalization_note}" if normalization_note else "")
            })

    # Cross-series electrical equivalents
    for cross, desc in rules["cross_series"].items():
        cross_pn = part_number.replace(prefix, cross, 1)
        output.append({
            "part_number": cross_pn,
            "type": "Electrical Equivalent",
            "details": desc + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })

    return output


# ============================================================
# CAPACITOR SUBSTITUTIONS
# ============================================================

def capacitor_substitutions(part_number: str, series: str, normalization_note: str = None) -> List[Dict]:
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
            "details": f"{p_desc}" + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })

    for cross, desc in rules["cross_series"].items():
        cross_pn = part_number.replace(series, cross, 1)
        output.append({
            "part_number": cross_pn,
            "type": "Electrical Equivalent",
            "details": desc + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })

    return output


# ============================================================
# INDUCTOR SUBSTITUTIONS
# ============================================================

def inductor_substitutions(part_number: str, normalization_note: str = None) -> List[Dict]:
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
            "details": f"{p_desc}" + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })

    return output


# ============================================================
# MOV (VARISTOR) SUBSTITUTIONS
# ============================================================

def mov_substitutions(part_number: str, normalization_note: str = None) -> List[Dict]:
    output = []

    if part_number.endswith("-TR"):
        output.append({
            "part_number": part_number,
            "type": "Original",
            "details": f"Tape & reel" + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })
        output.append({
            "part_number": part_number.replace("-TR", ""),
            "type": "Packaging Substitute",
            "details": f"Bulk / cut tape" + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })
    else:
        output.append({
            "part_number": part_number,
            "type": "Original",
            "details": f"Bulk / cut tape" + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })
        output.append({
            "part_number": f"{part_number}-TR",
            "type": "Packaging Substitute",
            "details": f"Tape & reel" + (f" | NOTE: {normalization_note}" if normalization_note else "")
        })

    return output




#  test_pn = [
#         "RC0805FR-07205KL",
#         "RC0603FR-0757K6L",
#         "RC1206FR-074R99L",
#         "RC0603FR-0722KL",
#         "RC1206FR-07332KL",
#         "CC0603KRX5R7BB475",
#         "RC0402FR-0710RL",
#         "RC0402FR-0715KL",
#         "RC0402FR-0747KL",
#         "AC0402FR-0751RL",
#         "CC0402KRX5R7BB105",
#         "RC0402FR-071K2P",
#         "CC0402KRX7R7BB224",
#         "RT0603DRD07127RL",
#         "RC0603FR-0710KL",
#         "AC0201FR-0710KL",
#         "CC0201JRNPO9BN120",
#         "RC0201FR-07100RL",
#         "RC0402FR-07330KL",
#         "CC0402KRX7R7BB224"


#     ]
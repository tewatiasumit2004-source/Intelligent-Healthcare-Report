import os, json

def generate_patient_summary(results, raw_text=""):
    if not results:
        return ("No structured laboratory values were detected. Please verify the report image/PDF quality. "
                "This tool provides educational assistance and does not provide a diagnosis.")
    abnormal=[r for r in results if r["status"]!="Normal"]
    lines=["The report analysis identified the following results:"]
    for r in results:
        lines.append(f'- {r["test"]}: {r["value"]} {r["unit"]} — {r["status"]}.')
    if abnormal:
        lines.append("")
        lines.append("Values marked High/Low are outside the demonstration reference ranges used by this prototype. "
                     "Reference ranges can differ between laboratories and individuals, so a clinician should interpret them.")
    else:
        lines.append("")
        lines.append("All detected values are within the demonstration reference ranges.")
    lines.append("This summary is educational and is not a medical diagnosis.")
    return "\n".join(lines)

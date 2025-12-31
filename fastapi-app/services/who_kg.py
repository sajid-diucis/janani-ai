# WHO Maternal Health Knowledge Graph (Python structure)
WHO_KNOWLEDGE_GRAPH = {
    "entities": {
        "danger_signs": {
            "id": "danger_signs",
            "label": "Danger Signs in Pregnancy",
            "type": "category",
            "children": [
                "vaginal_bleeding", "severe_headache", "blurred_vision", "high_fever",
                "convulsions", "abdominal_pain", "reduced_fetal_movement", "swelling"
            ]
        },
        "vaginal_bleeding": {
            "id": "vaginal_bleeding",
            "label": "Vaginal Bleeding",
            "type": "symptom",
            "guideline": "Immediate referral to hospital. Do not delay.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "severe_headache": {
            "id": "severe_headache",
            "label": "Severe Headache",
            "type": "symptom",
            "guideline": "Assess for pre-eclampsia. Refer if associated with visual changes or high BP.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "blurred_vision": {
            "id": "blurred_vision",
            "label": "Blurred Vision",
            "type": "symptom",
            "guideline": "Assess for pre-eclampsia. Refer if present.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "high_fever": {
            "id": "high_fever",
            "label": "High Fever",
            "type": "symptom",
            "guideline": "Suspect infection. Refer for urgent evaluation.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "convulsions": {
            "id": "convulsions",
            "label": "Convulsions",
            "type": "symptom",
            "guideline": "Immediate referral. Suspect eclampsia.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "abdominal_pain": {
            "id": "abdominal_pain",
            "label": "Severe Abdominal Pain",
            "type": "symptom",
            "guideline": "Urgent referral. Rule out abruption, labor, or infection.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "reduced_fetal_movement": {
            "id": "reduced_fetal_movement",
            "label": "Reduced Fetal Movement",
            "type": "symptom",
            "guideline": "Assess fetal wellbeing. Refer if persistent.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "swelling": {
            "id": "swelling",
            "label": "Swelling of Face/Hands",
            "type": "symptom",
            "guideline": "Assess for pre-eclampsia. Refer if associated with headache or visual changes.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "nutrition": {
            "id": "nutrition",
            "label": "Nutrition in Pregnancy",
            "type": "advice",
            "guideline": "Eat a balanced diet with iron, folic acid, and protein. Avoid alcohol and tobacco.",
            "references": [
                "https://www.who.int/publications/i/item/9789241548352"
            ]
        },
        "antenatal_visits": {
            "id": "antenatal_visits",
            "label": "Antenatal Care Visits",
            "type": "advice",
            "guideline": "At least 8 contacts recommended. Early booking is essential.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        },
        "medication_advice": {
            "id": "medication_advice",
            "label": "Medication Advice",
            "type": "advice",
            "guideline": "Do not prescribe or recommend specific drugs/doses. Always refer to a doctor.",
            "references": [
                "https://www.who.int/publications/i/item/9789241549359"
            ]
        }
    },
    "relations": [
        {"from": "danger_signs", "to": "vaginal_bleeding", "type": "has_sign"},
        {"from": "danger_signs", "to": "severe_headache", "type": "has_sign"},
        {"from": "danger_signs", "to": "blurred_vision", "type": "has_sign"},
        {"from": "danger_signs", "to": "high_fever", "type": "has_sign"},
        {"from": "danger_signs", "to": "convulsions", "type": "has_sign"},
        {"from": "danger_signs", "to": "abdominal_pain", "type": "has_sign"},
        {"from": "danger_signs", "to": "reduced_fetal_movement", "type": "has_sign"},
        {"from": "danger_signs", "to": "swelling", "type": "has_sign"}
    ]
}

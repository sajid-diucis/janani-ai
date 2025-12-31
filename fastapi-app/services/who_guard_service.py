# WHO Knowledge Graph Guard Service
from .who_kg import WHO_KNOWLEDGE_GRAPH

class WhoGuard:
    """
    Validates AI plans and responses against WHO maternal health guidelines.
    """
    def __init__(self):
        self.kg = WHO_KNOWLEDGE_GRAPH
        self.danger_signs = set(self.kg['entities']['danger_signs']['children'])
        self.medication_keywords = [
            'antibiotic', 'paracetamol', 'misoprostol', 'oxytocin', 'methergine',
            'drug', 'tablet', 'capsule', 'injection', 'dose', 'mg', 'ml', 'medicine', 'prescribe'
        ]

    def validate_response(self, response: str) -> dict:
        """
        Checks if the response is safe, guideline-aligned, and not giving forbidden advice.
        Returns dict with 'valid', 'issues', 'annotations'.
        """
        issues = []
        annotations = []
        valid = True

        # Check for forbidden medication advice
        for med in self.medication_keywords:
            if med in response.lower():
                valid = False
                issues.append('Mentions medication or dose: forbidden by WHO')
                annotations.append(self.kg['entities']['medication_advice']['guideline'])
                break

        # Check for missing referral on danger signs
        for sign in self.danger_signs:
            entity = self.kg['entities'][sign]
            if entity['label'].lower() in response.lower():
                if 'refer' not in response.lower() and 'হাসপাতাল' not in response:
                    valid = False
                    issues.append(f"Mentions {entity['label']} but does not advise referral")
                    annotations.append(entity['guideline'])

        # Annotate with relevant guidelines
        for eid, entity in self.kg['entities'].items():
            if entity['label'].lower() in response.lower():
                annotations.append(entity['guideline'])

        return {
            'valid': valid,
            'issues': issues,
            'annotations': list(set(annotations))
        }

    def annotate_with_guideline(self, response: str) -> str:
        """
        Appends relevant WHO guideline(s) to the response.
        """
        result = self.validate_response(response)
        if result['annotations']:
            return response + "\n\nWHO Guideline(s):\n- " + "\n- ".join(result['annotations'])
        return response

# Global instance
who_guard = WhoGuard()

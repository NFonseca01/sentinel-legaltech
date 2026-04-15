import re

class RGPDSanitizer:
    def __init__(self):
        # Patrones básicos para anonimización
        self.patterns = {
            "email": r'[\w\.-]+@[\w\.-]+\.\w+',
            "dni": r'\d{8}[A-Z]',
            "phones": r'(?:\+34|0034|34)?[ -]?(?:[6789][ -]?\d[ -]?\d[ -]?\d[ -]?\d[ -]?\d[ -]?\d[ -]?\d[ -]?\d)'
        }

    def sanitize_text(self, text):
        """Reemplaza datos sensibles con etiquetas genéricas."""
        sanitized = text
        for label, pattern in self.patterns.items():
            sanitized = re.sub(pattern, f"[{label.upper()}_REDACTED]", sanitized)
        return sanitized
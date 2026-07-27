from __future__ import annotations
import re
from core.models import PsychologyResult
from config.settings import SETTINGS

_PATTERNS = {
    "FOMO": [r"no me quiero quedar fuera", r"se me va", r"est[aá] volando", r"entrar ya", r"urgente"],
    "Revenge trading": [r"recuperar", r"desquitar", r"me la debe", r"venganza"],
    "Impulso": [r"un amigo", r"twitter", r"x dijo", r"porque s[ií]", r"tengo el presentimiento"],
}

def analyze_justification(text: str) -> PsychologyResult:
    clean = " ".join((text or "").lower().split())
    if len(clean) < SETTINGS.min_justification_chars:
        return PsychologyResult(True, "Plan insuficiente", "La justificación técnica es demasiado breve.")
    detected=[]
    for bias, patterns in _PATTERNS.items():
        if any(re.search(p, clean) for p in patterns): detected.append(bias)
    if detected:
        return PsychologyResult(True, " / ".join(detected), "Operación bloqueada por posible sesgo emocional.")
    required = ["entrada", "stop", "riesgo"]
    if not any(word in clean for word in required):
        return PsychologyResult(True, "Plan incompleto", "Incluye entrada, stop o riesgo en la justificación.")
    return PsychologyResult(False, "Ninguno", "La justificación contiene elementos objetivos de planificación.")

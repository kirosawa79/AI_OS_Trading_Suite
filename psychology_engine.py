import os
import json
from openai import OpenAI

class PsychologyEngine:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY", "DEMO_KEY"))

    def analizar_intencion_usuario(self, ticker, justificacion_texto):
        if not self.client.api_key or self.client.api_key == "DEMO_KEY":
            return {"status": "Error", "reason": "Llave API de OpenAI no configurada."}

        prompt_sistema = (
            "Eres el Psicólogo de Riesgo de un Fondo de Inversión institucional. "
            "Tu única misión es analizar la respuesta textual del operador humano para identificar "
            "si está bajo la influencia de un sesgo emocional o cognitivo dañino (FOMO, Revenge Trading, Impulso).\n\n"
            "REGLAS DE EVALUACIÓN:\n"
            "1. FOMO (Miedo a quedarse fuera): Busca palabras de urgencia como 'está volando', 'se me va', 'entrar ya'.\n"
            "2. REVENGE TRADING (Venganza): Busca intenciones de recuperar pérdidas pasadas ('recuperar lo de ayer', 'me la debe').\n"
            "3. IMPULSO/FALTA DE PLAN: Argumentos vagos o basados en terceros ('leí en X/Twitter', 'un amigo me dijo').\n\n"
            "DEBES responder EXCLUSIVAMENTE en el siguiente formato JSON estricto:\n"
            "{\n"
            "  \"bloquear_operacion\": true/false,\n"
            "  \"sesgo_detectado\": \"Nombre del sesgo o Ninguno\",\n"
            "  \"nivel_ansiedad\": \"Alta / Media / Baja\",\n"
            "  \"mensaje_diagnostico\": \"Mensaje directo para el operador.\"\n"
            "}"
        )

        prompt_usuario = f"Ticker: {ticker}\nJustificación: \"{justificacion_texto}\""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(response.choices.message.content)
        except Exception as e:
            return {"status": "Error", "reason": str(e)}

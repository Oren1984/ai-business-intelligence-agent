# src/llm/provider.py — NeuroOps Insight Engine
# LLM abstraction layer supporting Demo, OpenAI (Responses API), and Ollama backends.

import os
import json
import requests

class LLMProvider:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "demo").strip().lower()
        self.model = os.getenv("LLM_MODEL", "gpt-4.1-mini").strip()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")

    def generate(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt, context)
        if self.provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt, context)
        return self._demo_response(system_prompt, user_prompt, context)

    def _call_openai(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        if not self.openai_api_key:
            return "[OPENAI ERROR] Missing OPENAI_API_KEY. Falling back is recommended."

        url = f"{self.openai_base_url}/responses"
        final_input = f"System Instructions:\n{system_prompt}\n\nContext:\n{context}\n\nUser Request:\n{user_prompt}"

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "input": final_input,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "output_text" in data and data["output_text"]:
                return data["output_text"].strip()

            output = data.get("output", [])
            fragments = []
            for item in output:
                for content in item.get("content", []):
                    text = content.get("text")
                    if text:
                        fragments.append(text)
            if fragments:
                return "\n".join(fragments).strip()

            return "[OPENAI ERROR] Response received but no text output was found."
        except Exception as e:
            return f"[OPENAI ERROR] {e}"

    def _call_ollama(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        url = f"{self.ollama_base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nRequest:\n{user_prompt}"}
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip() or "[OLLAMA ERROR] Empty response."
        except Exception as e:
            return f"[OLLAMA ERROR] {e}"

    def _demo_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        preview = context[:800] if context else "No additional context."
        return (
            "DEMO MODE RESPONSE\n\n"
            f"System focus: {system_prompt[:180]}\n\n"
            f"User request: {user_prompt[:300]}\n\n"
            "Generated business-style answer:\n"
            "- The platform shows a usable AI BI architecture.\n"
            "- The current response is simulated because LLM_PROVIDER=demo.\n"
            "- Once OpenAI or Ollama is configured, this section will return live model output.\n\n"
            f"Context preview:\n{preview}"
        )

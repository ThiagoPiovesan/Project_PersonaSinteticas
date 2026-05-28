"""Configuração do sistema multi-agente Galaxies.

Carrega variáveis de ambiente e define constantes de configuração.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carregar .env do diretório raiz do projeto
BASE_DIR: Path = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# --- OpenAI ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# --- Caminhos ---
PROFILES_PATH: Path = BASE_DIR / "data" / "cluster_profiles.json"

# --- Validação ---
def validar_config() -> bool:
    """Verifica se a configuração mínima está presente.

    Returns:
        True se tudo OK.

    Raises:
        ValueError: Se a API key não estiver configurada.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-sua-chave-aqui":
        raise ValueError(
            "OPENAI_API_KEY não configurada.\n"
            "Copie .env.example para .env e preencha sua chave."
        )
    if not PROFILES_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de perfis não encontrado: {PROFILES_PATH}\n"
            "Execute primeiro: uv run python -m engine.clustering"
        )
    return True

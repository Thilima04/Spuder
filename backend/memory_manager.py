import os
import json
import datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parent / "spuder_memory.json"

class MemoryManager:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.data = {
            "owner_name": "Thiago",
            "owner_profile": {
                "role": "Criador & Operador Chefe",
                "biometrics_registered": False,
                "preferences": []
            },
            "facts": [],
            "projects": [],
            "notes": []
        }
        self.load()

    def load(self):
        """Carrega a memória permanente do disco."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"[Memory] Erro ao carregar memória: {e}")
        else:
            self.save()

    def save(self):
        """Persiste as memórias no arquivo JSON."""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory] Erro ao salvar memória: {e}")

    def add_fact(self, fact: str):
        """Adiciona um fato ou aprendizado sobre o usuário."""
        entry = {
            "fact": fact,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.data["facts"].append(entry)
        self.save()
        return f"Memória registrada: '{fact}', Senhor."

    def add_project(self, project_name: str, description: str = ""):
        """Registra um projeto em andamento."""
        entry = {
            "name": project_name,
            "description": description,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.data["projects"].append(entry)
        self.save()
        return f"Projeto '{project_name}' catalogado em meus arquivos centrais."

    def get_context_summary(self) -> str:
        """Gera um resumo conciso da memória para injetar no cérebro do Gemini."""
        lines = [f"Dono e Operador: Senhor {self.data.get('owner_name', 'Thiago')}."]
        
        facts = self.data.get("facts", [])
        if facts:
            lines.append("Fatos e Preferências Lembradas:")
            for f in facts[-6:]:
                lines.append(f"- {f['fact']}")
                
        projects = self.data.get("projects", [])
        if projects:
            lines.append("Projetos em Andamento:")
            for p in projects[-4:]:
                lines.append(f"- {p['name']}: {p.get('description', '')}")

        return "\n".join(lines)

    def extract_and_learn(self, user_text: str) -> str:
        """Detecta se o usuário pediu para memorizar algo."""
        lower = user_text.lower()
        triggers = ["lembre-se que", "lembre-se de que", "memorize que", "lembre que", "anote que", "guarde que"]
        
        for tr in triggers:
            if tr in lower:
                idx = lower.find(tr) + len(tr)
                fact = user_text[idx:].strip(" .!?,;")
                if fact:
                    return self.add_fact(fact)
        return ""

memory_manager = MemoryManager()

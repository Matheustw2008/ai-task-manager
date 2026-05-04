import logging
from typing import List
from groq import Groq, APIError, AuthenticationError, RateLimitError
from app.core.settings import settings
from app.models.task import Task

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        if not tasks:
            return []
        task_list = "\n".join(
            f"{i + 1}. [{task.category}] {task.title} - {task.description or 'sem descricao'}"
            for i, task in enumerate(tasks)
        )
        prompt = f"Analise as tarefas e retorne SOMENTE os numeros em ordem de prioridade, separados por virgula.\n\nTarefas:\n{task_list}\n\nResponda APENAS com os numeros. Exemplo: 3,1,2,4"
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                timeout=10,  # timeout de 10 segundos
            )
            response_text = response.choices[0].message.content.strip()
            order = [int(n.strip()) - 1 for n in response_text.split(",") if n.strip().isdigit()]
            prioritized = []
            seen = set()
            for idx in order:
                if 0 <= idx < len(tasks) and idx not in seen:
                    prioritized.append(tasks[idx])
                    seen.add(idx)
            for i, task in enumerate(prioritized):
                task.priority = i + 1
            return prioritized
        except AuthenticationError:
            logger.error("Chave do Groq invalida em prioritize_tasks")
            raise ValueError("Servico de IA indisponivel.")
        except RateLimitError:
            logger.error("Rate limit Groq em prioritize_tasks")
            raise ValueError("Limite de IA atingido. Tente em instantes.")
        except APIError as e:
            logger.error("APIError Groq prioritize_tasks", extra={"error": str(e)})
            raise ValueError("Erro no servico de IA.")
        except Exception as e:
            logger.error("Erro inesperado prioritize_tasks", extra={"error": str(e)})
            raise ValueError("Erro inesperado ao priorizar tarefas.")

    def generate_daily_summary(self, tasks: List[Task]) -> str:
        if not tasks:
            return "Nenhuma tarefa encontrada para hoje."
        completed = [t for t in tasks if t.is_completed]
        pending = [t for t in tasks if not t.is_completed]
        completed_text = "\n".join(f"- {t.title}" for t in completed) or "Nenhuma"
        pending_text = "\n".join(f"- {t.title}" for t in pending) or "Nenhuma"
        prompt = f"Gere um resumo diario motivador em portugues (max 3 paragrafos).\n\nConcluidas:\n{completed_text}\n\nPendentes:\n{pending_text}"
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                timeout=10,  # timeout de 10 segundos
            )
            return response.choices[0].message.content.strip()
        except AuthenticationError:
            logger.error("Chave do Groq invalida em generate_daily_summary")
            raise ValueError("Servico de IA indisponivel.")
        except RateLimitError:
            logger.error("Rate limit Groq em generate_daily_summary")
            raise ValueError("Limite de IA atingido. Tente em instantes.")
        except APIError as e:
            logger.error("APIError Groq generate_daily_summary", extra={"error": str(e)})
            raise ValueError("Erro no servico de IA.")
        except Exception as e:
            logger.error("Erro inesperado generate_daily_summary", extra={"error": str(e)})
            raise ValueError("Erro inesperado ao gerar resumo.")

from typing import List

from groq import Groq

from app.core.settings import settings
from app.models.task import Task


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

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
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

    def generate_daily_summary(self, tasks: List[Task]) -> str:
        if not tasks:
            return "Nenhuma tarefa encontrada para hoje."

        completed = [t for t in tasks if t.is_completed]
        pending = [t for t in tasks if not t.is_completed]

        completed_text = "\n".join(f"- {t.title}" for t in completed) or "Nenhuma"
        pending_text = "\n".join(f"- {t.title}" for t in pending) or "Nenhuma"

        prompt = f"Gere um resumo diario motivador em portugues (max 3 paragrafos).\n\nConcluidas:\n{completed_text}\n\nPendentes:\n{pending_text}"

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()

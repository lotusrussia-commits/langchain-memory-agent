import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()


@dataclass
class UserContext:
    """Контекст пользователя."""

    name: str
    learning_goal: str


def get_project_info(project_name: str) -> str:
    """Возвращает информацию об одном из учебных проектов пользователя."""

    projects = {
        "triage-mvp": (
            "FastAPI-сервис обработки обращений. "
            "Использует LLM для определения категории обращения, "
            "формирования черновика ответа и определения необходимости эскалации. "
            "Есть SQLite, валидация Pydantic, fallback и rate limit."
        ),
        "telegram-memory-bot": (
            "Telegram-бот с памятью. "
            "Использует Python, aiogram и ChromaDB для работы с историей "
            "и семантическим поиском."
        ),
        "pinecone-semantic-search": (
            "Проект семантического поиска с использованием Pinecone "
            "и embeddings."
        ),
        "docker-flask-homework": (
            "Учебный Flask-проект в Docker. "
            "Есть API-эндпоинты и Docker-контейнер."
        ),
    }

    normalized_name = project_name.lower().strip()

    return projects.get(
        normalized_name,
        f"Информация о проекте '{project_name}' не найдена.",
    )


model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0,
)


checkpointer = InMemorySaver()


agent = create_agent(
    model=model,
    tools=[get_project_info],
    checkpointer=checkpointer,
)


def ask_agent(question: str, thread_id: str = "demo-user") -> str:
    """Отправляет вопрос агенту и возвращает его ответ."""

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        },
        {
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    return result["messages"][-1].content


if __name__ == "__main__":
    print("LangChain Memory Agent")
    print("Введите вопрос или 'exit' для выхода.\n")

    while True:
        question = input("Вы: ").strip()

        if question.lower() in {"exit", "quit", "выход"}:
            print("До свидания!")
            break

        if not question:
            continue

        try:
            answer = ask_agent(question)
            print(f"\nАгент: {answer}\n")
        except Exception as e:
            print(f"\nОшибка: {e}\n")
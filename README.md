# LangChain Memory Agent

Консольный агент на LangChain, который помнит диалог в рамках одного запуска и отвечает на вопросы об учебных проектах через инструмент.

Агент собирается через `create_agent`, модель — `ChatOpenAI`, история диалога хранится в `InMemorySaver` из LangGraph. Каждый ход пишется в один и тот же поток (`thread_id`), поэтому агент видит предыдущие реплики, пока процесс не завершён.

## Возможности

- Диалог в терминале: вопрос → ответ, пока не введена команда выхода.
- Короткая память: предыдущие сообщения доступны агенту внутри одной сессии.
- Инструмент `get_project_info` — справочник по четырём учебным проектам.
- Модель, ключ и базовый URL задаются через переменные окружения, поэтому можно использовать OpenAI API или совместимый OpenAI API-прокси.

## Что сделано по заданию

В рамках дополнительного задания создан базовый AI-агент по примеру из урока.

Реализовано:

- агент на LangChain через `create_agent`;
- подключение модели `ChatOpenAI`;
- собственный инструмент `get_project_info`;
- передача инструмента агенту;
- память диалога через `InMemorySaver`;
- использование `thread_id` для сохранения состояния диалога;
- проверка работы памяти на нескольких последовательных сообщениях;
- проверка поведения памяти после перезапуска программы.

## Как это устроено

```text
Вы  →  ask_agent()  →  agent.invoke()
                          │
                          ├─ messages        история + новый вопрос
                          └─ thread_id       ключ чекпоинта
                                    │
                         InMemorySaver (память процесса)
                                    │
                         ChatOpenAI  ←→  get_project_info
                                    │
                              последний ответ
```

`ask_agent` отправляет только новое сообщение пользователя. Предыдущие реплики подтягивает чекпоинтер по `thread_id`. По умолчанию используется `"demo-user"`, поэтому все вопросы в одном запуске попадают в одну историю.

Память живёт в оперативной памяти процесса. После выхода из программы или перезапуска история пропадает.

## Инструмент

`get_project_info(project_name)` ищет проект по имени без учёта регистра и пробелов по краям. Если имени нет в справочнике, возвращает строку «информация не найдена».

| Имя | О чём проект |
| --- | --- |
| `triage-mvp` | FastAPI-сервис обработки обращений: категория, черновик ответа, эскалация, SQLite, Pydantic, fallback и rate limit |
| `telegram-memory-bot` | Telegram-бот с памятью на Python, aiogram и ChromaDB |
| `pinecone-semantic-search` | Семантический поиск на Pinecone и embeddings |
| `docker-flask-homework` | Учебный Flask API в Docker |

Агент вызывает инструмент сам, когда вопрос касается одного из этих проектов.

## Требования

- Python 3.12
- Ключ API, совместимый с OpenAI Chat Completions

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

В `.env` подставьте свой ключ:

```env
OPENAI_API_KEY=your_proxyapi_key_here
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
OPENAI_MODEL=gpt-4o-mini
```

| Переменная | Обязательна | По умолчанию | Назначение |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | да | — | ключ доступа к API |
| `OPENAI_BASE_URL` | нет | эндпоинт OpenAI | базовый URL, если используется прокси |
| `OPENAI_MODEL` | нет | `gpt-4o-mini` | имя модели |

`temperature` зафиксирован в коде и равен `0`.

Файл `.env` в git не попадает: он указан в `.gitignore`.

## Запуск

```bash
python main.py
```

```text
LangChain Memory Agent
Введите вопрос или 'exit' для выхода.

Вы: Расскажи про triage-mvp

Агент: ...

Вы: exit
До свидания!
```

Выход: `exit`, `quit` или `выход`. Пустая строка пропускается.

Пример, где видна память: сначала спросите «Расскажи про telegram-memory-bot», затем «А на чём он хранит историю?». Второй ответ опирается на предыдущий ход того же `thread_id`.

## Структура

```text
.
├── main.py            агент, инструмент, цикл ввода
├── requirements.txt   зависимости
├── .env.example       шаблон переменных окружения
└── .gitignore
```

## Зависимости

- [langchain](https://github.com/langchain-ai/langchain) — `create_agent` и вызов инструментов
- [langchain-openai](https://github.com/langchain-ai/langchain) — `ChatOpenAI`
- [langgraph](https://github.com/langchain-ai/langgraph) — `InMemorySaver`
- [python-dotenv](https://github.com/theskumar/python-dotenv) — загрузка `.env`

## Ограничения

- История не сохраняется на диск и не переживает перезапуск.
- Все пользователи CLI делят один `thread_id` (`demo-user`). Отдельные диалоги появятся, если передавать разные идентификаторы в `ask_agent`.
- Справочник проектов зашит в `get_project_info`. Новые проекты добавляются прямо в словарь `projects`.

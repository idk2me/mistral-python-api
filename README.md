# mistral-python-api
backend using Mistral AI's Le Chat to summarize research papers from arxiv.

Before you can run the project, you need to define the `MISTRAL_API_KEY` in `.env`

Then you need to install `uv` and run
```bash
uv venv
uv sync
uv run uvicorn main:app --reload
```

Then you can open up `http://localhost:8000/docs` to see the OpenAPI specification. You can now run the [frontend](https://github.com/idk2me/mistral-project-frontend).

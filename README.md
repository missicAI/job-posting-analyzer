# JobLens

JobLens reads a job posting and brings its main details together. It separates required skills from nice-to-have skills and keeps a quote from the original text so each item can be checked.

The result can be saved as JSON. If a posting leaves out its salary or location, that field stays empty.

## Run the app

Use Python 3.12. On Windows, run `CAI_DAT.bat` once, then open `CHAY_DEMO.bat`.

You can also install and run it from a terminal:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The sample view shows three prepared examples. To read a new posting, connect a model and select **Phân tích bằng LLM**.

## Connect a model

Install [Ollama](https://ollama.com/download), then run:

```bash
ollama pull llama3.2:3b
```

Copy `.env.example` to `.env` and restart the app. The example settings use Ollama on your own computer. You can change the model name in that file.

Another service can be used by setting `LLM_PROVIDER=compatible`, its address ending in `/v1`, the model name and your API key. The service needs to support JSON schema responses. Keep your key in `.env`.

## Inside the project

`app.py` contains the screen and buttons. `joblens/extraction.py` defines the information to collect and checks it against the posting. `joblens/llm.py` sends the request to the model.

The checks can catch an invented value or a missing quote. They cannot guarantee that every skill is placed in the right group, so the original text remains useful when reviewing a result.

To run the checks:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

With a model running, `python evaluate.py` compares its answers with the three prepared examples. This is a small starting check, rather than a broad measure of model quality.

Built with Python, Streamlit and Pydantic. Project code is available under the MIT license.

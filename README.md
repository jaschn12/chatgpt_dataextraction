# chatgpt_dataextraction
A small tool using Python and the ChatGPT API to answer questions about the content of a PDF file
and return an annotated PDF along with the found answers

## searchTerm 
In ```questions.json``` the value for searchTerm can contain any regex pattern
- ```Kl\\w{0,3}ger``` matches "Kläger" and "Klaeger" and "Klaeeger" and "Klger" but not "Klaaeeger"
- ```Kl.+ger``` matches "Kläger" and "Klaeger" and "Klager" and "Klüger" but not "Klger"

## Installation
I used conda with the following setup command:
````conda create -n [venv_name] python openai pypdf pytest````

## API Key
- Create .env file with content like:

````
OPENAI_API_KEY=abc123
AZURE_OPENAI_API_KEY=abc123
AZURE_OPENAI_ENDPOINT=abc123
````

## Run tests
```python -m pytest```


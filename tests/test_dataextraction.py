import pytest
import data_extraction
import os

# def test_...():
#   ...
#   assert()

def test_readConfig():
    questionsPath = os.path.join(".", "questions.json")
    configPath = os.path.join(".", "config.json")
    questions = data_extraction.readConfigFile(questionsPath)
    assert len(questions) > 0 # Dokumente
    assert len(list(questions.values())[0]) > 0 # Datenpunkte
    assert len(list(list(questions.values())[0].values())[0]) > 0 # Infos pro Datenpunkt

    structure = data_extraction.readConfigFile(configPath)["systemPrompt"]
    assert structure != {}

def test_dataextraction():
    with open(os.path.join("tests", "urteil.pdf"), "rb") as f:
        result = data_extraction.dataextraction(
            fileReader=f,
            docName="Gerichtsentscheidung"
        )
        assert result 
        f.seek(0)
        assert result.pdf.outputPdfStream.read() != result.pdf.inputPdfStream.read()
        result.pdf.outputPdfStream.seek(0)
    # save the pdf to disk
    with open(os.path.join("tests", "annotated_pdf.pdf"), "wb") as f:
        f.write(result.pdf.outputPdfStream.read())
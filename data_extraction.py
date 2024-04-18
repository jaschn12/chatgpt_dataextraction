import pypdf
import pypdf.annotations
import json 
import re
import io
import sqlite3
import os
from openai import OpenAI
# from openai import AzureOpenAI

class PdfFragment:
    "Repräsentation eines PDF-Teils inkl. Metadaten"
    def __init__(self, text:str, userMatrix:list, tmMatrix:list, fontDict:dict, fontSize:float, page:int) -> None:
        self.text = text
        self.page = page
        self.userMatrix = userMatrix
        self.tmMatrix = tmMatrix
        self.fontDict = fontDict
        self.fontSize = fontSize
    
class Searchable:
    """enthält einen oder mehrere PdfFragements, die zusammengenommen einen Abschnitt bilden, 
    der mithilfe des LLM durchsucht wird"""
    def __init__(self, fragments : list[PdfFragment] ) -> None:
        self.fragments = fragments
        self.highlights:list[tuple[int,pypdf.annotations.MarkupAnnotation]] = []
    
    @classmethod
    def createFragmentList(cls, 
                           fragments:list[PdfFragment], 
                           contextLength:int
                           ) -> list[list[PdfFragment]]:
        """args: a set of fragments and a specific context length
        returns: a list of lists of fragments; each sublist is suitable for constructing a Searchable
        the sublists overlap so that it is guaranteed that the contextLength is matched"""
        result = []
        contextLengthFactor = 2
        index = 0
        nextStartIndex = 0
        reachedEnd = False
        while not reachedEnd:
            currentSize = 0
            sublist = []
            nextStartIndex = index + 1 # always do at least one step forward
            for i in range(index, len(fragments)):
                # print(f"{ currentSize = }")
                fragment = fragments[i]
                sublist.append(fragment)
                currentSize += len(fragment.text)

                if currentSize < contextLength:
                    nextStartIndex = i + 1
                if currentSize > contextLength * contextLengthFactor:
                    break
            result.append(sublist)

            reachedEnd = (nextStartIndex >= len(fragments) - 1)

            index = nextStartIndex
        # for r in result:
        #     print("sublist:", " ".join([f.text for f in r]), end="\n\n")
        return result


    def getText(self):
        return " ".join(f.text for f in self.fragments)
    
    def createHighlights(self, description:str):
        # create description at beginning
        x,y = pypdf.mult(
            self.fragments[0].tmMatrix, 
            self.fragments[0].userMatrix
            )[4:]
        self.highlights.append(
            (self.fragments[0].page,
            pypdf.annotations.FreeText(
                text=description,
                rect=(
                    x - 40,
                    y,
                    x - 2.,
                    y + 40),
                font="Arial",
                bold=True,
                italic=False,
                font_size="20pt",
                border_color="FF0000", # hex color
                background_color="FFD580")) # light orange
        )        
        # draw boxes around fragments
        for fragment in self.fragments:
            transformation = pypdf.mult(
                fragment.tmMatrix, 
                fragment.userMatrix
                )
            x,y = transformation[4:]
            # print(f"highlight: {x,y = } for {fragment.text = }")
            # approximate the width of the text
            width = 0.5 * fragment.fontSize * len(fragment.text) * transformation[3]
            height = fragment.fontSize * transformation[3]
            rect=(x-5,y-5,x+width+5,y+height+5)
            quad_points = [rect[0], rect[1], rect[2], rect[1], rect[0], rect[3], rect[2], rect[3]]
            self.highlights.append(
                (fragment.page,
                pypdf.annotations.Highlight(
                    rect=rect,
                    quad_points=pypdf.generic.ArrayObject(
                        [pypdf.generic.FloatObject(quad_point) for quad_point in quad_points]),
                    highlight_color="FFD580"
                )))
        print(f"{ self.highlights }")
    
class PdfFile:
    "Repräsentation eines PDF Files, wie er an den Service übergeben wird"
    def __init__(self, inputPdfStream:io.BufferedReader, documentCategory:str) -> None:
        self.inputPdfStream = inputPdfStream
        self.documentCategory = documentCategory
        self.currentPage = 0
        self.fragments:list[PdfFragment] = []
        self.outputPdfStream = io.BytesIO()
        self.reader = pypdf.PdfReader(self.inputPdfStream)
        self.writer = pypdf.PdfWriter()
        for page in self.reader.pages:
            self.writer.add_page(page=page)

        """
        visitor: len:  26 -> zum Gerichtskos
        - user_matrix = [0.60016742325, 0.0, 0.0, -0.60016742325, 28.5, 1598.5189850000002]
        - tm_matrix = [1.0, 0.0, 0.0, -1.0, 30.0, 2125.0]

        visitor: len:  71 -> Die Parteien er
        - user_matrix = [0.60016742325, 0.0, 0.0, -0.60016742325, 28.5, 1598.5189850000002]
        - tm_matrix = [1.0, 0.0, 0.0, -1.0, 30.0, 2155.0]
        """

    def parsePdf(self) -> list[PdfFragment]:
        print(f"{self.reader.get_num_pages() = }")
        pageNr = 0 

        def visitor(text, userMatrix, tmMatrix, fontDictionary, fontSize):
            if len(text.strip()) == 0: return
            self.fragments.append(
                PdfFragment(text=text,
                            userMatrix=userMatrix,
                            tmMatrix=tmMatrix,
                            fontDict=fontDictionary,
                            fontSize=fontSize,
                            page=pageNr))
            # print(f"visitor: len: {len(text): 3} @ {pageNr}-> {text[:15].strip()}")
            # print(f"- {userMatrix = }")
            # print(f"- {tmMatrix = }")
            # print(f"- {fontDictionary = }")
            # print(f"- {fontSize = }")

        for pageNr, page in enumerate(self.reader.pages):
            page.extract_text(visitor_text=visitor)
        
        page.get

        return self.fragments
    
    def addHighlightsFromSearchable(self, searchable:Searchable):
        for higlight in searchable.highlights:
            self.writer.add_annotation(page_number=higlight[0], annotation=higlight[1])
    
    def createOutputPdf(self):
        print(f"{self.writer.write(self.outputPdfStream) = }")
        self.outputPdfStream.seek(0)

class LlmHandler:
    def __init__(self, config:dict) -> None:
        # self.client = OpenAI()
        # self.client = AzureOpenAI(
        #     azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        #     api_version="2024-02-01"
        #     )
        self.config = config
        self.dbPath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            config["dbName"])
        if config["useCache"] == "yes":
            with sqlite3.connect(self.dbPath) as conn:
                sql = """CREATE TABLE IF NOT EXISTS llmCache (
                    key INTEGER PRIMARY KEY AUTOINCREMENT,
                    promptBody TEXT,
                    answer TEXT
                    );"""
                conn.cursor().execute(sql)
            self.promptCacheLookup = self._promptCacheLookup
            self.add2cache = self._add2cache
        else:
            def noLookup(*args, **kwargs): return False
            def noCache(*args, **kwargs): return 
            self.promptCacheLookup = noLookup
            self.add2cache = noCache
            

    def createPromptBody(self, promptParts:dict, searchable:Searchable) -> str:
        try: dataTypePart = self.config["dataTypePart"][promptParts["dataType"]]
        except KeyError as error: 
            print(f"Key Error in function createPrompt(): {promptParts = } with {promptParts['dataType'] = }. Does this datatype exist?")
            return ""
        promptBody = self.config["structure"].format(**{
            "intro" : promptParts["promptIntro"] if promptParts["promptIntro"] != "default" else self.config["generalIntro"],
            "source" : searchable.getText(),
            "question" : promptParts["question"],
            "dataTypePart" : dataTypePart
        })
        return promptBody
    
    def callLlm(self, promptBody:str) -> str:
        # placeholder
        return "Das ist ein Text aus einem juristischen Dokument. --- Ja"
        
        raw_output = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.config["systemPrompt"]},
                {"role": "user", "content": promptBody}
            ],
            temperature=0.1,
            max_tokens=300
            )
        output = raw_output['choices'][0]['message']['content']
        return output

    def _promptCacheLookup(self, promptBody:str) -> str|bool:
        with sqlite3.connect(self.dbPath) as conn:
            lookup = conn.cursor().execute("SELECT answer FROM llmCache WHERE promptBody LIKE ?", (promptBody, )).fetchone()
        if lookup != None: return lookup[0]
        return False
    def _add2cache(self, promptBody:str, answer:str):
        with sqlite3.connect(self.dbPath) as conn:
            conn.cursor().execute("INSERT INTO llmCache (prompt, answer) VALUES (?, ?)", 
                                    (promptBody, answer))

class Datapoint:
    "Repräsentation eines Datenpunkts, bspw. ein Clausebase-Datafield"
    def __init__(self, llmHandler: LlmHandler, question:str, searchTerm:str, dataType:str, contextLength:int, 
                 defaultValue, promptIntro) -> None:
        # Input
        self.llmHandler = llmHandler
        self.question = question
        self.searchTerm = searchTerm
        self.dataType = dataType
        self.contextLength = contextLength
        self.defaultValue = defaultValue
        self.promptIntro = promptIntro
        # Output
        self.answer = None
        self.relevantSearchable = None
        self.result = defaultValue
    
    def findAnswer(self, searchables:list[Searchable]):
        filtered = [s for s in searchables if re.search(self.searchTerm, s.getText(), flags=re.IGNORECASE) != None]
        print(f"keyword: {self.searchTerm} -> {len(filtered)} Abschnitte gefunden")
        for searchable in filtered:
            print("text in filtered searchable:", searchable.getText())
            promptBody = self.llmHandler.createPromptBody(
                {   "dataType" : self.dataType,
                    "promptIntro" : self.promptIntro,
                    "question" : self.question}, 
                searchable)
            lookup = self.llmHandler.promptCacheLookup(promptBody=promptBody)
            if lookup: self.answer = lookup
            else: 
                self.answer = self.llmHandler.callLlm(promptBody=promptBody)
            self._evaluateAnswer()
            if self.result != self.defaultValue: # wenn Antwort gefunden
                self.relevantSearchable = searchable
                return
    
    def _evaluateAnswer(self):
        splitPhrase = "---"
        if self.dataType == "bool":
            index_sep = self.answer.find(splitPhrase)
            if index_sep == -1: int(0.9 * len(self.answer))
            if self.answer.find("Ja", index_sep) != -1: 
                #print("answer: ", self.answer)
                self.result = True
            elif self.answer.find("Nein", index_sep) != -1: self.result = False
            else: pass
                #print("evaluating the answer failed:", self.answer)
            
        elif self.dataType == "text": 
            index_sep = self.answer.find(splitPhrase)
            if index_sep == -1: 
                if len(self.answer) > 30:
                    #print("evaluating the answer failed:", self.answer)
                    return
                else: index_sep = 0
            self.result = self.answer[index_sep+len(splitPhrase):].strip()
        else:
            print("evaluate_answer(): unknown datatype:", self.dataType)

    def __str__(self) -> str:
        return "\n".join(str(element) for element in 
            [self.question, self.searchTerm, self.dataType, 
                self.defaultValue, self.answer, self.relevantSearchable, self.result])

class Result:
    def __init__(self, pdf) -> None:
        self.pdf : PdfFile = pdf
        # name : str, value : Any, pageNr : int
        self.values : dict = {}


def readConfigFile(filename : str) -> dict:
    config = {}
    with open(filename, "r") as f:
        config = json.load(f)
    return config

class DataExtractor:
    def __init__(self) -> None:
        self.questionsConfig = readConfigFile(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "questions.json"))
        self.config = readConfigFile(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "config.json"))
        self.llmHandler = LlmHandler(config=self.config)
        
    def __call__(self, fileReader: io.BufferedReader, docName:str):
        pdf = PdfFile(inputPdfStream=fileReader, documentCategory=docName)
        pdf.parsePdf()
        
        result = Result(pdf=pdf)

        questions = self.questionsConfig[docName]
        for datapointName, value in questions.items():
            datapoint = Datapoint(
                llmHandler =     self.llmHandler,
                question =       value["question"],
                searchTerm =     value["searchTerm"],
                dataType =       value["dataType"],
                contextLength =  value["contextLength"] if value["contextLength"] > 0 else self.config['defaultContextLength'],
                defaultValue =   value["defaultValue"],
                promptIntro =    value["promptIntro"]
            )

            # create searchables from fragments
            fragmentLists = Searchable.createFragmentList(pdf.fragments, datapoint.contextLength)
            searchables = [Searchable(fragments=fragmentList) for fragmentList in fragmentLists]

            # searching
            datapoint.findAnswer(searchables)

            # adding annotations
            if datapoint.relevantSearchable:
                searchable = datapoint.relevantSearchable
                searchable.createHighlights(description=datapointName)
                pdf.addHighlightsFromSearchable(searchable)
                pageNr = searchable.fragments[0].page
            else: pageNr = -1

            result.values.update({
                datapointName : {
                "value" : datapoint.result,
                "pageNr" : pageNr}
            })
        
        # write the pdf into memory
        pdf.createOutputPdf()
        return result 

if __name__ == "__main__":
    dataExtractor = DataExtractor()
    with open(os.path.join("tests", "urteil.pdf"), "rb") as f:
        result = dataExtractor(
            fileReader=f,
            docName="Gerichtsentscheidung"
        )
    print(result.values)
    # save the pdf to disk
    with open(os.path.join("tests", "annotated_pdf.pdf"), "wb") as f:
        f.write(result.pdf.outputPdfStream.read())
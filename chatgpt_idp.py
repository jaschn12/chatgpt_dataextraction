import openai 
import sqlite3
from pdfminer.high_level import extract_text
import re
import json
import pandas as pd

folder = "./"
document_filename = "urteil.pdf"
answer_filename = "answers"
text = extract_text(folder+document_filename)
conn = sqlite3.connect(folder+"dataextraction.db")
openai.api_key = open(folder+"openai_key.txt", "r").read().splitlines()[2]

paragraphs = []
current = ""
for line in text.split("\n"):
    if line=="": continue
    if len(current) + len(line) < 1000:
        current += "\n"+line
        continue
    paragraphs.append(current)
    #print("\n\ncurrent:", current)
    current = line

#print("len(paragraphs)", len(paragraphs))

class Datapoint:
    def __init__(self, question:str, keyword:str, dtype:str, default) -> None:
        self.question = question
        self.keyword = keyword
        self.dtype = dtype
        self.default = default
        self.answer = None
        self.relevant_text = ""
        self.result = default
    def find_answer(self, paragraphs):
        filtered = list(filter(lambda x: re.search(self.keyword, x, flags=re.IGNORECASE) != None, 
                           paragraphs))
        # filtered = list(filter(lambda x: x.find(self.keyword) != -1, 
        #                    paragraphs))
        print("keyword: {} -> {} Abschnitte gefunden".format(self.keyword, len(filtered)))
        for p in filtered:
            prompt = create_prompt(self, p)
            lookup = conn.cursor().execute("SELECT answer FROM chatgpt WHERE prompt LIKE ?", (prompt, )).fetchall()
            if lookup != []: self.answer = lookup[0][0]
            else: 
                self.answer = call_chatgpt(prompt)
                conn.cursor().execute("INSERT INTO chatgpt (prompt, answer) VALUES (?, ?)"
                                    , (prompt, self.answer))
                conn.commit()
            self.evaluate_answer()
            if self.result != self.default: # wenn Antwort gefunden
                self.relevant_text = p
                return
    
    def evaluate_answer(self):
        if self.dtype == "bool":
            index_sep = self.answer.find("---")
            if index_sep == -1: int(0.9 * len(self.answer))
            if self.answer.find("Ja", index_sep) != -1: 
                #print("answer: ", self.answer)
                self.result = True
            elif self.answer.find("Nein", index_sep) != -1: self.result = False
            else: pass
                #print("evaluating the answer failed:", self.answer)
            
        elif self.dtype == "text": 
            index_sep = self.answer.find("---")
            if index_sep == -1: 
                if len(self.answer) > 30:
                    #print("evaluating the answer failed:", self.answer)
                    return
                else: index_sep = 0
            self.result = self.answer.split("---")[1].strip()
        else:
            print("evaluate_answer(): unknown datatype:", self.dtype)

    def __str__(self) -> str:
        return "\n".join(str(element) for element in 
            [self.question, self.keyword, self.dtype, 
                self.default, self.answer, self.relevant_text, self.result])
        
            
def call_chatgpt(prompt:str) -> str:
    #print("prompt", prompt)
    #print()
    raw_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein präziser und sorgfältiger Assistent in einer Anwaltskanzlei."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300
        )
    output = raw_output['choices'][0]['message']['content']
    return output

def create_prompt(datapoint: Datapoint, abschnitt: str) -> None:
    if datapoint.dtype == "bool":
        prompt_dtype = "Beantworte die Frage nur mit 'Ja' oder 'Nein'."
    elif datapoint.dtype == "text": 
        prompt_dtype = "Gib eine Ein-Wort-Antwort. Bilde keinen Satz."
    else:
        print("unknown datatype in create_prompt()")
        return
    general_prompt = """Im folgenden erhältst du einen kurzen Textabschnitt aus einer Klageschrift. 
Abschnitt: 
{abschnitt}

Fasse den Abschnitt kurz zusammen. Füge dann drei Bindestriche ('---') ein. Beantworte danach diese Frage:
Frage: {frage} 
{prompt_dtype}
"""
    d = {"abschnitt": abschnitt, "prompt_dtype": prompt_dtype, "frage": datapoint.question}
    return general_prompt.format(**d)

datapoints = []
answers = []
# reading in the EXCEL file containing the questions
pd_input = pd.read_excel(folder+'chatgpt_questions.xlsx', dtype=str) 

for index, row in pd_input.iterrows():
    question=row['question']
    keyword=row['search_keyword']
    dtype=row['datatype']
    default=row['default']
    if not pd.notna(default): default = ""
    elif default == "true": default = True
    elif default == "false": default = False
    dp = Datapoint(question=question, keyword=keyword, dtype=dtype, default=default)
    datapoints.append(dp)

# go trough the questions and find the answers
for i, d in enumerate(datapoints[:]): 
    d.find_answer(paragraphs)
    print("{question} : {result}".format(**{'question' : d.question, 'result': d.result}))
    answers.append( {"question_nr" : i, 
                     "question" : d.question, 
                     "found_answer_in" : d.relevant_text, 
                     "chatgpt_answer" : d.answer if d.relevant_text != "" else "", 
                     "result" : d.result} )

filename = folder + document_filename.replace(".", "_") + "_" + answer_filename

# saving as json file
with open(filename + ".json", "w") as f:
    json.dump(answers, f, indent=3)
    print(f"saved in {filename}.json")
# also saving in Excel
df_out = pd.DataFrame.from_records(answers)
df_out.drop(columns=['found_answer_in']
            ).to_excel(filename + ".xlsx", sheet_name=document_filename.replace(".", "_")) 
print(f"saved in {filename}.xlsx")

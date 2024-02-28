from fastapi import UploadFile, Form, File, HTTPException,FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import extract_text,get_informations
from scrap import scrape_search_results
from ATS import getReport
from Task2 import find_score
import os
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "hello"

class filePathObj(BaseModel):
    filePath: str

@app.post("/resumeDetails")
def resume_details(obj:filePathObj):
    obj=extract_text(obj.filePath)
    text=obj["text"]
    result=get_informations(text)
    print(result)
    if(result==None):
        return "Sorry please try again"
    if(result!=None):
        result["is_image"]=obj["is_image"]
    output=getReport(result)
    return output



# @app.post("/pdftext")
# def pdfExtracter(obj:sourceObj):
#     files=os.listdir("resumes")
#     details={}
#     for file in files:
#         text=extract_text("resumes/{}".format(file))
#         details[file]=text
#     all_text=list(details.values())
#     names=list(details.keys())
#     max_index=similarity_count_finding(obj.source,all_text)
#     selected_name=names[max_index]
#     print(selected_name)
#     ans=scrape_search_results(resume_details[selected_name])
#     print(ans)
#     return ans


#task 2

class description(BaseModel):
    description:str
@app.post("/jobDescription")
def jobDescription(req:description):
    score=find_score(req.description)
    return score


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
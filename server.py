import time
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import extract_text
from scrap import scrape_search_results,course_suggestion
from ATS import getReport
from Parsing import calculate_description_score,Resume_parsing
app = FastAPI()
looping=""
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

@app.post("/candidate/resumeScore")
async def resume_details_with_skill_related_links(obj:filePathObj):
    previous=time.time()
    start_time=previous
    obj=extract_text(obj.filePath)
    if(isinstance(obj,str)):
        return obj

    current=time.time()
    print("Text extraction timing :",round(current-previous,2)," sec")
    previous=current
    text=obj["text"]
    result=Resume_parsing(text)
    current=time.time()
    print("Resume parsing timing :",round(current-previous,2)," sec")
    previous=current
    # print(result)
    if(result==None):
        return "Something went wrong, please try again"
    if(result!=None):
        result["is_image"]=obj["is_image"]
    related_courses=[]
    for index,skill in enumerate(result["Hard_skills"]):
        try:
            if(index==3):
                break

            # print(skill)
            courses=await course_suggestion(skill)
            related_courses.append(courses[0])
            current=time.time()
            print(f"Course {index + 1}.{skill} found timing : ",round(current-previous,2)," sec")
            previous=current
        except Exception as e:
            print(e)
    output=getReport(result)
    current=time.time()
    print("Final Report and score generation timing :",round(current-previous,2)," sec")
    previous=current
    output["Course_suggestions"]=related_courses
    print("Total timing : {} min".format(round((time.time()-start_time)/60,2)))
    return output



@app.post("/interviewer/resumeScore")
async def resume_details_with_name_related_links(obj:filePathObj):
    previous=time.time()
    start_time=previous
    obj=extract_text(obj.filePath)
    if(isinstance(obj,str)):
        return obj

    current=time.time()
    print("Text extraction timing :",round(current-previous,2)," sec")
    previous=current
    text=obj["text"]
    result=Resume_parsing(text)
    current=time.time()
    print("Resume parsing timing :",round(current-previous,2)," sec")
    previous=current
    print(result)
    if(result==None):
        return "Something went wrong, please try again"
    if(result!=None):
        result["is_image"]=obj["is_image"]
    linkedin_link={}
    for experience in result["Working_experience"]:
        query=f'{result["Contact_information"]["Name"]} - {experience["role"]} at {experience["Organization_name"]}'
        # print(query)
        linkedin_link=scrape_search_results(query)
        break

    current=time.time()
    print("Linkedin link found :",round(current-previous,2)," sec")
    previous=current
    output=getReport(result)
    current=time.time()
    print("Final Report and score generation timing :",round(current-previous,2)," sec")
    previous=current
    output["Linkedin_link"]=linkedin_link
    print("Total timing : {} min".format(round((time.time()-start_time)/60,2)))
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
@app.post("/jobDescriptionScore")
def jobDescription(req:description):
    score=calculate_description_score(req.description)
    return score

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
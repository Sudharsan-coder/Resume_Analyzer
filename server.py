from typing import List,Optional
import time
from multiprocessing import Process,Manager
from fastapi import FastAPI, File,Form, UploadFile, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from linkedInOptimizer import complete_analysis
from utils import extract_text
from scrap import scrape_search_results,course_suggestion
from ATS import getReport
from Parsing import calculate_description_score,Resume_parsing,description_parsing,parsing_resume_job_description,comparison_parsing
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
    return "To know more about this api, reach out to the /docs end point for the swagger documentary"

class ResumeReport(BaseModel):
    contactScore: float
    contactReview: str
    resumeObjectiveScore: int
    resumeObjectiveReview: str
    workExperienceScore: float
    workExperienceReview: str
    educationScore: float
    educationReview: str
    projectScore: float
    projectReview: str
    skillsScore: int
    skillsReview: str
    formatReview: str
    certificateScore: float
    certificateReview: str
    softSkillsScore: int


class FieldsToAdd(BaseModel):
    techStackOfProject: Optional[str]
    resumeObjective: Optional[str]
    linkedInInContactSection: Optional[str]
    completionYearInEducationSection: Optional[str]
    marksInEducationSection: Optional[str]
    courseInEducationSection: Optional[str]
    gitHubInContactSection: Optional[str]
    emailInContactSection: Optional[str]

class CandidateResumeScore(BaseModel):
    ats_score: float
    resumeReport: ResumeReport
    fieldsToAdd: FieldsToAdd


@app.post("/api/v1/candidate/resume-score")
async def resume_details_with_skill_related_links(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        obj=extract_text(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Provide only pdf files")
    if(isinstance(obj,str)):
        return obj
    text=obj["text"]
    result=Resume_parsing(text)
    if(result==None):
        raise HTTPException(status_code=400, detail="Something went wrong, please try again")
    else:
        result["is_image"]=obj["is_image"]
    # related_courses=[]
    # for index,skill in enumerate(result["Hard_skills"]):
    #     try:
    #         if(index==3):
    #             break
    #         courses=await course_suggestion(skill)
    #         related_courses.append(courses[0])
    #         current=time.time()
    #         print(f"Course {index + 1}.{skill} found timing : ",round(current-previous,2)," sec")
    #         previous=current
    #     except Exception as e:
    #         print(e)
    output=getReport(result)
   
    return output


class LinkedinDetails(BaseModel):
    Title: str
    link: str
    snippet: str

class InterviewerResumeScore(BaseModel):
    ats_score: float
    resumeReport: ResumeReport
    fieldsToAdd: FieldsToAdd
    Linkedin_details: LinkedinDetails

@app.post("/api/v1/interviewer/resume-score",response_model=InterviewerResumeScore)
async def resume_details_with_name_related_links(file: UploadFile = File(...)):
    contents = await file.read()
    previous=time.time()
    start_time=previous
    try:
        obj=extract_text(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Provide only pdf files")

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
    output["Linkedin_details"]=linkedin_link
    print("Total timing : {} min".format(round((time.time()-start_time)/60,2)))
    return output


class descriptionRequest(BaseModel):
    description:str

class descriptionReponse(BaseModel):
    Score: int
    Suggestions_to_improve: List[str]

@app.post("/api/v1/interviewer/job-description-score",response_model=descriptionReponse)
def jobDescription(req:descriptionRequest):
    score=calculate_description_score(req.description)
    return score


@app.post("/api/v1/interviewer/top-resumes")
async def topResumes(files: List[UploadFile] = File(...), description: str = Form(...)):
    with Manager() as manager:
        return_dict = manager.dict()
        processes = []
        description_obj=description_parsing(description)
        print(description_obj)
        for file in files:
            content=await file.read()
            p = Process(target=Comparator, args=(content, description_obj, return_dict))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        key=list(return_dict.keys())
        val=list(return_dict.values())
        for index in range(len(val)):
            for j in range(index,len(val)):
                if(val[index]["Total"]<val[j]["Total"]):
                    val[index],val[j]=val[j],val[index]
                    key[index],key[j]=key[j],key[index]

        return key
        # for file_path, result in return_dict.items():
        #     print(f'Result for {file_path}: {result}')

def Comparator(content, description, return_dict):
    text = extract_text(content)
    resume_obj = Resume_parsing(text)
    return_dict[resume_obj["Contact_information"]["Name"]] = parsing_resume_job_description(resume_obj, description)

# def topResumes(req:description):
#     text=extract_text("resumes/tamil.pdf")
#     # print(text)
#     return comparison_parsing(text,description)
    
# async def topResumes(file: List[UploadFile] = File(...), description: str = Form(...)):
#     def do_resume_parsing(text, return_dict):
#         return_dict['resume'] = Resume_parsing(text)

#     def do_description_parsing(description, return_dict):
#         return_dict['description'] = description_parsing(description)
#     contents=await file[0].read()
#     text =extract_text(contents)
#     # print(text)
#     with Manager() as manager:
#         return_dict = manager.dict()
#         p1 = Process(target=do_resume_parsing, args=(text, return_dict))
#         p2 = Process(target=do_description_parsing, args=(description, return_dict))

#         p1.start()
#         p2.start()

#         p1.join()
#         p2.join()

#         resume_obj = return_dict['resume']
#         description_obj = return_dict['description']

#     return parsing_resume_job_description(resume_obj, description_obj)


# API to get resume and description from the client
@app.post("/analyze-resume/")
async def analyze_resume(resume: UploadFile = File(...), job_description: str = Form(...)):
    resume_contents = await resume.read()
    resume_text = extract_text(resume_contents)["text"]
    result = complete_analysis(resume_text, job_description)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
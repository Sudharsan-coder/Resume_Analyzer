from typing import List
import time
from multiprocessing import Process,Manager
from fastapi import FastAPI, File,Form, UploadFile, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from linkedInOptimizer import complete_analysis,extract_text
# from utils import extract_text
from scrap import scrape_search_results,course_suggestion
from ATS import getReport
from Parsing import calculate_description_score,Resume_parsing,description_parsing,parsing_resume_job_description,comparison_parsing
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

# from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse

@app.post("/uploadfile/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.filename.endswith(".pdf"):
        contents = await file.read()
        print(contents)
        # Now you can save the contents to a file, or process it in some other way.
        return {"filename": file.filename, "content_type": file.content_type}
    else:
        return JSONResponse(content={"message": "Invalid file type"}, status_code=400)



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
    techStackOfProject: str
    resumeObjective: str
    linkedInInContactSection: str
    completionYearInEducationSection: str
    marksInEducationSection: str
    courseInEducationSection: str
    gitHubInContactSection: str


class CandidateResumeScore(BaseModel):
    ats_score: float
    resumeReport: ResumeReport
    fieldsToAdd: FieldsToAdd


@app.post("/api/v1/candidate/resume-score")
async def resume_details_with_skill_related_links(file: UploadFile = File(...)):
    contents = await file.read()
    # previous=time.time()
    # start_time=previous
    try:
        obj=extract_text(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Provide only pdf files")
    # print(obj)
    if(isinstance(obj,str)):
        return obj

    # current=time.time()
    # print("Text extraction timing :",round(current-previous,2)," sec")
    # previous=current
    text=obj["text"]
    result=Resume_parsing(text)
    # current=time.time()
    # print("Resume parsing timing :",round(current-previous,2)," sec")
    # previous=current
    if(result==None):
        return "Something went wrong, please try again"
    if(result!=None):
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
    # current=time.time()
    # print("Final Report and score generation timing :",round(current-previous,2)," sec")
    # previous=current
    # output["Course_suggestions"]=related_courses
    # print("Total timing : {} min".format(round((time.time()-start_time)/60,2)))
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
        # return "Please provide only the pdf files"
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

#task 2


class description(BaseModel):
    description:str
@app.post("api/v1/interviewer/job-description-score")
def jobDescription(req:description):
    score=calculate_description_score(req.description)
    return score


@app.post("/interviewer/topResumes")
# def topResumes(req:description):
#     text=extract_text("resumes/tamil.pdf")
#     # print(text)
#     return comparison_parsing(text,description)
    
async def topResumes(file: UploadFile = File(...), description: str = Form(...)):
    def do_resume_parsing(text, return_dict):
        return_dict['resume'] = Resume_parsing(text)

    def do_description_parsing(description, return_dict):
        return_dict['description'] = description_parsing(description)
    contents=await file.read()
    text =extract_text(contents)
    # print(text)
    with Manager() as manager:
        return_dict = manager.dict()
        p1 = Process(target=do_resume_parsing, args=(text, return_dict))
        p2 = Process(target=do_description_parsing, args=(description, return_dict))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        resume_obj = return_dict['resume']
        description_obj = return_dict['description']

    return parsing_resume_job_description(resume_obj, description_obj)

# def testing(req:description):
#     # text=extract_text("resumes/tamil.pdf")
#     with Manager() as manager:
#         return_dict = manager.dict()
#         processes = []
#         description_obj=description_parsing(req.description)
#         print(description_obj)
#         for file_name in os.listdir("resumes"):
#                 if file_name.endswith('.pdf'):  # or whatever file type you're using
#                     file_path = os.path.join("/home/sudha/Music/Sudharsan_bro_project/server/resumes", file_name)
                    
#                     p = Process(target=demo, args=(file_path,description_obj, return_dict))
#                     p.start()
#                     processes.append(p)
#         for p in processes:
#             p.join()
#         key=list(return_dict.keys())
#         val=list(return_dict.values())
#         for index in range(len(val)):
#             for j in range(index,len(val)):
#                 if(val[index]["Total"]<val[j]["Total"]):
#                     val[index],val[j]=val[j],val[index]
#                     key[index],key[j]=key[j],key[index]

#         return key
#         # for file_path, result in return_dict.items():
#         #     print(f'Result for {file_path}: {result}')

# def demo(file_path, description, return_dict):
#     text = extract_text(file_path)
#     resume_obj = Resume_parsing(text)
#     return_dict[file_path] = parsing_resume_job_description(resume_obj, description)


# API to get resume and description from the client
@app.post("/analyze-resume/")
async def analyze_resume(resume: UploadFile = File(...), job_description: str = Form(...)):
    resume_contents = await resume.read()
    resume_text = extract_text(resume_contents)["text"]
    result = complete_analysis(resume_text, job_description)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
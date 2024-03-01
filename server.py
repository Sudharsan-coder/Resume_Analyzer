import time
import os
from multiprocessing import Process,Manager
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import extract_text
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

# @app.get("/")
# def home():
#     return "hello"

class filePathObj(BaseModel):
    filePath: str

@app.post("/candidate/resumeScore")
async def resume_details_with_skill_related_links(obj:filePathObj):
    previous=time.time()
    start_time=previous
    obj=extract_text(obj.filePath)
    print(obj)
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
    current=time.time()
    print("Final Report and score generation timing :",round(current-previous,2)," sec")
    previous=current
    # output["Course_suggestions"]=related_courses
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

#task 2


class description(BaseModel):
    description:str
@app.post("/jobDescriptionScore")
def jobDescription(req:description):
    score=calculate_description_score(req.description)
    return score

@app.post("/interviewer/topResumes")
# def topResumes(req:description):
#     text=extract_text("resumes/tamil.pdf")
#     # print(text)
#     return comparison_parsing(text,description)

async def topResumes(req:description):
    def do_resume_parsing(text, return_dict):
        return_dict['resume'] = Resume_parsing(text)

    def do_description_parsing(description, return_dict):
        return_dict['description'] = description_parsing(description)

    text =extract_text("resumes/tamil.pdf")
    # print(text)
    with Manager() as manager:
        return_dict = manager.dict()
        p1 = Process(target=do_resume_parsing, args=(text, return_dict))
        p2 = Process(target=do_description_parsing, args=(req.description, return_dict))

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



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
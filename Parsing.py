from utils import gemini_json_response,skill_compare
from ATS import calculateScore

def Resume_parsing(resumeDetails):
    prompt='''Your task is to parse the resume details and give a json format which can be readily converted into dict using json.loads in python and if there is no relevent information found then use a empty string("").And don\'t use backticks or other special symbols in the output. The output must be in the below format 
    {{"Contact_information":{{"Name":"", "email":"", "phone":"", "Linkedin":"", "gitHub":""}},
    "Resume_summary":"mandatory field",
    "Working_experience" :[{{"Organization_name":"","role":"", "years_of_experience":"Always convert it into a single number in the year not in months"}}] (if available),
    "Projects":[{{"Name":"","description":"","tech_stack":""}}],
    "Certifications":[""] (if available),
    "Education" : [{{"Institution_name":"","Degree":"", "Marks":"" ,"Completion_year":""}}],
    "Achievements":[""](if avaliable),
    "Hard_skills":[""](always must be less than 3 words),
    "Soft_skills":[""](always must be less than 3 words),
    "Location":"",
    "Languages":"" }}
    '''
    text=f"The resume detail is :{resumeDetails}"
    # print(prompt)
    return gemini_json_response(0,prompt,text)


def find_number(string):
    for word in string.split(" "):
        if(word.isdigit()):
            return int(word)
    return 0
            
def has_number(string):
     return any(char.isdigit() for char in string)

def find_words_in_string(string,words):
    string=string.lower()
    for word in words:
        if(string.find(word.lower())>=0):
            return word
    return ""

def description_parsing(description):
    # parsed_info=gemini_json_response(0,'''You are a Job description parser. Task: Extract the information from the given description in a json format, which is readily converted into dict in python using the json.loads method.
    #                             Conditions: 1.The output must not contain any backticks or special characters
    #                             2. if there is no relevent information found then use a empty string(""),
    #                             3. if there is any number words then convert it into digit
    #                             4. Don't use new words other than the word in the given description
    #                             5. The Must_have_skills and the Nice_to_have_skills should always be less than 3 words
    #                             6. the output format must be like
    #                             {{"Job_title":"",
    #                             "Must_have_skills":[""](always must be a less than 3 words),
    #                             "Experience":"",
    #                             "Roles_and_responsibilities":"",
    #                             "Salary":"",
    #                             "Location":"",
    #                             "Nice_to_have_skills":"",
    #                             "Contact":""}}''',
    #                             f"The job description is :{description}")
    parsed_info=gemini_json_response(0,"""Your task is to parse the Job description and give a json format which can be readily converted into dict using json.loads in python and if there is no relevent information found then use a empty string("").And don\'t use backticks or other special symbols in the output. If there is any number words then convert it into digit. The output must be in the below format 
      {{"Job_title":"",
        "Must_have_skills":["always must be a less than 3 words"],
        "Experience":"Include the number without any special characters",
        "Roles_and_responsibilities":"",
        "Salary":"",
        "Location":"",
        "Nice_to_have_skills":["always must be less than 3 words"],
        "Contact":""
        "Qualification":""}}""",f"The Job description is :{description}")
    parsed_info["Timing"]=find_words_in_string(description,["full time","full-time","fulltime","part time","parttime","part-time"])
    parsed_info["Job_type"]=find_words_in_string(description,["onsite","on site","on-site","remote","hybrid","work from home"])

    # print(parsed_info)
    return parsed_info

def calculate_description_score(description):
    parsed_info=description_parsing(description)

    if parsed_info==None:
        return "Something went wrong, please try again."
    total_no_skills=len(parsed_info["Must_have_skills"])
    print(parsed_info["Must_have_skills"])
    score=0
    missing=[]
    if(len(parsed_info["Job_title"])>0):
        score+=5
    else:
        missing.append("Including the e_skills")
    if(total_no_skills>0):
        skills_score=total_no_skills*5
        if skills_score>=20:
            score+=20 
        else:
            score+=skills_score
            missing.append(f"Please include atleast 4 must have skills, We found only {total_no_skills} skills")
    else:
        missing.append("Including the Must have skill is a good practice")
    if(len(parsed_info["Experience"])>0):
        if has_number(parsed_info["Experience"]):
            score+=15
        else:
            score+=13
            missing.append("It is recommended to give the experience in number")
    else:
        missing.append("Experience")
    if(len(parsed_info["Roles_and_responsibilities"])>0):
        score+=12
    else:
        missing.append("Providing the roles and responsibilities is a good practice")
    if(len(parsed_info["Salary"])>0):
        if has_number(parsed_info["Salary"]):
            score+=11
        else:
            score+=7
            missing.append("It is recommended to give the salary in number")
    else:
        missing.append("Including the Salary package is a good practice")
    if(len(parsed_info["Timing"])>0):
        score+=8
    else:
        missing.append("Including the timing like (full time, part time) is a good practice")
    if(len(parsed_info["Location"])>0):
        score+=7
    else:
        missing.append("Including the Location is a good practice")
    if(len(parsed_info["Nice_to_have_skills"])>0):
        score+=6
    else:
        missing.append("Including the additional skills other then the required skill is a good practice")
    if(len(parsed_info["Job_type"])>0):
        score+=6
    else:
        missing.append("Including the job type like (onsite,remote or hybrid) is a good practice")
    if(len(parsed_info["Contact"])>0):
        score+=5
    else:
        missing.append("Including the contact details is a good practice")
    if(len(parsed_info["Qualification"])>0):
        score+=5
    else:
        missing.append("Including the Qualification details is a good practice")

    return {"score":score,"Suggestions_to_improve":missing}

def parsing_resume_job_description(resume,description):
    # print(resume)
    # print(description)
    score_info={}
    total=0
    resume_skills=resume["Hard_skills"]
    resume_skills.extend(resume["Soft_skills"])

    score=len(skill_compare(resume_skills,description["Must_have_skills"])["match"])*5
    score_info["Must_have_skills"]=score
    total+=score

    score=len(skill_compare(resume_skills,description["Nice_to_have_skills"])["match"])*2.5

    score_info["Nice_to_have_skills"]=score
    total+=score
    score=0
    expected_experience=find_number(description["Experience"])
    no_of_matching_qualifications=0
    if expected_experience>0:
        actual_experience=0
        for works in resume["Working_experience"]:
            if(works["Degree"]==description["Qualification"]):
                no_of_matching_qualifications+=1
            actual_experience+=int(works["years_of_experience"])
        experience_difference=actual_experience-expected_experience
        
        score_info["Qualification"]=no_of_matching_qualifications*3
        total+=no_of_matching_qualifications*3

        if(experience_difference>0):
            if(experience_difference==0):
                score+=2
            score+=experience_difference*2
    score_info["Experience"]=score
    total+=score

    ats=calculateScore(resume)["ats_score"]
    score_info["ats_score"]=round(ats/10,2)
    total+=round(ats/10,2)
    if(description["Location"]!='' and  description["Location"]==resume["Location"]):
        score_info["location"]=2.5
        total+=2.5
    
    score_info["Total"]=total

    return score_info

def comparison_parsing(resume,description):
    result=gemini_json_response(0,"""Task: Calculate a score for the resume using a job description.
                         conditions for scoring:
                         1. Each matching skill in the Must_have_skills with the job description carries 5 points
                         2. Each matching skill in the Nice_to_have_skills with the job description carries 2.5 points
                         3. If the experience asked in the description matches with resume then give 2 points, and if the resume has extra years of experience than need, then give 2 points for each extra years
                         4. If the location is mensioned in the description and if it matches then give 2.5 points 
                         The output must be in a json format with the key as string and value as number, which is readily converted into dict in python using the json.loads method with the below format:
                         {{"Must_have_skill":,"Nice_to_Have_skill":,"Experience":,"Location":,"Total":}}
                          ""","The resume detail is {}\nThe job description is {}".format(resume,description))
    return result
    

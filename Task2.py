from utils import gemini_json_response

def has_number(string):
     return any(char.isdigit() for char in string)

def find_score(description):
    parsed_info=gemini_json_response(0,'''You are a Job description parser. Task: Extract the information from the given description in a json format, which is readily converted into dict in python using the json.loads method.
                                Conditions: 1.The output must not contain any backticks or special characters
                                2. if there is no relevent information found then use a empty string(""),
                                3. if there is any number words then convert it into digit
                                4. Don't use new words other than the word in the given description
                                5. the output format must be like
                                {"Job_title":"",
                                "Must_have_skills":[""],
                                "Experience":"",
                                "Roles_and_responsibilities":"",
                                "Salary":"",
                                "Timing": ""(means the working timing either full time or part time),
                                "Location":"",
                                "Nice_to_have_skills":"",
                                "Job_type": ""(mean where to work either from home or office),
                                "Contact":""}''',
                                f"The job description is :{description}")
    
    total_no_skills=len(parsed_info["Must_have_skills"])
    if(parsed_info==None):
        return 0
    score=0
    missing=[]
    if(len(parsed_info["Job_title"])>0):
        score+=5
    else:
        missing.append("Must_have_skills")
    if(total_no_skills>0):
        skills_score=total_no_skills*5
        if skills_score>=20:
            score+=20 
        else:
            score+=skills_score
            missing.append(f"Please include atleast 4 must have skills, We found only {total_no_skills} skills")
        print(score)
    else:
        missing.append("Including the Must have skill is a good practice")
    if(len(parsed_info["Experience"])>0):
        if has_number(parsed_info["Experience"]):
            score+=15
        else:
            score+=10
            missing.append("It is recommended to give the experience in number")
    else:
        missing.append("Experience")
    if(len(parsed_info["Roles_and_responsibilities"])>0):
        score+=12
    else:
        missing.append("Providing the roles and responsibilities is a good practice")
    if(len(parsed_info["Salary"])>0):
        if has_number(parsed_info["Salary"]):
            score+=12
        else:
            score+=8
            missing.append("It is recommended to give the salary in number")
    else:
        missing.append("Salary")
    if(len(parsed_info["Timing"])>0):
        score+=8
    else:
        missing.append("Including the timming like (full time, part time) is a good practice")
    if(len(parsed_info["Location"])>0):
        score+=8
    else:
        missing.append("Including the LOcation is a good practice")
    if(len(parsed_info["Nice_to_have_skills"])>0):
        score+=7
    else:
        missing.append("Including the additional skills other then the required skill is a good practice")
    if(len(parsed_info["Job_type"])>0):
        score+=7
    else:
        missing.append("Including the job type like (onsite,remote or hybrid) is a good practice")
    if(len(parsed_info["Contact"])>0):
        score+=6
    else:
        missing.append("Including the contact is a good practice")
    print(missing)
    return {"score":score,"Suggestions_to_improve":missing}


from utils import gemini_json_response


def Resume_parsing(resumeDetails):
    prompt='Your task is to parse the resume details and give a json format which can be readily converted into dict using json.loads in python and if there is no relevent information found then use a empty string(""),. The output must be in the below format {{"Contact_information":{{"Name":"", "email":"", "phone":"", "Linkedin":"", "gitHub":""}},"Resume_summary":"mandatory field","Working_experience" :[{{"Organization_name":"","role":"", "years_of_experience":"Always convert it into a single number in the year not in months"}}] (if available),"Projects":[{{"Name":"","description":"","tech_stack":""}}],"Certifications":[""] (if available),"Education" : [{{"Institution_name":"","Degree":"", "Marks":"" ,"Completion_year":""}}],"Achievements":[""](if avaliable),Hard_skills":[""],"Soft_skills":[""] }}. And don\'t use backticks or other special symbols in the output.'
    text=f"The resume detail is :{resumeDetails}"
    # print(prompt)
    return gemini_json_response(0,prompt,text)


def has_number(string):
     return any(char.isdigit() for char in string)

def find_words_in_string(string,words):
    string=string.lower()
    for word in words:
        if(string.find(word.lower())>=0):
            return word
    return ""

def description_parsing(description):
    parsed_info=gemini_json_response(0,'''You are a Job description parser. Task: Extract the information from the given description in a json format, which is readily converted into dict in python using the json.loads method.
                                Conditions: 1.The output must not contain any backticks or special characters
                                2. if there is no relevent information found then use a empty string(""),
                                3. if there is any number words then convert it into digit
                                4. Don't use new words other than the word in the given description
                                5. the output format must be like
                                {{"Job_title":"",
                                "Must_have_skills":[""],
                                "Experience":"",
                                "Roles_and_responsibilities":"",
                                "Salary":"",
                                "Location":"",
                                "Nice_to_have_skills":"",
                                "Contact":""}}''',
                                f"The job description is :{description}")
    parsed_info["Timing"]=find_words_in_string(description,["full time","full-time","fulltime","part time","parttime","part-time"])
    parsed_info["Job_type"]=find_words_in_string(description,["onsite","on site","on-site","remote","hybrid","work from home"])

    print(parsed_info)
    return parsed_info

def calculate_description_score(description):
    parsed_info=description_parsing(description)

    if parsed_info==None:
        return "Something went wrong, please try again."
    total_no_skills=len(parsed_info["Must_have_skills"])
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
            score+=12
        else:
            score+=8
            missing.append("It is recommended to give the salary in number")
    else:
        missing.append("Including the Salary package is a good practice")
    if(len(parsed_info["Timing"])>0):
        score+=8
    else:
        missing.append("Including the timing like (full time, part time) is a good practice")
    if(len(parsed_info["Location"])>0):
        score+=8
    else:
        missing.append("Including the Location is a good practice")
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
        missing.append("Including the contact details is a good practice")

    return {"score":score,"Suggestions_to_improve":missing}
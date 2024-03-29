import warnings
from io import BytesIO
from dotenv import dotenv_values
import re
import pdf2image
import json
import pytesseract
import PyPDF2
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core._api.deprecation import LangChainDeprecationWarning

config = dotenv_values(".env")
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

def gemini_json_response(count,prompt,text):
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=config["GEMINI_API_KEY"])
    prompt+="{text}"

    # If you have local model then use this commented lines
    # config = {'max_new_tokens': 4096, 'context_length': 4096, 'temperature':0.1}
    # llm = CTransformers(model="./models/gemma-7b.gguf", model_type="text-generator",temperature=0.1,config=config)

    tweet_prompt = PromptTemplate.from_template(prompt)
    tweet_chain = LLMChain(llm=llm, prompt=tweet_prompt, verbose=False)

    try:
        response = tweet_chain.run(text=text)
        # print(response)
        obj=json.loads(response)
        # print(obj)
    except Exception as e:
        print(e)
        if count < 5:
            return gemini_json_response(count+1,prompt,text)
        else:
            return None
    return obj

def get_resume_information(resumeDetails):
    prompt='''Your task is to parse the resume details and give a json format which can be readily 
            converted into dict using json.loads in python and if there is no relevent information 
            found then use a empty string(""),. The output must be in the below format 
            "basicInfo": {{"name" : "", location : "", "email" : "", "gitHub" : ""}},
            "resumeHeadline":"mandatory field",
            "summary" : "", 
            "workingExperience" :[{{"Organization_name":"","role":"", "years_of_experience":"date or number"}}] (if available),
            "topSkills":[""](tools, frameworks, libraries, programming languages only),
            "education" : [{{"Institution_name":"","Degree":"", "Marks":"" ,"Completion_year":""}}],"Achievements":[""](if avaliable),
            "certifications":[""] (if available),
            "totalYearsOfExperience" : "Always convert it into a single number in the year not in months"
            }}. And don\'t use backticks or other special symbols in the output.'''
    text=f"The resume detail is :{resumeDetails}"
    return gemini_json_response(0,prompt,text)

def get_description_information(jobDescription):
    prompt='''Your task is to parse the job description details and give a json format which can be readily 
            converted into dict using json.loads in python and if there is no relevent information 
            found then use a empty string(""),. The output must be in the below format 
            {{"jobPosition":"mandatory field",
            "mustHaveSkills":[""](tools, frameworks, libraries only),
            "Summary" : "", 
            "yearsOfExperienceRequired" : "" (number only),
            "niceToHaveSkills":[""] (tools, frameworks, libraries only),
            "jobLocation"
            "streamOfEducation" : "" (if available),
            }}. And don\'t use backticks or other special symbols in the output.'''
    text=f"The Description detail is :{jobDescription}"
    return gemini_json_response(0,prompt,text)

# Parse text from binary data(pdf)
def extract_text(file):
    result = ""
    is_image = False
    pdfReader = PyPDF2.PdfReader(BytesIO(file))

    for pg in range(0, len(pdfReader.pages)):
        result += pdfReader.pages[pg].extract_text()

    if len(result) <= 0:
        print("It is an image resume")
        is_image = True
        images = pdf2image.convert_from_bytes(file)

        for pg, img in enumerate(images):
            result += pytesseract.image_to_string(img)

    return {"text": result, "is_image": is_image}

# Compare skills in description and user profile
def skill_compare(skills1, skills2):
    matching_skills = []
    not_match_skills = []
    for index, skill in enumerate(skills1):
        skills1[index] = skill.replace(" ", "").replace("-", "").replace(".", "").lower()
    skills2 = list(map(str.lower, skills2))
    for skill in skills2:
        skill_formated = skill.replace(" ", "").replace("-", "").replace(".", "").lower()
        if skill_formated in skills1:
            matching_skills.append(skill)
        else:
            not_match_skills.append(skill)
    return {"matchingSkills": matching_skills, "notMatchingSkills": not_match_skills}

# Skills Review
def generate_upskilling_paragraph(skills):
    if not skills:
        return "No specific skills to focus on for upskilling. However, continuous learning and professional development are always beneficial. Consider exploring new technologies or expanding your existing knowledge to stay competitive in the job market."
    
    skills_str = ", ".join(skills[:-1]) + ", and " + skills[-1] if len(skills) > 1 else skills[0]
    
    paragraph = f"In order to improve your prospects for recruitment, it's advisable to focus on enhancing your skills in the areas where you currently have gaps. "
    paragraph += f"The skills listed below are particularly important in this regard: {skills_str}. "
    paragraph += f"By investing time and effort into upskilling yourself in these areas, you can significantly increase your chances of securing desirable job opportunities."
    
    return paragraph

# Headline
def headline_match(headline, jobPosition):
    jobPosition_formatted = jobPosition.replace(" ", "").replace("-", "").replace(".", "").lower()
    headline_formatted = headline.replace(" ", "").replace("-", "").replace(".", "").lower()

    # Length checking
    headlineScore = 0
    if len(headline.split(" ")) < 6:
        headlineScore += len(headline.split(" "))/2
        lengthSuggestion = 'Good LinkedIn headlines are 6-12 words and take advantage of the 120 character limit.'
    else :
        headlineScore += 5
        lengthSuggestion = 'Length of headline is good.'

    # Special characters checking
    special_characters_count = sum(1 for char in headline if not char.isalnum())
    if special_characters_count > 2:
        headlineScore += 1
        specialCharactersSuggestion = "Your headline contains more than 2 special characters. Consider simplifying it for better readability."
    else:
        headlineScore += 5
        specialCharactersSuggestion = "Number of special characters in headline is acceptable."

    # Headline Match Checking
    if headline_formatted in jobPosition_formatted or jobPosition_formatted in headline_formatted:
        headlineScore += 10
        objective = f"Fantastic job including '{jobPosition}' in your headline! This simple step can greatly improve your visibility to recruiters, making it easier for them to find you. Keep up the excellent work!"
    else:
        headlineScore += 2
        objective = f"We recommend including the exact title '{jobPosition}' in your headline. Recruiters frequently search by job titles and exact phrasing ranks higher in search results."                                                                                  
    
    return {"length" : lengthSuggestion ,
            "headline": objective,
            "specialCharacters" : specialCharactersSuggestion,
            "headlineScore" : headlineScore,
            "sampleHeadline" : jobPosition}

# Education
def education_match(resumeDegree, descriptionDegree):
    matching_degrees = []
    educationScore = 0
    description_degree_formatted = descriptionDegree.replace(" ", "").replace("-", "").replace(".", "").lower()
    for degree_info in resumeDegree:
        resume_degree_formatted = degree_info['Degree'].replace(" ", "").replace("-", "").replace(".", "").replace(",", "").lower()
        if description_degree_formatted in resume_degree_formatted or resume_degree_formatted in description_degree_formatted:
            if description_degree_formatted != "" and resume_degree_formatted != "" :
               matching_degrees.append(descriptionDegree)
               educationScore = 10
    return {"matchingDegrees" : matching_degrees, "educationScore" : educationScore}

# Find Profile Experience
def extract_years_from_experience(text):
    start_index = text.find("Experience")
    end_index = text.find("Education")
    experience_text = text[start_index:end_index]

    # RE to find years
    pattern1 = r'(\d+)\s+years?'
    pattern2 = r'(\d+)\s+months?'

    # Find all matches of the pattern in the experience text
    matches1 = re.findall(pattern1, experience_text)
    matches2 = re.findall(pattern2, experience_text)

    # Convert the matched years to integers and sum them up
    total_years = sum(int(year) for year in matches1)
    total_months = sum(int(month) for month in matches2)
    return round(float(total_years) + float(total_months/12), 1)

# Combined function
def complete_analysis(resume, jobDescription):

    score = 0.0;

    # Get resume and Job description information
    resumeInfo = get_resume_information(resume)
    descriptionInfo = get_description_information(jobDescription)
    # print(resumeInfo)
    # print(descriptionInfo)

    # Perform skill comparison
    mustHave = skill_compare(resumeInfo["topSkills"], descriptionInfo["mustHaveSkills"])
    niceToHave = skill_compare(resumeInfo["topSkills"], descriptionInfo["niceToHaveSkills"])
    skillScore = len(mustHave["matchingSkills"])/len(mustHave["notMatchingSkills"]) * 50
    skill_comparison = {
        "mustHave": mustHave,
        "niceToHave": niceToHave
    }
    skillsReview = generate_upskilling_paragraph(mustHave["notMatchingSkills"])

    # Experience matching
    required_experience = descriptionInfo["yearsOfExperienceRequired"]
    profile_experience = extract_years_from_experience(resume)
    if float(profile_experience) < float(required_experience) :
        experienceScore = float(profile_experience)/float(required_experience)*10
        experience_matching = f"The job requires a minimum of {required_experience} years of hands-on experience, demonstrating proficiency in relevant skills and tasks. But you have only {profile_experience} years of experience."
    else :
        experienceScore = 20
        experience_matching = "The profile fulfills the criteria with their experience."
    score += experienceScore

    # Perform headline matching
    headline_matching = headline_match(resumeInfo["resumeHeadline"], descriptionInfo["jobPosition"])
    score += headline_matching["headlineScore"]
    
    # Perform education matching
    education_matching = education_match(resumeInfo["education"], descriptionInfo["streamOfEducation"])
    score += education_matching["educationScore"]

    # Check Name and location
    name = resumeInfo["basicInfo"]["name"]
    location = resumeInfo["basicInfo"]["location"]
    basicInfoScore = 0;
    if name :
        basicInfoScore += 5
        nameReview = "First and last name provided."
    else :
        nameReview = "Please provide you name in the profile"
    if location :
        basicInfoScore += 5
        locationReview = "You have included your location. It helps recruiters find you - more than 30% of recruiters will search by location."
    else :
        locationReview = "Please update your Location in the profile. Adding a specific location and country helps recruiters find you - more than 30% of recruiters will search by location."
    score += basicInfoScore

    return {
        "score" : score,
        "basicInfo": {"name" : nameReview , "location" : locationReview, "basicInfoScore" : basicInfoScore},
        "headline": headline_matching,
        "experience" : {"experienceReview" : experience_matching, "experienceScore" : experienceScore},
        "skills": {"skillsMatching" : skill_comparison, "skillsReview" : skillsReview, "skillScore" : skillScore},
        "education": education_matching
    }
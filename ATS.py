from utils import gemini_json_response


def calculateScore(resume):
    total = []
    missedFields=set()
    ats_score =0.0
    # Initial Scores

    contact_score = 0
    resume_objective_score = 0
    work_experience_score = 0
    education_score = 0
    project_score = 0
    skills_score = 0

    # Default Reviews

    contact_review = """You have provided all the necessary contact information in your resume, 
                    ensuring easy accessibility for potential employers. Well done on ensuring 
                    thorough communication channels!"""
    
    resume_objective_review = """The resume objective you've included succinctly outlines your career goals, 
                            providing recruiters with a clear understanding of your aspirations. It's a nice 
                            touch to personalize your application."""
    
    work_experience_review = """You have provided the necessary details about your work experience. 
                            This section offers insight into your professional journey. 
                            Nicely presented with relevant details that showcase your expertise and accomplishments."""
    
    education_review = """Your educational background is neatly displayed, adding depth to your qualifications. 
                        It's good to see your academics highlighted effectively. It is always good to add 
                        recent two educational qualifications"""
    
    project_review = """You have included sufficient details about your projects in your resume. This section is informative, 
                      shedding light on your practical skills and accomplishments. Well-described projects offer a clear 
                      picture of your capabilities and contributions."""
    
    skills_review = """You have included a good variety of skills in your resume. Your skills section is impressive with a 
                    wide range of competencies crucial for the role. It's evident that you possess a versatile skill set 
                    that aligns well with the job requirements, making you a strong candidate for consideration."""

    
    # Contact Section

    contactInfo = resume.get("Contact_information")
    missed_contact_fields = set()

    for key, value in contactInfo.items():
        if key in ["Name", "email", "phone", "Linkedin", "gitHub"] :
            if value is not None and value != "":
                    contact_score += 10 / 4
            else: 
                missedFields.add(key + " in contact section")
                missed_contact_fields.add(key)
                contact_review = """Make sure you provide the following fields in the Contact section: """ + ", ".join(missed_contact_fields) + """. Including comprehensive contact information ensures seamless communication between you and potential employers, facilitating swift follow-ups and interview scheduling, ultimately expediting the hiring process and enhancing your chances of securing opportunities."""  
        else :
            continue
    contact = {}     
    contact["name"] = "Contact"  
    contact["score"] = round(contact_score * 10, 1)
    contact["description"] = contact_review
    total.append(contact)
    ats_score += contact_score   

    # Resume Objective Section
            
    resumeObjective = resume.get("Resume_summary")
    if resumeObjective is not None:
        resume_objective_score += 10
    else:
        missedFields.add("Resume Objective")
        resume_objective_review = """Make sure you include the resume objective/summary in your resume. Enhance your resume 
                                objective by aligning it with the specific job role and company culture, showcasing your enthusiasm 
                                and commitment towards contributing to the organization's success."""
    objective = {}
    objective["name"] = "Objective"
    objective["score"] = round(resume_objective_score*10,1)
    objective["description"] = resume_objective_review
    total.append(objective)
    ats_score += resume_objective_score

    # Work Experience/Internships
    workExperience = resume.get("Working_experience")
    missed_experience_fields = set()
    experience = {}
    if(workExperience):
        total_jobs = len(workExperience)
        score_per_job = 15 / total_jobs if total_jobs > 0 else 0
        for job in workExperience:
            job_score = 0
            for key, value in job.items():
                if key in ["Organization_name", "role", "years_of_experience"] and value is not None and value != "":
                    job_score += score_per_job / 3
                else :
                    missedFields.add(key + " in Work Experience section")
                    missed_experience_fields.add(key)
                    work_experience_review = """Make sure you update the following fields for each organization you have worked in: """ + ", ".join(missed_experience_fields) + """. Include quantifiable achievements and results to substantiate your impact in previous roles, offering tangible evidence of your capabilities and demonstrating your potential value to prospective employers."""

            work_experience_score  += job_score
            ats_score += job_score
        experience["name"] = "Experience"
        experience["score"] = round((work_experience_score/15)*100, 1)
        experience["description"] = work_experience_review
    else :
        experience["name"] = "Experience"
        experience["score"] = 0
        experience["description"] = "The resume misses the experience section. To gain experience in your field as a fresher, consider internships or volunteer work in relevant organizations. Additionally, seek out projects or contribute to open-source initiatives to build practical skills and showcase your expertise."
    total.append(experience)

    # Education
    Education = {}
    Education["name"] = "Education"
    education = resume.get("Education")
    total_educations = len(education)
    missed_education_fields = set()

    if total_educations > 3 or total_educations == 0:
        Education["score"] = 0
        Education["description"] = "Please include any two recent educational qualifications"
    else:
        score_per_education = 5 / total_educations if total_educations > 0 else 0
        for degree in education:
            for key, value in degree.items():
                if key in ["Institution_name", "Degree", "Marks", "Completion_year"]:
                    if value is not None and value != "":
                        education_score += score_per_education / 5
                    else:
                        missedFields.add(key + " in education section")
                        missed_education_fields.add(key)
                        education_review = "Please ensure you update the following fields in the Education section to provide comprehensive information: " + ", ".join(missed_education_fields) + "."
                else :
                    continue
         
        Education["score"] = round(education_score * 20, 1)
        Education["description"] = education_review
        ats_score += education_score

    total.append(Education)


    Project = {}
    Project["name"] = "Project"
    project = resume.get("Projects")
    total_projects = len(project)
    missed_project_fields = set()

    score_per_project = 15 / total_projects if total_projects > 0 else 0

    for proj in project:
        for key, value in proj.items():
            if key in ["Name", "description", "tech_stack"] and value is not None and value != "":
                project_score += score_per_project / 3
            else:
                missedFields.add(key + " in project section")
                missed_project_fields.add(str(key).upper().replace("_", " "))
                project_review = """Please include essential details such as project name, brief description, and technologies utilized. 
                    Additionally, provide insights into project challenges, methodologies, and achieved outcomes, 
                    demonstrating problem-solving abilities, creativity, and project success. 
                    Missing fields: {}""".format(', '.join(missed_project_fields))
                
    Project["score"] = round((project_score / 15) * 100, 1)
    Project["description"] = project_review
    ats_score += project_score
    total.append(Project)

    # Skills
    Skills = {}
    skills_score = 0
    Skills["name"] = "Skills"
    skills = resume.get("Hard_skills")
    if len(skills) > 5 : skills_score = 20
    elif (len(skills) > 3) : skills_score = 15
    elif (len(skills) > 1) : skills_score = 10
    elif (len(skills) == 1) : skills_score = 5
    else : skills_review = """The provided skills are very less in number try to add more skills. Prioritize skills that are directly 
                            relevant to the job description and industry trends, emphasizing proficiency levels and any specialized 
                            expertise or certifications you possess to distinguish yourself as a top candidate."""
    
    Skills["score"] = round(skills_score*5, 1)
    Skills["description"] = skills_review
    total.append(Skills)
    ats_score += skills_score

    # Optional Sections - Certifications/Achievements/PDF resume/Soft Skills 
    # Image or PDF
    Format = {}
    Format["name"] = "Format"
    isImage = resume.get("is_image")
    if isImage == True:
        Format["score"] = 0
        Format["description"] = """You have uploaded an image resume which would fail in 
                                many ATS recruitment process. Please have a resume in PDF format"""
    else : 
        Format["score"] = 100
        Format["description"] = """Great that you have uploaded a PDF format of your resume, 
                                which can qualify in most of the ATS recruitment processes"""
        ats_score += 5
    total.append(Format)

    # Certifications
    Certifications = {}
    Certifications["name"] = "Certifications"
    if len(resume.get("Certifications")) :
        Certifications["score"] = 100
        Certifications["description"] = "Great that you have included certificates in your resume. It showcases the specific knowledge and skills you've acquired during your certification. This enables recruiters to assess your proficiency in areas directly related to the position you're applying for."
        ats_score += 2.5
    else :
        Certifications["score"] = 0
        Certifications["description"] = """Adding a section dedicated to certificates showcases the specific knowledge and skills you've 
                                        acquired during your certification. This enables recruiters to assess your proficiency in areas 
                                        directly related to the position you're applying for."""
        missedFields.add("Certifications")
    total.append(Certifications)

    # Achievements
    Achievements = {}
    Achievements["name"] = "Achievements"
    if len(resume.get("Achievements")) :
        Achievements["score"] = 100
        Achievements["description"] = "Great that you have included achievements in your resume, providing tangible evidence of your capabilities and contributions, thereby distinguishing you as a high-achieving candidate with a track record of success."
        ats_score += 2.5
    else :
        Achievements["score"] = 0
        Achievements["description"] = " Highlight significant accomplishments, such as awards, recognitions, or milestones attained in your career, providing tangible evidence of your capabilities, leadership, and contributions to previous employers, thereby distinguishing you as a high-achieving candidate with a track record of success."
    total.append(Achievements)
    
    # Soft Skills
    SoftSkills = {}
    SoftSkills["name"] = "Soft Skills"    
    total_softSkills = len(resume.get("Soft_skills"))
    if total_softSkills > 1 and total_softSkills < 5 :
        SoftSkills["score"] = 100
        SoftSkills["description"] = "Great that you have added soft skills in your resume, which is a great add on to the resume"
    elif total_softSkills == 1 :
        SoftSkills["score"] = 50
        SoftSkills["description"] = "Please Include two to five soft skills. By highlighting your soft skills, you can demonstrate your ability to work effectively in a team, communicate clearly, solve problems, and adapt to changing situations."
    else :
        SoftSkills["score"] = 0
        SoftSkills["description"] = """Soft skills are personal attributes and interpersonal abilities that complement 
                                    your technical skills and are often essential for success in the workplace. 
                                    By highlighting your soft skills, you can demonstrate your ability to work 
                                    effectively in a team, communicate clearly, solve problems, and adapt to changing situations."""
        missedFields.add("Softs kills")
    total.append(SoftSkills)
    mandatorySectionsScore = contact["score"] + objective["score"] + experience["score"] + Project["score"] + Skills["score"] + Education["score"]
    if(mandatorySectionsScore >= 450) :
        ats_score += 10
    elif mandatorySectionsScore >= 350 :
        ats_score += 5
    return {"total":total,"missedFields":missedFields,"ats_score":ats_score}


def getReport(resume):
    resumeReport = calculateScore(resume)
    missedFields=resumeReport["missedFields"]
    ats_score=resumeReport["ats_score"]
    fieldsToAdd = ""
    missedFields_str = "Just ask the user to include the following fields in the resume and say the importance of only that fields."
    for i in missedFields:
        missedFields_str += " '"+ i + "',"
    if len(missedFields):
        fieldsToAdd = gemini_json_response(0,'''You are a resume optimization chatbot. The user will give some important fields that are missing in the resume. 
                                      Your response should include only these sections and how it would improve the resume. 
                                      The output should be in json as I am sending this api response text as a json response to the front end.
                                      It should not contain any special characters,underscore or numbers.Use camel case for fieldnames in json.
                                      Just include headings as field. he output should be in this format : 
                                      {{"Field Name" : "Importance of this field and recommend to add this section in one paragraph (four lines)"}}''',missedFields_str)
        # fieldsToAdd = json.loads(fieldsToAdd)
        # fieldsToAdd = json.dumps(fieldsToAdd)
        # print(fieldsToAdd)
    return {"ats_score" : round(ats_score, 1), "resumeReport" : resumeReport["total"], "fieldsToAdd" : fieldsToAdd}

from utils import gemini_json_response


def calculateScore(resume):
    total = []
    missedFields=set()
    ats_score =0.0
    # Initial Scores

    contactScore = 0
    resumeObjectiveScore = 0
    workExperienceScore = 0
    educationScore = 0
    projectScore = 0
    skillsScore = 0

    # Default Reviews

    contactReview = """You have provided all the necessary contact information in your resume, 
                    ensuring easy accessibility for potential employers. Well done on ensuring 
                    thorough communication channels!"""
    
    resumeObjectiveReview = """The resume objective you've included succinctly outlines your career goals, 
                            providing recruiters with a clear understanding of your aspirations. It's a nice 
                            touch to personalize your application."""
    
    workExperienceReview = """Great! You have provided the necessary details about your work experience. 
                            This section is thorough, offering insight into your professional journey. 
                            Nicely presented with relevant details that showcase your expertise and accomplishments."""
    
    educationReview = """Your educational background is neatly displayed, adding depth to your qualifications. 
                        It's good to see your academics highlighted effectively. It is always good to add 
                        recent two educational qualifications"""
    
    projectReview = """You have included sufficient details about your projects in your resume. This section is informative, 
                      shedding light on your practical skills and accomplishments. Well-described projects offer a clear 
                      picture of your capabilities and contributions."""
    
    skillsReview = """You have included a good variety of skills in your resume. Your skills section is impressive with a 
                    wide range of competencies crucial for the role. It's evident that you possess a versatile skill set 
                    that aligns well with the job requirements, making you a strong candidate for consideration."""

    
    # Contact Section

    contactInfo = resume.get("Contact_information")
    for key, value in contactInfo.items():
        if key in ["Name", "email", "phone", "linkedin"] and value is not None and value != "":
            contactScore += 10 / 5
        else : 
            missedFields.add(key + " in Contact section")
            contactReview = """Make Sure You Provide Name, email, phone, linkedIn in your contact section. Including comprehensive 
                            contact information ensures seamless communication between you and potential employers, 
                            facilitating swift follow-ups and interview scheduling, ultimately expediting the hiring process 
                            and enhancing your chances of securing opportunities."""
    contact = {}     
    contact["name"] = "Contact"  
    contact["score"] = round(contactScore*10,1)
    contact["description"] = contactReview
    total.append(contact)
    ats_score += contactScore

    # Resume Objective Section
            
    resumeObjective = resume.get("Resume_summary")
    if resumeObjective is not None and value != "":
        resumeObjectiveScore += 10
    else:
        missedFields.add("Resume Objective")
        resumeObjectiveReview = """Make sure you include the resume objective/summary in your resume. Enhance your resume 
                                objective by aligning it with the specific job role and company culture, showcasing your enthusiasm 
                                and commitment towards contributing to the organization's success."""
    objective = {}
    objective["name"] = "Objective"
    objective["score"] = round(resumeObjectiveScore*10,1)
    objective["description"] = resumeObjectiveReview
    total.append(objective)
    ats_score += resumeObjectiveScore

    # Work Experience/Internships
    workExperience = resume.get("Working_experience")
    total_jobs = len(workExperience)
    score_per_job = 15 / total_jobs if total_jobs > 0 else 0
    for job in workExperience:
        job_score = 0
        for key, value in job.items():
            if key in ["Organization_name", "role", "years_of_experience"] and value is not None and value != "":
                job_score += score_per_job / 3
            else :
                missedFields.add(key + " in Work Experience section")
                workExperienceReview = """Make sure you update the Organization name, role and years of experience/date of all 
                                        the organisations you have worked in. Include quantifiable achievements and results to 
                                        substantiate your impact in previous roles, offering tangible evidence of your capabilities 
                                        and demonstrating your potential value to prospective employers."""
        workExperienceScore  += job_score
        ats_score += job_score
    experience = {}
    experience["name"] = "Experience"
    experience["score"] = round((workExperienceScore/15)*100, 1)
    experience["description"] = workExperienceReview
    total.append(experience)

    # Education
    Education = {}
    Education["name"] = "Education"
    education = resume.get("Education")
    total_educations = len(education)
    if total_educations > 3 or total_educations == 0:
        Education["score"] = 0
        Education["description"] = "Please try to include any two recent educational qualifications"
    else:
        score_per_education = 5 / total_educations if total_educations > 0 else 0
        for degree in education:
            for key, value in degree.items():
                if key in ["Institution_name", "Degree", "Marks", "Completion_year"] and value is not None and value != "":
                    educationScore += score_per_education / 4
                else :
                    missedFields.add(key + " in Education section")
                    educationReview = "Make sure you update the Education name, degree, marks and years of graduation"
        Education["score"] = round(educationScore*20, 1)
        Education["description"] = educationReview
        ats_score += educationScore
    total.append(Education)   

    # Projects
    Project = {}
    Project["name"] = "Project"
    project = resume.get("Projects")
    total_projects = len(project)
    score_per_project = 15/total_projects if total_projects > 0 else 0
    for proj in project:
        for key, value in proj.items():
            if key in ["Name", "description", "tech_stack"] and value is not None and value != "":
                projectScore += score_per_project / 3
            else :
                missedFields.add(key + " of project in Project section")
                projectReview = """Make Sure you provide your project name, short description, and tech stacks used in it. 
                                Provide context around project challenges, methodologies employed, and outcomes achieved, 
                                showcasing your problem-solving skills, creativity, and ability to drive successful project outcomes."""
    
    Project["score"] = round((projectScore/15)*100, 1)
    Project["description"] = projectReview
    ats_score += projectScore
    total.append(Project)

    # Skills
    Skills = {}
    skillsScore = 0
    Skills["name"] = "Skills"
    skills = resume.get("Hard_skills")
    if len(skills) > 5 : skillsScore = 20
    elif (len(skills) > 3) : skillsScore = 15
    elif (len(skills) > 1) : skillsScore = 10
    elif (len(skills) == 1) : skillsScore = 5
    else : skillsReview = """The provided skills are very less in number try to add more skills. Prioritize skills that are directly 
                            relevant to the job description and industry trends, emphasizing proficiency levels and any specialized 
                            expertise or certifications you possess to distinguish yourself as a top candidate."""
    
    Skills["score"] = round(skillsScore*5, 1)
    Skills["description"] = skillsReview
    total.append(Skills)
    ats_score += skillsScore

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
    Cerifications = {}
    Cerifications["name"] = "Cerifications"
    if len(resume.get("Certifications")) :
        Cerifications["score"] = 100
        Cerifications["description"] = "Great that you have included certificates in your resume"
        ats_score += 2.5
    else :
        Cerifications["score"] = 0
        Cerifications["description"] = """Adding a section dedicated to certificates showcases the specific knowledge and skills you've 
                                        acquired during your certification. This enables recruiters to assess your proficiency in areas 
                                        directly related to the position you're applying for."""
        missedFields.add("Certifications")
    total.append(Cerifications)

    # Achievements
    Achievements = {}
    Achievements["name"] = "Achievements"
    if len(resume.get("Achievements")) :
        Achievements["score"] = 100
        Achievements["description"] = "Great that you have included achievements in your resume"
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
        SoftSkills["description"] = "Please Include two to five soft skills"
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
                                      {{"fieldName" : "Importance of this field and recommend to add this section in one paragraph (four lines)"}}''',missedFields_str)

    return {"ats_score" : round(ats_score, 1), "resumeReport" : resumeReport["total"], "fieldsToAdd" : fieldsToAdd}

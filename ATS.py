from utils import gemini_json_response


def calculateScore(resume):
    total = {}
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
        if key in ["Name", "email", "phone", "linkedin", "github"] and value is not None and value != "":
            contactScore += 10 / 5
        else : 
            missedFields.add(key + " in Contact section")
            contactReview = """Make Sure You Provide Name, email and mailID in your contact section. Including comprehensive 
                            contact information ensures seamless communication between you and potential employers, 
                            facilitating swift follow-ups and interview scheduling, ultimately expediting the hiring process 
                            and enhancing your chances of securing opportunities."""
            
    total["contactScore"] = contactScore
    total["contactReview"] = contactReview
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
        
    total["resumeObjectiveScore"] = resumeObjectiveScore
    total["resumeObjectiveReview"] = resumeObjectiveReview
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
    total["workExperienceScore"] = workExperienceScore
    total["workExperienceReview"] = workExperienceReview

    # Education
    
    education = resume.get("Education")
    total_educations = len(education)
    if total_educations > 3 or total_educations == 0:
        total["educationScore"] = 0
        total["educationReview"] = "Please try to include any two recent educational qualifications"
    else:
        score_per_education = 5 / total_educations if total_educations > 0 else 0
        for degree in education:
            for key, value in degree.items():
                if key in ["Institution_name", "Degree", "Marks", "Completion_year"] and value is not None and value != "":
                    educationScore += score_per_education / 4
                else :
                    missedFields.add(key + " in Education section")
                    educationReview = "Make sure you update the Education name, degree, marks and years of graduation"
        total["educationScore"] = educationScore
        total["educationReview"] = educationReview
        ats_score += educationScore
        
    # Projects
    
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
    
    total["projectScore"] = projectScore
    total["projectReview"] = projectReview
    ats_score += projectScore

    # Skills
    
    skills = resume.get("Hard_skills")
    if len(skills) > 5 : skillsScore = 20
    elif (len(skills) > 3) : skillsScore = 15
    elif (len(skills) > 1) : skillsScore = 10
    elif (len(skills) == 1) : skillsScore = 5
    else : skillsReview = """The provided skills are very less in number try to add more skills. Prioritize skills that are directly 
                            relevant to the job description and industry trends, emphasizing proficiency levels and any specialized 
                            expertise or certifications you possess to distinguish yourself as a top candidate."""
    
    total["skillsScore"] = skillsScore
    total["skillsReview"] = skillsReview
    ats_score += skillsScore

    # Optional Sections - Certifications/Achievements/PDF resume/Soft Skills 
    
    # Image or PDF
    isImage = resume.get("is_image")
    if isImage == True:
        total["formatReview"] = """You have uploaded an image resume which would fail in 
                                many ATS recruitment process. Please have a resume in PDF format"""
    else : 
        total["formatScore"] = 5
        total["formatReview"] = """Great that you have uploaded a PDF format of your resume, 
                                which can qualify in most of the ATS recruitment processes"""
        ats_score += 5
   
    # Certifications
    if len(resume.get("Certifications")) :
        total["certificateScore"] = 2.5
        total["certificateReview"] = "Great that you have included certificates in your resume"
        ats_score += 2.5
    else :
        total["certificateScore"] = 0.0
        total["certificateReview"] = """Adding a section dedicated to certificates showcases the specific knowledge and skills you've 
                                        acquired during your certification. This enables recruiters to assess your proficiency in areas 
                                        directly related to the position you're applying for."""
        missedFields.add("Certifications")

    # Achievements
    # if len(resume.get("Achievements")) :
    #     total["achievementsScore"] = 2.5
    #     total["achievementsReview"] = "Great that you have included achievements in your resume"
    #     ats_score += 2.5
    # else :
    #     total["achievementsScore"] = 0.0
    #     total["achivementsReview"] = " Highlight significant accomplishments, such as awards, recognitions, or milestones attained in your career, providing tangible evidence of your capabilities, leadership, and contributions to previous employers, thereby distinguishing you as a high-achieving candidate with a track record of success."
    
    # Soft Skills
    total_softSkills = len(resume.get("Soft_skills"))
    if total_softSkills > 1 and total_softSkills < 5 :
        total["softSkillsScore"] = 5
    elif total_softSkills == 1 :
        total["softSkillsScore"] = 2.5
        total["softSkillsReview"] = "Please Include two to five soft skills"
    else :
        total["softSkillsScore"] = 0
        total["softSkillsReview"] = """Soft skills are personal attributes and interpersonal abilities that complement 
                                    your technical skills and are often essential for success in the workplace. 
                                    By highlighting your soft skills, you can demonstrate your ability to work 
                                    effectively in a team, communicate clearly, solve problems, and adapt to changing situations."""
        missedFields.add("Softs kills")
    # print(ats_score)
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
        # fieldsToAdd = json.loads(fieldsToAdd)
        # fieldsToAdd = json.dumps(fieldsToAdd)
        # print(fieldsToAdd)
    return {"ats_score" : str(round(ats_score, 1)) + "%", "resumeReport" : resumeReport["total"], "fieldsToAdd" : fieldsToAdd}

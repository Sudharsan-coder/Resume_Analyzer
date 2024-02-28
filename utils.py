import time
from dotenv import dotenv_values

config = dotenv_values(".env")
import pdf2image
import json
import pytesseract
import PyPDF2
# from langchain_community.llms import CTransformers
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def gemini_json_response(count,prompt,text):
    print("Attempt ",count)
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
        if count<5:
            return gemini_json_response(count+1,prompt,text)
        else:
            return None
    return obj


def get_informations(resumeDetails):
    prompt='Your task is to parse the resume details and give a json format which can be readily converted into dict using json.loads in python and if there is no relevent information found then use a empty string(""),. The output must be in the below format {{"Contact_information":{{"Name":"", "email":"", "phone":"", "Linkedin":"", "gitHub":""}},"Resume_summary":"mandatory field","Working_experience" :[{{"Organization_name":"","role":"", "years_of_experience":"date or number"}}] (if available),"Projects":[{{"Name":"","description":"","tech_stack":""}}],"Certifications":[""] (if available),"Education" : [{{"Institution_name":"","Degree":"", "Marks":"" ,"Completion_year":""}}],"Achievements":[""](if avaliable),Hard_skills":[""],"Soft_skills":[""] }}. And don\'t use backticks or other special symbols in the output.'
    text=f"The resume detail is :{resumeDetails}"
    # print(prompt)
    return gemini_json_response(0,prompt,text)

def extract_text(path):
    pdfFileObj = open(path, 'rb')  #reading the file
    result=""
    is_image=False
    pdfReader = PyPDF2.PdfReader(pdfFileObj) 

    for pg in range(0,len(pdfReader.pages)):
        result+=pdfReader.pages[pg].extract_text()  #extracting text directly

    if (len(result)<=0):  # if no text found, use ocr
        print("It is an image resume")
        is_image=True
        pdfFileObj.seek(0)  
        images = pdf2image.convert_from_bytes(pdfFileObj.read())  #converting the file object into bytes 

        for pg, img in enumerate(images):
            result+=pytesseract.image_to_string(img) #extracting the text using the ocr

    pdfFileObj.close()

    return {"text":result,"is_image":is_image}

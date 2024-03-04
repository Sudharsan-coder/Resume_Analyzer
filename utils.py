import time
from dotenv import dotenv_values

config = dotenv_values(".env")
import pdf2image
import json
import pytesseract
import PyPDF2
from io import BytesIO

# from langchain_community.llms import CTransformers
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

def gemini_json_response(count,prompt,text):
    print("Gemini's {} attempt ".format(count+1))
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=config["GEMINI_API_KEY"])
    prompt+="{text}"

    # If you have local model then use this commented lines
    # config = {'max_new_tokens': 4096, 'context_length': 4096, 'temperature':0.1}
    # llm = CTransformers(model="./models/gemma-7b.gguf", model_type="text-generator",temperature=0.1,config=config)

    tweet_prompt = PromptTemplate.from_template(prompt)
    tweet_chain = LLMChain(llm=llm, prompt=tweet_prompt, verbose=False)
    try:
        # d=
        response = tweet_chain.run(text=text)
        # print(response)
        if(response[0]=="`"):
            obj=json.loads(response[7:-3])
        else:
            obj=json.loads(response)  

        # print(obj)
    except Exception as e:
        print(e)
        if count<4:
            obj=gemini_json_response(count+1,prompt,text)
            return obj
        else:
            return None
    return obj


def extract_text(contents):

    result=""
    is_image=False
    pdf = PyPDF2.PdfReader(BytesIO(contents))
    for pg in range(0,len(pdf.pages)):
        result+=pdf.pages[pg].extract_text()  #extracting text directly

    if (len(result)<=0):  # if no text found, use ocr
        print("It is an image resume")
        is_image=True
        images = pdf2image.convert_from_bytes(contents)  #converting the file object into bytes 

        for pg, img in enumerate(images):
            result+=pytesseract.image_to_string(img) #extracting the text using the ocr

    return {"text":result,"is_image":is_image}

def skill_compare(skills1,skills2):
    matching_skills=[]
    not_match_skills=[]
    for index,skill in enumerate(skills1):
        skills1[index]=skill.replace(" ","").replace("-","").replace(".","").lower()
    skills2=list(map(str.lower,skills2))
    for skill in skills2:
        skill=skill.replace(" ","").replace("-","").replace(".","").lower()
        if skill in skills1:
            matching_skills.append(skill)
        else:
            not_match_skills.append(skill)
    return {"match":matching_skills,"not_match":not_match_skills}
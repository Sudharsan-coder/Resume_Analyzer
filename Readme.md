## Initial setup

Install the below packages :

```
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```
Then create an virtual environment and activate it, then install the requirements
```
pip install -r requirements.txt
```

Create a .env file and place the gemini api key with the variable name of "GEMINI_API_KEY"

To start the server, run the server.py file
```
python3 server.py
```
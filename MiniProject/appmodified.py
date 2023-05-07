from flask import Flask, render_template, request
import string
import operator
import PyPDF2
from transformers import pipeline
import easyocr
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
c=0
summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="tf")
num_sent=100

#------------Flask Application---------------#

app = Flask(__name__)


@app.route('/speech', methods=['GET','POST'])
def original_speech_form():
	text=""
	if request.method=="POST":
		print("FORM DATA RECEIVED")
		# if file not in request.files:
		# 	return redirect(request.url)
		file=request.files["file"]
		# if file.filename=="":
		# 	return redirect(request.url)
		if file:
			recognizer=sr.Recognizer()
			audiofile=sr.AudioFile(file)
			with audiofile as source:
				data=recognizer.record(source)
			text=recognizer.recognize_google(data, key=None)
	summary = summarizer(text, max_length=1000, min_length=0, do_sample=False)[0]['summary_text']
	return render_template("speech.html", original_text = text, output_summary = summary)





@app.route('/url', methods=['GET','POST'])
def original_url_form():
	global num_sent
	title = "Url Summarizer"
	if 'url-open' in request.form:
		page=request.form['url-open']
		r = requests.get(page)
		soup = BeautifulSoup(r.content, 'html.parser')
		s = soup.find('div', class_='entry-content')
 		
		lines = soup('p')
		

		t=[]
		for line in lines:
			t.append(line.text)
		
		x=''.join(t)
		num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
		summary = summarizer(x, max_length=num_sent, min_length=0, do_sample=False)[0]['summary_text']
		if c==1:
			summary=""
	else:
		x=""
		summary=""
	return render_template("url.html", title = title, original_text = x, output_summary = summary, num_sentences = num_sent)




@app.route('/image', methods=['GET','POST'])
def original_image_form():
	global num_sent
	title = "Image Summarizer"
	if 'file-open' in request.form:
		path=request.form['file-open']
		reader=easyocr.Reader(['en'])
		result=reader.readtext(path,paragraph=True)
		text=''
		for r in result:
			text+=r[1]+''
		num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
		summary_text = summarizer(text, max_length=num_sent, min_length=0, do_sample=False)[0]['summary_text']
		if c==1:
			summary_text=""
	else:
		text=""
		summary_text=""
	return render_template("image.html", title = title, original_text = text, output_summary = summary_text, num_sentences = num_sent)



@app.route('/file', methods=['GET','POST'])
def original_file_form():
	global num_sent
	title = "File Summarizer"
	if 'file-open' in request.form:
		pdf=request.form['file-open']
		pdfFileObj = open(pdf, 'rb') 
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
		pgno=int(request.form['page'])
		pageObj = pdfReader.getPage(pgno-1)
		text=pageObj.extractText()
		num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
		summary_text = summarizer(text, max_length=num_sent, min_length=0, do_sample=False)[0]['summary_text']
		if c==1:
			summary_text=""
	else:
		text=""
		summary_text=""
	return render_template("index1.html", title = title, original_text = text, output_summary = summary_text, num_sentences = num_sent)


@app.route('/text', methods=['GET','POST'])
def original_text_form():
	global num_sent
	title = "Text Summarizer"
	if 'input_text' in request.form:
		text = request.form['input_text'] #Get text from html
		num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
		summary_text = summarizer(text, max_length=num_sent, min_length=0, do_sample=False)[0]['summary_text']
		print(summary_text)
		if c==1:
			summary_text=""
	else:
		text=""
		summary_text=""
	return render_template("index.html", title = title, original_text = text, output_summary = summary_text, num_sentences = num_sent)


@app.route('/')
def homepage():
	title = "Text Summarizer"
	return render_template("index.html", title = title)
	
if __name__ == "__main__":
	app.debug = True
	app.run()

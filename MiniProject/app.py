import nltk
from nltk import *
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from flask import Flask, render_template, request, flash
import string
import operator
import PyPDF2

# nltk.download('punkt')
# nltk.download('stopwords')

#import bs4 as bs 
#import urllib2
#from urllib2 import urlopen

c=0

class summarize:

	def get_summary(self, input, max_sentences):
		sentences_original = sent_tokenize(input)

		#Remove all tabs, and new lines
		if (max_sentences > len(sentences_original)):
			c=1
			return ""
		s = input.strip('\t\n')
		
		#Remove punctuation, tabs, new lines, and lowercase all words, then tokenize using words and sentences 
		words_chopped = word_tokenize(s.lower())
		
		sentences_chopped = sent_tokenize(s.lower())

		stop_words = set(stopwords.words("english"))
		punc = set(string.punctuation)

		#Remove all stop words and punctuation from word list. 
		filtered_words = []
		for w in words_chopped:
			if w not in stop_words and w not in punc:
				filtered_words.append(w)
		total_words = len(filtered_words)
		
		#Determine the frequency of each filtered word and add the word and its frequency to a dictionary (key - word,value - frequency of that word)
		word_frequency = {}
		output_sentence = []

		for w in filtered_words:
			if w in word_frequency.keys():
				word_frequency[w] += 1.0 #increment the value: frequency
			else:
				word_frequency[w] = 1.0 #add the word to dictionary

		#Weighted frequency values - Assign weight to each word according to frequency and total words filtered from input:
		for word in word_frequency:
			word_frequency[word] = (word_frequency[word]/total_words)

		#Keep a tracker for the most frequent words that appear in each sentence and add the sum of their weighted frequency values. 
		#Each tracker index corresponds to each original sentence.
		tracker = [0.0] * len(sentences_original)
		for i in range(0, len(sentences_original)):
			for j in word_frequency:
				if j in sentences_original[i]:
					tracker[i] += word_frequency[j]

		#Get the highest weighted sentence and its index from the tracker. We take those and output the associated sentences.
		
		for i in range(0, len(tracker)):
			
			#Extract the index with the highest weighted frequency from tracker
			index, value = max(enumerate(tracker), key = operator.itemgetter(1))
			if (len(output_sentence)+1 <= max_sentences) and (sentences_original[index] not in output_sentence): 
				output_sentence.append(sentences_original[index])
			if len(output_sentence) > max_sentences:
				break
			
			#Remove that sentence from the tracker, as we will take the next highest weighted freq in next iteration
			tracker.remove(tracker[index])
		
		sorted_output_sent = self.sort_sentences(sentences_original, output_sentence)
		return (sorted_output_sent)
	# From the output sentences, sort them such that they appear in the order the input text was provided.
	# Makes it flow more with the theme of the story/article etc..
	def sort_sentences (self, original, output):
		sorted_sent_arr = []
		sorted_output = []
		for i in range(0, len(output)):
			if(output[i] in original):
				sorted_sent_arr.append(original.index(output[i]))
		sorted_sent_arr = sorted(sorted_sent_arr)

		for i in range(0, len(sorted_sent_arr)):
			sorted_output.append(original[sorted_sent_arr[i]])
		print (sorted_sent_arr)
		return sorted_output



#------------Flask Application---------------#

app = Flask(__name__)
@app.route('/file', methods=['GET','POST'])
def original_file_form():
	title = "File Summarizer"
	if 'file-open' in request.form:
		pdf=request.form['file-open']
		pdfFileObj = open(pdf, 'rb') 
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
		pgno=int(request.form['page'])
		pageObj = pdfReader.getPage(pgno-1)
		text=pageObj.extractText()
		max_value = sent_tokenize(text)
		num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
		sum1 = summarize()
		summary = sum1.get_summary(text, num_sent)
		if c==1:
			summary=""
	else:
		text=""
		summary=""
		max_value=0
	return render_template("index1.html", title = title, original_text = text, output_summary = summary, num_sentences = max_value)
@app.route('/text', methods=['GET','POST'])
def original_text_form():
	title = "Text Summarizer"
	if 'input_text' in request.form:
		text = request.form['input_text'] #Get text from html
		max_value = sent_tokenize(text)
		num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
		sum1 = summarize()
		summary = sum1.get_summary(text, num_sent)
		if c==1:
			summary=""
	else:
		text=""
		summary=""
		max_value=0
	return render_template("index.html", title = title, original_text = text, output_summary = summary, num_sentences = max_value)
@app.route('/')
def homepage():
	title = "Text Summarizer"
	return render_template("index.html", title = title)
	
if __name__ == "__main__":
	app.debug = True
	app.run()

#data source from user
print ('Hello, ')
print()
question=input('Please, enter your question and press enter. Mind your cases, write everything in lower case exept proper nouns')
print()
print()
print('your question is ', question)

#write firts character of the sentence in lower case just in case

question = list(question)
question[0] = question[0].lower()
question = ''.join(question)

#parse the question
print('importing NLP to analyse your question...')

import spacy

#use the web_md version of spacy otherwise similarity() function does not work

nlp = spacy.load('en_core_web_md')


doc=nlp(question)

for token in doc:
    print(token.text,token.pos_)
    
for ent in doc.ents:
    print(ent.text, ent.label_)
#identify question type aka. when where who why how

print('identifying target, type and detail question...')

possiblequestiontypes=['who','which','what','when', 'how','where']

i=0 
targetsubject=""
questiontype=""

#find the type of question
questiontype=''
for i in range(len(doc)):
    if doc[i].text in possiblequestiontypes:
        questiontype= doc[i].text
if questiontype=='':
        print('I can not find the question type')
               
#find the target subject
targetsubject=''
    #if there is a clear spacy entity use it as a target question
if len(doc.ents)>0:
        targetsubject=ent.text
        targetsubject=targetsubject.replace(" ","_")
    #if spacy does not found an entity take proper nouns, nouns and adjective found in the question
else:
    if "PROPN" == doc[i].pos_:
            targetsubject+=doc[i].text+"_"
    if "ADJ" == doc[i].pos_:
            targetsubject+=doc[i].text+"_"    
    if ("NOUN" == doc[i].pos_) and (doc[i].text not in possiblequestiontypes):
            targetsubject+=doc[i].text+"_"
    targetsubject=targetsubject[:-1]     
        
print('target subject is ',targetsubject)
print('target question is ',questiontype)

#look for question detail 
i=0
questiondetail=""
for i in range(len(doc)):
    if "ADJ" == doc[i].pos_:
            questiondetail+=doc[i].lemma_+"_"    
    if "VERB" == doc[i].pos_ and doc[i].lemma_!='do' and doc[i].lemma_!='be':
            questiondetail+=doc[i].text
print('question detail is ',questiondetail)

#scrape 
print('finding the wiki web that contains the answer....')

import urllib
import requests
import sys
from bs4 import BeautifulSoup
from bs4.element import Comment

#assign website to look
source="https://en.wikipedia.org/wiki/"+targetsubject

print('I am looking at ',source, ' for the answer....')

#handle errors if the web can not find
req = urllib.request.Request(source)
try: urllib.request.urlopen(req)
except urllib.error.URLError as e:
    print('Sorry, I can not answer your question')
    sys.exit()

#clean the text file 

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

html = urllib.request.urlopen(source).read()

scrapedtext=text_from_html(html)

#use nlp to find answer

print('looking through all possible sentences that may contains the answer....')

doc=nlp(scrapedtext)

#divide the text in sentences
sentences = [sent.string.strip() for sent in doc.sents]
#check how many sentances to analyse
print('number of sentence to analyse is ',len(sentences))
print()

#assign differnt entities types to different kind of questions

if questiontype=='when':
    Set_Entities=['DATE','EVENT','TIME']
if questiontype=='who':
    Set_Entities=['PERSON', 'NORP','ORG','GTE']
if questiontype=='where':
    Set_Entities=['FACT','ORG','GPE']
if questiontype=='how':
    Set_Entities=['QUANTITY','MONEY']
if questiontype=='which':
    Set_Entities=['DATE', 'EVENT','TIME','PERSON','NORP','ORG','GTE','GPE','LANGUAGE']
if questiontype=='what':
    Set_Entities=['DATE', 'EVENT','TIME','PERSON','NORP','ORG','GTE','GPE','LANGUAGE']
    
    
#the code looks all sentences for Question Detail
n_answer_found=0
for sent in doc.sents:
        
        sentence=sent.text
        words=sentence.split()
        
        #search words similar to the Question Detail
        word_similarity_max=0
        
        for i in range (len(words)):
            word_similarity = nlp(words[i]).similarity(nlp(questiondetail))
            if word_similarity>word_similarity_max:
                word_similarity_max=word_similarity
                
            
        if word_similarity_max>0.7 and len(words)>2:
            #look if there is any entity interesting to the question
            entities_count=0
            doc3=nlp(sent.text)
            Found=0
            for ent in doc3.ents:
                if ent.label_ in Set_Entities:
                    Found=1
            if Found==1:
                n_answer_found+=1
                print(n_answer_found, word_similarity_max, sentence) 
                print() 

if n_answer_found>0:
    print('I found ',n_answer_found,' answers for you. END')                
if n_answer_found==0:
        print('Sorry, I could find a wiki page but not the answer your requested')

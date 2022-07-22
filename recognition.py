# -*- coding: utf-8 -*-
"""recognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17uF0F6_x6SL_Gio0xEkgqlzFQuuhqzlV
"""

# import spacy 
import PyPDF2
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import benepar
import pickle
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
# import warning
import re
# from verbecc import Conjugators
from nltk.tokenize import TreebankWordTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sentence_transformers import SentenceTransformer, util
from numpy.linalg import svd
from gensim.models import Word2Vec, Doc2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument





class preprocess:
  """
  NLP preprocessing by Engineers at ISEP

  input: text
  """
  def __init__(self):
      # self.nlp = spacy.load('fr_core_news_sm')  ## download french model
      self.sentence_token = list()
      self.texts= list()
      self.word_token = TreebankWordTokenizer()
      self.tfidf = TfidfVectorizer()
      self.simple_vocab = 0
      # self.word2vec = 0

  def extract_text_pdf(self,pdf_directory):
      """
      This function collects text from a pdf and outputs a
      processed list of the text.

      input: pdf direcotry
      output: list of preprocessed text
      """
      pdf_clean_text = list()
      pdf =  open(pdf_directory,'rb')
      pdf = PyPDF2.PdfFileReader(pdf)
      texts= list()
      print(f'A total of {pdf.numPages} page(s) was identified in the PDF')
      for i in range(pdf.numPages):
        pagepdf = pdf.getPage(i)
        self.texts.append(self.lower_text(pagepdf.extractText()))
      self.preprocess_text(self.texts)

  def lower_text(self,text):
      return  text.strip().lower()

  def get_sentences(self,text): 
    return sent_tokenize(self.lower_text(text))    

  def clean_text(self,text):
      """
      This function involves any cleaning process
      to be done on the text before it goes for continues
      preprocesing. This function takes no parameter.

      input: None
      otput:splitted sentences based in part of speech tagging.
        """
      return self.get_sentences(text)

  def cosine_sim(self,u,v):
      """
      Cosine similarity function formulation
      """
      dist = 1.0 - np.dot(u, v) / (norm(u) * norm(v))
      return dist
  
  # def cosine_sim_avg(self,complex_words):
  #     """
  #     Computing the cosine similarity average of 
  #     each complex word to its sentence
  #     """
  #     word_cs_avg = []
  #     for word in complex_words:
  #       cs_avg = np.average(word2vec.wv.cosine_similarities(word2vec.wv[word],word2vec.wv[word2vec.wv.index_to_key]))
  #       word_cs_avg.append((word, cs_avg))
  #     sorted_list = sorted(word_cs_avg)
  #     return word_cs_avg

  # def cosine_sim_avg(self,sentence,complex_words,model):
  #     """
  #     Computing the cosine similarity average of 
  #     each complex word to its sentence
  #     """

  #     model = self.word2vec.load('word2vec.model')
  #     model.train([sentence], total_examples=1, epochs=1)
  #     model.vm.doesnt_match(sentence.split())
  #     word_cs_avg = []
  #     for word in complex_words:
  #         cs_avg = np.average(model.wv.cosine_similarities(word2vec.wv[word],word2vec.wv[word2vec.wv.index_to_key]))
  #         word_cs_avg.append((word, cs_avg))
  #     sorted_list = sorted(word_cs_avg)
  #     return word_cs_avg


  def get_similarity(value, sentence_vocab, sentence_emb_features):
      sorted_list = sorted(sentence_vocab, key = lambda word: cos_dis(sentence_emb_features[sentence_vocab.index(value),:],sentence_emb_features[sentence_vocab.index(word),:]),reverse=True)
      return sorted_list[:5]

  def tfidfvectorizer(self,corpus):
      """
      This function creates vocabulary of simple words based on 
      a set of corporas coming from Falc and simplified versions of 
      complex phrases.

      input: corpus
      output:corpus vocabulary, embedding retaining most of the information
      """
      tfidf_dim = self.tfidf.fit_transform(corpus)
      names = tfidf.get_feature_names() #Get set of vocabulary values
      cooccurencematrix = pd.DataFrame(data = tfidf_dim.toarray(), columns = names, index = names)
      U,S,V = svd(df) ##Single value decompistion for feature extraction
      emb_features = U[:,:20]

      return tfidf.vocabulary_.keys(), emb_features




  def preprocess_text(self,texts):
      """
      This function entails further preprocessing operations
      done on the text resulting in a set of tokens for each
      splitted sentence from text using spacy part of speech
      french tagging.

      input: None
      output: list of tokens associated to each sentence
      """
      try:
        count=1
        for text in texts:
          sentences = self.clean_text(text) ##Parser
          # print(f'The length of cleaned text {count} is {len(new_text)}, that of the original text {count} is {len(text)} and their ratio is {round(len(new_text)/len(text),2)}')
          # print()##add some space
          ##Lexical analyser and symmbol table creation per sentence
          for sentence in sentences:
            tokens = self.word_token.tokenize(sentence)
            tokens = [token for token in tokens if token != '\n'] ##Regular expression could also solve the problem
            tokens = [token for token in tokens if token.isalpha()] ##Removing numerical data
            if '\n ' in tokens:
                tokens.remove('\n ') ##Remove empty space symbols
            if len(tokens) != 0:
              self.sentence_token.append(tokens)
          count+=1 ##Count the number of available text
      except TypeError:
        print('Your data shoud be found inside a list')

class recognition:

   def __init__(self,all_words):
      # self.tokenized_sentences = tokenized_sentences
      # self.model = model_path
      self.token_to_complex = list()
      self.sentence_verbs = list()
      # self.model = Word2Vec(all_words, vector_size=100, window=5, min_count=1)
      # self.model.save('word2vec.model')
      # self.nlp = spacy.load('fr_core_news_sm')
      self.lexique = pd.read_table('http://www.lexique.org/databases/Lexique383/Lexique383.tsv')
      self.lexique = self.lexique.groupby('ortho').sum()
      # self.lexique2 = pd.read_csv('http://www.lexique.org/databases/FrenchLexiconProject/FLP.words.csv')
      # self.pca = PCA(n_components=1)
      # self.transformer = SentenceTransformer('all-MiniLM-L6-v2')
      # print(f'There is a total of {len(self.tokenized_sentences)} tokenized sentence(s)')
      # print()##Add some space
      # benepar.download('benepar_fr2')
      # ##Setup pipeline
      # if spacy.__version__.startswith('2'):
      #   self.nlp.add_pipe(benepar.BeneparComponent("benepar_fr2"))
      # else:
      #   self.nlp.add_pipe("benepar", config={"model": "benepar_fr2"})


   def complex_word_recognition(self,sentence_list,margin=0.2):
      """
      This function permits the extraction of complex words in 
      a sentence with the use of a classification model.

      input: tokenized set of sentences
      output: tokenized sentences with their associated complex words
      """
      # try:
        # count = 1

        # for tokens in self.tokenized_sentences:
        #   token_features = self.lexique2[self.lexique2['item'].isin(tokens)]
        #   token_features_num = token_features.select_dtypes(['int64','float64'])
        #   token_features_num = token_features_num.replace(-np.inf,0)
        #   input = self.pca.fit_transform(token_features_num)    
        #   # _sc = StandardScaler()
        #   # _pca = PCA(n_components = 1)
        #   # preprocess = Pipeline([
        #   #     ('std_scaler', _sc),
        #   #     ('pca', _pca),
        #   #     ('regressor', _model)
        #   # ])
        #   #          
        #    ##feature creation for model prediction
        #   ##load the model from disk
        #   filename = self.model ##path to machine learning model
        #   loaded_model = pickle.load(open(filename, 'rb'))
        #   result = loaded_model.predict(input)

        #   ##Getting the list of complex words in the tokenized sentence
        #   token_features['class'] = result
        #   token_features['class'] = token_features['class'].replace(to_replace=[1,0], value=['simple', 'complex'])
        #   complex_words = token_features[token_features['class'] == 'complex'].item.to_list()


        # def word2vec(self,all_words):
        #   """
        #   word2vec model create embedding of a corpus

        #   input: all_words 
        #   type: list of tokens from each sentence

        #   oputput vocabulary
        #   """


      result = []
      count = 0
      for sentence in sentence_list:
          for word in sentence:
              if word not in self.model.wv.index_to_key and count !=2 or count>2:
                print('word not in vocab',word)
                self.model = Word2Vec.load("word2vec.model")
                self.model.train([[sentence]], total_examples=1, epochs=1)
                count+=1
              else:
                cos_sim_avg = np.average(self.model.wv.cosine_similarities(self.model.wv[word],self.model.wv[self.model.wv.index_to_key]))
                print((word,cos_sim_avg))

                # if cos_sim_avg > margin:
                result.append((word,cos_sim_avg,round(float(self.lexique[self.lexique.index.isin([word])]['freqfilms2'].values),2)))
          print()
          result = sorted(result, key = lambda x:x[1], reverse = False)[:1]
          self.token_to_complex.append({'sentence_tokens':''.join(sentence),'complex_words':result},reverse=True)
          return  result, self.token_to_complex
          
          
      # except TypeError:
      #       print('Your data shoud be found inside a list')
            

          # ##Removing mistakes done ny model to capture complex words
          # for word in complex_words:
          #   if word in self.simple_vocab:
          #     complex_words.remove(word) 

          # ##Semantic filter control based on a margin
          # sentence_embeddings = self.transformer.encode(self.texts)
          # result = []
          # for word in complex_words:
          #   complex_word_embedding = self.transformer.encode(word)
          #   if abs(util.cos_sim(sentence_embeddings, complex_word_embedding).numpy()[0]) >= margin:
          #     print('The winning candidate is', end='')
          #     print((word, util.cos_sim(sentence_embeddings3, complex_word_embedding).numpy()[0]))
          #     result.append(word)
          # ##Add the results to its associated sentence
          # self.token_to_complex.append({'sentence_tokens':tokens,'complex_words':result})
          # print(f'Completed sentence {count} and stored')
          # count+=1


   def tense_recognition(self):
      count = 1
      for tokens in self.tokenized_sentences: 
        ##Parse tokens
        doc = self.nlp(' '.join(tokens))
        sent = list(doc.sents)[0]
        ##Visualize parsing
        print(sent._.parse_string)

        #Extract verbs in text
        verbs = list()
        exp = re.compile('[(V]* ') ##Regular expression to extract all verbs
        for i in range(0,len(tokens)):
          word = list(doc.sents)[0][i]
          print('word',word)
          if len(list(doc.sents)[0][i]._.labels)!=0:
            if 'VN' in list(doc.sents)[0][i]._.labels and 'VINF' not in list(doc.sents)[0][i]._.parse_string:
              verbs.append(word)
          elif exp.match(list(doc.sents)[0][i]._.parse_string):
            verbs.append(word)

        ##get the word lemme and its tense value
        view = self.lexique[(self.lexique['ortho'].isin([str(i) for i in verbs])) & (self.lexique['cgram'] == 'VER')]

        ##Create output in the form of a list
        for i in range(0,len(view.ortho.values)):
          self.sentence_verbs.append({'sentence_tokens':tokens,'verb':view.ortho.values[i], 'lemme':view.lemme.values[i], 'tense':view.infover.values[i]})
        print(f'Completed sentence {count} and stored')
        print()##add some space
        # cg.conjugate('être')['moods']['participe']['participe-passé'][0] ##Tense lookup
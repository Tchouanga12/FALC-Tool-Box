# -*- coding: utf-8 -*-

##TODO: just keep what is needed in the imports
import PyPDF2
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
import re
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from gensim.models import Word2Vec
import pickle


##TODO: Add descriptions to all functions approriately



class preprocess:
  """
  NLP preprocessing by Engineers at ISEP

  """
  def __init__(self):
      self.sentence_token = list()
      self.total_token = 0
      self.total_corpus_token = 0

  def extract_text_pdf(self,pdf_directory):
      """
      This function collects text from a pdf and outputs a
      processed list of the text.

      input: pdf direcotry
      output: list of preprocessed text
      """
      self.total_token = 0
      pdf =  open(pdf_directory,'rb')
      pdf = PyPDF2.PdfFileReader(pdf)
      print('Document ', pdf_directory)
      for i in range(pdf.numPages):
        print('Page ',i+1)
        pagepdf = pdf.getPage(i)
        _ , total = self.preprocess_text([self.lower_text(pagepdf.extractText())])
        self.total_token+=total
      print(f'In document {pdf_directory} a total of {pdf.numPages} page(s) was identified in the PDF and  {self.total_token} token(s) processed.')
      print()
      self.total_corpus_token+= self.total_token

      return self.sentence_token

  def lower_text(self,text):
      """
      removing spaces at the begining and end of string 
      and puts the text into small letters.

      input: text
      output: small case text
      """
      return  text.strip().lower()

  def get_sentences(self,text): 
      """
      Sentence tokenization or splitting function, breaks a bunch of 
      text into a set of sentence based on the dot (.) punctuation
      mark.

      input: text
      output: tokenized sentence
      """
      return sent_tokenize(self.lower_text(text),language='french')    

  def clean_text(self,text):
      """
      This function involves any cleaning process
      to be done on the text before it goes for continues
      preprocesing. This function takes no parameter.

      input: None
      output:splitted sentences based in part of speech tagging.
        """
      return self.get_sentences(text)

  def bind_num(self,matchobj):
      """
      Function to bind French numerical numbers

      input: regular expression object
      output: binded numerical number 
      """
      return ''.join(matchobj.group(0).split(' '))

  def preprocess_text(self,texts):
      """
      This function entails further preprocessing operations
      done on the text resulting in a set of tokens for each
      splitted sentence from text using spacy part of speech
      french tagging.

      input: list of sentence tokens
      output: list of tokens associated to each sentence
      """
      ##TODO: Revise the preprocess_text function for bugs fix-ups

      total = 0
      if type(texts) == str:
        print('ProcessErrror: Your input value should be in a form of a list try again')
      
      else: 
        try:
          count=1
          for text in texts:
            sentences = self.clean_text(text) ##Parser
            ##Lexical analyser and symmbol table creation per sentence
            for sentence in sentences:
              sentence = re.sub(",", ' ', sentence)
              sentence = re.sub("[0-9]+\s*.[0-9]+\s*.[0]+", self.bind_num, sentence)
              sentence = re.sub(r"http\S+", "", sentence)
              sentence = re.sub("[A-Za-z0-9]*@[A-Za-z0-9]*.[A-Za-z]*", '', sentence)
              tokens = word_tokenize(sentence, language='french')
              tokens = [re.sub("[a-z]+[',’,']",'', token) for token in tokens] 
              tokens = [token for token in tokens if token != '\n'] ##Regular expression could also solve the problem
              tokens = [token for token in tokens if token not in ['*','.',',','«','(',')','»',"l'",'-',';','[',']','—',':','…','?','–','...','!','’',"'",'•','/','➢','&','|','=']] 
              tokens = [re.sub("[.,•]",'', token) for token in tokens]
              
              
              if '\n ' in tokens:
                  tokens.remove('\n ') ##Remove empty space symbols
              if len(tokens) != 0:
                self.sentence_token.append(tokens)
                total += len(tokens)
            count+=1 ##Count the number of available text
            print(f'The total number of {total} token(s) has been processed')
        except TypeError:
          print('Your data shoud be found inside a list')
        
        return self.sentence_token, total

class recognition:

   def __init__(self):

      self.token_to_complex = list()
      self.sentence_verbs = list()
      self.model = 0
      self.complex_words = 0
      self.lemmatizer = FrenchLefffLemmatizer()
      ##Part of speech tagging pretrained model
      tokenizer = AutoTokenizer.from_pretrained("gilf/french-postag-model")
      model = AutoModelForTokenClassification.from_pretrained("gilf/french-postag-model")
      self.nlp_token_class = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)
      self.lexique = pd.read_table('http://www.lexique.org/databases/Lexique383/Lexique383.tsv')
      self.lexique = self.lexique.groupby('ortho').sum() ##Grouping words to remove the obstacle of grammatical category
      self.pca = PCA(n_components=1)


   def classifier1(self,model_path,tokens):
            """
            This contains the preprocessing steps and model prediction with the use
            of the trained decision tree classifie based on principal component 
            analysis.

            input: path to the trained model, tokens
            output: predicted complex word from sentence
            """
            # TODO: Try to implement the log feature engineering strategy from coursera.
            # TODO: Fix problem ValueError: Found array with 0 sample(s) (shape=(0, 19)) while a minimum of 1 is required.

            ##Preprocessing features of each token
            valid_tokens = []
            ratio = []
            for token in tokens:
              if token in self.lexique.index.values:
                valid_tokens.append(token)
                # ratio.append(round(len(valid_tokens)/len(tokens),2))
            if len(valid_tokens) != 0:
              token_features = self.lexique[self.lexique.index.isin(valid_tokens)]
              token_features_num = token_features.select_dtypes(['int64','float64'])
              token_features_num = token_features_num.replace(-np.inf,0)
              input = self.pca.fit_transform(token_features_num)          

              ##load the model from disk
              loaded_model = pickle.load(open(model_path, 'rb'))
              result = loaded_model.predict(input)

              ##Getting the list of complex words in the tokenized sentence
              token_features_new = token_features.copy()
              token_features_new['class'] = result
              token_features_new['class'] = token_features_new['class'].replace(to_replace=[1,0], value=['simple', 'complex'])
              self.complex_words = token_features_new[token_features_new['class'] == 'complex'].index.to_list()

            return self.complex_words


   def complex_word_recognition(self,sentence_list,classifier1,model,truth=''):
      """
      This function permits the extraction of complex words in 
      a sentence with the use of a classification model.

      input: tokenized set of sentences
      output: tokenized sentences with their associated complex words
      """
      #TODO: Fix the problem of RuntimeWarning: invalid value encountered in true_divide explained_variance_ = (S ** 2) / (n_samples - 1)
      #TODO: Fix the problem UserWarning: `grouped_entities` is deprecated and will be removed in version v5.0.0, defaulted to `aggregation_strategy="simple"` instead.grouped_entities` is deprecated and will be removed in version v5.0.0, defaulted to"
      #TODO: Update perfarmances by playing with validation test1 and test2 and also if possible play with another POS tagging model
      self.token_to_complex = list()
      final = []
      result = []
      lemme = ''
      complex_word_pos_dict = {}
      if type(sentence_list[0]) == str:
        print('TypeError:Your input value should be in a form of a list try again') ##Check data validity
      else:

        not_found = []

        self.model = Word2Vec.load(model) ## load word2vec model

        for sentence in sentence_list: ## Get each sentence in the sentence list
            for word in sentence: ## Get each word in each sentence
                if word not in self.model.wv.index_to_key:
                  not_found.append(word) ## If sentence not found in vocabulary update rhe vocabulary
            if len(not_found) !=0:
              self.model.build_vocab([not_found], update=True)
              self.model.train([not_found],total_examples=self.model.corpus_count, epochs=self.model.epochs) #Then retrain the model
            
            complex_words = self.classifier1(classifier1,sentence)
            self.complex_words.remove(self.model.wv.doesnt_match(complex_words)) 
            for word in self.complex_words:
                  cos_sim_avg = np.average(self.model.wv.cosine_similarities(self.model.wv[word],self.model.wv[sentence])) \
                  * self.lexique[self.lexique.index.isin([word])]['freqfilms2'].values ## Compute cosine similarity of each word with words in the vocabulary giving a specific value to differentiate betwwen complex and simple words.
                  
                  if cos_sim_avg < 1:
                    final.append(word)
            
            ###obtaining the tag of the complex word
            for item in self.nlp_token_class(' '.join(sentence)):
              for complex_word in final:
                if item['word'] == complex_word:
                  print(' '.join(sentence))
                  print('found similar word', item['word'])
                  print('the grammtical cat of word: ', item['entity_group'])
                  print('Lemma: ',self.lemmatizer.lemmatize(complex_word,'all'))
                  print('length: ', len(self.lemmatizer.lemmatize(complex_word,'all')))
                  if len(self.lemmatizer.lemmatize(complex_word,'all')) > 0:
                    if item['entity_group'] == 'V' or  item['entity_group'] == 'VIMP' or item['entity_group'] == 'VINF'or item['entity_group'] == 'VPP'or item['entity_group']=='VPR':
                      print('found word entity like verbe', item['word'])
                      for i in self.lemmatizer.lemmatize(complex_word,'all'):
                          print('check: ',i[1])
                          if i[1] == 'v':
                            lemme = i[0]                    
                            complex_word_pos_dict[complex_word] = [lemme,'VER']
                            print('found entity', item['entity_group'] )
                            print()

                    elif item['entity_group'] == 'NPP' or item['entity_group'] == 'NC':
                      print('found word entity like nom', item['word'])
                      for i in self.lemmatizer.lemmatize(complex_word,'all'):
                            print('check: ',i[1])
                            if i[1] == 'nc':
                              lemme = i[0]
                              complex_word_pos_dict[complex_word] = [lemme,'NC']
                              print('found entity', item['entity_group'] )
                              print()

                    elif item['entity_group'] ==  'ADJWH' or item['entity_group'] ==  'ADJ':
                      print('found word entity like adjective', item['word'])                 
                      for i in self.lemmatizer.lemmatize(complex_word,'all'):
                            print('check: ',i[1])
                            if i[1] == 'adj':
                              lemme = i[0]
                              complex_word_pos_dict[complex_word] = [lemme,'ADJ']
                              print('found entity', item['entity_group'] )
                              print()

                    elif item['entity_group'] ==  'ADVWH' or item['entity_group'] ==  'ADV':
                      print('found word entity like adverb', item['word'])
                      print('Lemma: ',self.lemmatizer.lemmatize(complex_word,'all'))
                      for i in self.lemmatizer.lemmatize(complex_word,'all'):
                            print('check: ',i[1])
                            if i[1] == 'adv':
                              lemme = i[0]
                              complex_word_pos_dict[complex_word] = [lemme,'ADV']
                              print('found entity', item['entity_group'] )
                              print()

                    else:
                      if item['entity_group'] == 'U' or item['entity_group'] == 'CS':
                        print('word validaity test 2')
                        print('Deleted a bad complex word: ', complex_word)
                        final.remove(complex_word)
                        print('confirm deletion....', complex_word)
                      # else:
                      #   print('Lemma: ',self.lemmatizer.lemmatize(complex_word,'all'))
                      #   print(item['entity_group'])
                      #   print(complex_word)
                      #   for i in self.lemmatizer.lemmatize(complex_word,'all'):
                      #           print('check: ',i[1])
                      #           lemme = i[0]                      
                      #           complex_word_pos_dict[complex_word] = [lemme,item['entity_group']]
                      #           print('I did the else case')
                      #           print()
                  
                  else:
                      print('word validaity test 1')
                      print('Deleted a bad complex word: ',complex_word)
                      final.remove(complex_word)
                      print('confirm deletion....', complex_word)
                      print()

            result.append([' '.join(sentence),complex_word_pos_dict])

            ##Updated storage
            final = []
            complex_word_pos_dict = {}

      return  result, 


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

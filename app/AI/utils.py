import spacy
import numpy as np

nlp = spacy.load("en_core_web_sm")

def tokenize(sentence):
        #print(text)
        return [tok.text.lower() for tok in nlp.tokenizer(sentence)]

def bag_of_words(sentence, all_words):

        bag = np.zeros(len(all_words), dtype=np.float32)
        for i, w in enumerate(all_words):
                if w in sentence:
                        bag[i] = 1.0
        return bag
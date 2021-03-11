import sys
import xml.etree.ElementTree as ET
import re
from nltk.stem import PorterStemmer
import math
from collections import Counter
from datetime import datetime

startTime = datetime.now()

# is the stopword file going to be in the directory??
ps = PorterStemmer()

f=open("englishST.txt","r")
stopwords = [word for line in f for word in line.split()]
stopSet=set(stopwords)
f.close()

#----------------------INDEX GENERATION --------------------------------
#-----------------------------------------------------------------------
def invertedIndex(name):

    def preprocess(document):
        words = [word.lower() for word in re.findall('\w+', document) if not word.lower() in stopSet]
        return words

    def getIdandText(doc):
        docId=int(doc.find("DOCNO").text)
        headline = doc.find('HEADLINE').text
        text=doc.find("TEXT").text
        terms=preprocess(headline+text)
        return docId,terms

    
    root = ET.parse(name).getroot()
    index={}
    for doc in root.findall('DOC'):
        docId,terms=getIdandText(doc)

        for pos, term in enumerate(terms): 
            #stem the term
            term = ps.stem(term) 
            if term in index:
                # each term has a list containing the freq and a dictionary of documents with positions
                if docId in index[term][1]: 
                    index[term][1][docId].append(pos)
                else:
                    index[term][0]+=1 # update document frequency
                    index[term][1][docId]=[pos]
            else:
                index[term]=[]
                # frequency is 1. 
                index[term].append(1) 
                # The postings list is initially empty. 
                index[term].append({})       
                index[term][1][docId] = [pos] 
    
    return index


index = invertedIndex("trec.sample.xml")
docNum= len(set([doc for term in index.keys() for doc in index[term][1].keys()]))


#----------------------BOOLEAN QUERY EVALUATION---------------------------------
#-------------------------------------------------------------------------------

def getPhraseOrProximityDocuments(terms,isPhrase,proximity):
    results=[]
    match=0
    words= [ps.stem(word.lower()) for word in terms if not word in stopSet]
   
    # do not allow term that does not exist as key 
    if words[0] not in index.keys() or words[1] not in index.keys():
        return []
  
    for doc in index[words[0]][1].keys(): # loop through the documents of the first word
        # if the document is common between the two terms 
        if doc in index[words[1]][1].keys():
            # get the list of positions of the two terms 
            pos0=index[words[0]][1][doc]
            pos1=index[words[1]][1][doc]
            if isPhrase and doc not in results and phraseSearch(pos0,pos1):
                results.append(doc)
            elif not isPhrase and doc not in results and proximitySearch(proximity,pos0,pos1):
                results.append(doc)                
   
    return results

def phraseSearch(pos0,pos1):
    for p0 in pos0:
        for p1 in pos1:
            if p1-p0==1:
                return True
    return False

def proximitySearch(proximity,pos0,pos1):

    
    for p0 in pos0:
        for p1 in pos1:
            if abs(p1-p0)<=proximity:
                return True
    return False

def getNotDoc(notDocs):
    return [doc for term in index.keys() for doc in index[term][1].keys() if doc not in notDocs]

def getTermDoc(query):   
    docs=[] 
    if query not in stopSet:
        query=ps.stem(query.lower())
         # do not allow term that does not exist as key
        docs=list(index[query][1].keys()) if query in index.keys() else []
    return docs

def processQueryExtended(query):
    documents=[]
    if '"' in query:
        print("phrase",query)
        query = query.split('"')[1::2] # get phrase out of the quotes
        documents=getPhraseOrProximityDocuments(query[0].split(),True,proximity=None)
    elif "#" in query:
        proximity= int(query[query.find("#")+1:query.find("(")])
        terms= query[query.find("(")+1:query.find(")")].split(",")
        documents=getPhraseOrProximityDocuments(terms,False,proximity)
    else:  
        print("normal")
        documents=getTermDoc(query)
    
    return documents


def processQuery(query):
    print(query)
    documents=[]
    for q in query:

        if "NOT" in q:
            print("not")
            notDocs=processQueryExtended(q.split("NOT ")[1]) # return documents to be reversed
            documents.append(getNotDoc(notDocs))
        # if '"' in q:
        #     print("phrase",q)
        #     q = q.split('"')[1::2] # get phrase out of the quotes
        #     documents.append(getPhraseOrProximityDocuments(q[0].split(),True,proximity=None))
        # elif "NOT" in q:
        #     print("not")
        #     documents.append(getNotDoc(getTermDoc(q.split()[1])))
        # elif "#" in q:
        #     proximity= int(q[q.find("#")+1:q.find("(")])
        #     terms= q[q.find("(")+1:q.find(")")].split(",")
        #     documents.append(getPhraseOrProximityDocuments(terms,False,proximity))
        else:  
            print("normal")
            # documents.append(getTermDoc(q))
            documents.append(processQueryExtended(q))
    
    return documents

# def processQuery(query):
#     print(query)
#     documents=[]
#     flag=[]
#     for q in query:
#         # if "NOT" in q:
#         #     print("not")
#         #     notDocs=processQuery([q.split("NOT ")[1]]) # return documents to be reversed
#         #     documents.append(getNotDoc(notDocs))
#         if '"' in q:
#             print("phrase",q)
#             q = q.split('"')[1::2] # get phrase out of the quotes
#             documents.append(getPhraseOrProximityDocuments(q[0].split(),True,proximity=None))
#         elif "NOT" in q:
#             print("not")
#             documents.append(getNotDoc(getTermDoc(q.split()[1])))
#         elif "#" in q:
#             proximity= int(q[q.find("#")+1:q.find("(")])
#             terms= q[q.find("(")+1:q.find(")")].split(",")
#             documents.append(getPhraseOrProximityDocuments(terms,False,proximity))
#         else:  
#             print("normal")
#             documents.append(getTermDoc(q))
    
#     return documents

def getBooleanQueryResults(query):
    if " AND " in query:
        query=[q.strip() for q in query.split("AND")]
        documents= processQuery(query)
        results=list(set(documents[0]).intersection(documents[1]))
    elif " OR " in query:
        query=[q.strip() for q in query.split("OR")]
        documents= processQuery(query)
        results=list(set(documents[0]).union(documents[1]))
    else:
        results= processQuery([query])[0] # get first list that comes back

    return sorted(results)


booleanQueries={}
f=open("queries.boolean.txt","r")
queriesList = [line.strip() for line in f.readlines()]
f.close()

for query in queriesList:
    query=query.split(" ",1)
    booleanQueries[int(query[0])]=query[1]

with open("results.boolean.txt", "w")  as booleanResultsFile:  
    for qid in booleanQueries.keys():
        documents=getBooleanQueryResults(booleanQueries[qid])
        for doc in documents:
            booleanResultsFile.write("{},{}\n".format(qid,doc))

booleanResultsFile.close()

#----------------------RANKED QUERY EVALUATION---------------------------------
#------------------------------------------------------------------------------

# ADDITIONAL METHODS USED IN RANKED QUERY EVALUATION

def getTermFrequency(term,doc):
    if term not in stopSet:
        term=ps.stem(term.lower())
    return len(index[term][1][doc])


def processRankedQuery(terms):
    rankIndex={} # dictionary with {term1:{doc1:score1,doc2:score2},term2:{...}}
    relevantDocs=[]
    for term in terms:
        relevantDocs=getTermDoc(term)
        df=len(relevantDocs)
        rankIndex[term]={}
        idf=math.log10(docNum/df) if df!=0 else 0
        for doc in relevantDocs:
            tf=getTermFrequency(term,doc)
            score=(1+math.log10(tf))*idf
            rankIndex[term][doc]=score


    relDoc=Counter()
    # add dictionaries of the form {doc1:score1,doc2:score2} together, while adding the value
    # of those with the same keys
    for term in terms:
        relDoc+=Counter(rankIndex[term])
    
    return relDoc.most_common(150)

rankedQueries={}
f=open("queries.ranked.txt","r")
rankedQueriesList = [line.strip() for line in f.readlines()]
f.close()

for query in rankedQueriesList:
    query=query.split(" ",1)
    rankedQueries[int(query[0])]=query[1]


with open("results.ranked.txt", "w")  as rankedResultsFile:  
    for qid in rankedQueries.keys():
        terms=[term for term in rankedQueries[qid].split()]
        # re.findall('\w+', rankedQueries[qid]
        print(terms)
        documents=processRankedQuery(terms)
        for doc,score in documents:
            rankedResultsFile.write("{},{},{:.4f}\n".format(qid,doc,score))

rankedResultsFile.close()


with open("index.txt", "w")  as indexFile:
    for term in index.keys():
        indexFile.write("{}:{}\n".format(term,index[term][0]))
        for doc in index[term][1].keys():
            indexFile.write("\t{}:{}\n".format(doc,str(index[term][1][doc]).strip('[]')))

indexFile.close()

print(datetime.now() - startTime)
import re
import math
import time

start_time = time.time()


class PostingsList:
    """
    class of a postings_list implementing skip pointers

    parameters:
    ------------
    docs:  documents of the postings lists

    interval: interval to be skipped, matters when creating the posting list and its nodes
    """
    def __init__(self, docs=None, interval=3):
        if docs is None:
            docs = []
        self.docs = sorted(docs)  
        self.root = None  
        self.interval = interval  
        self.create_postings_list(docs)

    def create_postings_list(self, docs):
        """
        method that creates a postings list

        stores the root node of the linked list/postings list in the root attribute of the class and 
        constructs a postings list node that can skip to the node that comes next regarding the skip interval 
        
        parameters:
        -----------
        docs: document ids that are used to construct a postings list
        """
        if not docs:
            return

        self.root = PostingsListNode(docs[0])
        current = self.root
        nodes = [current]  

        for doc_id in docs[1:]:
            new_node = PostingsListNode(doc_id)
            current.next = new_node
            current = new_node
            nodes.append(new_node)

        for i in range(0, len(nodes), self.interval):
            if i + self.interval < len(nodes):
                nodes[i].next_skip = nodes[i + self.interval]

    def form_intersection_with(self, other):
        """
        forms the intersection of two postings lists and returns a new postings list

        parameters:
        -----------
        other: the postings list that intersects

        returns:
        --------
        result: postings list resulting from intersecting the two
        """
        intersecting_docs = self.get_intersecting_documents(other)
        return PostingsList(
            docs=intersecting_docs, 
            interval=int(math.sqrt(len(self.docs))) if len(self.docs) >= 9 else 3
            )

    def get_intersecting_documents(self, other):
        """
        finding intersecting documents of two postings lists

        parameters:
        -----------
        other: the postings list that intersects

        returns:
        --------
        result: list of document ids that are present in both postings lists
        """
        result = []
        p1, p2 = self.root, other.root

        while p1 != None and p2 != None:
            if p1.doc == p2.doc:
                result.append(p1.doc)
                p1, p2 = p1.next, p2.next
            elif p1.doc < p2.doc:
                while p1.next_skip and p1.next_skip.doc <= p2.doc:
                    p1 = p1.next_skip
                else:
                    p1 = p1.next
            else:
                while p2.next_skip and p2.next_skip.doc <= p1.doc:
                    p2 = p2.next_skip
                else:
                    p2 = p2.next

        return list(set(result))

class PostingsListNode:
    """
    node of postings list 

    parameters:
    ------------
    doc: the document the node represents
    """
    def __init__(self, doc):
        self.doc = doc  
        self.next = None  
        self.next_skip = None 

class InvertedIndex:
    """
    class of an inverted index

    uses postings lists for querying

    parameters:
    -----------
    index: a dictionary with postings lists in raw format (lists of document ids and unsorted)
    """
    def __init__(self, index: dict):
        self.index = index

    def query(self, text):
        """
        method to query for text 
        
        queries are treated in a way that "malaria vaccines" becomes "malaria AND vaccines". 
        Text is split at special characters and spaces.

        parameters:
        ------------
        text: text to be queried
        """
        intersection = None
        tokens = re.split(r"(?:\s+|\s*[.!?\\-]+\s+|\s+[.!?\\-]+\s*)", text)
        for token in tokens:
            if token not in self.index or not token:
                continue

            postings_list = PostingsList(
                docs=self.index[token], 
                interval=int(math.sqrt(len(self.index[token]))) if len(self.index[token]) >= 9 else 3
                )
            
            if intersection is not None:
                intersection = intersection.form_intersection_with(postings_list)
            else:
                intersection = postings_list
        
        return intersection.docs if intersection else []

def index(file_path):
    """
    indexes the content of a text file for the use of querying in an inverted index

    in our case the file contains a column of unique ids that are omitted to spare resources

    parameters:
    -----------
    file_path: path to the text file

    returns:
    --------
    index: dictionary with tokens as keys and document ids in a list
    """
    index = {}
    doc_id = 0
    with open(file_path) as tweets:
        tweet = tweets.readline()
        while tweet != "":
            tokens = re.split(r"(?:\s+|\s*[.!?\\-]+\s+|\s+[.!?\\-]+\s*)", tweet)

            for token in tokens:
                if not token:
                    continue

                if not re.match(r"\d{7,}", token): 
                    if token not in index:
                        index[token] = []
                    
                    index[token].append(doc_id)
                
            tweet = tweets.readline()
            doc_id += 1

    return index

index = index("/Users/user/Downloads/tweets.csv")

inverted_index = InvertedIndex(index)
docs = inverted_index.query("peanut")
    
idf1 = (math.log(120000/(1+len(docs))))

docs = inverted_index.query("walnut")

idf2 = (math.log(120000/(1+len(docs))))

print(f"idf of peanut is {idf1}, idf of walnut is {idf2} and 2 cooccurences ")

end_time = time.time()

print(f"Execution time: {end_time - start_time} seconds")

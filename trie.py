import os, pickle, sys
from collections import defaultdict
from nltk.corpus import brown

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.count = 0

class ProbabilisticTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, sequence):
        node = self.root
        for word in sequence:
            word = word.lower()
            node = node.children[word]
            node.count += 1

    def predict(self, prefix):
        node = self.root
        for word in prefix:
            word = word.lower()
            if word not in node.children:
                return []
            node = node.children[word]

        total = sum(child.count for child in node.children.values())
        predictions = []
        for word, child in node.children.items():
            prob = child.count / total
            predictions.append((word, prob))

        return sorted(predictions, key=lambda x: -x[1])[:3]

def build_trie(with_logs=True):
    if with_logs:
        print("Building trie…")
    trie = ProbabilisticTrie()
    sents = list(brown.sents())
    n = len(sents)

    for idx, sent in enumerate(sents):
        if with_logs and idx % 1000 == 0:
            sys.stdout.write(f"\rProgress: {idx}/{n} ({(idx/n)*100:.1f}%)")
            sys.stdout.flush()
        sent = [w.lower() for w in sent]
        for i in range(len(sent)-2):
            trie.insert(sent[i:i+3])
    if with_logs:
        sys.stdout.write("\r Trie built!                                \n")
    return trie

def save_trie(trie, path):
    with open(path, "wb") as f:
        pickle.dump(trie, f)

def load_trie(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

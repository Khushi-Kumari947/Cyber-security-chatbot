import faiss
import pickle
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from rapidfuzz import process, fuzz

class CyberSearchEngine:
    def __init__(self):
        print("Initializing Optimized Engine...")
        # Load Tuned Model (Force CPU)
        self.model = SentenceTransformer('./cyber_model_tuned', device='cpu')
        
        # Load Quantized Index
        self.index = faiss.read_index("vector_store/cyber.index")
        self.index.nprobe = 10  # Crucial for IVF index accuracy
        
        # Load Answer Metadata
        with open("vector_store/metadata.pkl", "rb") as f:
            self.answers = pickle.load(f)
            
        # Initialize BM25 with small token limit to save RAM
        tokenized_corpus = [str(ans).lower().split()[:20] for ans in self.answers.values()]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str):
        query = query.lower().strip()
        
        # 1. Semantic Search (FAISS) - Get Top 5 candidates for re-ranking
        q_emb = self.model.encode([query]).astype('float32')
        D, I = self.index.search(q_emb, k=5)
        
        # Filter out invalid FAISS indices (-1)
        valid_indices = [idx for idx in I[0] if idx != -1]
        if not valid_indices:
            return "No relevant info found."

        # 2. BM25 Search
        query_tokens = query.split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        best_bm25_idx = np.argmax(bm25_scores)
        
        # 3. Optimized Fuzzy Matching (Only match against top candidates)
        candidate_answers = {idx: self.answers[idx] for idx in valid_indices}
        # Add BM25 best match to candidates if it's not already there
        candidate_answers[best_bm25_idx] = self.answers[best_bm25_idx]
        
        fuzzy_result = process.extractOne(
            query, 
            candidate_answers, 
            scorer=fuzz.WRatio
        )
        
        # 4. Final Hybrid Decision Logic
        # Prioritize high-confidence Fuzzy/BM25 for exact keyword/typo correction
        if fuzzy_result and fuzzy_result[1] > 85:
            final_idx = fuzzy_result[2]
        elif bm25_scores[best_bm25_idx] > 15:
            final_idx = best_bm25_idx
        else:
            # Fallback to the top Semantic match
            final_idx = valid_indices[0]
            
        return self.answers.get(final_idx, "No relevant info found.")
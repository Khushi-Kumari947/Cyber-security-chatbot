import faiss
import pickle
import pandas as pd
import os
from sentence_transformers import SentenceTransformer

# 1. Setup Absolute Paths
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_script_dir)
model_path = os.path.join(project_root, 'model')
# Note: Ensure extension is .xlsx (Excel) or .csv depending on your file
data_path = os.path.join(project_root, 'data', 'final_Training.xlsx') 

print(f"Loading model from: {model_path}")
model = SentenceTransformer(model_path, local_files_only=True)

def create_knowledge_base():
    # 2. Ensure output directory exists
    vector_store_path = os.path.join(project_root, "vector_store")
    os.makedirs(vector_store_path, exist_ok=True)
    
    # 3. Load and Encode Data
    df = pd.read_excel(data_path)
    questions = df['Question'].astype(str).tolist()
    
    print(f"Encoding {len(questions)} questions...")
    embeddings = model.encode(questions, show_progress_bar=True, batch_size=64)
    
    # 4. Initialize FAISS Index (MUST be inside the function)
    d = 384  # Dimension for all-MiniLM-L6-v2
    nlist = 100 
    quantizer = faiss.IndexFlatIP(d)
    
    # Define 'index' clearly here
    index = faiss.IndexIVFScalarQuantizer(quantizer, d, nlist, faiss.ScalarQuantizer.QT_8bit)
    
    print("Training and adding to index...")
    index.train(embeddings)
    index.add(embeddings)
    
    # 5. Save Files (MUST be inside the function to see 'index')
    index_save_path = os.path.join(vector_store_path, "cyber.index")
    faiss.write_index(index, index_save_path)
    
    metadata_save_path = os.path.join(vector_store_path, "metadata.pkl")
    with open(metadata_save_path, "wb") as f:
        pickle.dump(df['Answer'].to_dict(), f)
    
    print(f"✅ Success! Saved index and metadata to {vector_store_path}")

if __name__ == "__main__":
    create_knowledge_base()
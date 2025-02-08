from contextual_vectordb import context_vectordb
from evaluation.evaluate import evaluate_db, evaluate_db_advanced

if __name__ == "__main__":
    # context_vectordb.embed_docs_contextual("/home/hoangphan/Data/data/codebase_chunks.json")
    # context_vectordb.embed_docs_basic("/home/hoangphan/Data/data/codebase_chunks.json")

    # results5 = evaluate_db(context_vectordb, '/home/hoangphan/Data/data/evaluation_set.jsonl', 5)
    # results10 = evaluate_db(context_vectordb, '/home/hoangphan/Data/data/evaluation_set.jsonl', 10)
    # results20 = evaluate_db(context_vectordb, '/home/hoangphan/Data/data/evaluation_set.jsonl', 20)

    # results5 = evaluate_db_advanced(context_vectordb, '/home/hoangphan/Data/data/evaluation_set.jsonl', 5)
    results10 = evaluate_db_advanced(context_vectordb, '/home/hoangphan/Data/data/evaluation_set.jsonl', 10)
    results20 = evaluate_db_advanced(context_vectordb, '/home/hoangphan/Data/data/evaluation_set.jsonl', 20)

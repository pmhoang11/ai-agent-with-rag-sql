import re
from typing import List

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
import config
from loguru import logger


def rerank_results(query: str, results: List[Document], k: int = 5) -> List[Document]:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=64
    )

    summaries = []

    for i, result in enumerate(results):
        origin_content = result.metadata.get("origin_content")
        contextualized_content = result.metadata.get("contextualized_content")
        if origin_content and contextualized_content:
            summary = f"[{i}] Document: {origin_content}\nContext: {contextualized_content}"
        else:
            summary = f"[{i}] Document: {result.page_content}"

        summaries.append(summary)
    joined_summaries = "\n\n".join(summaries)

    prompt = f"""
Query: {query}
You are about to be given a group of documents, each preceded by its index number in square brackets. Your task is to select the only {k} most relevant documents from the list to help us answer the query.

<documents>
{joined_summaries}
</documents>

Output only the indices of {k} most relevant documents in order of relevance, separated by commas, enclosed in XML tags here:
<relevant_indices>put the numbers of your indices here, seeparted by commas</relevant_indices>
"""
    try:
        mess = [
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(mess)

        # Extract the indices from the response
        match = re.search(r"<relevant_indices>(.*?)</relevant_indices>", response.content)
        if match:
            indices_str = match.group(1)
            relevant_indices = list(map(int, indices_str.split(",")))
        # If we didn't get enough valid indices, fall back to the top k by original order
        else:
            relevant_indices = list(range(min(k, len(results))))

        # Ensure we don't have out-of-range indices
        relevant_indices = [idx for idx in relevant_indices if idx < len(results)]

        # Return the reranked results
        reranked_results = [results[idx] for idx in relevant_indices[:k]]

        return reranked_results

    except Exception as e:
        logger.error(f"An error occurred during reranking: {str(e)}")
        # Fall back to returning the top k results without reranking
        return results[:k]

import os
import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are a helpful assistant.
You must follow these rules strictly:

1. ONLY answer based on the information provided in the context below
2. If the context does not contain information to answer the question, say "This information is not available in the provided context"
3. Do NOT make up, assume, or infer information that is not explicitly stated in the context
4. Be concise and direct in your answers
5. Do NOT add extra information or explanations beyond what is asked

Context from UG Student Handbook:
{context}

---

Question: {question}

Answer (based only on the context above):"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def generate_followup_questions(context_text: str, current_response: str, db, max_questions: int = 3) -> list[str]:
    """Generate follow-up questions based on the context and current response."""
    prompt = f"""Based on the following context and response, generate {max_questions} specific follow-up questions 
    that can be answered from the context. The questions should be directly answerable from the context.
    
    Context:
    {context_text}
    
    Current Response:
    {current_response}
    
    Generate exactly {max_questions} follow-up questions in the following format:
    1. First question?
    2. Second question?
    3. Third question?"""
    
    model = OllamaLLM(model="deepseek-r1:1.5b")
    questions_text = model.invoke(prompt)
    
    # Extract questions from the response
    questions = []
    for line in questions_text.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
            # Remove number/bullet point and any following punctuation/whitespace
            question = line[line.find(' ')+1:].lstrip('.- ')
            if question and question[0].isupper() and question.endswith('?'):
                # Verify the question can be answered from the context
                results = db.similarity_search(question, k=1)
                if results and len(results[0].page_content) > 20:  # Simple check for relevant content
                    questions.append(question)
                    if len(questions) >= max_questions:
                        break
    
    return questions

def query_rag(query_text: str, db_path: str, get_followups: bool = False):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=db_path, embedding_function=embedding_function)

    # Get more context for better follow-up questions
    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    import re
    def remove_think_blocks(text):
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    model = OllamaLLM(model="deepseek-r1:1.5b")
    response_text = model.invoke(prompt)
    response_text = remove_think_blocks(response_text)
    cleaned_response = re.sub(r"^\s*Answer:.*$", "", response_text, flags=re.MULTILINE).strip()

    reference_map = {}
    
    answer_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_response) if s.strip()]
    
    for i, sentence in enumerate(answer_sentences[:3]):  # Limit to first 3 sentences for references
        # Search for chunks most similar to this sentence
        sentence_results = db.similarity_search_with_score(sentence, k=1)
        
        if not sentence_results:
            continue
            
        doc, score = sentence_results[0]
        if score > 0.8:  
            continue
            
        meta = doc.metadata
        source_file = os.path.basename(meta.get("source", "?"))
        
        if source_file.lower().endswith('.pdf'):
            source_file = source_file[:-4]
            
        if any(x in source_file.lower() for x in ['prologue', 'table of contents', 'index']):
            continue
            
        try:
            page = int(meta.get("page", 0)) + 1
        except (ValueError, TypeError):
            page = meta.get("page", 1)
            
        ref_text = f"page {page}"
        
        if ref_text not in reference_map.values():
            ref_num = len(reference_map) + 1
            reference_map[ref_num] = ref_text
        
        # Add reference number to the sentence in the answer
        answer_sentences[i] = f"{sentence} [{ref_num}]"
    
    # Rebuild the response with reference numbers
    cleaned_response = ' '.join(answer_sentences)
    
    # Add references section at the bottom if we have any
    if reference_map:
        cleaned_response += "\n\nReferences:\n"
        for num, ref in reference_map.items():
            cleaned_response += f"[{num}] {ref}\n"
    
    # Generate follow-up questions if requested
    followup_questions = []
    if get_followups and len(cleaned_response) > 0:
        try:
            followup_questions = generate_followup_questions(context_text, cleaned_response, db)
        except Exception as e:
            print(f"Error generating follow-up questions: {str(e)}")
    
    return {
        "response": cleaned_response,
        "followup_questions": followup_questions
    }


if __name__ == "__main__":
    main()

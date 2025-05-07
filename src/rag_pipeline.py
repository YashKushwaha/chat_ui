from src.llms import extract_tags_from_text

def generate_answer(question, embedder, vectorstore, llm):
    query_embedding = embedder.embed(question)
    relevant_chunks = vectorstore.retrieve(query_embedding)
    context = "\n".join(
        [f"Source: {doc['metadata'].get('source_file', 'unknown')}\n{doc['text']}" for doc in relevant_chunks]
    )
    prompt = f"Answer the question using the context below:\nContext:\n{context}\n\nQuestion: {question}"
    response = llm.generate(prompt)
    return response

def generate_answer_with_filtering(question, embedder, vectorstore, llm): 
    query_embedding = embedder.embed(question)
    filter_dict = {"tags": extract_tags_from_text(question, llm) }
    print(filter_dict)

    relevant_chunks_with_no_filtering = vectorstore.retrieve(query_embedding)
    relevant_chunks = vectorstore.retrieve(query_embedding, filter=filter_dict)
    
    #

    context = "\n".join(
        [f"Source: {doc['metadata'].get('source_file', 'unknown')}\n{doc['text']}" for doc in relevant_chunks]
    )

    context_wo_filtering = "\n".join(
        [f"Source: {doc['metadata'].get('source_file', 'unknown')}\n{doc['text']}" for doc in relevant_chunks_with_no_filtering]
    )
    if context == context_wo_filtering:
        print('No advantage to filtering')

    print(5*'==')
    prompt = f"Answer the question using the context below:\nContext:\n{context}\n\nQuestion: {question}"
    response = llm.generate(prompt)
    return response


def format_history(history):
    return "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history])

def generate_answer_with_history(question, embedder, vectorstore, llm, chat_history=None):
    query_embedding = embedder.embed(question)
    relevant_chunks = vectorstore.retrieve(query_embedding)
    context = "\n".join(
        [f"Source: {doc['metadata'].get('source_file', 'unknown')}\n{doc['text']}" for doc in relevant_chunks]
    )

    history_text = ""

    if chat_history:
            for message in chat_history:
                history_text += f"{message['role'].capitalize()}: {message['content']}\n"

    prompt = (
        f"You are a helpful assistant.\n"
        f"{history_text}\n\n"
        f"Answer the question using the context below:\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )
    response = llm.generate(prompt)
    return response

def generate_answer_with_image(question, image_path, text_embedder, image_embedder,vectorstore, llm, chat_history=None):
    system_prompt = 'You are a helpful assistant'
    image_embeddings = image_embedder(image_path)    
    prompt = f"{system_prompt}\nUSER:<image_embeddings>\n{question}\nASSISTANT:"
    response = llm.generate(image_embeddings=image_embeddings, prompt=prompt)
    return response

def explain_image_pipeline(question, image_embedder, image_path, llm):
    image = image_embedder.embed(image_path)    
    system_prompt = 'You are a helpful assistant'
    #prompt = f'{system_prompt}\nUSER:<image>\n{question}\nASSISTANT'
    prompt = question  
    response = llm.generate(prompt, image)
    return response


def image_generation_pipeline(question, llm):

    response = llm.generate(question)
    print('response -> ', response)
    return response


from string import Template
### RAG PROMPTS ###

system_prompt = Template("\n".join(["You are a highly intelligent AI assistant that helps people find information efficiently",
                 " Use the provided context to answer the user's question accurately and concisely.",
                  " If the context does not contain relevant information, respond with 'I'm sorry, I couldn't find any relevant information to answer your question.'"]))

document_prompt = Template("\n".join([
    "## Document: $doc_num",
    "### Content: $chunk_text"]))


footer_prompt = Template("\n".join(["Based on the above documents, answer the following question:",
                                    "## Question: $user_question",
                                    "## Answer:"]))
                                    
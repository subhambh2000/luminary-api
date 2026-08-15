import logging
from typing import AsyncGenerator, cast

from groq import AsyncGroq, AsyncStream
from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionChunk

from app.config import settings
from app.services.session_store import Message

def build_context(chunks: list[dict]) -> str:
    logging.debug(f"Building context from {len(chunks)} chunks")
    context = "\n\n---\n\n".join(
        [
            f"Source: {chunk["source_file"]} - {chunk["header_path"]} \n {chunk["content"]}"
            for chunk in chunks
        ]
    )

    logging.debug(f"Context built successfully. Total size: {len(context)} characters")
    return context


def build_prompt(
        question: str,
        context: str
) -> tuple[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]:
    system_prompt = """
    You are a helpful assitant that answers questions based on the user's personal Obsidian notes.
    You will only use information present in the provided context.
    If the answer is not in the context, you should say so clearly rather than guessing.
    If you are unable to find the answer from the provided context, you should respond that you don't know,
    instead of giving guessing and providing assumption based answer.
    
    Also, answer the question in a conversational style, no need to explicitly give the content from the context or notes file directly.
    If someone greets you or says hi, greet them back, reply with hi, hello or other suitable words.
    Cite the source file used for refering to specific information but just provide the source names at the end or bottom.
    For generic questions like - "Hi, what can you help with" or similar type, no need to mention source.
    If the source has _about.md, don't mention that. Definitely mention the other ones. 
    The response should be like an answer to a question or a explanation to a query, not like a copy paste of source text.
    """

    user_message = f"""
    Context:
    {context}
    
    Question: {question}
    """
    system_prompt = ChatCompletionSystemMessageParam(role="system", content=system_prompt)
    user_message = ChatCompletionUserMessageParam(role="user", content=user_message)
    return system_prompt, user_message


async def generate(
        client: AsyncGroq,
        model: str,
        question: str,
        chunks: list[dict],
        history: list[Message]
) -> AsyncGenerator[str, None]:
    logging.debug(f"Generating response for question: {question}")
    logging.debug(f"Number of chunks received: {len(chunks)}")
    context = build_context(chunks)
    logging.debug(f"Context length: {len(context)} characters")
    if not context:
        yield "I couldn't find any relevant information in your notes for this question"
        return

    (system_prompt, user_message) = build_prompt(question, context)

    if not model:
        yield "model not provided"
        return

    logging.debug(f"Calling Groq API with model: {model}, max_tokens: {model}, temperature: {model}")

    response = cast(
        AsyncStream[ChatCompletionChunk],
        await client.chat.completions.create(
            model=model,
            messages=[system_prompt, *(history or []), user_message],
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            stream=True
        ))

    complete_response = ""
    finish_reason = ""
    async for chunk in response:
        choice = chunk.choices[0]
        token = choice.delta.content
        if token is not None:
            complete_response += token
            yield token

        if choice.finish_reason is not None:
            finish_reason = choice.finish_reason

    if finish_reason == "length":
        yield "\n[Warning: response was cut off — consider increasing MAX_TOKENS]"

    logging.debug(
        f"Response generation complete. Length: {len(complete_response)} characters, Finish reason: {finish_reason}")
    return

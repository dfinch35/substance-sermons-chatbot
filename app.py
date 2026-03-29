import chainlit as cl
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from dotenv import load_dotenv
import textwrap


load_dotenv()

@cl.on_chat_start
async def start():
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_collection("substance_knowledge")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    
    llm = Anthropic(
        model="claude-4-6-sonnet-2026-03-14", 
        temperature=0.2,
        max_tokens=1024
    )
    
    query_engine = index.as_chat_engine(
        llm=llm,
        similarity_top_k=8,
        response_mode="compact",   # or "tree_summarize" for longer answers
        system_prompt="""
        You are a warm, encouraging, biblically faithful chatbot for Substance Church and Pastor Peter Haas.
        Answer ONLY using content from his blog posts and Substance Church sermons.
        Always preserve Pastor Peter's approachable, slightly humorous, deeply pastoral tone.
        When referencing a sermon, include its title and date.
        Be accurate — never add doctrine or hallucinate.
        """
    )
    
    cl.user_session.set("query_engine", query_engine)

@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get("query_engine")
    response = await cl.make_async(query_engine.chat)(message.content)
    
    # Build rich source elements with date + YouTube link
    source_elements = []
    
    for idx, node in enumerate(response.source_nodes):
        metadata = node.metadata
        source_type = metadata.get("type", "unknown")
        
        if source_type == "sermon":
            title = metadata.get("title", "Substance Church Sermon")
            sermon_date = metadata.get("date", "Unknown date")
            youtube_url = metadata.get("source_url", "")
            
            # Create a clean source card
            source_text = f"**{title}**  \n"
            source_text += f"**Date:** {sermon_date}  \n"
            
            if youtube_url:
                source_text += f"[Watch on YouTube]({youtube_url})"
            
            # Add a short relevant excerpt (first 300 chars) as context
            excerpt = textwrap.shorten(node.text, width=300, placeholder="...")
            if excerpt:
                source_text += f"\n\n**Relevant excerpt:**\n{excerpt}"
            
            element = cl.Text(
                content=source_text,
                name=f"Source {idx+1}: {title}",
                display="side"   # or "inline"
            )
            source_elements.append(element)
            
        elif source_type == "blog":
            title = metadata.get("title", "Pastor Peter Haas Blog")
            url = metadata.get("source", metadata.get("url", ""))
            source_text = f"**{title}** (Blog Post)"
            if url:
                source_text += f"\n[Read the full post]({url})"
            element = cl.Text(content=source_text, name=f"Blog Source {idx+1}")
            source_elements.append(element)
    
    # Send the main response + sources
    await cl.Message(
        content=response.response,
        elements=source_elements
    ).send()

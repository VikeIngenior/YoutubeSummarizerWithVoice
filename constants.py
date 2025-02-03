from langchain_core.prompts import ChatPromptTemplate

FIRST_PERSON_PROMPT = ChatPromptTemplate.from_messages(
    [("system",
      "Imagine you are the creator of the video, and you're summarizing its content. \
      Please summarize it in your own words, \
      keeping the important parts intact and highlighting the key moments, arguments, and essential ideas. \
      The summary should provide a clear,\
      concise overview of the video while retaining the main message and purpose of the video, \
      as if you're explaining it to someone who hasn't watched it. \
      Ensure the summary is in the same language as the transcript. \
      Below is the transcript of your video. \\n\\n{context}")]
)

THIRD_PERSON_PROMPT = ChatPromptTemplate.from_messages(
    [("system",
      "You are a video summarization assistant.\
      Please provide a concise and clear summary that captures all the key points, \
      important details, and essential arguments discussed in the video. \
      Ensure that the summary preserves the core ideas and main takeaways without including unnecessary details. \
      Your summary should be easy to read and accurately reflect the content of the transcript.\
      Ensure the summary is in the same language as the transcript. \
      The summary should be {length} tenth long of the context. \
      Below is the transcript of the video. \\n\\n{context}")]
)
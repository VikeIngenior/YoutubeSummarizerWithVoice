# 🎥 Youtube Video Summarizer
This project is a Youtube Video Summarization and Video Q&A System using various tools. 
Using <b>LangChain</b>’s <i>document_loaders</i> module and the <i>YoutubeLoader</i> class, 
the system extracts video transcripts and processes them with a preferred language model such as GPT-4o mini, Claude, Gemini, or DeepSeek to generate a concise summary. 
The summarized text is then converted into speech using <b>OpenAI’s tts-1</b> model, providing an audio version of the summary.
Lastly, a simple RAG system (with memory) is integrated using <b>LangChain</b> and <b>Chroma</b> vector database, allowing users to chat with the video content.

## 🚀 Features
<ul>
  <li>Multilingual Support: English, Turkish, German, French, Spanish</li>
  <li>Model Selection: Gpt 4o Mini, Claude 3 Opus, Gemini 2.0 Flash, </li>
  <li>Summary Type: If the video features a single person talking about themselves, the summary can be generated in the first person.</li>
  <li>Summary Length: Short or Long</li>
  <li>Audio Summary</li>
  <li>Q&A System with Chat History</li>
</ul>

## 🛠 Setup
### Clone the repository
<ul>
  <li><code>git clone https://github.com/VikeIngenior/YoutubeSummarizerWithVoice.git</code></li>
  <li><code>cd YoutubeSummarizerWithVoice</code></li>
</ul>

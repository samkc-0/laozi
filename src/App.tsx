import versesSource from "../data/laozi.json";
import "./index.css";

const sentenceBreaks = /[。！？；]/u;
const stripPunctuation = /[，。、！？；：]/gu;

const verses = (versesSource as string[]).map((text, index) => {
  const sentences = text
    .trim()
    .split(sentenceBreaks)
    .map(sentence => sentence.replace(stripPunctuation, "").replace(/\s+/gu, "").trim())
    .filter(Boolean)
    .map(sentence => Array.from(sentence));

  return {
    id: index + 1,
    sentences,
  };
});

export function App() {
  return (
    <main className="reader" aria-label="道德經">
      <div className="reader-track">
        {verses.map(chapter => (
          <article className="chapter" key={chapter.id}>
            <div className="chapter-text" role="text">
              {chapter.sentences.map((sentence, sentenceIndex) => (
                <span className="sentence" key={`${chapter.id}-${sentenceIndex}`}>
                  {sentence.map((character, characterIndex) => (
                    <span className="character" key={`${chapter.id}-${sentenceIndex}-${characterIndex}`}>
                      {character}
                    </span>
                  ))}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}

export default App;

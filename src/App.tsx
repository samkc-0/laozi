import { useState } from "react";
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
  const [hovered, setHovered] = useState<{
    chapterId: number;
    sentenceIndex: number;
    characterIndex: number;
    character: string;
    x: number;
    y: number;
  } | null>(null);

  return (
    <main className="reader" aria-label="道德經">
      <div className="reader-track">
        {verses.map(chapter => (
          <article className="chapter" key={chapter.id}>
            <div
              className="chapter-text"
              role="text"
              onMouseLeave={() => setHovered(current => (current?.chapterId === chapter.id ? null : current))}
            >
              {chapter.sentences.map((sentence, sentenceIndex) => (
                sentence.map((character, characterIndex) => {
                  const isSentenceHovered =
                    hovered?.chapterId === chapter.id && hovered.sentenceIndex === sentenceIndex;
                  const isCharacterHovered = isSentenceHovered && hovered.characterIndex === characterIndex;

                  return (
                    <span
                      className={[
                        "character",
                        isSentenceHovered ? "is-sentence-hovered" : "",
                        isCharacterHovered ? "is-character-hovered" : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      key={`${chapter.id}-${sentenceIndex}-${characterIndex}`}
                      onMouseEnter={event => {
                        const rect = event.currentTarget.getBoundingClientRect();

                        setHovered({
                          chapterId: chapter.id,
                          sentenceIndex,
                          characterIndex,
                          character,
                          x: Math.min(rect.left + 28, window.innerWidth - 300),
                          y: Math.min(rect.bottom + 16, window.innerHeight - 180),
                        });
                      }}
                    >
                      {character}
                    </span>
                  );
                })
              ))}
            </div>
          </article>
        ))}
      </div>
      {hovered ? (
        <aside
          className="character-popup"
          style={{
            left: `${Math.max(16, hovered.x)}px`,
            top: `${Math.max(16, hovered.y)}px`,
          }}
        >
          <p className="popup-character">{hovered.character}</p>
          <p className="popup-pinyin">placeholder pinyin</p>
          <p className="popup-definition">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
            labore et dolore magna aliqua.
          </p>
        </aside>
      ) : null}
    </main>
  );
}

export default App;

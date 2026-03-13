import { useEffect, useRef, useState } from "react";
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
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const [hovered, setHovered] = useState<{
    chapterId: number;
    sentenceIndex: number;
    characterIndex: number;
    character: string;
  } | null>(null);

  useEffect(() => {
    const scroller = scrollerRef.current;

    if (!scroller) {
      return;
    }

    scroller.scrollLeft = scroller.scrollWidth - scroller.clientWidth;
  }, []);

  return (
    <main className="reader-shell" aria-label="道德經">
      <div className="reader" ref={scrollerRef}>
        <div className="reader-track">
          {verses.map((chapter, chapterIndex) => (
            <article
              className="chapter"
              key={chapter.id}
            >
              <div
                className="chapter-text"
                role="text"
                onMouseLeave={() => setHovered(current => (current?.chapterId === chapter.id ? null : current))}
              >
                {chapter.sentences.map((sentence, sentenceIndex) =>
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
                        onMouseEnter={() => {
                          setHovered({
                            chapterId: chapter.id,
                            sentenceIndex,
                            characterIndex,
                            character,
                          });
                        }}
                      >
                        {character}
                      </span>
                    );
                  })
                )}
              </div>
            </article>
          ))}
        </div>
      </div>

      <aside className="character-popup" aria-live="polite">
        <p className="popup-character">{hovered?.character ?? "道"}</p>
        <p className="popup-pinyin">placeholder pinyin</p>
        <p className="popup-definition">
          {hovered
            ? "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
            : "Hover a character to inspect it here. Lorem ipsum dolor sit amet, consectetur adipiscing elit."}
        </p>
      </aside>
    </main>
  );
}

export default App;

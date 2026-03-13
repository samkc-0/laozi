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
  const [pinned, setPinned] = useState<{
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

  const activeSelection = pinned ?? hovered;
  const pinnedSentence =
    pinned ? verses[pinned.chapterId - 1]?.sentences[pinned.sentenceIndex]?.join("") ?? "" : "";

  return (
    <main className="reader-shell" aria-label="道德經">
      <aside className="pinned-sentence" aria-live="polite">
        <p>{pinnedSentence}</p>
      </aside>

      <div className="reader" ref={scrollerRef}>
        <div className="reader-track">
          {verses.map(chapter => (
            <article className="chapter" key={chapter.id}>
              <div
                className="chapter-text"
                role="text"
                onMouseLeave={() => setHovered(null)}
              >
                {chapter.sentences.map((sentence, sentenceIndex) =>
                  sentence.map((character, characterIndex) => {
                    const isPinnedSentence =
                      pinned?.chapterId === chapter.id && pinned.sentenceIndex === sentenceIndex;
                    const isPinnedCharacter = isPinnedSentence && pinned.characterIndex === characterIndex;
                    const isHoveredSentence =
                      hovered?.chapterId === chapter.id && hovered.sentenceIndex === sentenceIndex;
                    const isHoveredCharacter = isHoveredSentence && hovered.characterIndex === characterIndex;

                    return (
                      <span
                        className={[
                          "character",
                          isPinnedSentence ? "is-pinned-sentence" : "",
                          isPinnedCharacter ? "is-pinned-character" : "",
                          isHoveredSentence ? "is-hovered-sentence" : "",
                          isHoveredCharacter ? "is-hovered-character" : "",
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
                        onClick={() => {
                          setPinned(current =>
                            current?.chapterId === chapter.id &&
                            current.sentenceIndex === sentenceIndex &&
                            current.characterIndex === characterIndex
                              ? null
                              : {
                                  chapterId: chapter.id,
                                  sentenceIndex,
                                  characterIndex,
                                  character,
                                }
                          );
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
        <p className="popup-character">{activeSelection?.character ?? ""}</p>
        <p className="popup-pinyin">{activeSelection ? "placeholder pinyin" : ""}</p>
        <p className="popup-definition">
          {activeSelection
            ? "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
            : ""}
        </p>
      </aside>
    </main>
  );
}

export default App;

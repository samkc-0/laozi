import { useEffect, useRef, useState } from "react";
import versesSource from "../data/laozi.json";
import "./index.css";

const sentenceBreaks = /[。！？；]/u;
const stripPunctuation = /[，。、！？；：]/gu;

const verses = (versesSource as string[]).map((text, index) => {
  const sentences = text
    .trim()
    .split(sentenceBreaks)
    .map((sentence) =>
      sentence.replace(stripPunctuation, "").replace(/\s+/gu, "").trim(),
    )
    .filter(Boolean)
    .map((sentence) => Array.from(sentence));

  return {
    id: index + 1,
    sentences,
  };
});

function clampChapter(value: number) {
  return Math.min(verses.length, Math.max(1, value));
}

function toChineseNumeral(value: number) {
  const digits = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"];

  if (value <= 10) {
    return value === 10 ? "十" : digits[value];
  }

  if (value < 20) {
    return `十${digits[value % 10]}`;
  }

  const tens = Math.floor(value / 10);
  const ones = value % 10;
  return `${digits[tens]}十${ones === 0 ? "" : digits[ones]}`;
}

export function App() {
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const chapterRefs = useRef<Array<HTMLElement | null>>([]);
  const [currentChapter, setCurrentChapter] = useState(1);
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

    let lastScrollLeft = scroller.scrollLeft;

    const handleScroll = () => {
      if (scroller.scrollLeft !== lastScrollLeft) {
        setPinned((current) => (current ? null : current));
        lastScrollLeft = scroller.scrollLeft;
      }
    };

    handleScroll();
    scroller.addEventListener("scroll", handleScroll, { passive: true });

    return () => scroller.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const scroller = scrollerRef.current;

    if (!scroller) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        let bestMatch: { chapter: number; ratio: number } | null = null;

        for (const entry of entries) {
          if (!entry.isIntersecting) {
            continue;
          }

          const chapter = Number(
            (entry.target as HTMLElement).dataset.chapter ?? "1",
          );

          if (!bestMatch || entry.intersectionRatio > bestMatch.ratio) {
            bestMatch = { chapter, ratio: entry.intersectionRatio };
          }
        }

        if (bestMatch) {
          setCurrentChapter((current) =>
            current === bestMatch!.chapter ? current : bestMatch!.chapter,
          );
        }
      },
      {
        root: scroller,
        threshold: [0.5, 0.66, 0.8, 0.95],
      },
    );

    for (const chapter of chapterRefs.current) {
      if (chapter) {
        observer.observe(chapter);
      }
    }

    return () => observer.disconnect();
  }, []);

  const activeSelection = pinned ?? hovered;
  const pinnedSentence = pinned
    ? (verses[pinned.chapterId - 1]?.sentences[pinned.sentenceIndex]?.join(
        "",
      ) ?? "")
    : "";

  return (
    <main className="reader-shell" aria-label="道德經">
      <aside className="pinned-sentence" aria-live="polite">
        <p>{pinnedSentence}</p>
      </aside>

      <div className="reader" ref={scrollerRef}>
        <div className="reader-track">
          {verses.map((chapter) => (
            <article
              className="chapter"
              key={chapter.id}
              data-chapter={chapter.id}
              ref={(node) => {
                chapterRefs.current[chapter.id - 1] = node;
              }}
            >
              <div
                className="chapter-text"
                role="text"
                onMouseLeave={() => setHovered(null)}
              >
                {chapter.sentences.map((sentence, sentenceIndex) =>
                  sentence.map((character, characterIndex) => {
                    const isPinnedSentence =
                      pinned?.chapterId === chapter.id &&
                      pinned.sentenceIndex === sentenceIndex;
                    const isPinnedCharacter =
                      isPinnedSentence &&
                      pinned.characterIndex === characterIndex;
                    const isHoveredSentence =
                      hovered?.chapterId === chapter.id &&
                      hovered.sentenceIndex === sentenceIndex;
                    const isHoveredCharacter =
                      isHoveredSentence &&
                      hovered.characterIndex === characterIndex;

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
                          setPinned((current) =>
                            current?.chapterId === chapter.id &&
                            current.sentenceIndex === sentenceIndex &&
                            current.characterIndex === characterIndex
                              ? null
                              : {
                                  chapterId: chapter.id,
                                  sentenceIndex,
                                  characterIndex,
                                  character,
                                },
                          );
                        }}
                      >
                        {character}
                      </span>
                    );
                  }),
                )}
              </div>
            </article>
          ))}
        </div>
      </div>

      <aside className="character-popup" aria-live="polite">
        <p className="popup-character">{activeSelection?.character ?? ""}</p>
        <p className="popup-pinyin">
          {activeSelection ? "placeholder pinyin" : ""}
        </p>
        <p className="popup-definition">
          {activeSelection
            ? "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
            : ""}
        </p>
      </aside>

      <div className="chapter-indicator" aria-live="polite">
        {toChineseNumeral(currentChapter)}
      </div>
    </main>
  );
}

export default App;

"""Text metrics of a narration script (one sentence per line, optional "[m:ss] " prefix).
python script_metrics.py script.txt [--minutes 14.9]
Prints: words, sentences, words/sentence, short sentences (<=4 words), you/your per 100 words, numbers per minute,
question marks, "imagine/picture" imperatives, transition openers (But / And / So / Meaning), top emotion words.
"""
import re, sys, collections

EMOTION = ["terrif", "nightmare", "shock", "death", "die", "dead", "fear", "afraid", "suffocat", "trap", "secret", "precious",
           "treasure", "irony", "ironic", "strange", "amazing", "impossible", "victory", "agony", "blood", "cram", "escape"]
TRANSITIONS = ["but", "and", "so", "meaning", "because", "yet", "now", "here", "that is why", "this takes us", "imagine", "let's", "come on"]

def metrics(path, minutes=None):
    lines = [re.sub(r"^\[\d+:\d\d\]\s*", "", l).strip() for l in open(path, encoding="utf-8") if l.strip()]
    text = " ".join(lines)
    words = re.findall(r"[A-Za-z’'\-]+", text)
    nw = len(words)
    lens = [len(re.findall(r"[A-Za-z’'\-]+", l)) for l in lines]
    you = sum(1 for w in words if w.lower() in ("you", "your", "yours", "yourself"))
    we = sum(1 for w in words if w.lower() in ("we", "our", "us"))
    nums = re.findall(r"\b\d[\d,\.]*\b", text)
    questions = sum(1 for l in lines if l.endswith("?"))
    imper = sum(1 for l in lines if re.match(r"^(Try|Imagine|Picture|Listen|Stand|Look|Think|Remember|Let’s|Let's|Come on|Close|Open)\b", l))
    openers = collections.Counter()
    for l in lines:
        for t in TRANSITIONS:
            if l.lower().startswith(t):
                openers[t] += 1; break
    emo = collections.Counter()
    for w in words:
        for e in EMOTION:
            if w.lower().startswith(e):
                emo[e] += 1
    out = {
        "words": nw, "sentences": len(lines), "words_per_sentence": round(nw / max(1, len(lines)), 1),
        "sentences_le4_words_pct": round(100 * sum(1 for L in lens if L <= 4) / max(1, len(lens)), 1),
        "sentences_ge25_words_pct": round(100 * sum(1 for L in lens if L >= 25) / max(1, len(lens)), 1),
        "you_per_100w": round(100 * you / max(1, nw), 1), "we_per_100w": round(100 * we / max(1, nw), 1),
        "numbers": len(nums), "questions": questions, "imperative_openers": imper,
        "transition_openers": dict(openers.most_common(8)), "emotion_words": dict(emo.most_common(10)),
    }
    if minutes:
        out["wpm"] = round(nw / minutes, 1); out["numbers_per_min"] = round(len(nums) / minutes, 1)
    return out

if __name__ == "__main__":
    p = sys.argv[1]
    m = float(sys.argv[sys.argv.index("--minutes") + 1]) if "--minutes" in sys.argv else None
    for k, v in metrics(p, m).items():
        print(f"{k}: {v}")

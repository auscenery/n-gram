import kenlm
import sys
import jiagu

if __name__ == "__main__":
    sentence = sys.argv[1]
    arpa_path = sys.argv[2]
    model = kenlm.Model(arpa_path)
    print(sentence)
    sentence = " ".join(jiagu.seg(sentence))
    print(sentence)
    print(model.score(sentence, bos = True, eos = True))
    result = model.full_scores(sentence, bos = True, eos = True)
    for e in result:
       print(e)
    print(model.perplexity(sentence))

from itertools import chain
from functools import reduce

from django.db.models import Q

from firstaid.models import Tip
from utils.helpers import save_in_redis, get_from_redis


def run_search(query):
    stopwords = get_from_redis('stopwords', None)
    if not stopwords:
        stopwords = load_stopwords()
    tokens_with_stopwords = set(query.split())
    tokens = tokens_with_stopwords.difference(set(stopwords))
    tips = Tip.objects.filter(
        reduce(lambda x, y: x | y,
               [Q(ailment__icontains=token)
                | Q(symptoms__icontains=token)
                | Q(causes__icontains=token)
                for token in tokens]
               )
    )

    tips_and_scores = []
    for tip in tips:
        symptoms = set(tip.symptoms.split())
        tokens = set(tokens)
        tokens_present = symptoms.intersection(tokens)
        score = len(tokens_present)
        tips_and_scores.append((tip, score))
    tips_and_scores.sort(key=lambda x: x[1], reverse=True)
    results = [tip_and_score[0] for tip_and_score in tips_and_scores]
    return results


def load_stopwords():
    with open('firstaid/utils/stopwords.txt') as file:
        words = [line.replace('\n', '') for line in file]
    save_in_redis('stopwords', words, 60 * 60 * 24)
    return words

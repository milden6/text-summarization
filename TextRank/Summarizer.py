from math import log10

from .PageRankWeighted import pagerank_weighted_scipy as _pagerank
from .Utils.TextCleaner import clean_text_by_sentences as _clean_text_by_sentences
from .Commons import build_graph as _build_graph
from .Commons import remove_unreachable_nodes as _remove_unreachable_nodes


def _set_graph_edge_weights(graph):
    for sentence_1 in graph.nodes():
        for sentence_2 in graph.nodes():

            edge = (sentence_1, sentence_2)
            if sentence_1 != sentence_2 and not graph.has_edge(edge):
                similarity = _get_similarity(sentence_1, sentence_2)
                if similarity != 0:
                    graph.add_edge(edge, similarity)

    # Обрабатывает случай, когда все сходства равны нулю.
    # Итоговое резюме будет состоять из случайных предложений.
    if all(graph.edge_weight(edge) == 0 for edge in graph.edges()):
        _create_valid_graph(graph)


def _create_valid_graph(graph):
    nodes = graph.nodes()

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i == j:
                continue

            edge = (nodes[i], nodes[j])

            if graph.has_edge(edge):
                graph.del_edge(edge)

            graph.add_edge(edge, 1)


def _get_similarity(s1, s2):
    words_sentence_one = s1.split()
    words_sentence_two = s2.split()

    common_word_count = _count_common_words(words_sentence_one, words_sentence_two)

    log_s1 = log10(len(words_sentence_one))
    log_s2 = log10(len(words_sentence_two))

    if log_s1 + log_s2 == 0:
        return 0

    return common_word_count / (log_s1 + log_s2)


def _count_common_words(words_sentence_one, words_sentence_two):
    return len(set(words_sentence_one) & set(words_sentence_two))


def _format_results(extracted_sentences, split, score):
    if score:
        return [(sentence.text, sentence.score) for sentence in extracted_sentences]
    if split:
        return [sentence.text for sentence in extracted_sentences]
    return "\n".join([sentence.text for sentence in extracted_sentences])


def _add_scores_to_sentences(sentences, scores):
    for sentence in sentences:
        # Добавляет счет к объекту, если он есть.
        if sentence.token in scores:
            sentence.score = scores[sentence.token]
        else:
            sentence.score = 0


def _get_sentences_with_word_count(sentences, words):
    """ Учитывает список предложений, возвращает список предложений с
     общим количеством слов, аналогично предоставленному количеству слов.
    """
    word_count = 0
    selected_sentences = []
    # Цикл, пока не будет достигнуто количество слов.
    for sentence in sentences:
        words_in_sentence = len(sentence.text.split())

        # Проверяет, дает ли включение предложения лучшее приближение
        # к параметру слова.
        if abs(words - word_count - words_in_sentence) > abs(words - word_count):
            return selected_sentences

        selected_sentences.append(sentence)
        word_count += words_in_sentence

    return selected_sentences


def _extract_most_important_sentences(sentences, ratio, words):
    sentences.sort(key=lambda s: s.score, reverse=True)

    # Если не выбрана опция «слова», количество предложений
    # уменьшается на установленное соотношение.
    if words is None:
        length = len(sentences) * ratio
        return sentences[:int(length)]

    # Иначе, соотношение игнорируется.
    else:
        return _get_sentences_with_word_count(sentences, words)


def summarize(text, language, ratio=0.2, words=None, split=False, scores=False):
    if not isinstance(text, str):
        raise ValueError("Text parameter must be a Unicode object (str)!")

    # Получает список обработанных предложений.
    sentences = _clean_text_by_sentences(text, language)

    # Создает граф и рассчитывает коэффициент подобия для каждой пары узлов.
    graph = _build_graph([sentence.token for sentence in sentences])
    _set_graph_edge_weights(graph)

    # Удалите все узлы с весами всех ребер, равными нулю.
    _remove_unreachable_nodes(graph)

    # PageRank не может работать в пустом графе.
    if len(graph.nodes()) == 0:
        return [] if split else ""

    # Ранжирует токены, используя алгоритм PageRank. Возвращает словарь предложения -> оценок
    pagerank_scores = _pagerank(graph)

    # Добавляет итоговые оценки к объектам предложения.
    _add_scores_to_sentences(sentences, pagerank_scores)

    # Извлекает наиболее важные предложения с выбранным критерием.
    extracted_sentences = _extract_most_important_sentences(sentences, ratio, words)

    # Сортирует извлеченные предложения по порядку появления в исходном тексте.
    extracted_sentences.sort(key=lambda s: s.index)

    return _format_results(extracted_sentences, split, scores)


def get_graph(text):
    sentences = _clean_text_by_sentences(text)

    graph = _build_graph([sentence.token for sentence in sentences])
    _set_graph_edge_weights(graph)

    return graph

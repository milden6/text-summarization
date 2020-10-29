from .Graph import Graph
import numpy
import math

epsilon = 1e-4

def build_graph(sequence):
    graph = Graph()
    for item in sequence:
        if not graph.has_node(item):
            graph.add_node(item)
    return graph


def remove_unreachable_nodes(graph):
    for node in graph.nodes():
        if sum(graph.edge_weight((node, other)) for other in graph.neighbors(node)) == 0:
            graph.del_node(node)


def rate_sentences(document):
    matrix = create_matrix(document)
    ranks = power_method(matrix, epsilon)
    return {sent: rank for sent, rank in zip(document.sentences, ranks)}


def power_method(matrix, epsilon):
        transposed_matrix = matrix.T
        sentences_count = len(matrix)
        p_vector = numpy.array([1.0 / sentences_count] * sentences_count)
        lambda_val = 1.0

        while lambda_val > epsilon:
            next_p = numpy.dot(transposed_matrix, p_vector)
            lambda_val = numpy.linalg.norm(numpy.subtract(next_p, p_vector))
            p_vector = next_p

        return p_vector


def rate_sentences_edge(words1, words2):
    rank = sum(words2.count(w) for w in words1)
    if rank == 0:
        return 0.0

    assert len(words1) > 0 and len(words2) > 0
    norm = math.log(len(words1)) + math.log(len(words2))
    if numpy.isclose(norm, 0.):
        # This should only happen when words1 and words2 only have a single word.
        # Thus, rank can only be 0 or 1.
        assert rank in (0, 1)
        return float(rank)
    else:
        return rank / norm

def to_words_set(sentence):
    words = map(sentence.words.lower(), sentence.words)
    return [stem_word(w) for w in words if w not in stop_words]

def create_matrix(document):
    """Create a stochastic matrix for TextRank.
    Element at row i and column j of the matrix corresponds to the similarity of sentence i
    and j, where the similarity is computed as the number of common words between them, divided
    by their sum of logarithm of their lengths. After such matrix is created, it is turned into
    a stochastic matrix by normalizing over columns i.e. making the columns sum to one. TextRank
    uses PageRank algorithm with damping, so a damping factor is incorporated as explained in
    TextRank's paper. The resulting matrix is a stochastic matrix ready for power method.
    """
    sentences_as_words = [to_words_set(sent) for sent in document.sentences]
    sentences_count = len(sentences_as_words)
    weights = numpy.zeros((sentences_count, sentences_count))

    for i, words_i in enumerate(sentences_as_words):
        for j in range(i, sentences_count):
            rating = rate_sentences_edge(words_i, sentences_as_words[j])
            weights[i, j] = rating
            weights[j, i] = rating

    weights /= (weights.sum(axis=1)[:, numpy.newaxis] + _ZERO_DIVISION_PREVENTION)

    # In the original paper, the probability of randomly moving to any of the vertices
    # is NOT divided by the number of vertices. Here we do divide it so that the power
    # method works; without this division, the stationary probability blows up. This
    # should not affect the ranking of the vertices so we can use the resulting stationary
    # probability as is without any postprocessing.
    return numpy.full((sentences_count, sentences_count), (1. - damping) / sentences_count) \
       + damping * weights
# encoding=utf8
"""
Dette er et script for å gjøre statistisk mapping
"""
import h5py
import numpy as np
import re
from glob import glob
from time import time
from math import log
import csv
from rdflib.graph import Graph
from rdflib.namespace import OWL, RDF, DC, DCTERMS, FOAF, XSD, URIRef, Namespace, SKOS
from scipy.stats.contingency import chi2_contingency

print 'Load catalogue data'
h5f = h5py.File('hume_ddc.hdf5', 'r')
pairs = h5f['pairs'][:]
h5f.close()

unique_pairs = np.array([pair.split('!', 1) for pair in set(['!'.join(pair) for pair in pairs])])

# 1258837 pairs, 592948 unique pairs

# Count frequencies
print 'Count frequencies'
ac = {}
bc = {}
pc = {}
for pair in pairs:
    a, b = pair
    z = '!'.join(pair)
    ac[a] = ac.get(a, 0) + 1
    bc[b] = bc.get(b, 0) + 1
    pc[z] = pc.get(z, 0) + 1


def contigency_table(u, v):
    """
    Contigency table
          | u      | !u
    ------------------------
    v     | a00    | a01
    !v    | a10    | a11
    ------------------------

    where !u means "not u"
    """

    tot = pairs.shape[0]

    k = np.zeros((2, 2), dtype=np.uint16)
    k[0, 0] = pc['!'.join([u, v])]
    k[0, 1] = bc[v] - k[0, 0]
    k[1, 0] = ac[u] - k[0, 0]
    k[1, 1] = tot - k[0, 0] - k[0, 1] - k[1, 0]
    return k


def association_ratio(u, v):
    """
    Daille Balact (1994)[1]

    [1] Computational Linguistics Volume 16, Number 1, March 1990
        http://www.aclweb.org/anthology/J90-1003

    association ratio, close to the concept of mutual information
    introduced by [Church and Hanks, 1990]

        I(a,b) = \log_2\frac{P(ab)}{P(a)P(b)}
               = \log_2\frac{a}{(a+b)(a+c)}

    ~ Sannsynligheten P(ab) for at a og b opptrer sammen delt på sannsynlighetene
      P(a) for at a opptrer og P(b) for at b opptrer.
      Nullhypotesen er at P(ab) ~ P(a)P(b) og dermed I(a,b) ~ 0
    ~ Sannsynligheter P(x) finnes ved å telle antall ganger x opptrer
      og dele på antall ganger x kan opptre (antall par)

    Siden brøken <= 1 vil log-verdien være negativ.

    Since the association ratio becomes unstable when the
    counts are very small, we will not discuss word pairs with
    f(i,j) <= 5. An improvement would make use of t-scores,
    and throw out pairs that were not significant. Unfortunately,
    this requires an estimate of the variance off(x,y),

    When I(x, y) is large, the association ratio produces very
    credible results not unlike those reported in Palermo and
    Jenkins (1964)

    As a very rough rule; of thumb, we have observed that pairs
    with I(x, y) > 3 tend to be interesting, and pairs with smaller
    I(x, y) are generally not.

    Example:

        >>> association_ratio('Semantikk', '401.43')
        7.193355518769993

        >>> association_ratio('Semantikk', '415')
        5.093616053331041

        >>> association_ratio('Semantikk', '435')
        4.1475759248446655

    """
    if type(u) == unicode:
        u = u.encode('utf-8')
    if type(v) == unicode:
        v = v.encode('utf-8')

    no_assoc_value = 0

    k = contigency_table(u, v)
    Pab = float(k[0, 0]) / pairs.shape[0]
    Pa = float(k[0, 0] + k[0, 1]) / pairs.shape[0]
    Pb = float(k[0, 0] + k[1, 0]) / pairs.shape[0]

    if k[0, 0] <= 5:
        print "Unstable for freq <= 5, returning zero"
        return no_assoc_value

    den = Pa * Pb
    if den == 0:
        return no_assoc_value
    val = log(Pab / den, 2)

    return val


def loglike(u, v):
    """
    The Log likelihood function by Dunning (1993)[1] in the form given by Daille (1994)[2] and used by OCLC (2001)[3]

    [1] Dunning, “Accurate Methods for the Statistics of Surprise and Coincidence.”. Comput. Linguist. 19 (1993), 61-74
    [2] Daille, Beatrice. 1994. “Study and Implementation of Combined Techniques for Automatic Extraction of Terminology.” In The Balancing Act: Combining Symbolic and Statistical Approaches to Language. Proceedings of the Workshop 1 July 1994, New Mexico State University, Las Cruces, New Mexico. Bernardsville, NJ: Association for Computational Linguistics.
    [3] Diane Vizine-Goetz (2001) “Popular LCSH with Dewey Numbers”, J. Library Administration, 34:3-4, 293-300, DOI: 10.1300/J111v34n03_08

    Example:

        >>> loglike('Semantikk', '401.43')
        1606.7918067276478

        >>> loglike('Semantikk', '415')
        581.8043093271554

        >>> loglike('Semantikk', '435')
        56.54494120180607

    """
    if type(u) == unicode:
        u = u.encode('utf-8')
    if type(v) == unicode:
        v = v.encode('utf-8')

    a = pc['!'.join([u, v])]
    b = ac[u] - a
    c = bc[v] - a
    d = pairs.shape[0] - c - b - a
    # print a,b,c,d
    try:
        return a * log(a) + b * log(b) + c * log(c) + d * log(d) - (a + b) * log(a + b) - (a + c) * log(a + c) - (b + d) * log(b + d) - (c + d) * log(c + d) + (a + b + c + d) * log(a + b + c + d)
    except ValueError:
        # print 'Failed for ', u, v
        return 0


def pair_association(unique_pairs, test_statistic):
    t0 = time()
    ll = {}
    for pair in unique_pairs:
        z = '!'.join(pair)
        ll[z] = test_statistic(pair[0], pair[1])
    t1 = time()
    print t1 - t0, 'secs'
    return ll


def write_mappings():

    # Include all pairs:
    # ll = pair_association(unique_pairs, loglike)

    # Only pairs with frequency >= 5:
    unique_pars_5 = np.array([a.split('!') for a, b in pc.items() if b >= 5])

    ll = pair_association(unique_pars_5, loglike)

    print 'Write mappings'
    lls = sorted(ll.items(), key=lambda x: x[1])

    ww = np.array(ll.values())
    mn = ww.mean()

    print "- Mean LL is {:2f}".format(mn)
    print "- {:.2f} % is >= mean LL".format(float(ww[ww >= mn].shape[0]) / ww.shape[0])
    print "- {:.2f} % is < mean LL".format(float(ww[ww < mn].shape[0]) / ww.shape[0])

    # Whether to lookup DDC labels and add them to the mapping sheet
    addDdcLabels = False

    if addDdcLabels:
        # Load WebDewey data
        g = Graph()
        for x in glob('../../webdewey/DDK23/*.ttl'):
            print x
            g.load(x, format='turtle')

    fsj = re.compile('.*\(Form\)')
    with open('mappings.csv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        for x in lls[::-1]:
            if x[1] < mn:
                break

            q = x[0].split('!', 1)

            if fsj.match(q[0]):  # Utelat form
                continue

            if addDdcLabels:
                lab = g.preferredLabel(URIRef('http://dewey.info/class/' + q[1] + '/e23/'), labelProperties=[SKOS.prefLabel, SKOS.altLabel])
                if len(lab) != 0:
                    lab = lab[0][1].value
                else:
                    lab = '(no label)'
                # Term, Dewey, Dewey Caption, Loglike
                writer.writerow([q[0], q[1], lab.encode('utf-8'), x[1]])
            else:
                # Term, Dewey, Loglike
                writer.writerow([q[0], q[1], x[1]])


def check_single(c, voc=0, lim=1):
    """
    Find the most frequently occuring pair partners for any given term.
    Attributes:
        c   : the term
        voc : the vocabulary index
        lim : don't include pairs with frequency less than <lim>

    Example: For hume:'Semantikk', the most frequent partner is ddc:'401.43'
    (occuring on 381 documents), followed by ddc:'415' (220 documents) and so on...

        >>> check_single('Semantikk', 0, 10)
        [('401.43', 381)
         ('415', 220)
         ('401.4', 75)
         ('491.70143', 44)
         ('401', 44)
         ('430.143', 37)
         ('401.41', 31)
         ('440.143', 29)
         ('435', 29)
         ('445', 27)
         ('401.9', 25)
         ...]

    To start from a DDC number, use voc=1:

        >>> check_single('779.092', 1, 10)
    """
    if type(c) == unicode:
        c = c.encode('utf-8')
    s, d = np.unique(pairs[pairs[:, voc] == c][:, not voc], return_counts=True)
    if len(d) == 0:
        print '{}: No pairs found'.format(c)
        return []
    ff = d >= lim
    gg = np.argsort(d[ff])[::-1]

    if len(d[ff]) == 0:
        print '{}: No pairs found with frequency >= {}'.format(c, lim)
        return []

    # for x in zip(s[ff][gg], d[ff][gg]):
    #     print '({}, {}) : {}'.format(c, x[0], x[1])

    return zip(s[ff][gg], d[ff][gg])


def simple_test(term):
    x = []
    for q in check_single(term, 0, 5):
        ll = loglike(term, q[0])
        ar = association_ratio(term, q[0])
        x.append([u'({}, {})'.format(term, q[0]), q[1], ll, ar])

    x = sorted(x, cmp=lambda a, b: -cmp(a[2], b[2]))

    for a in x[:3]:
        print u'{:40s} {:5d} {:8.1f} {:6.1f}'.format(*a)

# (Verbalfraser, 415) : 17
# (Verbalfraser, 435) : 6


if __name__ == '__main__':
    write_mappings()


# docs['140107312']
# Out[3]: {'alpha': ['791.4372'], 'beta': ['Film', 'Filmanalyse']}

# Make list of *unique* objects, ddc and terms
# objs = list(set(dh['ddc'][:, 0].tolist()))
# alpha = list(set(dh['ddc'][:, 1].tolist()))
# beta = list(set(dh['hume'][:, 1].tolist()))
# print len(objs), len(alpha), len(beta)

# Datatype: 8-bit unsigned integer (0 to 255) burde holde eller?
# o_ab = np.zeros((len(alpha), len(beta)), dtype=np.uint8)
# o_a = np.zeros((len(alpha)), dtype=np.uint8)
# o_b = np.zeros((len(beta)), dtype=np.uint8)

# total = len(docs)
# progress = 0
# for id, doc in docs.items():
#     progress += 1
#     if progress % 10000 == 0:
#         print '{:.0%}'.format(float(progress) / total)

#     i = objs.index(id)
#     for x in doc['alpha']:
#         a = alpha.index(x)
#         o_a[a] += 1
#         for y in doc['beta']:
#             b = beta.index(y)
#             o_ab[a, b] += 1

#     for x in doc['beta']:
#         b = beta.index(x)
#         o_b[b] += 1

# print 'Antall par: %d' % (np.count_nonzero(o_ab))


# def find_candidate_mappings(pairs):

#     pairs_sorted = pairs.argsort()[::-1]
#     maxfreq = pairs[pairs_sorted[0]]
#     howmany = np.sum(pairs == maxfreq)

#     mappings = []
#     for q in range(howmany):
#         etreff = pairs[pairs_sorted[q]]
#         epop = pairs.sum()


#         vekt = float(etreff) / epop * (1 + 0.05 * epop)  # svak vekting av populasjonsstørrelse, slik at 2/2 gir høyere vekt enn 1/1, men 2/3 fremdeles gir lavere vekt enn 1/1.. osv..

#         if vekt >= minvekt:
#             # emne, klass, antall (e,k)-par, antall e
#             mappings.append({
#                 'emne': emner[e],
#                 'klass': klasser[pairs_sorted[q]],
#                 'emne_treff': etreff,
#                 'emne_populasjon': epop,
#                 'vekt': vekt
#             })

#             # a = np.arange(1,16, dtype=np.float)
#             # b = np.arange(1,16, dtype=np.float)
#             # c = (a[:, np.newaxis] / b) * (1. + 0.05*b)

#     return mappings


# for a in range(alpha):
#     for b in range(beta):
#         pair_freq = o_ab[a,b]
#         if pair_freq < 2:
#             continue
#         a_freq = float(o_a[a]) / len(alpha)
#         b_freq = float(o_b[b]) / len(beta)

#         log_likelihood(pair_freq, a_freq, b_freq)


#     emne = alpha[a]
#     q1 = o_a[a]
#     q2 = o_ab[a].sum()

#     b = find_related_b(o_ab[a])

#     print emne, q1, q2  # BUrde gi samme?


#     break

import subprocess
import os
from copy import deepcopy

# inputfile specifies the moses.ini, and we process moses.ini
# to get the feature weights for the decoding model.
def get_feature_weight(inputfile):
    openfile = open(inputfile, 'r')
    feature_weight = {}
    for line in openfile:
        if line == "[weight-t]\n":
            index = "tm"
            feature_weight[index] = []
            for line in openfile:
                if line == '\n':
                    break
                line = float(line[:-1])
                feature_weight[index].append(line)
        if line == "[weight-d]\n":
            index = "d"
            feature_weight[index] = []
            for line in openfile:
                if line == '\n':
                    break
                line = float(line[:-1])
                feature_weight[index].append(line)
        if line == "[weight-l]\n":
            index = "lm"
            feature_weight[index] = []
            for line in openfile:
                if line == '\n':
                    break
                line = float(line[:-1])
                feature_weight[index].append(line)
        if line == "[weight-w]\n":
            index = "w"
            feature_weight[index] = []
            for line in openfile:
                if line == '\n':
                    break
                line = float(line[:-1])
                feature_weight[index].append(line)
    return feature_weight

# This is the function process the line in n-best to get feature vector
def get_feature_vector(feature_line):
    items = feature_line.split(" ")
    for i in xrange(0, len(items)):
        if items[i][-1:] == ":":
            items[i] = items[i][:-1]
    feature_vector = {}
    for i in xrange(0, len(items)):
        if items[i] == 'd' or items[i] == 'lm' or items[i] == 'tm' or items[i] == 'w':
            index = items[i]
            feature_vector[index] = []
            i += 1
            while i<len(items) and items[i] != 'd' and items[i] != 'lm' and items[i] != 'tm' and items[i] != 'w':
                feature_vector[index].append(float(items[i]))
                i += 1
    return feature_vector

# Process the n-best list to get the translated candidate
# along with the feature vectors and scores
def proce_nbest_list(inputfile, n_len):
    openfile = open(inputfile, 'r')
    candidates_table = {}
    for line in openfile:
        elements = line.split('|||')
        # After spliting the sentence into several parts, We trim 
        # the space in front of and at back of the sentence
        for i in xrange(0, len(elements)):
            while elements[i][:1] == ' ':
                elements[i] = elements[i][1:]
            while elements[i][-1:] == ' ':
                elements[i] = elements[i][:-1]
        elements[0] = int(elements[0])
        elements[3] = float(elements[3])
        feature_vector = get_feature_vector(elements[2])
        if elements[0] not in candidates_table:
            candidates_table[elements[0]] = [(elements[1], feature_vector, elements[3])]
        elif elements[0] in candidates_table:
            candidates_table[elements[0]].append((elements[1], feature_vector, elements[3]))
    return candidates_table

# Calculate the bleu score for all the translation cadidates of 
# one sentence, and return the ranked list based on bleu score
def cal_bleu_score(hypothesis, bleu_file):
    bleu_ranking = []
    openfile = open(bleu_file)
    index = 0
    for i in xrange(0, len(hypothesis)):
        (candi_sen, feature, score) = hypothesis[i]
        bleu_score = 0
        for line in openfile:
             elements = line.split(' ||| ')
             bleu_score = float(elements[1])
             break
        if 0 == len(bleu_ranking):
            bleu_ranking = [(candi_sen, feature, bleu_score)]
        else:
            insert_index = 0
            while bleu_score < bleu_ranking[insert_index][2]:
                insert_index += 1
                if insert_index == len(bleu_ranking):
                    break
            bleu_ranking.insert(insert_index,(candi_sen, feature, bleu_score))
    return bleu_ranking

####################################################################
#                  test code. need delete.                         #
####################################################################
def test_bleu_score(hypothesis, ref_files):
    bleu_ranking = []
    out = open('bleu.txt', 'w')
    for i in xrange(0, len(hypothesis)):
        (candi_sen, feature, score) = hypothesis[i]
        bleu_score = score + 5*i
        if 0 == len(bleu_ranking):
            bleu_ranking = [(i, candi_sen, feature, bleu_score)]
        else:
            insert_index = 0
            while bleu_score < bleu_ranking[insert_index][3]:
                insert_index += 1
                if insert_index == len(bleu_ranking):
                    break
            bleu_ranking.insert(insert_index,(i, candi_sen, feature, bleu_score))
    for (index, sen, feat, score) in bleu_ranking:
        out.write(str(index))
        out.write('. ' + sen + str(score) + '\n')
    out.flush()
    out.close()
    return bleu_ranking

def linear_function(weight, hypothesis):
    out = open('new_weight.txt', 'w')
    new_ranking = []
    for i in xrange(0, len(hypothesis)):
        (candi_sen, feature, score) = hypothesis[i]
        new_score = cal_feat_score(feature, weight)
        if 0 == len(new_ranking):
            new_ranking = [(i, candi_sen, feature, new_score)]
        else:
            insert_index = 0
            while new_score < new_ranking[insert_index][3]:
                insert_index += 1
                if insert_index == len(new_ranking):
                    break
            new_ranking.insert(insert_index,(i, candi_sen, feature, new_score))
    for (index, sen, feat, score) in new_ranking:
        out.write(str(index))
        out.write('. ' + sen + str(score) + '\n')
    out.flush()
    out.close()
    return

####################################################################
#                  test code. need delete.                         #
####################################################################

# Learning the minimum margin for the candidate translations
def learning_margin(cand_ranking, feat_weight, top_r, bottom_k):
    ranking = []
    for i in xrange(0, len(cand_ranking)):
        (sen, feat, score) = cand_ranking[i]
        score = cal_feat_score(feat, feat_weight)
        if 0 == len(ranking):
            ranking = [(sen, feat, score)]
        else:
            insert_index = 0
            while score < ranking[insert_index][2]:
                insert_index += 1
                if insert_index == len(ranking):
                    break
            ranking.insert(insert_index,(sen, feat, score))
    cand_ranking = ranking
    margin = ranking[top_r-1][2] - ranking[len(ranking)-bottom_k][2]
    return margin

def cal_feat_score(feat_vec, feat_weight):
    score = 0
    for i in xrange(0, len(feat_vec['tm'])):
        score += feat_vec['tm'][i]*feat_weight['tm'][i]
    for i in xrange(0, len(feat_vec['lm'])):
        score += feat_vec['lm'][i]*feat_weight['lm'][i]
    for i in xrange(0, len(feat_vec['w'])):
        score += feat_vec['w'][i]*feat_weight['w'][i]
    for i in xrange(0, len(feat_vec['d'])):
        score += feat_vec['d'][i]*feat_weight['d'][i]
    return score

# Do the tuning to update the feature vector, golden_ranking defines
# the right ranking for the translation candidates 
def tuning_feature_weight(golden_ranking, feat_weight, top_r, bottom_k, margin):
    u_vec = []
    for i in xrange(0, len(golden_ranking)):
        u_vec.append(0)
    for i in xrange(0, top_r):
        for j in xrange(len(golden_ranking)-bottom_k, len(golden_ranking)):
            (cand_sen, top_feat, score) = golden_ranking[i]
            (cand_sen, bottom_feat, score) = golden_ranking[j]
            top_score = cal_feat_score(top_feat, feat_weight)
            bottom_score = cal_feat_score(bottom_feat, feat_weight)
            if (top_score - bottom_score) < margin:
                u_vec[i] += 0.01
                u_vec[j] -= 0.01
    for i in xrange(0, len(u_vec)):
        if u_vec[i] != 0:
            (sen, feat_vec, score) = golden_ranking[i]
            for j in xrange(0, len(feat_vec['tm'])):
                feat_weight['tm'][j] += u_vec[i]*feat_vec['tm'][j]
            for j in xrange(0, len(feat_vec['lm'])):
                feat_weight['lm'][j] += u_vec[i]*feat_vec['lm'][j]
            for j in xrange(0, len(feat_vec['w'])):
                feat_weight['w'][j] += u_vec[i]*feat_vec['w'][j]
            for j in xrange(0, len(feat_vec['d'])):
                feat_weight['d'][j] += u_vec[i]*feat_vec['d'][j]       
    return feat_weight

def copy_feat_weight(new_weight, feat_weight):
    new_weight['tm'] = []
    new_weight['lm'] = []
    new_weight['w'] = []
    new_weight['d'] = []
    for i in xrange(0, len(feat_weight['tm'])):
        new_weight['tm'].append( feat_weight['tm'][i])
    for i in xrange(0, len(feat_weight['lm'])):
        new_weight['lm'].append( feat_weight['lm'][i])
    for i in xrange(0, len(feat_weight['w'])):
        new_weight['w'].append(feat_weight['w'][i])
    for i in xrange(0, len(feat_weight['d'])):
        new_weight['d'].append(feat_weight['d'][i])

def uniform_feat_weight(feat_weight):
    total_value = 0
    for j in xrange(0, len(feat_weight['tm'])):
        total_value += feat_weight['tm'][j]
    for j in xrange(0, len(feat_weight['lm'])):
        total_value += feat_weight['lm'][j]
    for j in xrange(0, len(feat_weight['w'])):
        total_value += feat_weight['w'][j]
    for j in xrange(0, len(feat_weight['d'])):
        total_value += feat_weight['d'][j]

    for j in xrange(0, len(feat_weight['tm'])):
        feat_weight['tm'][j] /= total_value
    for j in xrange(0, len(feat_weight['lm'])):
        feat_weight['lm'][j] /= total_value
    for j in xrange(0, len(feat_weight['w'])):
        feat_weight['w'][j] /= total_value
    for j in xrange(0, len(feat_weight['d'])):
        feat_weight['d'][j] /= total_value

if __name__ == '__main__':
    import sys
    candidates_table = proce_nbest_list("NBestList", 100)
    print len(candidates_table)

    bleu_ranking = []
    for i in xrange(0, len(candidates_table)):
        bleu_file = "bleu_result/bleu_sentence"+str(i+1)
        bleu_ranking.append(cal_bleu_score(candidates_table[i],bleu_file))

    #print bleu_ranking[0][0][2]

    feature_weight = get_feature_weight("moses.ini")
    print feature_weight
    for itr in xrange(0,10):
        for i in xrange(0, len(candidates_table)):
            bleu_file = "bleu_result/bleu_sentence"+str(i+1)
            margin = learning_margin(candidates_table[i], feature_weight, 10, 10)
            tuning_feature_weight(bleu_ranking[i], feature_weight, 10, 10, margin)

    uniform_feat_weight(feature_weight)
    print feature_weight

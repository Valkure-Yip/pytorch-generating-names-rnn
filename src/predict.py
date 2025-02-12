from model import *
from data import *
import torch
import torch.autograd
import sys
import decimal
import numpy as np

EOS = n_letters-2
SOS = n_letters-1
# rnn = torch.load(sys.argv[1])
rnn = torch.load('char-rnn-generation1.pt')
beam_size = 8

def getSoftmaxIndex(top, j):
    return int(top[j]/n_letters)
def getLetterIndex(top, j):
    return int(top[j]%n_letters)

def sample(category):
    category_tensor = Variable(categoryTensor(category))
    input = [Variable(torch.LongTensor([SOS]))]
    hiddens = [rnn.initHidden()]*beam_size
    hprobs = [0]*beam_size
    names = ['']*beam_size
    outs = []
    scores = []
    iters = 0

    while len(input) > 0:

        probs = []

        for j in range(0, len(input)):
            output, hiddens[j] = rnn(category_tensor, input[j], hiddens[j])
            output += hprobs[j]
            probs.append(output.data)

        if len(probs) == 1:
            probs = probs[0]
        else:
            probs = torch.cat(probs)

        if iters != 0:
            howmany = len(input)
        else:
            howmany = beam_size

        topv, topi = probs.topk(howmany)
        topv, topi = topv.numpy(), topi.numpy()

        input = []
        old_names = list(names)
        old_hiddens = list(hiddens)
        old_hprobs = list(hprobs)
        hiddens = []
        names = []
        hprobs = []
        for j in range(howmany):
            if getLetterIndex(topi, j) != EOS:
                hiddens.append(old_hiddens[getSoftmaxIndex(topi, j)])
                names.append(old_names[getSoftmaxIndex(topi, j)] + all_letters[getLetterIndex(topi, j)])
                hprobs.append(float(topv[j]))
                input.append(Variable(torch.LongTensor([getLetterIndex(topi, j)])))
            else:
                candidate = old_names[getSoftmaxIndex(topi, j)]
                score = old_hprobs[getSoftmaxIndex(topi, j)] / len(candidate)
                outs.append(candidate)
                scores.append(score)
        iters+=1


    return outs, scores
for cat in all_categories:
    outs, scores = sample(cat)
    print('====== {}'.format(cat))
    for i in range(beam_size):
        print('{} {}'.format(outs[i], scores[i]))

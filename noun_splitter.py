# coding=utf-8
# Copyright 2020 Leo Kim and David Oh.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pycrfsuite
from joblib import Parallel, delayed, cpu_count


class NounSplitter:
    def __init__(self, model_path='./model/np2.crfsuite',  n_jobs=1):
        self.n_jobs = min(max(1, n_jobs), cpu_count())
        self.model_path = model_path
        if not os.path.isfile(model_path):
            raise ValueError(
                "Can't find a model file at path '{}'. ".format(model_path)
            )

    def load_tagger(self):
        tagger = pycrfsuite.Tagger()
        tagger.open(self.model_path)
        return tagger

    def do_split(self, tagger, sentence):
        sent = ' '.join(sentence.split())  # erase duplicate whitespaces
        input_val = sent2input(sent)
        output_val = tagger.tag(input2features(input_val))
        out_sentence = self.__make_out_sentence(input_val, output_val)
        return out_sentence

    def __make_out_sentence(self, input_val, output_val):
        sent = ''
        for (char, space), split in zip(input_val, output_val):
            if space == '1' or split == '1':
                char = f' {char}'
            sent += char
        return sent.strip()

    def split_sentences(self, sentences):
        def split_by_one_job(batch_sentences):
            tagger = self.load_tagger()
            return [self.do_split(tagger, sentence) for sentence in batch_sentences]

        if type(sentences) is not list and type(sentences) is str:
            sentences = list(sentences)

        length_sentences = len(sentences)
        if (self.n_jobs > 1) and (length_sentences > 5e3):
            import operator
            import functools
            th = length_sentences // self.n_jobs + 1
            res = Parallel(n_jobs=self.n_jobs, backend='loky')(
                delayed(split_by_one_job)(sentences[i * th:(i + 1) * th]) for i in range(self.n_jobs))
            # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
            return functools.reduce(operator.iconcat, res, [])
        else:
            return split_by_one_job(sentences)



def sent2input(sent):
    # start = datetime.now()
    input_val = []
    prev_char = None
    for curr_char in sent:
        # print(curr_idx, curr_char)
        if not curr_char == ' ':
            if prev_char == ' ':
                input_val.append((curr_char, '1'))
            else:
                input_val.append((curr_char, '0'))
        prev_char = curr_char
    # print(f'first {datetime.now()-start}')
    return input_val


def input2features(input_val):
    chars_1 = ('__S-2__', '0')
    chars_2 = ('__S-1__', '0')
    chars_3 = ('__S+1__', '0')
    chars_4 = ('__S+2__', '0')
    temp_array = [chars_1, chars_2, *input_val, chars_3, chars_4]
    return [char2features(temp_array, idx) for idx in range(2, len(temp_array) - 2)]


def char2features(sent, i):
    features = {
        'bias': 1.0,
        'chars[-2]': sent[i - 2][0],
        'chars[-1]': sent[i - 1][0],
        'chars[0]': sent[i][0],
        'chars[1]': sent[i + 1][0],
        'chars[2]': sent[i + 2][0],
        'space[-2]': sent[i - 2][1],
        'space[-1]': sent[i - 1][1],
        'space[0]': sent[i][1],
        'space[1]': sent[i + 1][1],
        'space[2]': sent[i + 2][1],
        'chars[0]_space[0]': sent[i][0] + '_' + sent[i][1],
        'chars[-1]_space[-1]': sent[i - 1][0] + '_' + sent[i - 1][1],
        'chars[1]_space[1]': sent[i + 1][0] + '_' + sent[i + 1][1]
    }
    return features


if __name__ == '__main__':
    from datetime import datetime

    # 1) 여러 문장을 한 번에 처리하는 방법
    start = datetime.now()
    sent = [f'{i}번째 문장입니다.' for i in range(5000)]
    splitter = NounSplitter(n_jobs=4)
    rs = splitter.split_sentences(sent)
    print(rs[:10])
    print(rs[-10:])
    print(f'Duration : {datetime.now()-start}')

    # 2) 한문장씩 처리하는 방법
    start = datetime.now()
    sent = '하나의 문장입니다.'
    splitter = NounSplitter()
    tagger = splitter.load_tagger()
    rs = splitter.do_split(tagger, sent)
    print(rs)
    print(f'Duration : {datetime.now() - start}')
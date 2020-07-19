import os
from noun_splitter import sent2input, input2features
import pycrfsuite


def create_training_dataset(file_path):
    features = []
    labels = []
    sentence = ''
    label = []
    with open(file_path, 'r', encoding='utf-8') as r:
        for line in r:
            line = line.strip()
            if not line:
                feature = input2features(sent2input(sentence))
                features.append(feature)
                labels.append(label)
                sentence = ''
                label = []
            else:
                try:
                    char, space, split = line.split('\t')
                    if sentence == '': # 문장의 처음은 무조건 1
                        split = '1'
                    if space == '1':
                        sentence += ' '
                    sentence += char
                    label.append(split)
                except:
                    pass
    assert len(features) == len(labels)
    return features, labels


def train(features, labels, model_path='./np2.crfsuite', do_eval=True, verbose=True):
    start = datetime.now()
    params = {
        'c1': 1e-3,  # L1 penalty
        'c2': 1.0,  # L2 penalty
        'max_iterations': 100,
        'feature.minfreq': 50
    }
    trainer = pycrfsuite.Trainer(verbose=verbose)
    trainer.set_params(params)
    for x, y in zip(features, labels):
        trainer.append(x, y)
    trainer.train(model_path, )
    print(f'Training time : {datetime.now()-start}')
    print(f'Saving model to {model_path}')
    if do_eval:
        evaluate(features, labels, model_path)


def evaluate(features, labels, model_path='./np2.crfsuite'):
    tagger = pycrfsuite.Tagger()
    tagger.open(model_path)
    all = 0
    acc = 0
    for x, y_true in zip(features, labels):
        y_pred = tagger.tag(x)
        for true, pred in zip(y_true, y_pred):
            if true == pred:
                acc += 1
            all += 1
    print(f'Evaluated accuracy result : {acc/all*100:.2f}%')


if __name__ == '__main__':
    corpus_dir = './output'
    files = os.listdir(corpus_dir)
    print(f"training data : {files}")
    files_path = [os.path.join(corpus_dir, file) for file in files if file.endswith('.tsv')]
    features, labels = [], []
    for file in files_path:
        tmp = create_training_dataset(file)
        features.extend(tmp[0])
        labels.extend(tmp[1])
    assert len(features) == len(labels)
    train(features, labels)

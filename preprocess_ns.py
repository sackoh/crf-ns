import argparse
import os
from datetime import datetime

'''
## splitter로 labeling(1) 하는 경우
- 해당 음절에 `##`이 없고,
    - 해당 음절의 형태소가 list에 있으면 => 1
    - 해당 음절의 형태소가 list에 없으면
        - 이전 음절의 형태소가 list에 있으면 => 1
        - 이전 음절의 형태소가 list에 없으면 => 0
- 해당 음절에 `##`이 있으면 => 0

## space로 labeling(1) 하는 경우
- 해당 음절이 `''`일 때

## 문장분리를 하는 경우
- 이전 음절과 해당 음절이 모두 `' '`일 때

'''

SPLIT_POS = ['NNG', 'NNP', 'XR', 'SS', 'SO']


def processing_data(input_file_path, output_file_path):
    reader = open(input_file_path, 'r')
    writer = open(output_file_path, 'w')
    prev_char, prev_pos = '', ''
    sentence = []
    for i, line in enumerate(reader):
        line = line.strip()
        # 음절과 형태소 정보 확인
        if not line:
            curr_char, curr_pos = '', ''
            # 문장분리
            if prev_char == '' and curr_char == '':
                # print(''.join([' ' + s[0] if s[2] == 1 else s[0] for s in sentence]))
                # print(sentence)
                if sentence:
                    for char, space, split in sentence:
                        writer.write(f'{char}\t{space}\t{split}\n')
                    writer.write('\n')
                sentence = []
                prev_char, prev_pos = '', ''

            prev_char, prev_pos = '', ''
        else:
            curr_char, curr_pos = line.split('/')[0], line.split('/')[-1]
            if not curr_char:
                curr_char = '/'

            # 레이블링 Split
            if not curr_char.startswith('##'):
                if curr_pos in SPLIT_POS:  # "학/NNG"
                    split = 1
                else:  # "이/JKS"
                    if prev_pos in SPLIT_POS:  # "##액/NNG", "이/JKS"
                        split = 1
                    else:  # "7/SN", "천/NR" | "", "1/SN"
                        split = 0
            elif curr_char.startswith('##'):
                curr_char = curr_char[2:]
                split = 0
            else:
                split = 0

            # 레이블링 Space
            if prev_char == '':
                space = 1
            else:
                space = 0

            sentence.append((curr_char, space, split))

            prev_char, prev_pos = curr_char, curr_pos


if __name__ == '__main__':
    start = datetime.now()

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True)
    parser.add_argument('--output_file', type=str, default='result.tsv')
    args = parser.parse_args()

    OUTPUT_DIR = './output'
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    processing_data(args.input_file, os.path.join(OUTPUT_DIR, args.output_file))
    print('Successfully processed data : {}'.format(datetime.now() - start))
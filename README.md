# crf-ns
 noun splitter using python-crfsuite
 
1. Download dataset to each directory
    - dataset
    
2. Preprocess dataset
    ```shell
    $ python preprocess_ns.py --input_file=$INPUT_PATH --output_file=$OUTPUT_PATH
   ```
    - dn_bnlp_1_1_split.txt
    - sejong-all-split.txt
    
3. Train CRF model
    ```shell
    $ python trainer.py
    ```
    - train crf model from preprocessed data inside `output` directory
    - trained model *np2.crfsuite* is saved into `model` directory

4. Usage

    1) tagging multiple sentences at once
        ```python
        from noun_splitter import NounSplitter
        
        sentences = [f'{i}번째 문장입니다.' for i in range(5e3)]
        noun_splitter = NounSplitter(model_path='./model/np2.crfsuite', n_jobs=-1)
        noun_splitter.split_sentences(sentences)
        # ['0번째 문장 입니다.', '1번째 문장 입니다.', '2번째 문장 입니다.', ... ]
        ```
     2) tagging sentences one-by-one
         ```python
        from noun_splitter import NounSplitter
        
        sentence = '하나의 문장입니다.'
        noun_splitter = NounSplitter(model_path='./model/np2.crfsuite')
        tagger = noun_splitter.load_tagger()
        noun_splitter.do_split(tagger, sentence)
        # '하나의 문장 입니다.'
        ```
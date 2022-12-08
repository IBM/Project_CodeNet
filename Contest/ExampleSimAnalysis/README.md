# Example of contest test set evaluation

Author: [Vladimir Zolotov](mailto:zolotov@us.ibm.com)


This directory holds an example of program `TestSetEval.py` and `scrip test_eval.sh` for evaluating a contest test set on source code similarity.

The program is given only as an example. It is expected that the contestants write their own test set evaluation program better suitable for their operational environment, file formats and ML framework.

The program `TestSetEval.py`  accepts a test set consisting of two components:

1. Directory with source code files of C++ programs to detect similarity or dissimilarity with each other.
2. csv file of a test set in the following format:

`<sample number>,<path to 1-st file>,<path to 2-nd file>`

where `path to 1-st file` and `path to 2-nd file` specify paths to the pair of files to detect similarity or dissimilarity. The paths are specified relative to the directory with source code files. Here is an example of the csv file of the test set:

```
pair-id,file1,file2
1,p02761/s682789980.cpp,p02761/s060579067.cpp
2,p02817/s224840938.cpp,p03360/s804824036.cpp
3,p01085/s591760635.cpp,p01085/s734466918.cpp
```

The program `TestSetEval.py` can also accept a csv file of ground truth labels in the following format:
`<sample number>,<label>`. Here is an example of the file with ground truth labels:

```
pair-id,similar
1,1
2,0
3,1
```

The program `TestSetEval.py`  write down the computed similarity predictions as a csv file in the following format:

`<sample number>,<path to 1-st file>,<path to 2-nd file>,<similarity score><prediction>`

where `similarity score` is the computed probability that the pair of files are similar and, `prediction` is the computed prediction of the similarity. Here is an example of this file:

```
pair-id,file1,file2,confidence,prediction
1,f8610.cpp,f8588.cpp,0.06234602,Dissimilar
2,f1089.cpp,f9389.cpp,0.15431221,Dissimilar
3,f9570.cpp,f9593.cpp,0.89995503,Similar
```

If the file with ground truth labels is given the program also computes the accuracy of the test set evaluation and prints it to the console report.

The program uses the Codenet tokenizer from https://github.com/IBM/Project_CodeNet/tree/main/tools/tokenizer and 
Keras API of TensorFlow ML framework.  However, it can be easily modified to  for a different ML framework.

Program has the following arguments:
*  The directory with source code files to analyze similarity.
*  The csv file with sample pairs to analyze similarity
*  The path to tokenizer of source code files. This should be the Codenet tokenizer from https://github.com/IBM/Project_CodeNet/tree/main/tools/tokenizer. Its default value is `tokenize`.
*  The TensorFlow checkpoint file with the trained DNN. Its default value is `./dnn_ckpt`.
*  The csv file with ground truth labels. If it is omitted the program does not compute the accuracy of testset evaluation.
*  The file to write down the computed similarity predictions.
*  The batch size.  Its default value is 400.
*  The mode of Keras training progress bar. By default the program depicts the progress bar on the console.

The program usage can be obtained with the command: `python TestSetEval.py -h`, which gives the following output:

```
usage: TestSetEval [-h] [--labels LABELS] [--dnn DNN] [--tokenizer TOKENIZER]
                   [--predictions PREDICTIONS] [--batch BATCH]
                   [--progress {0,1,2}]
                   source_code test

positional arguments:
  source_code           directory with source code files to analyze similarity
  test                  file with sample pairs to analyze similarity

optional arguments:
  -h, --help            show this help message and exit
  --labels LABELS       file with similarity labels of test samples
  --dnn DNN             checkpoint file with trained dnn
  --tokenizer TOKENIZER
                        path to tokenizer of source code files
  --predictions PREDICTIONS
                        file to write similarity predictions
  --batch BATCH         batch size
  --progress {0,1,2}    mode of Keras training progress bar
```

The directory has also a script  calling the program with and without ground truth labels.


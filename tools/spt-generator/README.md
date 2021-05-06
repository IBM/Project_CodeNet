# AI4Code SPT generator
Featurize programming source code for the ML/DL pipeline in AI4Code project.
We currently support 4 languages (C, C++, Python, Java). This tool generates Simplified Parse Tree (SPT)
for each recognized program, which follows the similar idea presented in Facebook Aroma paper (https://arxiv.org/pdf/1812.01158.pdf). New ideas/representations are very welcome here!

## Project structure
- [src](src):
Contains SPT generating java programs.
- [scripts](scripts):
Contains necessary scripts that compile and run the tool.
- [resources](resources):
Contains external libraries necessary to build this project.
- [examples](examples):
Contains some (C/C++/Java/Python) samples.

## How to run (on a Linux box)
1. set up common environment variables:

```
source spt.profile
```

This step establishes some environment variables, which are useful for the project building and running.

2. build the project:

``` 
./scripts/build/gen_g4.sh (Optional, only required to do it once to generate parser related java files.)
./scripts/build/compile.sh 
```

This step  compiles and packages the tool. 

3. Tokenizer (./scripts/run/tokenize.sh)
This tool automatically distinguishes 4 types of language (.c, .cpp, .java and .py) based on the input file extension and create tokens for the source code input file. 

(i) Help info can be obtained by 

```
./scripts/run/tokenize.sh -h 
```

(ii) Single file (e.g., hellworld.c) processing with output to stdout 

``` 
./scripts/run/tokenize.sh ./examples/c/helloworld.c 
```

(iii) Single file processing (e.g., helloworld.c) with output to a specified directory (e.g., /tmp) 

```
./scripts/run/tokenize.sh -d=/tmp ./examples/c/helloworld.c 
``` 

Tokens csv file (csv RFC 4180 compliant) [helloworld.csv](examples/demos/c/helloworld.csv) is generated under the specified output directory (e.g., /tmp). CSV header: seqnr, start, stop, text, class, channel, line, column. 

(iv) Batch processing 

``` 
./scripts/run/tokenize.sh --batch ./examples/demos/c/spt_input.txt 
``` 

Note the --batch option and the input file contains a list of pairs, the first of which is the source code to be analyzed and the second of which is the output directory. An example of such input file is provided at [spt_input.txt](examples/demos/c/spt_input.txt)

4. SPTGenerator (./scripts/run/spt-gen.sh)

This tool automatically distinguishes 4 types of language (.c, .cpp, .java and .py) based on input file extension and create both tokens and SPT for the input source code. Note that if for any reason this tool cannot properly analyze the source code, it will generate a warning message that indicates the given input file "cannot be processed" and forgo generating any tokens or SPT.

(i) Help info can be obtained by 

``` 
./scripts/run/spt-gen.sh -h 
```


(ii) Single file processing (e.g., helloworld.c) with output to a specified directory (e.g., /tmp) 

```
./scripts/run/spt-gen.sh -d=/tmp ./examples/c/helloworld.c
``` 

SPT .json file [helloworld.json](examples/demos/c/helloworld.json) is generated under the specified output directory (e.g., /tmp) and complies with the [AI4Code graph schema](../json-graph). There are two types of node defined: Token node and Rule node. They share a common set of attributes: "id" (BFS ordered index), "label" (the string representation of the node, literals for the token node and Facebook Aroma style representation for rule node), "node-type" (Token or Rule), "type-rule-name" (the rule name used to parse this node). Additionally, Token node has a field "token_id", which corresponds to the "seqnr" in the tokenizer CSV file. Tokens csv file(csv RFC 4180 compliant) [helloworld.csv](examples/demos/c/helloworld.csv) is also generated under the specified output directory (e.g., /tmp). To enable matching between the tokens file and SPT file, the "seqnr" field in .csv and "token_id" field in .json match each other.

Finally, one can use the [.json to .dot generation tool] (../json-graph/tree/master/src) to generate a .png visualization for the .json file. The visualization of above-mentioned .json is [helloworld.png](examples/demos/c/helloworld.png).

(iii) Batch processing 

``` 
./scripts/run/spt-gen.sh --batch ./examples/demos/c/spt_input.txt 
```

Note the --batch option and the input file contains a list of pairs, the first of which is the source code to be analyzed and the second of which is the output directory. An example of such input file is provided at [spt_input.txt](examples/demos/c/spt_input.txt)



5. C/C++ preprocessing

This tool is based on Antlr4, which cannot handle C/C++ preprocessing (e.g., macros expansion). To circumvent this, we recommend users to do the following for each C/C++ file.

(i) Remove include headers by doing 

``` 
grep -P -v '^[ \t]*#[ ]*include[ ]*[\<|\"].*(?<!\*\/)$'
``` 

on the input file and generating a post-op file (note -P requires your grep supports Perl style regular expression).

(ii) Use gcc/g++ -E to pre-process the file generated in the previous step.


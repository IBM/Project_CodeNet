/* Copyright (c) 2021 International Business Machines Corporation
   Prepared by: Geert Janssen <geert@us.ibm.com>

   This program finds clusters of near-duplicate files of source code.
   The clusters do not overlap; each input sample is either assigned to a
   unique cluster or is declared to be a singleton set.

   Input format is lines of tokenized source file data. Each line is:
     <unique id (e.g. full filename path)> TAB <list of tokens>
   The list of tokens is never empty and tokens are either separated by
   solely SPACES or solely TABs.
     <token> ( SP <token> )*, or
     <token> ( TAB <token> )*
   (Also, all comments have been removed.)

   All token strings across all samples are collected in a vocabulary.
   That way all strings are stored only once and are associated with
   a unique index (counted from 0). All further processing can be done
   with the index; Jaccard similarity and LCS do not need the strings.
   The inverse relation is stored in the vector tokid2string.

   Per sample, the tokens are first inserted in an unordered_map keyed
   by the token id and recording a list of all positions for this token.
   Clearly, the length of this list per token is the token frequency.
   Then this dictionary is copied into a vector and sorted by the keys.
   Since we don't need the positions per token, this vector is split in
   a token_bag recording just the frequency and a token_seq.

   This way we have with minimal memory use represented the original sample
   both as a sequence of tokens (token_seq) and as a multiset (token_bag).
   The bag of token representation can be seen as a sparse feature vector:
   A feature is a vocabulary index and it either does not occur in a sample
   or it does occur with a certain recorded frequency. Having the bag ordered
   by index eases the computation of metrics like Jaccard and dot-product.

   Be careful to keep results deterministic. Using unordered_map for ids
   does not obey order of insertion of course, but depends on some hash
   function.

   All samples are in memory.
*/

#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>		// sqrt()
#include <unistd.h>		// getopt()
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>

static int debug = 0;		 // when 1 debug output to stderr
static int verbose = 0;		 // when 1 info output to stderr
static int nowarn = 0;		 // when 1 warnings are suppressed
static int csv_summary = 0;	 // when 1 output in CSV format
static int out_singles = 0;	 // when 1 output singletons as well
static unsigned num_tokens_threshold = 20;
static unsigned num_samples_discarded = 0;
static double threshold_0 = 0.9; // Jaccard, LCS, COSINE
static double threshold_1 = 0.8; // Jaccard
static enum { JACCARD, LCS, COSINE } mode = JACCARD;
static const char *delim = " ";
static const char *filename = "stdin";

using namespace std;

// Original input token sequence:
typedef vector<unsigned> TokenSeq;
// Single element of TokenBag:
typedef pair<unsigned, unsigned> TokenFreq;
// (Arbitrarily) sorted sequence of tokens in order to compare them:
typedef vector<TokenFreq> TokenBag;
// Pair of doubles:
typedef pair<double, double> Double2;

// all strings
static unordered_map<string, unsigned> vocabulary;
//static vector<string> tokid2string; NOT USED

struct Sample {
  string id;
  TokenSeq token_seq;
  TokenBag token_bag;
  bool flag;

  Sample(const string &id) : id(id), flag(false) {}

  // Sample size equals length of token sequence.
  unsigned size() const {
    return token_seq.size();
  }

#if 0
  // NOT USED
  void show(FILE *fp = stderr) const {
    fputs("tokens:", fp);
    for (auto k : token_seq)
      fprintf(fp, " %s", tokid2string[k].c_str());
    fputc('\n', fp);
  }
#endif
};

// all samples
static unordered_set<string> all_ids;
static vector<Sample> samples; // in order of input

/* Split tokens and determine number of occurrences and store as
   vectors under id in global samples.
*/
static void process_sample(const char *id, char *tokens)
{
  // Verify uniqueness of id:
  if (all_ids.find(id) != all_ids.end()) {
    if (!nowarn)
      fprintf(stderr, "(W): Non-unique id %s; sample discarded.\n", id);
    return;
  }

  Sample s(id);
  unsigned num_tokens = 0;
  // Per token instance string record all its positions:
  typedef vector<unsigned> Positions;
  typedef pair<unsigned, Positions> TokenPos;
  unordered_map<unsigned, Positions> dict;

  // Split the tokens:
#if 1
  char *p = tokens;
  do {
    const char *token = p;
    while (*p && *p != *delim)
      p++;
    // Here: *p == '\0' || *p == delim
    if (token == p) // empty token
      break;
    if (*p == *delim)
      *p++ = '\0';
    //use token:

    unsigned token_id; // unique id for token string
    // Uniquely store all token strings in global vocabulary:
    auto it = vocabulary.find(token);
    if (it == vocabulary.end()) { // a fresh one
      token_id = vocabulary.size();
      vocabulary[token] = token_id;
      //tokid2string.push_back(token); NOT USED
    }
    else
      token_id = it->second;
    // Locally store all positions for this token:
    dict[token_id].push_back(num_tokens); // size of second is frequency
    num_tokens++;

  } while (true);

#else
  // strtok is slow
  const char *token = strtok(tokens, delim);
  while (token) {
    unsigned token_id; // unique id for token string
    // Uniquely store all token strings in global vocabulary:
    auto it = vocabulary.find(token);
    if (it == vocabulary.end()) { // a fresh one
      token_id = vocabulary.size();
      vocabulary[token] = token_id;
      //tokid2string.push_back(token); NOT USED
    }
    else
      token_id = it->second;
    // Locally store all positions for this token:
    dict[token_id].push_back(num_tokens); // size of second is frequency
    num_tokens++;
    token = strtok(NULL, delim);
  }
#endif
  // In Allamanis paper this is number of identifier tokens.
  // Hard to tell from a token list (of unknown language).
  if (num_tokens < num_tokens_threshold) {
    num_samples_discarded++;
    if (!nowarn)
      fprintf(stderr, "(W): Sample %s has less than %u tokens; discarded.\n",
	      id, num_tokens_threshold);
    return;
  }

  // Should we normalize the frequencies? Don't think so.

  // Convert dict to vector (order does not matter):
  vector<TokenPos> vec;
  for (const auto &t : dict)
    vec.emplace_back(t);

  // Sort by token id:
  sort(vec.begin(), vec.end(),
       [](const TokenPos &a, const TokenPos &b)
       { return a.first < b.first; });

  // Fill in token_bag and token_seq:
  s.token_seq.resize(num_tokens);
  s.token_bag.resize(vec.size());
  for (unsigned i = 0, size = vec.size(); i < size; i++) {
    unsigned token_id = vec[i].first;
    // Stuff token id and frequency in bag (multiset):
    s.token_bag[i] = {token_id, vec[i].second.size()};
    // Put token_id in all the required positions:
    for (auto p : vec[i].second)
      s.token_seq[p] = token_id;
  }

  samples.emplace_back(s);
}

/* Longest Common Subsequence (LCS) (not necessarily consecutive)
   Simplified. O(mn) time, O(n) space.
*/
static unsigned lcs(const TokenSeq &X, const TokenSeq &Y,
		    const unsigned m, const unsigned n)
{
  // Here: m,n >= 0.
  unsigned L[2][n+1]; // small 2 by n+1 matrix
  unsigned bi; // odd(i)

  // 0-th row and 0-th column contains all zeroes:
  for (unsigned j = 0; j<=n; j++) // at least once
    L[0][j] = 0;
  L[1][0] = 0;

  for (unsigned i = 1; i<=m; i++) { // at least once
    bi = i & 1;
    for (unsigned j = 1; j<=n; j++) // at least once
      if (X[i-1] == Y[j-1])
	L[bi][j] = L[1-bi][j-1] + 1;
      else
	L[bi][j] = max(L[1-bi][j], L[bi][j-1]);
    // After seeing i elems: L[bi][n] <= i is actual length; i is upperbound.
    // i - L[bi][n] is # different elements; might only get larger (1 per row)
    //cerr << "L[" << i << "][n]: " << L[bi][n] << endl;
    //if (L[bi][n] >= mincommon) break;
  }
  /* L[m][n] contains length of LCS for X[0..n-1] and Y[0..m-1] */
  return L[bi][n];
}

// An upperbound for the length of an LCS.
static unsigned lcs_upperbound(const TokenBag &t1, const TokenBag &t2)
{
  unsigned share_1 = 0;	// card. of intersection considering multiplicity

  // Lock-step traversal of the 2 vectors:
  auto it1 = t1.cbegin();
  auto it2 = t2.cbegin();
  auto t1_cend = t1.cend();
  auto t2_cend = t2.cend();

  while (it1 != t1_cend && it2 != t2_cend) {
    if (it1->first < it2->first)
      ++it1;
    else
    if (it1->first > it2->first)
      ++it2;
    else { // intersection
      share_1 += it1->second < it2->second ? it1->second : it2->second;
      ++it1; ++it2;
    }
  }
  return share_1;
}

/* Compute cosine similarity of 2 multisets.
*/
static double cosine(const TokenBag &t1, const TokenBag &t2)
{
  double dot = 0.0;
  double norm1 = 0.0;
  double norm2 = 0.0;

  // Lock-step traversal of the 2 vectors:
  auto it1 = t1.cbegin();
  auto it2 = t2.cbegin();
  auto t1_cend = t1.cend();
  auto t2_cend = t2.cend();

  // Feature value is the frequency.
  while (it1 != t1_cend && it2 != t2_cend) {
    // For normalization:
    norm1 += it1->second * it1->second;
    norm2 += it2->second * it2->second;

    if (it1->first < it2->first)
      ++it1;
    else
    if (it1->first > it2->first)
      ++it2;
    else { // intersection of features
      dot += it1->second * it2->second;
      ++it1; ++it2;
    }
  }
  // Handle leftover tails:
  for (; it1 != t1_cend; ++it1)
    norm1 += it1->second * it1->second;
  for (; it2 != t2_cend; ++it2)
    norm2 += it2->second * it2->second;

  return dot / sqrt(norm1 * norm2);
}

/* Compute Jaccard similarity of 2 multisets, both with ignoring an
   element's multiplicity and with considering it. The first case of
   course equals to assuming an overall multiplicity of 1.
   Returns a pair of numbers.
*/
static Double2 jaccard(const TokenBag &t1, const TokenBag &t2)
{
  unsigned share_0 = 0;	// card. of intersection ignoring multiplicity
  unsigned total_0 = 0;	// card. of union ignoring multiplicity
  unsigned share_1 = 0;	// card. of intersection considering multiplicity
  unsigned total_1 = 0;	// card. of union considering multiplicity

  /* Example:
     A   = 1 1 2   3 3 3 4 4 5    | 1 2 3 4 5   |  9 | 5
     B   =     2 2 3 3 3 4     6  |   2 3 4   6 |  7 | 4
     ---------------------------------------------------
     A*B =     2   3 3 3 4        |   2 3 4     |  5 | 3
     A+B=  1 1 2 2 3 3 3 4 4 5 6  | 1 2 3 4 5 6 | 11 | 6

     share_0 = 3, total_0 =  6, share_0/total_0 = 0.5
     share_1 = 5, total_1 = 11, share_1/total_1 = 0.45
     (of course _0 and _1 the same when multiplicity is 1 overall)

     Note: result numbers are independent, can have
     share_0/total_0 (<, ==, >) share_1/total_1
  */

  // Lock-step traversal of the 2 vectors:
  auto it1 = t1.cbegin();
  auto it2 = t2.cbegin();
  auto t1_cend = t1.cend();
  auto t2_cend = t2.cend();

  while (it1 != t1_cend && it2 != t2_cend) {
    total_0++;
    if (it1->first < it2->first) // difference
      total_1 += (it1++)->second;
    else
    if (it1->first > it2->first) // difference
      total_1 += (it2++)->second;
    else { // intersection
      share_0++;
      // just as fast as single if
      total_1 += max(it1->second, it2->second);
      share_1 += min(it1->second, it2->second);
      ++it1; ++it2;
    }
  }
  // Handle leftover tails:
  while (it1 != t1_cend) {
    total_0++;
    total_1 += (it1++)->second;
  }
  while (it2 != t2_cend) {
    total_0++;
    total_1 += (it2++)->second;
  }
  return { double(share_0)/total_0, double(share_1)/total_1 };
}

/* Check pairs of samples for similarity.
   All n(n-1)/2 pairs are considered in principle.
   Avoid a quadratic number of tests by flagging samples
   that are found similar.
*/
static void check_samples()
{
  unsigned num_clusters = 0;
  unsigned max_cluster_size = 0;
  unsigned total_cluster_size = 0;
  unsigned singletons = 0;
  unsigned num_samples = samples.size();

  if (!num_samples)
    return;

  // Output only non-singleton clusters separated by a blank line.

  // Tried using a std::queue for inner loop but does not seem to affect
  // performance much. Probably because of underlying deque.
  // Even simple queue using fixed size array does no improve things.

  for (auto it1 = samples.begin(), end = samples.end(); it1 != end; ++it1) {
    //fprintf(stderr, "id: %s\n", it1->id.c_str());
    if (it1->flag) continue;
    const unsigned s1 = it1->size();
    // FIXME: Put all samples similar to this one in a cluster.
    unsigned cluster_size = 1;
    for (auto it2 = next(it1), end = samples.end(); it2 != end; ++it2) {
      if (it2->flag) continue;
      const unsigned s2 = it2->size(); 

      // Allow s2 to deviate up to +- 5% from s1:
      if (::abs(s1 - s2) * 100.0 / s1 > 5.0) continue;

      switch (mode) {
      case LCS: {
	// Cheap upperbound calculation:
	unsigned up = lcs_upperbound(it1->token_bag, it2->token_bag);
	if (up < s1 * threshold_0)
	  continue;

	unsigned lcs_len = lcs(it1->token_seq, it2->token_seq, s1, s2);
	if (lcs_len >= s1 * threshold_0) {
	  // Flag it2 (always beyond it1) as dealt with:
	  it2->flag = true;
	  if (cluster_size == 1)
	    fprintf(stdout, "%s:     (%3u)\n", it1->id.c_str(), s1);
	  fprintf(stdout, "%s: %3u (%3u)\n", it2->id.c_str(), lcs_len, s2);
	  cluster_size++;
	}
	break;
      }

      case JACCARD: {
	Double2 similarity = jaccard(it1->token_bag, it2->token_bag);
	if (similarity.first  >= threshold_0 &&
	    similarity.second >= threshold_1) {

	  // Flag it2 (always beyond it1) as dealt with:
	  it2->flag = true;
	  if (cluster_size == 1)
	    fprintf(stdout, "%s:\n", it1->id.c_str());
	  fprintf(stdout, "%s: %5.2f,%5.2f\n", it2->id.c_str(),
		  similarity.first, similarity.second);
	  cluster_size++;
	}
	break;
      }

      case COSINE: {
	double similarity = cosine(it1->token_bag, it2->token_bag);
	if (similarity >= threshold_0) {
	  // Flag it2 (always beyond it1) as dealt with:
	  it2->flag = true;
	  if (cluster_size == 1)
	    fprintf(stdout, "%s:\n", it1->id.c_str());
	  fprintf(stdout, "%s: %5.2f\n", it2->id.c_str(), similarity);
	  cluster_size++;
	}
	break;
      }
      }
    }
    if (cluster_size > 1) {
      if (next(it1) != end)
	fputc('\n', stdout);
      num_clusters++;
      if (cluster_size > max_cluster_size)
	max_cluster_size = cluster_size;
      total_cluster_size += cluster_size;
    }
    else {
      if (out_singles) {
	fprintf(stdout, "%s:\n", it1->id.c_str());
	if (next(it1) != end)
	  fputc('\n', stdout);
      }
      singletons++;
    }
  }

  // Sanity check:
  assert(total_cluster_size + singletons == num_samples);

  // samples with size 1 cluster: num_samples - total_cluster_size
  // unique samples: num_clusters + size 1 samples
  // duplication factor: (num_samples - unique samples) / num_samples
  // = (total_cluster_size - num_clusters) / num_samples

  if (csv_summary) {
   // identifier,samples,discarded,unique,clusters,duplicates,max,average,factor
    fprintf(stderr, "%s,%u,%u,%u,%u,%u,%u,%.1f,%.1f%%\n",
	    filename, num_samples+num_samples_discarded, num_samples_discarded,
	    num_samples + num_clusters - total_cluster_size,
	    num_clusters, total_cluster_size, max_cluster_size,
	    double(total_cluster_size)/num_clusters,
	    (total_cluster_size - num_clusters) * 100.0 / num_samples);
  }
  else
  fprintf(stderr,
	  "Found %u clusters (avg: %3.1f, max: %u) among the %u samples.\n"
	  "Duplication factor: %5.1f%%\n",
	  num_clusters, double(total_cluster_size)/num_clusters,
	  max_cluster_size, num_samples,
	  (total_cluster_size - num_clusters) * 100.0 / num_samples);
}

int main(int argc, char *argv[])
{
  extern int optind;
  int option;
  char const *opt_str = "cdhi:j:m:M:o:stvw";
  char usage_str[80];

  char *outfile = 0;
  unsigned num_files = 0;	// number of files read

  sprintf(usage_str, "usage: %%s [ -%s ] [ FILE ]\n", opt_str);

  /* Process arguments: */
  while ((option = getopt(argc, argv, opt_str)) != EOF) {
    switch (option) {

    case 'c':
      csv_summary = 1;
      break;

    case 'd':
      debug = verbose = 1;
      break;

    case 'h':
fputs(
"This program finds clusters of near-duplicate files of source code.\n"
"The input is a file (or files) with one sample per line. A sample consists\n"
"of a unique (within the input) identifier for the source code, e.g.\n"
"its file name or its file name path, and a list of space-separated tokens.\n\n"
"Two samples are reported as near-duplicates depending on the thresholds set\n"
"for the various similarity metrics (thresholds must be in [0..1]):\n"
"1. in Jaccard mode, the set similarity score must meet the 1st threshold and\n"
"   the multiset score meet the 2nd threshold;\n"
"2. in LCS mode, the ratio of common subsequence length and input length must\n"
"   be at least the 1st threshold value;\n"
"3. in Cosine mode, the cosine similarity must be at least the 1st threshold.\n\n"
, stdout);
fprintf(stderr, usage_str, basename(argv[0]));
fputs(
"\nCommand line options are:\n"
"-c       : output summary in CSV instead of plain text (default) to stderr.\n"
"-d       : print debug info to stderr; implies -v.\n"
"-h       : print just this text to stderr and stop.\n"
"-i<num>  : 1st Jaccard (or LCS, or Cosine) threshold value (default 0.9).\n"
"-j<num>  : 2nd Jaccard threshold value (default 0.8).\n"
"-m<mode> : operation mode either jaccard (default), lcs, or cosine.\n"
"-M<int>  : samples smaller than this number are discarded (default 20).\n"
"-o<file> : name for output file (instead of stdout).\n"
"-s       : also output singleton clusters (default don't).\n"
"-t       : insist tokens are TAB-separated (default autodetect).\n"
"-v       : print action summary to stderr.\n"
"-w       : suppress all warning messages.\n",
      stderr);
      return 0;

    case 'i':
      threshold_0 = atof(optarg);
      break;

    case 'j':
      threshold_1 = atof(optarg);
      break;

    case 'm':
      if (!strcmp(optarg, "jaccard"))
        mode = JACCARD;
      else if (!strcmp(optarg, "lcs"))
        mode = LCS;
      else if (!strcmp(optarg, "cosine"))
        mode = COSINE;
      else {
	if (!nowarn)
	  fprintf(stderr, "(W): Invalid mode %s (using jaccard).\n", optarg);
        mode = JACCARD;
      }
      break;

    case 'M':
      num_tokens_threshold = atoi(optarg);
      break;

    case 'o':
      outfile = optarg;
      break;

    case 's':
      out_singles = 1;
      break;

    case 't':
      delim = "\t";
      break;

    case 'v':
      verbose = 1;
      break;

    case 'w':
      nowarn = 1;
      break;

    case '?':
    default:
      fputs("(F): unknown option. Stop.\n", stderr);
      fprintf(stderr, usage_str, argv[0]);
      return 1;
    }
  }

  if (outfile && outfile[0]) {
    if (!freopen(outfile, "w", stdout)) {
      fprintf(stderr, "(F): cannot open %s for writing.\n", outfile);
      exit(3);
    }
  }

  char *line = NULL;
  size_t alloc_len;
  ssize_t nchars;

  // CSV header (once)
  /*
  if (csv_summary)
    fputs("identifier,samples,discarded,unique,clusters,duplicates,max,"
	  "average,factor\n", stderr);
  */
  if (optind == argc)
    goto doit;

  do {
    filename = argv[optind];
    if (!freopen(filename, "r", stdin)) {
      if (!nowarn)
	fprintf(stderr, "(W): Cannot read file %s.\n", filename);
      continue;
    }

  doit:
    unsigned linenr = 0;
    num_files++;

    if (verbose) fprintf(stderr, "(I): Processing file %s...\n", filename);

    while ((nchars = getline(&line, &alloc_len, stdin)) != -1) {
      linenr++;

      // Remove white-space from end of line:
      char *p = line + nchars;
      while (isspace(*(p-1)))
	p--;
      *p = '\0';

      // Skip blank lines:
      if (!*line) continue;

      // Split line at first TAB:
#if 1
      const char *id = p = line;
      while (*p && *p != '\t')
	p++;
      // Here: *p == '\0' || *p == '\t'
      if (*p != '\t') {
	fprintf(stderr, "(W): Line %u with id `%s' has no tokens; skipped.\n",
		linenr, id);
	continue;
      }
      *p++ = '\0';
      char *tokens = p;
#else
      const char *id = strtok(line, "\t");
      char *tokens = strtok(NULL, "");
      p = tokens;
#endif
      // if see a TAB in tokens assume delim="\t"
      if (delim[0] == ' ')
	for (; *p; p++)
	  if (*p == '\t') {
	    delim = "\t";
	    break;
	  }

      process_sample(id, tokens);
    }
  } while (++optind < argc);
  //if (line) free(line);

  if (verbose)
    fprintf(stderr, "(I): Total distinct tokens in vocabulary: %u\n",
	    vocabulary.size());

  check_samples();

  if (num_files > 1 && verbose)
    fprintf(stderr, "(I): Total number of files processed: %u\n", num_files);

  return 0;
}

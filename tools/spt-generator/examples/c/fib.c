#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
int fib(int n){
  if(n==0 || n==1){
    return n;
  }
  return fib(n-1)+fib(n-2);
}

int main(int argc, char **argv){
  assert(argc==2);
  int n = atoi(argv[1]);
  printf("fib(%d) is %d \n", n, fib(n));
  return 0;
}

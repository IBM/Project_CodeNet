/* add.c
     * a simple C program
     */
      
#include <stdio.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
int main(int n, char **argv)
{
  assert(n==2);
  int i, sum = 0;
  int last = atoi(argv[1]);
  for ( i = 1; i <= last; i++ ) {
    sum += i;
  } 
  printf("sum = %d\n", sum);
  return 0;
}

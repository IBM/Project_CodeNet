BEGIN {
    idx = 0
    delete cache
    FS=","
}

function map(x) {
    if (! (x in cache)) {
	cache[x] = idx++;
    }
    
    return cache[x]
}

{
    for(i = 1; i <= NF; i++) {
	if (i > 1) {
	    printf(",") >>FILENAME ".csv"
	}
	printf("%s", map($i)) >>FILENAME ".csv"
    }
    print "" >>FILENAME ".csv"
}

# Access Project CodeNet through SQL Queries

## Table of Contents

   * [Introduction](#introduction)
   * [Installation](#installation)
   * [Creating a sqltool.rc file](#creating-a-sqltoolrc-file)
   * [Prepare Project CodeNet for use with HSQLDB](#prepare-project-codenet-for-use-with-hsqldb)
   * [Define the table schemas](#define-the-table-schemas)
   * [A few simple SQL queries](#a-few-simple-sql-queries)

## Introduction

Project CodeNet metadata is available as CSV files in a rigid directory
structure. To abstract away from this structure and the peculiarities
of the metadata organization, we can use a database approach to the
metadata that allows for generic SQL queries to retrieve all kinds of
statistics but more importantly select file names of submissions
depending on all kinds of criteria.

One particular database is ideally suited to work with CSV files:
[*HyperSQL Database* (HSQLDB)](http://hsqldb.org). HSQLDB uses the CSV
files as persistent
storage and uses memory caches to speed up the queries.

HSQLDB is a simple but complete database software
implemented in Java. The main attractive feature is that it can link to
CSV files as tables and use them as persistent storage. This implies
that SQL queries can directly run off existing (even read-only) CSV
files without any modifications.

## Installation

Here we explain how to install and set up HSQLDB to work with the
Project CodeNet dataset. We assume `$PREFIX` to be a suitable system directory
like e.g. `/usr/local` and `$HOME` to expand to a user's home directory.

This brief guide is in no way a substitute for the excellent and
extensive [documentation](http://hsqldb.org/web/hsqlDocsFrame.html)
and [howtos](http://hsqldb.org/web/howto.html) that accompany HSQLDB.

We assume the use of (the latest as of writing) version 2.6.0 of HSQLDB.
(Any future newer version will probably work just as well).

The required software can be downloaded from
<http://www.hsqldb.org/download/hsqldb_260_jdk8/>.
That website offers the 2 files `hsqldb-2.6.0-jdk8.jar` and
`sqltool-2.6.0-jdk8.jar`. Rename the files to
`hsqldb.jar` and `sqltool.jar`, respectively.

Important files and their use are:

>`hsqldb.jar`
: The jar file containing all classes of the database engine proper.
Typically resides in some system accessible directory, like:
`$PREFIX/lib/hsqldb-2.6.0/hsqldb/lib/`

>`sqltool.jar`
: The jar file that provides an interactive command-line user interface (CLI)
to the database. Resides next to `hsqldb.jar`.

>`sqltool`
: A wrapper around `sqltool.jar` that calls the Java JVM and starts the
CLI. Typically to be found in a `bin` directory, like `$PREFIX/bin/`.
Its contents could be something like:
```bash
#!/usr/bin/env bash

HSQLDB_HOME=$PREFIX/lib/hsqldb-2.6.0/hsqldb

# allow csv to reside anywhere (and not just inside db directory)
java -Dtextdb.allow_full_path=false -jar $HSQLDB_HOME/lib/sqltool.jar "$@"
```

>`sqltool.rc`
The configuration file consulted by `sqltool`.
To be located in the user's home directory, e.g.
`$HOME/sqltool.rc`

>`DatabaseManagerSwing`
: A wrapper around `hsqldb.jar` that provides a graphical interface (GUI) to
the database. Can be found in the same bin directory as `sqltool`.

## Creating a `sqltool.rc` file

This configuration file specifies the various databases via URLs and
access rights. For simplicity we here assume a single user who is the
database administrator using the default user name `SA` without a
password. This is expressed as follows in `sqltool.rc`:

```
urlid .+
username SA
password
```

Assume we create the database (a collection of CSV files that become
the database tables) in a directory `$HOME\DB`. This is made known to
HSQLDB as follows and added to `sqltool.rc`:

```
urlid project_codenet
url jdbc:hsqldb:file:${user.home}/DB/project_codenet;shutdown=true
transiso TRANSACTION_READ_COMMITTED
```

Make sure that the directory exists: `mkdir -p $HOME/DB`.
With the configuration file in place, we can test our set up so far by
running `sqltool` and doing a few simple queries:

```bash
# Not really necessary, but for convenience, go to the DB directory:
$ cd $HOME/DB

# Start the sqltool program and make it use the (empty) project_codenet db:
# (You will get a message and eventually the sql> prompt.)
$ sqltool project_codenet
SqlTool v. 6140.
...
sql> 
```

You can explore some of the commands and browse the system tables.
Here are a few examples:

```bash
# Get help about \ commands:
sql> \?
# Get a list of user tables (result is none):
sql> \dt
# Get a list of system tables:
sql> \dS
# Get the list of known users (only 1: SA):
sql> select * from information_schema.system_users;
# Quit the program (\q or simply ^D in a Linux shell):
sql> \q
```

This will leave behind the files `project_codenet.properties` and
`project_codenet.script` in the `DB` directory. These are the files used by
HSQLDB to record the database properties, the table schemas, etc.
In general you should not delete them.

## Prepare Project CodeNet for use with HSQLDB

HSQLDB equates a database table with a CSV file. In Project CodeNet we have a
CSV per problem which is not very convenient. It is better to merge
all problem metadata (`p?????.csv`) into a single CSV file. Note
however that each problem CSV has its own header; these need to be
stripped off first. Since the dataset is read-only we must make a copy
of the metadata directory. As an example we show the necessary steps:

```bash
# Make sure we are in the database directory:
$ cd $HOME/DB

# Copy the metadata from Project CodeNet:
$ cp -r Project_CodeNet/metadata .

# Move the problem_list out and rename:
$ mv metadata/problem_list.csv problems.csv

# Get a separate header file:
$ head -n1 metadata/p00000.csv > submissions_header.csv

# Strip off all headers:
$ find metadata -type f -exec sed -i -e '1d' {} \;

# Create a single CSV file:
$ cat submissions_header.csv metadata/p?????.csv > submissions.csv

# For safety make the CSV files read-only:
$ chmod 444 problems.csv submissions.csv

# The metadata copy and submissions_header are no longer needed:
$ rm -rf metadata submissions_header.csv
```

Now we can create HSQLDB tables for `problems.csv` and `submissions.csv`.

## Define the table schemas

To create a database table we need to specify its columns, the type of
value in each column and optionally some specific constraints or
properties for that column. All this is specified in an SQL
create table statement. Run `sqltool` and enter the following SQL statements
to accomplish the table creation and linking to the corresponding CSV files:

```bash
$ cd $HOME/DB
$ sqltool project_codenet
```
```sql
sql> CREATE TEXT TABLE problems(
    id            VARCHAR( 6)    PRIMARY KEY NOT NULL,
    name          VARCHAR(64),
    dataset       VARCHAR(16)    NOT NULL,
    time_limit    INTEGER,
    memory_limit  INTEGER,
    rating        INTEGER,
    tags          VARCHAR(64),
    complexity    VARCHAR(32)
);

SET TABLE problems READ ONLY;

SET TABLE problems SOURCE 'problems.csv;encoding=UTF-8;\
cache_rows=50000;cache_size=10240000;ignore_first=true;\
fs=,;qc=\quote';

sql> CREATE TEXT TABLE submissions(
    submission_id     VARCHAR(10)    PRIMARY KEY NOT NULL,
    problem_id        VARCHAR( 6)    NOT NULL,
    user_id           VARCHAR(10)    NOT NULL,
    date              BIGINT         NOT NULL,
    language          VARCHAR(16)    NOT NULL,
    original_language VARCHAR(16)    NOT NULL,
    filename_ext      VARCHAR(16)    NOT NULL,
    status            VARCHAR(32)    NOT NULL,
    cpu_time          INTEGER        NOT NULL,
    memory            INTEGER        NOT NULL,
    code_size         INTEGER        NOT NULL,
    accuracy          VARCHAR(16)
);

SET TABLE submissions READ ONLY;

SET TABLE submissions SOURCE 'submissions.csv;encoding=UTF-8;\
cache_rows=50000;cache_size=10240000;ignore_first=true;\
fs=,;qc=\quote';

sql> commit;
sql> \q
```

Note the `commit` command (abbreviated as `\=`); this is absolutely
vital: it commits all the changes to the database. Without it all our
effort would get lost as soon as we quit. The commit of the
submissions table will take a while (maybe several minutes) because
the large `submissions.csv` file has to be read and converted into an
internal format. So be patient.

## A few simple SQL queries

```sql
sql> -- How many distinct programming languages are used:
sql> select count(distinct language) from submissions;

sql> -- How many submissions per language:
sql> select language, count(*) as nr_submissions
       from submissions group by language
       order by nr_submissions desc;

sql> -- how many accepted submissions with code size >= 500 per language:
sql> select language, count(*) as accepted_submissions
       from submissions
       where status = 'Accepted' and code_size >= 500
       group by language order by accepted_submissions desc;

sql> -- How many problems with >= 200 accepted submissions per language:
sql> select language, count(*) as problems
       from (select problem_id, language, count(*) as accepted
               from submissions where status = 'Accepted'
               group by problem_id, language
               having count(*) >= 200)
       group by language order by problems desc;
```

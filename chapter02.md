<!-- README.md is generated from README.Rmd. -->
init
====

Spark's Python and Scala Shells
-------------------------------

-   In Spark, computation operations are expressed through distributed collections that are automatically parallelized across the cluster. These collections are called *resilient distributed datasets*, or *RDDs*. RDDs are Spark's fundamental abstraction for distributed data and computation.

<!-- -->

    # start spark

    # python shell
    pyspark

    # scala shell
    spark-shell

    # disable verbose logging message
    # cp conf/log4j.properties.template conf/log4j.properties
    # emacs conf/log4j.properties
    # -> log4j.rootCategory=INFO, console
    # <- log4j.rootCategory=WARN, console

Spark's Core Concepts
---------------------

-   At a high level, every Spark application consists of a driver program that launches various parallel operations on a cluster. The driver program contains application's main function and defines distributed datasets on the cluster, then applies operations to them. The driver program in interactive runs is the Spark shell itself, and one could just type in the operations one wants to run.

-   Driver programs access Spark through a SparkContext object, which represents a connection to a computing cluster. In the shell, a SparkContext is automatically created as the variable called sc.

-   RDDs are built with a given a SparkContext: call `sc.textFile()` to create an RDD representing the lines of text in a file. Then, various operations such as `count()` can run on RDDs. To run these operations, driver programs typically manage a number of nodes called executors. For example, when `count()` is running on a cluster, different machines might count lines in different ranges of the file.

<!-- -->

    pyspark

    sc

    ln = sc.textFile("README.md")

    ln.count()

    ln.first()

    pyLn = ln.filter(lambda line: "Python" in line)

    pyLn.first()

Standalone Spark Applications
=============================

    # run standalone scripts
    spark-submit my_script.py

    # init spark in python
    from pyspark import SparkConf, SparkContext

    # create SparkContext with clusterURL and applicationName
    sc = SparkContext(conf = SparkConf().setMaster("local").setAppName("My App"))

-   On Azure HDInsight with Spark: `pyspark` is init by file: `/usr/hdp/2.4.2.0-258/spark/python/pyspark/shell.py`

<!-- -->

    pyspark

    >>> SparkContext()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/hdp/2.4.2.0-258/spark/python/pyspark/context.py", line 112, in __init__
        SparkContext._ensure_initialized(self, gateway=gateway)
      File "/usr/hdp/2.4.2.0-258/spark/python/pyspark/context.py", line 261, in _ensure_initialized
        callsite.function, callsite.file, callsite.linenum))
    ValueError: Cannot run multiple SparkContexts at once; existing SparkContext(app=PySparkShell, master=yarn-client) created by <module> at /usr/hdp/2.4.2.0-258/spark/python/pyspark/shell.py:43

    # shell.py

    # Licensed to the Apache Software Foundation (ASF) under one or more
    # contributor license agreements.  See the NOTICE file distributed with
    # this work for additional information regarding copyright ownership.
    # The ASF licenses this file to You under the Apache License, Version 2.0
    # (the "License"); you may not use this file except in compliance with
    # the License.  You may obtain a copy of the License at
    #
    #    http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    #

    """
    An interactive shell.

    This file is designed to be launched as a PYTHONSTARTUP script.
    """

    import atexit
    import os
    import platform

    import py4j

    import pyspark
    from pyspark.context import SparkContext
    from pyspark.sql import SQLContext, HiveContext
    from pyspark.storagelevel import StorageLevel

    # this is the deprecated equivalent of ADD_JARS
    add_files = None
    if os.environ.get("ADD_FILES") is not None:
        add_files = os.environ.get("ADD_FILES").split(',')

    if os.environ.get("SPARK_EXECUTOR_URI"):
        SparkContext.setSystemProperty("spark.executor.uri", os.environ["SPARK_EXECUTOR_URI"])

    sc = SparkContext(pyFiles=add_files)
    atexit.register(lambda: sc.stop())

    try:
        # Try to access HiveConf, it will raise exception if Hive is not added
        sc._jvm.org.apache.hadoop.hive.conf.HiveConf()
        sqlContext = HiveContext(sc)
    except py4j.protocol.Py4JError:
        sqlContext = SQLContext(sc)
    except TypeError:
        sqlContext = SQLContext(sc)

    # for compatibility
    sqlCtx = sqlContext

    print("""Welcome to
          ____              __
         / __/__  ___ _____/ /__
        _\ \/ _ \/ _ `/ __/  '_/
       /__ / .__/\_,_/_/ /_/\_\   version %s
          /_/
    """ % sc.version)
    print("Using Python version %s (%s, %s)" % (
        platform.python_version(),
        platform.python_build()[0],
        platform.python_build()[1]))
    print("SparkContext available as sc, %s available as sqlContext." % sqlContext.__class__.__name__)

    if add_files is not None:
        print("Warning: ADD_FILES environment variable is deprecated, use --py-files argument instead")
        print("Adding files: [%s]" % ", ".join(add_files))

    # The ./bin/pyspark script stores the old PYTHONSTARTUP value in OLD_PYTHONSTARTUP,
    # which allows us to execute the user's PYTHONSTARTUP file:
    _pythonstartup = os.environ.get('OLD_PYTHONSTARTUP')
    if _pythonstartup and os.path.isfile(_pythonstartup):
        with open(_pythonstartup) as f:
            code = compile(f.read(), _pythonstartup, 'exec')
            exec(code)

-   Follow Book and [This Blog](http://www.mccarroll.net/blog/pyspark2/), a simple word count in pyspark:

<!-- -->

    # chapter02_wc.py

    import os
    import sys
    import platform

    import py4j

    import pyspark
    from pyspark.context import SparkContext
    from pyspark.sql import SQLContext, HiveContext
    from pyspark.storagelevel import StorageLevel

    # init - create SparkContext on Azure HdInsight
    # on Azure HdInsight master was deafult to yarn
    sc = SparkContext(appName="wc")

    print "sys.argv[1]: ", sys.argv[1] 

    wc = sc.textFile(sys.argv[1]) \
      .map( lambda x: x.replace(',',' ').replace('.',' ').replace('-',' ').lower()) \
      .flatMap(lambda x: x.split(" ")) \
      .map(lambda x: (x, 1)) \
      .reduceByKey(lambda x, y: x + y)

    print wc.collect()

-   Note that on Azure HdInsight, `master` is default to `yarn` and path is deafult to `wasb:://[usrname]@[storageAccount]/deafultPath/`. As a result, the input file for the above word count scripts should be on HDFS, rather than local.

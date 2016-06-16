<!-- README.md is generated from README.Rmd. -->
RDD
===

RDD Basics
----------

-   An RDD in Spark is simply an immutable distributed collection of objects. Each RDD is split into multiple partitions, which may be computed on different nodes of the cluster. RDDs can contain any type of Python, Java, or Scala objects, including userdefined classes.

-   Once created, RDDs offer two types of operations: transformations and actions.

    -   Transformations construct a new RDD from a previous one. Like `filter()`.

    -   Actions, on the other hand, compute a result based on an RDD, and either return it to the driver program or save it to an external storage system (e.g., HDFS). Like `first()`.

    -   Transformations and actions are different because of the way Spark computes RDDs. Although new RDDs can be defined at any time, Spark computes them only in a **lazy** fashion—that is, the first time they are used in an action.

-   Finally, Spark's RDDs are by default recomputed each time one run an action on them. If one would like to reuse an RDD in multiple actions, ask Spark to **persist** it using `RDD.persist()`.

    -   `RDD.persist()` can define persistence level as MEMORY\_ONLY, MEMORY\_ONLY\_SER, MEMORY\_AND\_DISK, MEMORY\_AND\_DISK\_SER and DISK\_ONLY.

    -   `cache()` is the same as calling `persist()` with the default storage level.

-   To summarize, every Spark program and shell session will work as follows:

    1.  Create some input RDDs from external data.

    2.  Transform them to define new RDDs using transformations like filter().

    3.  Ask Spark to persist() any intermediate RDDs that will need to be reused.

    4.  Launch actions such as count() and first() to kick off a parallel computation, which is then optimized and executed by Spark.

Creating RDDs
-------------

-   Spark provides two ways to create RDDs: loading an external dataset and parallelizing a collection in driver program.

    -   Parallelize a collection: often in testing, entire dataset in memory on one machine.

    <!-- -->

        # python
        lines = sc.parallelize(["pandas", "i like pandas"])

    -   Load data from external storage:

    <!-- -->

        # python
        lines = sc.textFile("/path/to/README.md")

[RDD Operations](https://spark.apache.org/docs/1.1.1/api/python/pyspark.rdd.RDD-class.html)
-------------------------------------------------------------------------------------------

-   Again, RDDs support two types of operations: transformations and actions.

    -   Transformations are operations on RDDs that return a new RDD, such as `map()` and `filter()`. Spark keeps track of the set of dependencies between different RDDs, called the **lineage graph**, when one derives new RDDs from each other using transformations. It uses this information to compute each RDD on demand and to recover lost data if part of a persistent RDD is lost.

    -   Actions are operations that return a result to the driver program or write it to storage, and kick off a computation, such as `count()` and `first()`.

    -   Whenever confused whether a given function is a transformation or an action, look at its return type: **transformations return RDDs, whereas actions return some other data type**.

    -   Lazy evaluation: when a transformation is called on an RDD, the operation is not immediately performed. Instead, Spark internally records metadata to indicate that this operation has been requested. Rather than thinking of an RDD as containing specific data, it is best to **think of each RDD as consisting of instructions on how to compute the data that we build up through transformations**. Loading data into an RDD is lazily evaluated in the same way transformations are. So, when we call sc.textFile(), the data is not loaded until it is necessary.

-   Passing Functions to Spark

    -   Three options in Python for passing functions into Spark: lambda expressions, top-level functions, or locally defined functions.

    <!-- -->

        # Passing functions in Python
        word = rdd.filter(lambda s: "error" in s)
        def containsError(s):
          return "error" in s
        word = rdd.filter(containsError)

    -   Note: when passing functions watch out for inadvertently serializing the object containing the function. When a function passed is the member of an object, or contains references to fields in an object (e.g., self.field), Spark sends the entire object to worker nodes, which can be much larger than the bit of information needed. Sometimes this can also cause program to fail, if class contains objects that Python can't figure out how to pickle. Instead, just extract the fields needed from object into a local variable and pass them.

    <!-- -->

        # Passing a function with field references (don't do this!)
        class SearchFunctions(object):
          def __init__(self, query):
            self.query = query
          def isMatch(self, s):
            return self.query in s
          def getMatchesFunctionReference(self, rdd):
            # Problem: references all of "self" in "self.isMatch"
            return rdd.filter(self.isMatch)
          def getMatchesMemberReference(self, rdd):
            # Problem: references all of "self" in "self.query"
            return rdd.filter(lambda x: self.query in x)

        # Python function passing without field references
        class WordFunctions(object):
          ...
          def getMatchesNoReference(self, rdd):
            # Safe: extract only the field we need into a local variable
            query = self.query
            return rdd.filter(lambda x: query in x)

-   See all PySpark RDD class methods at <https://spark.apache.org/docs/1.1.1/api/python/pyspark.rdd.RDD-class.html>.

Common Transformations and Actions
----------------------------------

-   Transformations and Actions Applied to All Basic RDDs

    -   Basic RDD transformations on an RDD containing {1, 2, 3, 3}

        <table style="width:51%;">
        <colgroup>
        <col width="19%" />
        <col width="11%" />
        <col width="11%" />
        <col width="9%" />
        </colgroup>
        <thead>
        <tr class="header">
        <th align="left">Function Name</th>
        <th align="left">Purpose</th>
        <th align="left">Example</th>
        <th align="left">Result</th>
        </tr>
        </thead>
        <tbody>
        <tr class="odd">
        <td align="left">map()</td>
        <td align="left">Apply a function to each element in the RDD and return an RDD of the result.</td>
        <td align="left">rdd.map(x =&gt; x + 1)</td>
        <td align="left">{2, 3, 4, 4}</td>
        </tr>
        <tr class="even">
        <td align="left">flatMap()</td>
        <td align="left">Apply a function to each element in the RDD and return an RDD of the contents of the iterators returned. Often used to extract words.</td>
        <td align="left">rdd.flatMap(x =&gt; x.to(3))</td>
        <td align="left">{1, 2, 3, 2, 3, 3, 3}</td>
        </tr>
        <tr class="odd">
        <td align="left">filter()</td>
        <td align="left">Return an RDD consisting of only elements that pass the condition passed to filter().</td>
        <td align="left">rdd.filter(x =&gt; x != 1)</td>
        <td align="left">{2, 3, 3}</td>
        </tr>
        <tr class="even">
        <td align="left">distinct()</td>
        <td align="left">Remove duplicates - expensive as shuffle required.</td>
        <td align="left">rdd.distinct()</td>
        <td align="left">{1, 2, 3}</td>
        </tr>
        <tr class="odd">
        <td align="left">sample(withReplacement, fraction, [seed])</td>
        <td align="left">Sample an RDD, with or without replacement.</td>
        <td align="left">rdd.sample(false, 0.5)</td>
        <td align="left">Nondeterministic</td>
        </tr>
        </tbody>
        </table>

    -   Two-RDD transformations on RDDs containing {1, 2, 3} and {3, 4, 5}

        <table style="width:51%;">
        <colgroup>
        <col width="19%" />
        <col width="11%" />
        <col width="11%" />
        <col width="9%" />
        </colgroup>
        <thead>
        <tr class="header">
        <th align="left">Function Name</th>
        <th align="left">Purpose</th>
        <th align="left">Example</th>
        <th align="left">Result</th>
        </tr>
        </thead>
        <tbody>
        <tr class="odd">
        <td align="left">union()</td>
        <td align="left">Produce an RDD containing elements from both RDDs - duplicates keeps as duplicates.</td>
        <td align="left">rdd.union(other) {1, 2, 3, 3, 4, 5}</td>
        </tr>
        <tr class="even">
        <td align="left">intersection()</td>
        <td align="left">RDD containing only elements found in both RDDs - duplicates are removed even in single RDD - expensive as shuffle required.</td>
        <td align="left">rdd.intersection(other)</td>
        <td align="left">{3}</td>
        </tr>
        <tr class="odd">
        <td align="left">subtract()</td>
        <td align="left">Remove the contents of one RDD - diff(x, y) - expensive as shuffle required.</td>
        <td align="left">rdd.subtract(other)</td>
        <td align="left">{1, 2}</td>
        </tr>
        <tr class="even">
        <td align="left">cartesian()</td>
        <td align="left">Cartesian product between RDD X and Y.</td>
        <td align="left">rdd.cartesian(other) {(1, 3), (1,4), ..., (3,5)}</td>
        </tr>
        </tbody>
        </table>

    -   Basic RDD actions on an RDD containing rdd {1, 2, 3, 3}

        <table style="width:51%;">
        <colgroup>
        <col width="19%" />
        <col width="11%" />
        <col width="11%" />
        <col width="9%" />
        </colgroup>
        <thead>
        <tr class="header">
        <th align="left">Function Name</th>
        <th align="left">Purpose</th>
        <th align="left">Example</th>
        <th align="left">Result</th>
        </tr>
        </thead>
        <tbody>
        <tr class="odd">
        <td align="left">collect()</td>
        <td align="left">Return all elements from the RDD.</td>
        <td align="left">rdd.collect()</td>
        <td align="left">{1, 2, 3, 3}</td>
        </tr>
        <tr class="even">
        <td align="left">count()</td>
        <td align="left">Number of elements in the RDD.</td>
        <td align="left">rdd.count()</td>
        <td align="left">4</td>
        </tr>
        <tr class="odd">
        <td align="left">countByValue()</td>
        <td align="left">Number of times each element occurs in the RDD.</td>
        <td align="left">rdd.countByValue()</td>
        <td align="left">{(1, 1), (2, 1), (3, 2)}</td>
        </tr>
        <tr class="even">
        <td align="left">take(num)</td>
        <td align="left">Return num elements from the RDD.</td>
        <td align="left">rdd.take(2)</td>
        <td align="left">{1, 2}</td>
        </tr>
        <tr class="odd">
        <td align="left">top(num)</td>
        <td align="left">Return the top num elements the RDD.</td>
        <td align="left">rdd.top(2)</td>
        <td align="left">{3, 3}</td>
        </tr>
        <tr class="even">
        <td align="left">takeOrdered(num, key=None)</td>
        <td align="left">Return num elements based on provided ordering.</td>
        <td align="left">rdd.takeOrdered(3, key = lambda x: -x)</td>
        <td align="left">{3, 3, 2}</td>
        </tr>
        <tr class="odd">
        <td align="left">takeSample(withReplacement, num, [seed])</td>
        <td align="left">Return num elements at random.</td>
        <td align="left">rdd.takeSample(false, 1)</td>
        <td align="left">Nondeterministic</td>
        </tr>
        <tr class="even">
        <td align="left">reduce(func)</td>
        <td align="left">Combine the elements of the RDD together in parallel (e.g., sum). rdd.reduce((x, y) =&gt; x + y)</td>
        <td align="left">9</td>
        </tr>
        <tr class="odd">
        <td align="left">fold(zero, op)</td>
        <td align="left">Same as reduce() but with the provided zero value.</td>
        <td align="left">rdd.fold(0)((x, y) =&gt; x + y)</td>
        <td align="left">9</td>
        </tr>
        <tr class="even">
        <td align="left">aggregate(zeroValue, seqOp, combOp)</td>
        <td align="left">Similar to reduce() but used to return a different type.</td>
        <td align="left">rdd.aggregate((0, 0), lambda acc, value: (acc[0] + value, acc[1] + 1), lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1]))</td>
        <td align="left">(9, 4)</td>
        </tr>
        <tr class="odd">
        <td align="left">foreach(func)</td>
        <td align="left">Apply the provided function to each element of the RDD.</td>
        </tr>
        </tbody>
        </table>

    -   yg.note: The difference between reduce() and fold():

        -   reduce is a "... commutative and associative binary operator" as specifically specified on the [Spark documentation](http://spark.apache.org/docs/1.0.0/api/scala/index.html#org.apache.spark.rdd.RDD), whereas,

        -   fold only requires associativity, not commutativity, under the (strict) Map Reduce programming model we cannot define fold because chunks do not have an ordering, Spark does have fold because its framework is a super-set of the Map Reduce programming model and can order its chunks, well you can actually do this in Hadoop too, but Scalding doesn't seem to expose this functionality in the current version, so there is no fold method in Scalding, only foldLeft.

        -   simply put, reduce works without an order of cumulation, fold requires an order of cumulation and it is that order of cumulation that necessitates a zero value NOT the existence of the zero value that distinguishes them.

    -   yg.note: I know map() is a transformation and foreach() is an action, but what is the difference between map and foreach?

        -   [The main difference between the two methods is conceptual and stylistic: you use forEach when you want to do something to or with each element of an array (doing "with" is what the post you cite meant by "side-effects", i think), whereas you use map when you want to copy and transform each element of an array (without changing the original).](http://stackoverflow.com/questions/354909/is-there-a-difference-between-foreach-and-map)

        -   [The important difference between them is that map accumulates all of the results into a collection, whereas foreach returns nothing. map is usually used when you want to transform a collection of elements with a function, whereas foreach simply executes an action for each element.](http://stackoverflow.com/questions/3034392/what-use-does-the-javascript-foreach-method-have-that-map-cant-do/4927981#4927981)

-   Statistical Functions on RDDs of Numbers - chapter06

-   key/value Operations on RDDs of key/value Pairs - chapter04

Persistence (Caching)
---------------------

-   Spark has many levels of persistence - In Scala and Java, the default persist() will store the data in the JVM heap as unserialized objects. In Python, it always serialize the data that persist stores, so the default is instead stored in the JVM heap as pickled objects. When it write data out to disk or off-heap storage, that data is also always serialized.

-   Persistence levels from org.apache.spark.storage.StorageLevel and pyspark.StorageLevel; if desired we can replicate the data on two machines by adding \_2 to the end of the storage level

<table style="width:74%;">
<colgroup>
<col width="8%" />
<col width="15%" />
<col width="12%" />
<col width="13%" />
<col width="11%" />
<col width="12%" />
</colgroup>
<thead>
<tr class="header">
<th align="left">Level</th>
<th align="left">Space used</th>
<th align="left">CPU time</th>
<th align="left">In memory</th>
<th align="left">On disk</th>
<th align="left">Comments</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td align="left">MEMORY_ONLY</td>
<td align="left">High</td>
<td align="left">Low</td>
<td align="left">Y</td>
<td align="left">N</td>
</tr>
<tr class="even">
<td align="left">MEMORY_ONLY_SER</td>
<td align="left">Low</td>
<td align="left">High</td>
<td align="left">Y</td>
<td align="left">N</td>
</tr>
<tr class="odd">
<td align="left">MEMORY_AND_DISK</td>
<td align="left">High</td>
<td align="left">Medium</td>
<td align="left">Some</td>
<td align="left">Some</td>
<td align="left">Spills to disk if there is too much data to fit in memory.</td>
</tr>
<tr class="even">
<td align="left">MEMORY_AND_DISK_SER</td>
<td align="left">Low</td>
<td align="left">High</td>
<td align="left">Some</td>
<td align="left">Some</td>
<td align="left">Spills to disk if there is too much data to fit in memory. Stores serialized representation in memory.</td>
</tr>
<tr class="odd">
<td align="left">DISK_ONLY</td>
<td align="left">Low</td>
<td align="left">High</td>
<td align="left">N</td>
<td align="left">Y</td>
</tr>
</tbody>
</table>

-   RDDs come with a method `unpersist()` that allows manually remove persisted data from the cache.

-   yg.note: [pyspark documenation](https://spark.apache.org/docs/1.1.1/api/python/pyspark.rdd.RDD-class.html):

    -   `rdd.checkpoint()`: Mark this RDD for checkpointing. It will be saved to a file inside the checkpoint directory set with SparkContext.setCheckpointDir() and all references to its parent RDDs will be removed. This function must be called before any job has been executed on this RDD. It is strongly recommended that this RDD is persisted in memory, otherwise saving it on a file will require recomputation.

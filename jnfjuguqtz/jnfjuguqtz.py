import random, os
from pyspark import SparkContext
sc =SparkContext()
NUM_SAMPLES = os.environ["num_samples"]
NUM_SAMPLES=int(NUM_SAMPLES)
def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1

count = sc.parallelize(range(0, NUM_SAMPLES)) \
             .filter(inside).count()
print("Pi is roughly %f" % (4.0 * 1 / NUM_SAMPLES))
import numpy
import math
import pandas as pd

print("m", int((float(1936802415164)-float(1710206951735))/1e6))
# print("m", int((float(1710227306959)-float(1710206951735))/1e6))
# print("a", int((float(1710222454664)-float(1710206951735))/1e6))
# print("a", int((float(1710242840406)-float(1710206951735))/1e6))
# print("m", int((float(1710246929762)-float(1710206951735))/1e6))
# print("a", int((float(1710262829420)-float(1710206951735))/1e6))
# print("m", int((float(1710266918776)-float(1710206951735))/1e6))
# print(float(1710227306959)-float(1710206951735))
# print(int((float(1710227306959)-float(1710206951735))/1e6))

# st = numpy.append([5, 6], 2, axis=None)
# print(st)

a=4
for i in range(1000):
    if i>=a:
        break
    else:
        print(i)

print(math.isnan(numpy.NaN))

df = pd.DataFrame()
df.columns = ['st', 'ax', 'ay']

# TODO: Parse the XML file, save the values from sensors as g,m,v (+maybe wifi), the use a similar algorithm to the other program from the paper (check the max difference between time 0 and time n, iterate thorugh that interval range, for every range map the x,y,z values of each sensor in a dict/list, then create a dataframe to vizualize better the values)

if __name__ == "__main__":
    pass
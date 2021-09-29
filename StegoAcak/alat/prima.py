#Source:https://www.geeksforgeeks.org/nearest-prime-less-given-number-n/ 
# Python3 program to find the nearest
# prime to n.
import math
MAX = 5000
 
# array to store all primes less
# than 10^6
primes = []
 
# Utility function of Sieve of Sundaram
def Sieve():
 
    n = MAX
 
    # In general Sieve of Sundaram, produces
    # primes smaller than (2*x + 2) for a
    # number given number x
    nNew = int(math.sqrt(n))
 
    # This array is used to separate numbers
    # of the form i+j+2ij from others where
    # 1 <= i <= j
    marked = [0] * (int(n / 2 + 500))
 
    # eliminate indexes which does not
    # produce primes
    for i in range(1, int((nNew - 1) / 2) + 1):
        for j in range(((i * (i + 1)) << 1),
                        (int(n / 2) + 1), (2 * i + 1)):
            marked[j] = 1
 
    # Since 2 is a prime number
    primes.append(2)
 
    # Remaining primes are of the form
    # 2*i + 1 such that marked[i] is false.
    for i in range(1, int(n / 2) + 1):
        if (marked[i] == 0):
            primes.append(2 * i + 1)
 
# modified binary search to find nearest
# prime less than N
def binarySearch(left, right, n):
    if (left <= right):
        mid = int((left + right) / 2)
 
        # base condition is, if we are reaching
        # at left corner or right corner of
        # primes[] array then return that corner
        # element because before or after that
        # we don't have any prime number in
        # primes array
        if (mid == 0 or mid == len(primes) - 1):
            return primes[mid]
 
        # now if n is itself a prime so it will
        # be present in primes array and here
        # we have to find nearest prime less than
        # n so we will return primes[mid-1]
        if (primes[mid] == n):
            return primes[mid - 1]
 
        # now if primes[mid]<n and primes[mid+1]>n
        # that means we reached at nearest prime
        if (primes[mid] < n and primes[mid + 1] > n):
            return primes[mid]
        if (n < primes[mid]):
            return binarySearch(left, mid - 1, n)
        else:
            return binarySearch(mid + 1, right, n)
 
    return 0

def driver(n):
    Sieve()
    return binarySearch(0, len(primes), n)
 
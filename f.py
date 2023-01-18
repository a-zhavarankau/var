A = [1,    2,   3,   4,   5,   6,   7,   8,   9,    9]
B = ["c", "a", "b", "c", "a", "b", "c", "a", "b", "c"]

b_keys = set(B)
d = {i: 0 for i in b_keys}
for i, j in zip(B, A):
    d[i] += j


print(b_keys)
print(d)
# Criterion E via GF(2)[x] gcd: exists a in mu_e\{1} with 1+a in mu_e  <=>  gcd(x^e+1,(x+1)^e+1) nontrivial
import math
def pmod(a,b):
    db=b.bit_length()
    while a and a.bit_length()>=db: a^=b<<(a.bit_length()-db)
    return a
def pgcd(a,b):
    while b: a,b=b,pmod(a,b)
    return a
def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1;b>>=1
    return r
def ppow(a,e):
    r=1
    while e:
        if e&1: r=pmul(r,a)
        a=pmul(a,a); e>>=1
    return r
def qualifies(e):
    f=(1<<e)|1; g=ppow(0b11,e)^1
    return pgcd(f,g).bit_length()>1
def critE(l,m):
    ex=l*m//math.gcd(l,m)
    while ex%2==0: ex//=2
    return any(qualifies(e) for e in range(3,ex+1) if ex%e==0)
if __name__=='__main__':
    print({e:qualifies(e) for e in (3,5,7,9,11,13,15,17,19,21,25,31,49,73,97)})

package org.lofar.calc;
/*************************************************************************
 *  Compilation:  javac Complex.java
 *  Execution:    java Complex
 *
 *  Data type for complex numbers.
 *
 *  The data type is "immutable" so once you create and initialize
 *  a complex object, you cannot change its value. The "final"
 *  keyword when declaring re and im enforces this rule, making it
 *  a compile-time error to change the .re or .im fields after
 *  they've been initialized.
 *
 *  % java Complex
 *  a = a = 5.0 + 6.0i
 *  b = -3.0 + 4.0i
 *  c = -39.0 + 2.0i
 *  d = -39.0 + -2.0i
 *  e = 5.0
 *
 *************************************************************************/

public class Complex {
    final double re;   // the real part
    final double im;   // the imaginary part

    // create a new object with the given real and imaginary parts
    public Complex(double real, double imag) {
        this.re = real;
        this.im = imag;
    }

    // return a string representation of the invoking object
    public String toString()  { return re + " + " + im + "i"; }

    // return |this|
    public double abs() { return Math.sqrt(re*re + im*im);  }

    // return a new object whose value is (this + b)
    public Complex plus(Complex b) { 
        Complex a = this;             // invoking object
        double real = a.re + b.re;
        double imag = a.im + b.im;
        Complex sum = new Complex(real, imag);
        return sum;
    }

    // return a new object whose value is (this - b)
    public Complex minus(Complex b) { 
        Complex a = this;   
        double real = a.re - b.re;
        double imag = a.im - b.im;
        Complex diff = new Complex(real, imag);
        return diff;
    }

    // return a new object whose value is (this * b)
    public Complex times(Complex b) {
        Complex a = this;
        double real = a.re * b.re - a.im * b.im;
        double imag = a.re * b.im + a.im * b.re;
        Complex prod = new Complex(real, imag);
        return prod;
    }

    // return a new object whose value is (this * alpha)
    public Complex times(double alpha) {
        return new Complex(alpha * re, alpha * im);
    }

    // return a new object whose value is the conjugate of this
    public Complex conjugate() {  return new Complex(re, -im); }


    // sample client for testing
    public static void main(String[] args) {
        Complex a = new Complex( 5.0, 6.0);
        System.out.println("a = " + a);

        Complex b = new Complex(-3.0, 4.0);
        System.out.println("b = " + b);

        Complex c = b.times(a);
        System.out.println("c = " + c);

        Complex d = c.conjugate();
        System.out.println("d = " + d);

        double e = b.abs();
        System.out.println("e = " + e);

        Complex f = a.plus(b);
        System.out.println("f = " + f);
    }

}



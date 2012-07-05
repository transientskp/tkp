package org.lofar.calc;
/*************************************************************************
 *  Compilation:  javac Phasor.java
 *  Execution:    java Phasor
 *
 *  Data type for complex numbers.
 *
 *  The data type is "immutable" so once you create and initialize
 *  a complex object, you cannot change its value. The "final"
 *  keyword when declaring mod and phi enforces this rule, making it
 *  a compile-time error to change the .amp or .phi fields after
 *  they've been initialized.
 *
 *  % java Complex
 *  a = a = 5.0 + 6.0i
 *   za = |z|exp(i phi)
 *  b = -3.0 + 4.0i
 *  c = -39.0 + 2.0i
 *  d = -39.0 + -2.0i
 *  e = 5.0
 *
 *************************************************************************/

public class Phasor {
    final double mod;   // the modulus
    final double phi;   // the phase
    final Complex c;

    // create a new object with the given real and imaginary parts
    public Phasor(double mod, double phi) {
        this.mod = mod;
        this.phi = phi;
	//TODO: Afhankelijk van het kwadrant waarin de phasor zich bevindt
	//krijgt re of im een min-teken.
	this.c = new Complex(mod * Math.cos(phi), mod * Math.sin(phi));
    }

    // return a string representation of the invoking object
    public String toString()  { return "|" + mod + "| exp(i " + phi + ")"; }

    // return |this|
    public double abs() { return mod;  }

    // return a new object whose value is (this + b)
    public Phasor plus(Phasor b) { 
        Phasor a = this;             // invoking object
	System.out.println("plus: ph a = " + a.toString());
	System.out.println("plus: ph b = " + b.toString());
	Complex d = new Complex(b.mod * Math.cos(b.phi), b.mod * Math.sin(b.phi));
	System.out.println("plus: ph b -> c d = " + d.toString());
	Complex csum = c.plus(d);
	System.out.println("plus: c csum = " + csum.toString());
	Phasor sum = new Phasor(Math.sqrt(csum.re * csum.re + csum.im * csum.im), Math.atan(csum.im / csum.re));
	System.out.println("plus: ph sum = " + sum.toString());
        return sum;
    }

    // return a new object whose value is (this - b)
    public Phasor minus(Phasor b) { 
        Phasor a = this;   
	Complex d = new Complex(b.mod * Math.cos(b.phi), b.mod * Math.sin(b.phi));
	Complex cdiff = c.minus(d);
	Phasor diff = new Phasor(Math.sqrt(cdiff.re * cdiff.re + cdiff.im * cdiff.im), Math.atan(cdiff.im / cdiff.re));
        return diff;
    }

    // return a new object whose value is (this * b)
    public Phasor times(Phasor b) {
        Phasor a = this;
	Complex d = new Complex(b.mod * Math.cos(b.phi), b.mod * Math.sin(b.phi));
	Complex cprod = c.times(d);
	Phasor prod = new Phasor(Math.sqrt(cprod.re * cprod.re + cprod.im * cprod.im), Math.atan(cprod.im / cprod.re));
        return prod;
    }

    // return a new object whose value is (this * alpha)
    public Phasor times(double alpha) {
        return new Phasor(alpha * mod, phi);
    }

    // return a new object whose value is the conjugate of this
    public Phasor conjugate() {  return new Phasor(mod, -phi); }


    // sample client for testing
    public static void main(String[] args) {
        //Complex a = new Complex( 5.0, 6.0);
	// Same  phasor as complex number above for comparison
        Phasor a = new Phasor(Math.sqrt(25. + 36.), Math.atan(6./5.));
        System.out.println("a = " + a);

        //Complex b = new Complex(-3.0, 4.0);
        Phasor b = new Phasor(Math.sqrt(9. + 16.), Math.atan(-4./3.));
        System.out.println("b = " + b);

        Phasor c = b.times(a);
        System.out.println("c = " + c);

        Phasor d = c.conjugate();
        System.out.println("d = " + d);

        double e = b.abs();
        System.out.println("e = " + e);

        Phasor f = a.plus(b);
        System.out.println("a = " + a);
        System.out.println("b = " + b);
        System.out.println("f = " + f);
    }

}



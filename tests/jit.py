#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Test.
#
import py
from rpython import conftest


class o:
    view = False
    viewloops = True
#    viewloops = False
conftest.option = o
from rpython.jit.metainterp.test.test_ajit import LLJitMixin

from som.vm.universe import Universe, Exit
import som.compiler.sourcecode_compiler as sourcecode_compiler


cp = py.path.local(__file__).dirpath().dirpath().join("Smalltalk").strpath


class TestLLtype(LLJitMixin):

    def _compile_and_lookup(self, source, start):
        u = Universe()
        u.setup_classpath(cp)
        u._initialize_object_system()
        cls = sourcecode_compiler.compile_class_from_string(source, None, u)
        obj = u.new_instance(cls)
        invokable = cls.lookup_invokable(u.symbol_for(start))
        return u, obj, invokable

    def _run_meta_interp(self, program, main_method):
        universe, rcvr, invokable = self._compile_and_lookup(program, main_method)

        def interp_w():
            try:
                invokable.invoke(None, rcvr, None)
            except Exit as e:
                return e.code
            return -1

        self.meta_interp(interp_w, [],
                         listcomp=True, listops=True, backendopt=True)

    def test_inc(self):
        self._run_meta_interp("""
            C_0 = (
                run = ( | tmp |
                        tmp := 1.
                        10000 timesRepeat: [
                          tmp := tmp + 1 ].
                        ^tmp
                )
            )
            """, "run")
    
    def test_purewhile(self):
        self._run_meta_interp("""
            C_0 = (
                run = ( | tmp |
                        tmp := 1.
                        [ tmp < 10000 ] whileTrue: [
                            tmp := tmp + 1 ].
                        ^tmp
                )
            )
            """, "run")

    def test_rec(self):
        self._run_meta_interp("""
            C_1 = (
                count: n = ( ^ (n > 0)
                                 ifTrue: [self count: n - 1]
                                 ifFalse: [n]
                )
                run = ( ^ self count: 100000 )
            )
            """, "run")


    def test_sieve(self):
        self._run_meta_interp("""
           "Adapted from Sieve.som"
            Sieve = (
                benchmark = (
                    | flags result |
                    flags  := Array new: 5000.
                    result := self sieve: flags size: 5000.
                    ^ (result = 669)
                )

                sieve: flags size: size = (
                    | primeCount |
                    primeCount := 0.
                    flags putAll: true.
                    2 to: size do: [ :i |
                        (flags at: i - 1) ifTrue: [
                            | k |
                            primeCount := primeCount + 1.
                            k := i + i.
                            [ k <= size ] whileTrue: [
                                flags at: k - 1 put: false. k := k + i ]]].
                    ^primeCount
                )
            )""", "benchmark")

    def test_field(self):
        self._run_meta_interp("""
           "Adapted from FieldLoop.som"
            FieldLoop = (
                | counter |

                benchmark = ( | iter |
                    counter := 0.
                    iter := 20000.

                    [ iter > 0 ] whileTrue: [
                      iter := iter - 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.

                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.

                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.

                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.

                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.

                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.
                      counter := counter + 1.]
                )
            )""", "benchmark")
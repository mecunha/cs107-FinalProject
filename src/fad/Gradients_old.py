#!/usr/bin/env python3

from FADiff import FADiff
import numpy as np


class Scal:
    """
    A class for...
    """
    def __init__(self, val, der=None, parents=[], name=None, new_input=False):
        """
        Inputs
        ------
            val : float
                value of the scalar variable
            der : float, dictionary
                derivative of the scalar variable
            parents : list of Scal objects
                the parent/grandparent vars of the variable
            name : str
                the name of the variable
            new_input : boolean
                if variable is an input variable
        """
        self._val = val
        if new_input:                       # Creating input var?
            self._der = {}                  # Add gradient dict for new var
            for var in FADiff._fadscal_inputs:    # Update gradient dicts for all vars
                self._der[var] = 0    # Partial der of others as 0 in self
                var._der[self] = 0    # Self's partial der as 0 in others
            self._der[self] = der     # Self's partial der in self
            FADiff._fadscal_inputs.append(self)   # Add self to global vars list
        else:
            self._der = der
        self._name = name  # TODO: Utilize if have time?
        self._parents = parents

    
    ### Basic Operations ###
    
    def __add__(self, other):
        """
        Adds self with other (self + other)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try: # if other is a Scal
            val = self._val + other._val
            der = {}
            for var, part_der in self._der.items(): 
                der[var] = part_der + other._der.get(var)
            parents = self._set_parents(self, other) 
        except AttributeError: # if other is a constant
            val = self._val + other
            der = self._der
            parents = self._set_parents(self)
        return Scal(val, der, parents)

    def __radd__(self, other):
        """
        Adds other with self (other + self)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        return self.__add__(other)

    def __sub__(self, other):
        """
        Subtracts other from self (self - other)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try:  # if other is a Scal
            val = self._val - other._val 
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives 
                der[var] = part_der - other._der.get(var)
            parents = self._set_parents(self, other)
        except AttributeError: # if other is a constant
            val = self._val - other
            der = self._der
            parents = self._set_parents(self)
        return Scal(val, der, parents)

    def __rsub__(self, other):
        """
        Subtracts self from other (other - self)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try:  # if other is a Scal
            val = other._val - self._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives 
                der[var] = other._der.get(var) - part_der
            parents = self._set_parents(self, other)
        except AttributeError: # if other is a constant
            val = other - self._val
            for var, part_der in self._der.items(): # loop through partial derivatives 
                der[var] = other - part_der
            parents = self._set_parents(self)
        return Scal(val, der, parents)
    
    def __mul__(self, other):
        """
        Mulitples self with other (self * other)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try: # if other is a Scal
            val = self._val * other._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives 
                der[var] = part_der * other._val + self._val * other._der.get(var) 
            parents = self._set_parents(self, other) 
        except AttributeError: # if other is a constant
            val = self._val * other
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = part_der * other
            parents = self._set_parents(self)
        return Scal(val, der, parents)

    def __rmul__(self, other):
        """
        Mulitples other with self (other * self)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        return self.__mul__(other)
    
    def __truediv__(self, other):
        """
        Divides self by other (self / other)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try: # if other is a Scal
            val = self._val / other._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives 
                der[var] = (part_der * other._val - self._val * other._der.get(var)) / (other._val * other._val)
            parents = self._set_parents(self, other) 
        except AttributeError: # if other is a constant
            val = self._val / other
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = part_der / other
            parents = self._set_parents(self)
        return Scal(val, der, parents)

    def __rtruediv__(self, other):
        """
        Divides other by self (other / self)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try: # if other is a Scal
            val = other._val / self._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives 
                der[var] = (self._val * other._der.get(var) - part_der * other._val) / (self._val * self._val)
            parents = self._set_parents(self, other) 
        except AttributeError: # if other is a constant
            val = other / self._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = (- other / (self._val * self._val)) * part_der
            parents = self._set_parents(self)
        return Scal(val, der, parents)

    def __pow__(self, other):
        """
        Raises self the other power (self ** other)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try: # if other is a Scal
            val = self._val ** other._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = other._val * (self._val ** (other._val - 1.)) * part_der
            parents = self._set_parents(self, other)
        except AttributeError: # if other is a constant
            val = self._val ** other
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = other * (self._val ** (other - 1.)) * part_der
            parents = self._set_parents(self)
        return Scal(val, der, parents)
    
    def __rpow__(self, other):
        """
        Raises other the self power (other ** self)
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: new Scal object
        """
        try: # if other is a Scal
            val = other._val ** self._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = (other._val ** self._val) * np.log(other._val) * part_der
            parents = self._set_parents(self, other)
        except AttributeError: # if other is a constant
            val = other ** self._val
            der = {}
            for var, part_der in self._der.items(): # loop through partial derivatives
                der[var] = (other ** self._val) * np.log(other) * part_der
            parents = self._set_parents(self)
        return Scal(val, der, parents)
    
    def __neg__(self):
        """
        Negates self (- self)
        
        Inputs: self (Scal object)
        Returns: new Scal object
        """
        val = - self._val
        der = {}
        for var, part_der in self._der.items():
            der[var] = - part_der
        parents = self._set_parents(self, other)
        return Scal(var, der, parents)
    
    
    ### Comparison Operators ###

    def __eq__(self, other):
        """
        Checks if self equals other
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: Boolean (True if self equals other, False otherwise)
        """
        try: # if other is a Scal
            return self._val == other._val
        except AttributeError: # if other is a constant
            return self._val == other
        
    def __ne__(self, other):
        """
        Checks if self does not equal other
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: Boolean (True if self does not equal other, False otherwise)
        """
        try: # if other is a Scal
            return self._val != other._val
        except AttributeError: # if other is a constant
            return self._val != other      
        
    def __lt__(self, other):
        """
        Checks if self is less than other
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: Boolean (True if self is less than other, False otherwise)
        """
        try: # if other is a Scal
            return self._val < other._val
        except AttributeError: # if other is a constant
            return self._val < other 
        
    def __le__(self, other):
        """
        Checks if self is less than or equal to other
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: Boolean (True if self is less than or equal to other, False otherwise)
        """
        try: # if other is a Scal
            return self._val <= other._val
        except AttributeError: # if other is a constant
            return self._val <= other   
        
    def __gt__(self, other):
        """
        Checks if self is greater than other
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: Boolean (True if self is greater than other, False otherwise)
        """
        try: # if other is a Scal
            return self._val > other._val
        except AttributeError: # if other is a constant
            return self._val > other 
        
    def __ge__(self, other):
        """
        Checks if self is greater than or equal to other
        
        Inputs: self (Scal object), other (either Scal object or constant)
        Returns: Boolean (True if self is greater than or equal to other, False otherwise)
        """
        try: # if other is a Scal
            return self._val >= other._val
        except AttributeError: # if other is a constant
            return self._val >= other 
    
    def __hash__(self):
        """
        Ensures that objects which are equal have the same hash value
        
        Inputs: self (Scal object)
        Returns: integer ID of self
        """
        return id(self)
 
    @property
    def val(self):
        '''Returns value'''
        return np.array([self._val])

    @property
    def der(self):
        '''Returns partial derivatives wrt all root input vars used'''
        parents = []
        for var, part_der in self._der.items():
            if var in self._parents:
                parents.append(part_der)
        if parents:                           # For output vars
            return parents
        elif self in FADiff._fadscal_inputs:       # For input vars (no parents)
            return np.array(self._der[self])

    @staticmethod
    def _set_parents(var1, var2=None):
        '''Sets parent/grandparent vars (including root input vars used)'''
        parents = []
        parents.append(var1)
        for parent in var1._parents:
            parents.append(parent)
        if var2:
            parents.append(var2)
            for parent in var2._parents:
                parents.append(parent)
        parents = list(set(parents))
        return parents
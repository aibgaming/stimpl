from typing import Any, Tuple, Optional

from stimpl.expression import *
from stimpl.types import *
from stimpl.errors import *

"""
Interpreter State
"""


class State(object):
    def __init__(self, variable_name: str, variable_value: Expr, variable_type: Type, next_state: 'State') -> None:
        self.variable_name = variable_name
        self.value = (variable_value, variable_type)
        self.next_state = next_state

    def copy(self) -> 'State':
        variable_value, variable_type = self.value
        return State(self.variable_name, variable_value, variable_type, self.next_state)

    def set_value(self, variable_name, variable_value, variable_type):
        return State(variable_name, variable_value, variable_type, self)

    def get_value(self, variable_name) -> Any:
        """ TODO: DONE. """
        if self.variable_name == variable_name:
            return self.value
        elif self.next_state == None:
            return None
        else:
            return self.next_state.get_value(variable_name)

    def __repr__(self) -> str:
        return f"{self.variable_name}: {self.value}, " + repr(self.next_state)


class EmptyState(State):
    def __init__(self):
        pass

    def copy(self) -> 'EmptyState':
        return EmptyState()

    def get_value(self, variable_name) -> None:
        return None

    def __repr__(self) -> str:
        return ""


"""
Main evaluation logic!
"""


def evaluate(expression: Expr, state: State) -> Tuple[Optional[Any], Type, State]:
    match expression:
        case Ren():
            return (None, Unit(), state)

        case IntLiteral(literal=l):
            return (l, Integer(), state)

        case FloatingPointLiteral(literal=l):
            return (l, FloatingPoint(), state)

        case StringLiteral(literal=l):
            return (l, String(), state)

        case BooleanLiteral(literal=l):
            return (l, Boolean(), state)

        case Print(to_print=to_print):
            printable_value, printable_type, new_state = evaluate(
                to_print, state)

            match printable_type:
                case Unit():
                    print("Unit")
                case _:
                    print(f"{printable_value}")

            return (printable_value, printable_type, new_state)

        case Sequence(exprs=exprs) | Program(exprs=exprs):
            """ TODO: DONE. """
            new_variable, new_type, new_state =None, None, state        # Intialize an empty variable with None type
            EMPTY_FLAG = True
            
            for expr in exprs:
                EMPTY_FLAG = False                                                  # Flip the flag varaible since exprs is not Empty
                new_variable, new_type, new_state = evaluate(expr, new_state)       # Assign the new variable with each evaluated expression
            if EMPTY_FLAG:
                return (None, Unit(), state)                                        # Return an Empty variable of Unit() type if no exprs is Empty 
            return(new_variable,new_type,new_state)

        case Variable(variable_name=variable_name):
            value = state.get_value(variable_name)
            if value == None:
                raise InterpSyntaxError(
                    f"Cannot read from {variable_name} before assignment.")
            variable_value, variable_type = value
            return (variable_value, variable_type, state)

        case Assign(variable=variable, value=value):

            value_result, value_type, new_state = evaluate(value, state)

            variable_from_state = new_state.get_value(variable.variable_name)
            _, variable_type = variable_from_state if variable_from_state else (
                None, None)

            if value_type != variable_type and variable_type != None:
                raise InterpTypeError(f"""Mismatched types for Assignment:
            Cannot assign {value_type} to {variable_type}""")

            new_state = new_state.set_value(
                variable.variable_name, value_result, value_type)
            return (value_result, value_type, new_state)

        case Add(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Add:
            Cannot add {left_type} to {right_type}""")

            match left_type:
                case Integer() | String() | FloatingPoint():
                    result = left_result + right_result
                case _:
                    raise InterpTypeError(f"""Cannot add {left_type}s""")

            return (result, left_type, new_state)

        case Subtract(left=left, right=right):
            """ TODO: DONE. """
            result = 0
            left_result, left_type, new_state = evaluate(left, state)           # Evaluate left variable tuple
            right_result, right_type, new_state = evaluate(right, new_state)    # Evaluate right variable tuple

            if left_type != right_type:                                         # Ensure that both variables are the same type
                raise InterpTypeError(f"""Mismatched types for Subtract:
            Cannot subtract {right_type} from {left_type}""")
            
            # Since both variables are the same type, just check the left variable
            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result - right_result         # Perform subtraction and pass the result
                case _:
                    raise InterpTypeError(f"""Cannot subtract {left_type}s""")
            return (result, left_type, new_state)               # Return result variable tuple

        case Multiply(left=left, right=right):
            """ TODO: DONE. """
            result = 0
            left_result, left_type, new_state = evaluate(left, state)           # Evaluate left variable tuple
            right_result, right_type, new_state = evaluate(right, new_state)    # Evaluate right variable tuple

            if left_type != right_type:                                         # Ensure that both variables are the same type
                raise InterpTypeError(f"""Mismatched types for Multiply:
            Cannot multiply {left_type} with {right_type}""")

            # Since both variables are the same type, just check the left variable
            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result * right_result         # Perform multiplication and pass the result
                case _:
                    raise InterpTypeError(f"""Cannot multiply {left_type}s""")
            
            return (result, left_type, new_state)           # Return result variable tuple

        case Divide(left=left, right=right):
            """ TODO: DONE. """
            result = 0
            left_result, left_type, new_state = evaluate(left, state)           # Evaluate left variable tuple
            right_result, right_type, new_state = evaluate(right, new_state)    # Evaluate right variable tuple

            if left_type != right_type:                                         # Ensure that both variables are the same type
                raise InterpTypeError(f"""Mismatched types for Divide:
            Cannot divide {right_type} from {left_type}""")

            if right_result == 0:
                raise InterpMathError(f"""Cannot divide by 0""")    # Raise a math error if division by 0 is attempted

            # Since both variables are the same type, just check the left variable
            match left_type:
                case Integer():
                    result = left_result // right_result        # Perform integer division and pass the result
                case FloatingPoint():
                    result = left_result / right_result         # Perform regular float division and pass the result
                case _:
                    raise InterpTypeError(f"""Cannot divide {left_type}s""")
            return (result, left_type, new_state)           # Return result variable tuple

        case And(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for And:
            Cannot evaluate {left_type} and {right_type}""")
            match left_type:
                case Boolean():
                    result = left_value and right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical and on non-boolean operands.")

            return (result, left_type, new_state)

        case Or(left=left, right=right):
            """ TODO: DONE. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:             # Raise type error to prevent mismatching of types
                raise InterpTypeError(f"""Mismatched types for Or:
            Cannot evaluate {left_type} or {right_type}""")
            
            # Since both variables are the same type, just check the left variable
            match left_type:
                case Boolean():
                    result = left_value or right_value      # Pass the result of or operator
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical Or on non-boolean operands.")

            return (result, left_type, new_state)       # Return result tuple

        case Not(expr=expr):
            """ TODO: DONE. """
            new_value, new_type, new_state = evaluate(expr, state)
            match new_type:
                case Boolean():
                    result = not(new_value)   # Value evaluated by Not operation
                case _:
                    raise InterpTypeError("Cannot perform logical Not on non-boolean operands.")
            return (result, new_type, new_state)        # Return result tuple

        case If(condition=condition, true=true, false=false):
            """ TODO: DONE. """
            condition_value, condition_type, new_state = evaluate(condition, state)
            match condition_type:
                case Boolean():
                    result = condition_value            # Just pass the condition value to the result
                case _:  
                    raise InterpTypeError("Cannot evaluate logical If on non-boolean conditions.")
                
            if result:                              # Evaluate the boolean condition value and return true/false (don't use python True/False)
                return evaluate(true, new_state)
            return evaluate(false, new_state)


        case Lt(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            # Raise type error to prevent mismatching of types
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lt:
            Cannot evaluate {left_type} < {right_type}""")

            # Since both variables are the same type, just check the left variable
            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value < right_value       # Pass the result of < operator
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform < on {left_type} type.")

            return (result, Boolean(), new_state)       

        case Lte(left=left, right=right):
            """ TODO: DONE. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None
            
            # Raise type error to prevent mismatching of types
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lte:
            Cannot evaluate {left_type} <= {right_type}""")

            # Since both variables are the same type, just check the left variable
            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value <= right_value          # Pass the result of <= operator
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform <= on {left_type} type.")

            return (result, Boolean(), new_state)

        case Gt(left=left, right=right):
            """ TODO: DONE. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            # Raise type error to prevent mismatching of types
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gt:
            Cannot evaluate {left_type} > {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value > right_value       # Pass the result of > operator
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform > on {left_type} type.")

            return (result, Boolean(), new_state)

        case Gte(left=left, right=right):
            """ TODO: DONE. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            # Raise type error to prevent mismatching of types
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gte:
            Cannot evaluate {left_type} >= {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value >= right_value      # Pass the result of >= operator
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform >= on {left_type} type.")

            return (result, Boolean(), new_state)

        case Eq(left=left, right=right):
            """ TODO: DONE. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Eq:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value == right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform = on {left_type} type.")

            return (result, Boolean(), new_state)

        case Ne(left=left, right=right):
            """ TODO: DONE. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Ne:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value != right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform != on {left_type} type.")

            return (result, Boolean(), new_state)

        case While(condition=condition, body=body):
            """ TODO: Implement. """
            condition_result, condition_type, new_state = evaluate(condition, state)
            match condition_type:
                case Boolean():                   # Condition type should be boolean
                    while(condition_result):    # Iterate while condition_result is true
                        body_result, body_type, new_state = evaluate(body, new_state)   # Evaluate body if condition is true
                        condition_result, condition_type, new_state = evaluate(condition, new_state) # Re-evaluate condition each iteration  
                    return (condition_result, condition_type, new_state) # Return the condition tuple once iteration is over
                case _:
                    raise InterpTypeError(f"Cannot evaluate non-boolean conditional")

        case _:
            raise InterpSyntaxError("Unhandled!")
    pass


def run_stimpl(program, debug=False):
    state = EmptyState()
    program_value, program_type, program_state = evaluate(program, state)

    if debug:
        print(f"program: {program}")
        print(f"final_value: ({program_value}, {program_type})")
        print(f"final_state: {program_state}")

    return program_value, program_type, program_state

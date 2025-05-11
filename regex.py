from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occurred character is handled by current state
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    def __init__(self):
        super().__init__()
        self.next_states: list[State] = []

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self) -> None:
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self):
        super().__init__()
        self.next_states: list[State] = []

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.next_states: list[State] = []
        self.symbol = symbol

    def check_self(self, curr_char: str) -> bool | Exception:
        return curr_char == self.symbol


class StarState(State):
    def __init__(self, checking_state: State):
        self.next_states: list[State] = []
        self.checking_state = checking_state
        self.next_states.append(checking_state)

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):
    def __init__(self, checking_state: State):
        self.next_states: list[State] = []
        self.checking_state = checking_state
        self.next_states.append(checking_state)

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state: State = StartState()
        prev_state, tmp_next_state = self.curr_state, self.curr_state

        i = 0
        after_star_plus_added, before_checking_star = None, None
        while i < len(regex_expr):
            char = regex_expr[i]
            next_symbol = regex_expr[i+1] if len(regex_expr) != i + 1 else None
            if next_symbol == '*':
                ascii_state = self.__init_next_state(char, prev_state)
                tmp_next_state = self.__init_next_state(next_symbol, ascii_state)
                ascii_state.next_states.append(tmp_next_state)

                prev_state.next_states.append(tmp_next_state)
                prev_state = tmp_next_state

                after_star_plus_added = ascii_state

                i += 2
                continue

            tmp_next_state = self.__init_next_state(char, prev_state)

            if after_star_plus_added is not None:
                after_star_plus_added.next_states.append(tmp_next_state)
                after_star_plus_added, before_checking_star = None, None

            if isinstance(tmp_next_state, PlusState):
                after_star_plus_added = tmp_next_state.checking_state

            prev_state.next_states.append(tmp_next_state)
            prev_state = tmp_next_state
            i += 1

        termination_state = TerminationState()
        if after_star_plus_added is not None:
            after_star_plus_added.next_states.append(termination_state)

        prev_state.next_states.append(termination_state)

    def __init_next_state(
        self, next_token: str, prev_state: State
    ) -> State:
        match next_token:
            case ".":
                new_state = DotState()

            case "*":
                new_state = StarState(prev_state)

            case "+":
                new_state = PlusState(prev_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string: str) -> bool:
        curr, i, curr_str_symbol = self.curr_state, 0, ''
        while i < len(string):
            curr_str_symbol = string[i]
            for state in curr.next_states:
                if isinstance(state, (StarState, PlusState)):
                    for s in state.next_states:
                        if s.check_self(curr_str_symbol):
                            curr = s

                    break

                elif state.check_self(curr_str_symbol):
                    curr = state
                    break

            else:
                return False

            i += 1

        curr = curr.next_states[0] if (isinstance(curr.next_states[0], (StarState, PlusState))
                                       and curr_str_symbol == curr.next_states[0].checking_state)\
            else curr
        return any(isinstance(state, TerminationState) for state in curr.next_states)

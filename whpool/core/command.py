
import abc
import argparse
from typing import List


class CommandResult:
    """
    Encapsulates the result of running a command.
    """
    def __init__(self, successful: bool, errors: List[str]):
        self.successful = successful
        self.errors = errors

    def was_successful(self) -> bool:
        """
        Returns True if the command was completed successfully, False otherwise
        """
        return self.successful

    def get_errors(self) -> List[str]:
        """
        A list of errors from running the command. Should return an empty
        list if no errors occurred.
        """
        return self.errors

    def __str__(self) -> str:
        """
         Returns a string representation of this object.
         """
        fullname = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return f"{fullname}@{id(self)}[result: {self.successful}, errors: {self.errors}]"


class Command(metaclass=abc.ABCMeta):
    """
    Interface for commands run via the CLI
    """
    @abc.abstractmethod
    def __call__(self, args: argparse.Namespace) -> CommandResult:
        raise NotImplementedError

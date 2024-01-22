#!/usr/bin/python3
"""Defines the my AirBnb console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def custom_parser(arg):
    curly_brace = re.search(r"\{(.*?)\}", arg)
    normal_brackets = re.search(r"\[(.*?)\]", arg)
    if curly_brace is None:
        if normal_brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:normal_brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(normal_brackets.group())
            return retl
    elif curly_brace is None:
            lexer = split(arg[:curly_brace.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(curly_brace.group())
            return retl


class MBNBCommand(cmd.Cmd):
    """Defines custom BnB command interpreter.

    Attributes:
       prompt (str): The command prompt.
    """

    prompt = "(hbnb) "
    __classes = {
            "BaseModel",
            "User",
            "State",
            "City",
            "Place",
            "Amenity",
            "Review"
    }

    def emptyline(self):
        """Do nothing upon receiving empty line."""
        pass

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
                "all": self.do_all,
                "show": self.do_show,
                "destroy": self.do_destroy,
                "count": self.do_count,
                "update": self.do_update
        }
        match_com = re.search(r"\.", arg)
        if match_com is not None:
            argl = [arg[:match_com.span()[0]], arg[match_com.span()[1]:]]
            match_com = re.search(r"\((.*?)\)", argl[1])
            if match_com is not None:
                command = [argl[1][:match_com.span()[0]], match_com.group()[1:-1]]
                if command[0] in argdict.keys():
                    call = "{} {}".format(argl[0], command[1])
                    return argdict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

    def do_quit(self, arg):
        """Quit command to exit program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit program."""
        print("")
        return True

    def do_create(self, arg):
        """Usage: create <class>
        Create a new class instance and print its id."""
        argl = custom_parser(arg)
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in MBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(argl[0])().id)
            storage.save()

    def do_show(self, arg):
        """Usage: show <class> <id>
        Display the string representation of a class instance of a given id."""
        argl = custom_parser(arg)
        objdict = storage.all()
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in MBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argl[0], argl[1]) not in objdict:
            print("** no instance found **")
        else:
            print(objdict["{}.{}".format(argl[0], argl[1])])

    def do_destroy(self, arg):
        """Usage: destroy <class> <id>
        Delete a class instance of a given id."""
        argl = custom_parser(arg)
        objdict = storage.all()
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in MBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(argl[0], argl[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class>
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        argl = custom_parser(arg)
        if len(argl) > 0 and argl[0] not in MBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            for obj in storage.all().values():
                if len(argl) > 0 and argl[0] == obj.__class__.__name__:
                    objl.append(obj.__str__())
                elif len(argl) == 0:
                    objl.append(obj.__str__())
            print(objl)

    def do_count(self, arg):
        """Usage: count <class>
        Retrieve the number of instances of a given class."""
        argl = custom_parser(arg)
        count = 0
        for obj in storage.all().values():
            if argl[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
        <class>.update(<id>, <dictionary>)
        Update class instance of given id by adding or updating
        given attribute key/value pair or dictionary."""
        argl = custom_parser(arg)
        objdict = storage.all()
        
        if len(argl) == 0:
            print("** class name missing **")
            return False
        if argl[0] not in MBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(argl) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
            return False
        if len(argl) == 2:
            print("** attribute name missing **")
            return False
        if len(argl) == 3:
            try:
                type(eval(argl[2])) != dict
            except NameError:
                print("** value missing **")
                return False
        
        if len(argl) == 4:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            if argl[2] in obj.__class__.__dict__.keys():
                valtype = type(obj.__class__.__dict__[argl[2]])
                obj.__dict__[argl[2]] = valtype(argl[3])
            else:
                obj.__dict__[argl[2]] = argl[3]
        elif type(eval(argl[2])) == dict:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            for k, v in eval(argl[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    valtype = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = valtype(v)
                else:
                    obj.__dict__[k] = v
        storage.save()

if __name__ == "__main__":
    MBNBCommand().cmdloop()

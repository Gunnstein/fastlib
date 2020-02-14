# -*- coding: utf-8 -*-
import string


__all__ = ["TemplateStringFormatter", "TemplateFileFormatter"]

class TemplateStringFormatter(object):
    fmt_dict = {}
    def __init__(self, template_str):
        """Use a template from a string

        Load a template string and substitute the 
        template keys with property values of this class.

        Assume that the following template string is defined

            a = ${a}
            b = ${b}

        then instanciate the TemplateStringFormatter and add properties 
        corresponding to the template keys (${}) found in the template file.

            >>> ft = FileTemplater("template.txt")
            >>> ft.a = 9
            >>> ft.b = "hello"
        
        you can then return the template string with the property values 
        substituted for the template keys by the substitute method

            >>> ft.substitute()
                a = 9
                b = hello

        it is also possible to write the substitute results directly to a file
            >>> ft.write("result.txt")

        and the "result.txt" file will contain

            a = 9
            b = hello 

        Arguments
        ---------
        template_str : str
            A template string where ${key} is to substituted with the `key` 
            property value.
        """
        self.template = string.Template(template_str)

    def str_formatter(self, key, val):
        try: 
            fmt = self.fmt_dict[key]
        except KeyError:
            fmt = "{0:>11}"
        sval = str(val)
        if isinstance(val, float):
            if val > 1e6:
                sval = '{0:.5E}'.format(val)
        try:
            s_fmt = fmt.format(sval)
        except TypeError:
            s_fmt = None
        return s_fmt


    def substitute(self):
        out_dict = {key: self.str_formatter(key, val) 
                    for key, val in self.__dict__.items()}
        try:
            return self.template.substitute(**out_dict)
        except KeyError as e:
            print(
                "{0}Error: key {1} found in template but not as property of {0}.".format(
                self.__class__.__name__, e))

    def write(self, filename):
        with open(filename, 'w+') as fout:
            fout.write(self.substitute())


class TemplateFileFormatter(TemplateStringFormatter):
    def __init__(self, filename):
        """Use a template from a text file.

        Load a template file from a text file and substitute the 
        template keys with property values of this class.

        Assume that a template file "template.txt" exists with the following
        content

            a = ${a}
            b = ${b}

        then instanciate the TemplateFileFormatter and add properties 
        corresponding to the template keys (${}) found in the template file.

            >>> ft = FileTemplater("template.txt")
            >>> ft.a = 9
            >>> ft.b = "hello"
            >>> ft.write("result.txt")

        then the "result.txt" file will contain

            a = 9
            b = hello 

        Arguments
        ---------
        filename : str
            Filename of the template file. 
        """
        with open(filename, 'r') as fin:
            super(TemplateFileFormatter, self).__init__(fin.read())
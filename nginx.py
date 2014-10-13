from pyparsing import Word


class NginxConfig(object):
    def __init__(self):
        # from https://github.com/vvojvoda/py-nginx/blob/b6d5c2e651efe0af38475c8a966c92dca8a79cd5/pynginx/nginx.py#L8
       
        word = Word(alphanums + '-' + '_' + '.' + '/' + '$' + ':')
        server = Literal('server').suppress()
        location = Literal('location')
        lbrace = Literal('{').suppress()
        rbrace = Literal('}').suppress()

        config_line = NotAny(rbrace) + word + Group(OneOrMore(word)) + Literal(';').suppress()
        location_def = location + word + lbrace + Group(OneOrMore(Group(config_line))) + rbrace
        self.server_def = server + lbrace + OneOrMore(Group(location_def) | Group(config_line)) + rbrace

        comment = Literal('#') + Optional(restOfLine)
        self.server_def.ignore(comment)
 

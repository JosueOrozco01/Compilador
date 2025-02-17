import re

texto = """
int suma(int a, int b) {
    int resultado = b - a;
    resultado = resultado + b;
    if (a > b) {
        print("a es mayor que b");
    } else {
        print("b es mayor o igual que a");
    }
    for (int i = 0; i < 10; i+) {
        print("i");
    }
    return resultado;

    while (contador < 5) {
        print("a");
        a = 3 + 1;
}
}
"""

# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(if|else|return|int|float|void|class|while|for|print)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+\b',
    "OPERATOR": r'[\+\-\*/=<>!]',  
    "DELIMITER": r'[(),;{}]',  
    "STRING": r'"[^"]*"',  
    "WHITESPACE": r'\s+'  
}

def tokenize(text):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)

    tokens_encontrados = []

    for match in patron_regex.finditer(text):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))

    return tokens_encontrados

tokens = tokenize(texto)

# Analizador sintáctico
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            print(f"{token_actual[0]}: {token_actual[1]}")  # Imprimir el token en el formato deseado
            return token_actual
        else:
            raise SyntaxError(f'Error sintáctico: se esperaba {tipo_esperado}, pero se encontró: {token_actual}')

    def parsear(self):
        self.funcion()
        print('Análisis sintáctico exitoso')

    def funcion(self):
        self.coincidir('KEYWORD')  # int
        self.coincidir('IDENTIFIER')  # suma
        self.coincidir('DELIMITER')  # (
        self.parametros()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        self.cuerpo()
        self.coincidir('DELIMITER')  # }

    def parametros(self):
        self.coincidir('KEYWORD')  # int
        self.coincidir('IDENTIFIER')  
        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
            self.coincidir('DELIMITER')  # ,
            self.coincidir('KEYWORD')  # int
            self.coincidir('IDENTIFIER')  

    def cuerpo(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            token_actual = self.obtener_token_actual()
            if token_actual[0] == 'KEYWORD' and token_actual[1] == 'return':
                self.coincidir('KEYWORD')  # return
                self.expresion()
                self.coincidir('DELIMITER')  # ;
            elif token_actual[0] == 'KEYWORD':
                if token_actual[1] in ['while', 'for']:
                    self.ciclo()
                elif token_actual[1] == 'if':
                    self.condicional()
                elif token_actual[1] == 'print':
                    self.funcion_print()
                else:
                    self.declaracion_variable()
            elif token_actual[0] == 'IDENTIFIER':
                self.asignacion()
            else:
                raise SyntaxError(f'Error sintáctico inesperado en {token_actual}')

    def ciclo(self):
        tipo_ciclo = self.obtener_token_actual()[1]  
        self.coincidir('KEYWORD')  # while o for
        self.coincidir('DELIMITER')  # (
        
        if tipo_ciclo == 'for':
            self.coincidir('KEYWORD')  # int
            self.coincidir('IDENTIFIER')  # variable de control
            self.coincidir('OPERATOR')  # =
            self.coincidir('NUMBER')  # valor inicial
            self.coincidir('DELIMITER')  # ;

            self.coincidir('IDENTIFIER')  # variable de control
            self.coincidir('OPERATOR')  
            self.coincidir('NUMBER') 
            self.coincidir('DELIMITER')  # ;

            self.coincidir('IDENTIFIER')  # variable de control
            if self.obtener_token_actual() and self.obtener_token_actual()[1] in ['++', '--']:  
                self.coincidir('OPERATOR')  
            else:
                self.coincidir('OPERATOR')  # =
                self.expresion()  
        elif tipo_ciclo == 'while':
            self.expresion()

        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        self.cuerpo()  # cuerpo del ciclo
        self.coincidir('DELIMITER')  # }

    def condicional(self):
        self.coincidir('KEYWORD')  # if
        self.coincidir('DELIMITER')  # (
        self.expresion()  
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        self.cuerpo()  # Cuerpo del if
        self.coincidir('DELIMITER')  # }

        if self.obtener_token_actual() and self.obtener_token_actual()[1] == 'else':
            self.coincidir('KEYWORD')  # else
            self.coincidir('DELIMITER')  # {
            self.cuerpo()  # Cuerpo del else
            self.coincidir('DELIMITER')  # }

    def funcion_print(self):
        self.coincidir('KEYWORD')  # print
        self.coincidir('DELIMITER')  # (
        self.coincidir('STRING')  # Cadena de texto
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # ;

    def declaracion_variable(self):
        self.coincidir('KEYWORD')  # int, float, etc.
        self.coincidir('IDENTIFIER')  # nombre de la variable
        self.coincidir('OPERATOR')  # =
        self.expresion()
        self.coincidir('DELIMITER')  # ;

    def asignacion(self):
        self.coincidir('IDENTIFIER')  # nombre de la variable
        self.coincidir('OPERATOR')  # =
        self.expresion()
        self.coincidir('DELIMITER')  # ;

    def expresion(self):
        if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER']:
            self.coincidir(self.obtener_token_actual()[0])  # variable 
            while self.obtener_token_actual() and self.obtener_token_actual()[0] == 'OPERATOR':
                self.coincidir('OPERATOR')  # +, -, *, /
                if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER']:
                    self.coincidir(self.obtener_token_actual()[0])  # otra variable
                else:
                    raise SyntaxError(f'Error sintáctico: se esperaba IDENTIFIER o NUMBER, pero se encontró: {self.obtener_token_actual()}')

try:
    print('Se inicia el análisis sintáctico')
    parser = Parser(tokens)
    parser.parsear()
except SyntaxError as e:
    print(e)

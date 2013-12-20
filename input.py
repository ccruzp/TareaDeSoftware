#funciones generales para facilitar las entradas por consola

from datetime import datetime
def validate(value, *validators):
    #Devuelve si value es valido dado validators
    return all(x(value) for x in validators)

def readValue(ask_string, format_function, *validators):
    #Pide un valor consistentemente hasta que `format_function` no de error
    while True:
        try:
            tr = format_function(raw_input(ask_string))
            if validate(tr, *validators):
                return tr
            else:
                print "La entrada que introduciste no es valida."
                continue
        except ValueError:
            print 'La entrada que introduciste no sigue el formato esperado'

def valueLength(x, y):
    def f(z):
        return x <= len(z) <= y
    return f

def valueBetween(x, y):
    def f(z):
        return x <= z <= y
    return f

def afterToday(x):
    return x > datetime.now()

INFINITE = float('inf')
notEmpty = valueLength(1, INFINITE)
greaterThanZero = valueBetween(1, INFINITE)
validTime = 

#Elimina espacios vacios
def splitter(x):
    def f(z):
        return [r.strip() for r in z.split(x) if r.strip()]
    return f

commaSeparate = splitter(',')
boolFormat = lambda x: x == 's'
toDate = lambda x: datetime.strptime(x, '%d/%m/%Y')

def readRawValues(*args):
    raw_values = {}
    for (k,(q, w, v)) in args:
        raw_values[k] = readValue(q, w, *v)
    return raw_values

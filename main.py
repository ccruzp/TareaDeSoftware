import random
from datetime import datetime
from collections import OrderedDict
from input import readRawValues, notEmpty, valueLength, commaSeparate, toDate, boolFormat, \
    greaterThanZero, afterToday, valueBetween
import numpy as np
import matplotlib.pyplot as plt

toTopico = lambda x: set(Topico.getOrCreate(y) for y in commaSeparate(x))
toDatetime = lambda x: datetime.strptime(x, '%d/%m/%Y')
toAutor = lambda x: set(Autor.find(int(y)) for y in commaSeparate(x))


#Funcion para dibujar los histogramas
def Dibujamofo(eje_x,eje_y):
    pos = np.arange(len(eje_x))
    width = 1.0

    ax = plt.axes()
    ax.set_xticks(pos + (width / 2))
    ax.set_xticklabels(eje_x)
    plt.bar(pos, eje_y, width, color='b')
    plt.show()


class Model(object):
    objects = {}
    @classmethod
    def find(cls, xid):
        return cls.objects.get(xid, None);


class Persona(Model):
    '''Persona participante en el CLEI'''
    nextId = 1
    objects = {}
    def __init__(self,pk=None,nombre=None,apellido=None,institucion=None,correo=None):
        self.nombre = nombre
        self.apellido = apellido
        self.institucion = institucion
        self.correo = correo

    #Se le agrega el id unico a la persona
    def save(self):
        self.pk = Persona.nextId
        Persona.nextId += 1
        Persona.objects[self.pk] = self


    def __hash__(self):
        return hash(self.pk)

    def __eq__(self, other):
        return self.pk == other.pk

    #Lectura de los datos ingresador por el usuario. No puede ser un campo vacio
    @staticmethod
    def readRaw():
        return readRawValues(
            ('nombre',('Nombre: ', str, [notEmpty]),),
            ('apellido',('Apellido: ', str, [notEmpty]),),
            ('institucion',('Institucion :', str, [notEmpty]),),
            ('correo',('Correo: ', str, [notEmpty])),
        )

    @classmethod
    def read(cls):
        return cls(**Persona.readRaw())


class Topico(Model):
    objects = {}
    def __init__(self, nombre):
        self.nombre = nombre
        self.articulos = set()

    def save(self, topicos=None):
        self.pk = self.nombre
        Topico.objects[self.nombre] = self

    #funcion para buscar si un topico ya existe o si hay que crearlo
    @classmethod
    def getOrCreate(cls, xid):
        if xid in cls.objects:
            return cls.objects[xid]
        else:
            t = cls(xid)
            t.save()
            return t

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return other.nombre == self.nombre

    def __repr__(self):
        return 'Topico[%s]' % self.nombre

class MiembroCP(Persona):
    '''Miembro de un Comite de Programa del CLEI'''
    objects = {}
    def __init__(self, *args, **kwargs):
        self.esPresidente = kwargs.pop('esPresidente')
        self.experticies = kwargs.pop('experticies')
        self.correcciones = {}
        self.cp = set()
        super(MiembroCP, self).__init__(*args, **kwargs)

    def save(self):
        super(MiembroCP, self).save()
        MiembroCP.objects[self.pk] = self

    #Al campo de correcciones se le agrega el key del articulo que debe evaluar
    # y al articulo se le agrega el miembroCP que lo evalua
    def asignarArticulo(self, art):
        self.correcciones[art] = 0
        art.agregarEvaluador(self)

    #Se coloca la nota asociada al articulo
    def evaluarArticulo(self, art, nota):
        self.correcciones[art] = nota
        art.setNota(nota)

    #Se leen los valores ingresados. Se transforma el input en booleano.
    @staticmethod
    def readRaw():
        return readRawValues(
            ('esPresidente', ('Es el presidente del comite? [s/n] ', boolFormat, [])),
            ('experticies',('Lista de experticies (separados por coma [,]): ', toTopico, [notEmpty]))
        )

    @classmethod
    def read(cls):
        values = Persona.readRaw()
        values.update(MiembroCP.readRaw())
        return cls(**values)

class Autor(Persona):
    objects = {}
    paises = {}
    def __init__(self, *args, **kwargs):
        self.pais = kwargs.pop('pais')
        self.articulos = set()
        super(Autor, self).__init__(*args, **kwargs)

    def agregarArticulo(self, articulo):
        self.articulos.add(articulo)
        articulo.agregarAutor(self)

    def save(self):
        super(Autor, self).save()
        Autor.objects[self.pk] = self
        if self.pais not in Autor.paises:
            Autor.paises[self.pais]=0
        Autor.paises[self.pais] +=1

    @staticmethod
    def readRaw():
        return readRawValues(
            ('pais',('Pais: ', str, [notEmpty])),
        )
    @classmethod
    def read(cls):
        values = Persona.readRaw()
        values.update(Autor.readRaw())
        return cls(**values)

    def __str__(self):
        return "[%d] %s %s" % (self.pk, self.nombre, self.apellido)


class CP(Model):
    '''Comite de Programa del CLEI'''
    objects = {}
    def __init__(self, clei):
        self.clei = clei
        self.miembros = set()
        self.presidente = None

    def __hash__(self):
        return hash(self.clei)

    def __eq__(self, other):
        return self.clei == other.clei

    def save(self):
        self.pk = self.clei
        CP.objects[self.pk] = self

    #Se verifica que el nuevo miembro a ingresar no sea presidente, si ya existe
    #otro miembro que es presidente. Se agrega al CP
    def agregarMiembro(self, miembro):
        if miembro.esPresidente and self.presidente is not None:
            raise ValueError('No se puede tener mas de un presidente')
        if miembro.esPresidente:
            self.presidente = miembro
        self.miembros.add(miembro)
        miembro.cp.add(self)


    #Se le solicita el numero de miembros del CP al usuario
    #ciclamos agregando nuevos miembros, y verificamos no haya mas
    #de un presidente, o ninguno
    @classmethod
    def read(cls, clei):
        cp = cls(clei)
        n = int(raw_input('Numero de miembros para el CP de este CLEI? '))
        print "Recordar que debe existir EXACTAMENTE un (1) miembro que actue como presidente"
        print "En caso de no marcar algun miembro como presidente, debera volver a cargar los miembros hasta que uno sea presidente"
        while len(cp.miembros) < n:
            print "Miembro #%d" % (len(cp.miembros)+1)
            print '='*50
            nuevoMiembro = MiembroCP.read()
            try:
                nuevoMiembro.save()
                cp.agregarMiembro(nuevoMiembro)
            except ValueError:
                print 'Ya existe un miembro que es presidente, reintentar'
            if len(cp.miembros) == n and not any(miembro.esPresidente for miembro in cp.miembros):
                print 'No agregaste ningun miembro presidente'
                print 'Se borrara la lista de miembros, y debes agregarlos nuevamente con ALGUN presidente'
                cp.miembros = set()
        return cp

    @classmethod
    def aceptarPorPais(cls,p):
        aceptados= []
        no_aceptados = {}
        for x in Articulo.porPais:
            # m es el minimo entre el limite y numero maximo de articulos por paises
            m = min(p, len(Articulo.porPais[x]))
            # Lista de aceptados por pais, y la lista ordenada por nota de las no aceptadas

            aceptados +=  list(sorted(set(Articulo.porPais[x]),key = lambda x: x.nota))[:m]
            no_aceptados = list(sorted(set(Articulo.porPais[x]),key = lambda x: x.nota))[m:]

            print x,":\n Aceptados:",aceptados,"\n No aceptados:",no_aceptados,"\n","*"*50

    # @classmethod
    # def cortePorNota(cls,n1,n2):
    #     aceptados = []
    #     no_aceptados = []
    #     for x in Articulo.objects:


class Clei(Model):
    '''CLEI'''
    objects = {}
    def __init__(self, fechaInscripcion, fechaTopeArticulo, fechaNotificacion,
                 dias, tarifaReducida, tarifaNormal):
        self.fechaInscripcion = fechaInscripcion
        self.fechaTopeArticulo = fechaTopeArticulo
        self.fechaNotificacion = fechaNotificacion
        self.dias = dias
        self.tarifaReducida = tarifaReducida
        self.tarifaNormal = tarifaNormal
        self.cp = None
        self.topicos = set()
        self.articulos = set()

    #Le colocamos al clei como clave la tripleta de las fechas de inscripcion
    #fecha tope de articulo y fecha de notificacion.
    def save(self):
        self.pk = (self.fechaInscripcion, self.fechaTopeArticulo, self.fechaNotificacion)
        Clei.objects[self.pk] = self

    def asignarArticulos(self):
        # iteramos sobre todos los articulos, y aleatoriamente
        # seleccionamos 2 o mas arbitros, cada arbitro es un miembro CP
        arbitros = [x for x in MiembroCP.objects.values() if self in [y.clei for y in x.cp]]
        articulos = [x for x  in Articulo.objects.values() if x.clei == self]
        n = len(arbitros)
        for art in articulos:
            tamanoMuestra = random.randint(2, n)
            arbitros_seleccionados = random.sample(arbitros, tamanoMuestra)
            # asignamos a nuestros arbitros este articulo
            for arbitro in arbitros_seleccionados:
                arbitro.asignarArticulo(art)

    #Creamos las listas de articulos aceptados y empatados
    def particionarArticulos(self, n):
        #Articulos que cumplen con las condiciones minimas para ser elegidos
        articulosValidos = [x for x in Articulo.objects.values() if x.clei == self and x.nota >= 3.0 and x.correcciones >= 2]
        #ordenamos por nota
        articulosValidos.sort(key=lambda x: x.nota)
        #Creamos un diccionario con key=nota, value= lista de articulos con esa nota
        agrupados = OrderedDict()
        for art in reversed(articulosValidos):
            if art.nota in agrupados:
                agrupados[art.nota].append(art)
            else:
                agrupados[art.nota] = [art]
        aceptados = []
        empatados = []
        for (k, v) in agrupados.items():
            if len(aceptados)+len(v) <= n:
                aceptados += v
            else:
                empatados = v
                break
        return aceptados, empatados


    def __hash__(self):
        return hash((self.fechaInscripcion, self.fechaTopeArticulo, self.fechaNotificacion))

    def __eq__(self, other):
        attr = ['fechaInscripcion', 'fechaTopeArticulo', 'fechaNotificacion',
                'dias', 'tarifaReducida', 'tarifaNormal']
        return all(getattr(self, x) == getattr(other, x) for x in attr)

    def agregarTopico(self, topic):
        self.topicos.add(topic)

    @staticmethod
    def readRaw():

        return readRawValues(
            ('fechaInscripcion',('Fecha de Inscripcion [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('fechaTopeArticulo',('Fecha de Tope Articulos [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('fechaNotificacion',('Fecha de Notificacion [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('dias',('Dias conferencia: ', int, [greaterThanZero]),),
            ('tarifaReducida',('Tarifa reducida: ', float, [greaterThanZero]),),
            ('tarifaNormal',('Tarifa normal: ', float, [greaterThanZero]),),
            ('topicos',('Lista de topicos CLEI (lista separado por coma [,]): ', toTopico, [notEmpty])),
        )

    @classmethod
    def read(cls):
        values = Clei.readRaw()
        topicos = values.pop('topicos')
        dat_clei = Clei(**values)
        for t in topicos:
            t.save()
            dat_clei.agregarTopico(t)
        dat_cp = CP.read(dat_clei)
        dat_clei.cp = dat_cp
        return dat_clei


class Articulo(Model):
    objects = {}
    #Diccionario con key pais, value lista de articulos
    porPais ={}
    ACEPTADO, RECHAZADO, REVISANDO, ESPERANDO = range(4)
    def __init__(self, titulo, clei, pclaves):
        self.titulo = titulo
        if len(pclaves) > 5:
            raise ValueError('No se puede tener mas de 5 palabras claves')
        self.pclaves = pclaves
        self.status = Articulo.ESPERANDO
        self.nota = 0
        self.correcciones = 0
        self.autores = set()
        self.topicos = set()
        self.evaluadores = set()
        self.clei = clei

    def agregarAutor(self, autor):
        self.autores.add(autor)
        autor.articulos.add(self)

    def agregarTopico(self, topico):
        self.topicos.add(topico)
        topico.articulos.add(self)

    def agregarEvaluador(self, evaluador):
        self.evaluadores.add(evaluador)
        self.status = Articulo.REVISANDO

    def setNota(self, nota):
        sumatoria = self.correcciones*self.nota
        self.correcciones += 1
        self.nota = (nota+sumatoria)/float(self.correcciones)

    def save(self):
        self.pk = self.titulo
        Articulo.objects[self.pk] = self

    def __hash__(self):
        return hash(self.titulo)

    def __eq__(self, other):
        return other.titulo == self.titulo

    def __str__(self):
        tr = 'Titulo: %s\nAutores: %s'
        return tr % (self.titulo,
                     ', '.join('%s %s' % (x.nombre, x.apellido) for x in self.autores))

    def __repr__(self):
        return "Articulo[%s]" % (self.titulo)


    @staticmethod
    def readRaw():
        return readRawValues(
            ('titulo', ('Titulo: ', str, [notEmpty])),
            ('pclaves', ('Palabras claves (separadas por coma [,]): ', commaSeparate, [valueLength(1, 5)])),
            ('autores', ('Autores (IDENTIFICADORES UNICOS separados por coma [,]):', toAutor, [notEmpty])),
            ('topicos', ('Topicos (separados por coma [,]): ', toTopico, [notEmpty]))
        )

    @classmethod
    def read(cls, clei):
        values = Articulo.readRaw()
        autores = values.pop('autores')
        topicos = values.pop('topicos')
        art = Articulo(values['titulo'], clei, values['pclaves'])
        for autor in autores:
            art.agregarAutor(autor)
        for topico in topicos:
            art.agregarTopico(topico)
        art.save()
        return art

    @classmethod
    def agruparPorPais(cls):
        cls.porPais ={}
        for articulo in cls.objects.values():
            for autor in articulo.autores:
                if autor.pais in cls.porPais:
                    cls.porPais[autor.pais].append(articulo)
                else:
                    cls.porPais[autor.pais] =[articulo]
        for pais in cls.porPais:
            cls.porPais[pais] = list(sorted(set(cls.porPais[pais]),key= lambda x: x.nota))


# class Inscripcion(Persona):
#     def __init__(self,direccion,pag_web,telefono):
#         self.direccion = direccion
#         self.pagina_web = pag_web
#         self.telefono = telefono


# class Evento(object):
#     def __init__(self,fecha,hora_inicio,hora_fin):
#         self.fecha = fecha
#         self.hora_inicio = hora_inicio
#         self.hora_fin = hora_fin

#     def Duracion(self):
#         return self.hora_fin-self.hora_inicio

#     def GetLugar(self):

#     def GenerarPrograma(self):

# class Lugar(object):
#     def __init__(self,nombre,ubicacion,capacidad):
#         self.nombre = nombre
#         self.ubicacion = ubicacion
#         self.capacidad = capacidad




##################
#    Interface   #
##################

if __name__ == '__main__':
    print '='*50
    print "Bienvenido al CLEI"
    print "Iniciando proceso de creacion de un nuevo CLEI"
    print '='*50
    clei = Clei.read()
    clei.save()
    print '='*50
    n = int(raw_input("Cuantos autores hay? "))
    print '='*50
    for i in range(n):
        print "Autor #%d" % (i+1)
        autor = Autor.read()
        autor.save()
    print '='*50
    print 'Lista de autores registrados'
    print '='*50
    for x in sorted(Autor.objects.values(), key=lambda x: x.pk):
        print x
    print '='*50
    print 'Articulos'
    print '='*50
    n = int(raw_input("Cuantos articulos hay? "))
    for i in range(n):
        art = Articulo.read(clei)
        art.save()
    print '='*50
    print 'Lista de articulos registrados con sus autores'
    for art in Articulo.objects.values():
        print art
    print '='*50
    print "Haciendo una asignacion aleatoria de articulos..."
    clei.asignarArticulos()
    print '='*50
    print 'Proceso de evaluacion'
    print '='*50
    print 'A continuacion para cada miembro del CP se presentaran los articulos que debe evaluar y se preguntara para cada uno la nota'
    for miembrocp in clei.cp.miembros:
        print '-'*50
        print 'Articulos asignados a %s %s' % (miembrocp.nombre, miembrocp.apellido)
        print '-'*50
        for art in miembrocp.correcciones.keys():
            print art
            values = readRawValues(
                ('nota', ('Nota asignada [1-5]: ', int, [valueBetween(1, 5)]))
            )
            miembrocp.evaluarArticulo(art, values['nota'])
    n_articulos = int(raw_input("Numero de articulos a aceptar?"))
    aceptados, empatados = clei.particionarArticulos(n_articulos)
    print '='*50
    print 'Articulos aceptados'
    print '='*50
    for art in aceptados:
        print '%s\nNota: %f' % (art, art.nota)
    print '='*50
    print 'Articulos empatados'
    print '='*50
    for art in empatados:
        print '%s\nNota: %f' % (art, art.nota)

    #Histogramas
    #Por autor
    dicc_plot_autor = {}
    dicc_plot_topico= {}
    dicc_plot_inst = {}
    dicc_plot_pais= {}

    for art in aceptados:

        for topico in art.topicos:
            if topico.nombre not in dicc_plot_topico:
                dicc_plot_topico[topico.nombre] = 0
            dicc_plot_topico[topico.nombre] +=1

        for autor in art.autores:
            nombre_completo = '%s %s' % (autor.nombre, autor.apellido)
            if nombre_completo not in dicc_plot_autor:
                dicc_plot_autor[nombre_completo] = 0
            dicc_plot_autor[nombre_completo] += 1


            if autor.institucion not in dicc_plot_inst:
                dicc_plot_inst[autor.institucion] = 0
            dicc_plot_inst[autor.institucion] +=1

            if autor.pais not in dicc_plot_pais:
                dicc_plot_pais[autor.pais] = 0
            dicc_plot_pais[autor.pais] +=1

    print '='*50
    p = int(raw_input("Ingrese minimo de articulos a aceptar por pais: "))
    Articulo.agruparPorPais()
    CP.aceptarPorPais(p)

    n1 = int(raw_input("Ingrese el punto de corte: "))
    n2 = int(raw_input("Ingrese el segundo punto de corte: "))

    # CP.notaCorte()

    # Dibujamofo(dicc_plot_autor.keys(), dicc_plot_autor.values())
    # #Por topico
    # Dibujamofo(dicc_plot_topico.keys(), dicc_plot_topico.values())

    # #Por institucion
    # Dibujamofo(dicc_plot_inst.keys(), dicc_plot_inst.values())

    # #Por pais
    # Dibujamofo(dicc_plot_pais.keys(), dicc_plot_pais.values())

import random
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from input import readRawValues, notEmpty, valueLength, commaSeparate, toDate, boolFormat, \
    greaterThanZero, afterToday, valueBetween, betweenOneAndFour
import numpy as np
import matplotlib.pyplot as plt

toTopico = lambda x: set(Topico.getOrCreate(y) for y in commaSeparate(x))
toDatetime = lambda x: datetime.strptime(x, '%d/%m/%Y')
toAutor = lambda x: set(Autor.find(int(y)) for y in commaSeparate(x))
toModerador = lambda x: MiembroCP.find(int(x))
toCharlista = lambda x: Persona.find(int(x))
toHora = lambda x: datetime.strptime(x, '%H:%M')
toLugar = lambda x: Lugar.find(str(x))
toArticulo = lambda x: set(Articulo.find(str(y)) for y in commaSeparate(x))

def representacionPorPais(articulo, count):
    # saca un promedio de la representacion de los paises de los
    # autores del articulo
    s = 0
    n = 0
    for autor in articulo.autores:
        s += count[autor.pais]
        n += 1
    return s/float(n)

def obtenerCuentaPorPais(articulos):
    countPaises = defaultdict(int)
    for art in articulos:
        seen = set()
        for autor in art.autores:
            if autor.pais not in seen:
                countPaises[autor.pais] += 1
                seen.add(autor.pais)
    return countPaises

def horasCoinciden(horaIniA,horaFinA,horaIniB,horaFinB):
    coincide = horaIniA <= horaIniB < horaFinA
    coincide = coincide or (horaIniB <= horaIniA < horaFinB)
    return coincide

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

class Inscripcion(Persona):
    '''Participante del CLEI'''
    charlas = {}
    talleres = {}
    charlasTalleres = {}
    descuento = {}
    objects = {}

    def __init__(self, *args, **kwargs):
        self.dirPostal = kwargs.pop('dirPostal')
        self.pagWeb = kwargs.pop('pagWeb')
        self.telf = kwargs.pop('telf')
        self.tipo = kwargs.pop('tipo')
        self.fecha = datetime.today()
        super(Inscripcion, self).__init__(*args, **kwargs)

    def save(self):
        super(Inscripcion, self).save()
        if (self.tipo == 1):
            Inscripcion.charlas[self.pk] = self
        elif (self.tipo == 2):
            Inscripcion.talleres[self.pk] = self
        elif (self.tipo == 3):
            Inscripcion.charlasTalleres[self.pk] = self
        else:
            Inscripcion.descuento[self.pk] = self
        Inscripcion.objects[self.pk] = self

    @staticmethod
    def readRaw():
        return readRawValues(
            ('dirPostal', ('Direccion postal: ', str, [notEmpty])),
            ('telf', ('Telefono: ', str, [notEmpty])),
            ('pagWeb', ('Pagina Web: ', str, [])),
            ('tipo', ('Ingrese el tipo de inscripcion:\n1 - Solo charlas\n2 - Solo talleres\n3 - Charlas y talleres\n4 - Descuentos\n', int, [betweenOneAndFour])),
        )

    @classmethod
    def read(cls):
        values = Persona.readRaw()
        values.update(Inscripcion.readRaw())
        return cls(**values)

    def __str__(self):
        return "[%d] %s %s %s %s %s %s" %(self.pk, self.nombre, self.apellido, self.dirPostal, self.telf, self.pagWeb, self.fecha.strftime("%d/%m/%Y"))

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
    def aceptarPorPais(cls,p,n_articulos):
        # primero aceptamos los p-mejores articulos por pais
        aceptados= set()
        for pais in Articulo.porPais:
            cuantos = min(p, len(Articulo.porPais[pais]))
            aceptados |= set(x for x in Articulo.porPais[pais][:cuantos])

        # Ahora del resto tratamos de aceptar los mejores articulos
        # dependiendo de los paises menos representados... whatever
        # that is.
        paisCount = obtenerCuentaPorPais(aceptados)
        r_count = n_articulos - len(aceptados)
        no_aceptados = [x for x in Articulo.objects.values()
                        if x not in aceptados]
        resto = set()
        while len(resto) < r_count:
            poss = [(x.nota, -representacionPorPais(x, paisCount), x)
                    for x in no_aceptados]
            try:
                agg = max(poss)
            except ValueError:
                break
            else:
                if agg not in resto:
                    resto.add(agg[-1])
                    no_aceptados.remove(agg[-1])
                    paisCount = obtenerCuentaPorPais(aceptados|resto)
        return list(aceptados), list(resto)

    @classmethod
    def cortePorNota(cls,n1,n2):
        # aceptamos todos los articulos con nota mayor o igual a n1
        aceptados = [x
                     for x in Articulo.objects.values()
                     if x.nota >= n1]
        # determinaremos el segundo batch de articulos a aceptar
        count = obtenerCuentaPorPais(aceptados)
        no_aceptados = [(x.nota, -representacionPorPais(x, count), x)
                        for x in Articulo.objects.values()
                        if x not in aceptados]
        resto = []
        while True:
            try:
                prox = max(no_aceptados)
            except ValueError:
                break
            else:
                if prox[-1].nota > n2:
                    resto.append(prox[-1])
                    count = obtenerCuentaPorPais(aceptados+resto)
                    no_aceptados = [(x.nota, -representacionPorPais(x, count), x)
                                    for (_, _, x) in no_aceptados
                                    if x != prox[-1]]
                else: break


        return aceptados, resto

    @classmethod
    def proporcionalPorPaises(cls, n):
        # n es cuantos articulos en total se van a aceptar
        propPaises = int(round(0.8*n))
        total = sum(len(x) for x in Articulo.porPais.values())
        aceptados = set()
        # print 'Aceptare %d articulos' % propPaises
        # print 'Hay en total participando %d articulos' % total
        for x in Articulo.porPais.values():
            num = len(x)/float(total)
            # print 'Proporcion: %f' % num
            # queremos aceptar 80% *(num/count) articulo de este pais
            aceptables = min(len(x), int(round(propPaises * num)))
            # print 'Aceptare de este pais %d articulos' % aceptables
            aceptados |= set([y for y in x[:aceptables]])

        r_count = n_articulos - len(aceptados)
        no_aceptados = [x for x in Articulo.objects.values()
                        if x not in aceptados]
        resto = set()
        while len(resto) < r_count:
            poss = [(x.nota, x)
                    for x in no_aceptados]
            try:
                agg = max(poss)
            except ValueError:
                break
            else:
                if agg not in resto:
                    resto.add(agg[-1])
                    no_aceptados.remove(agg[-1])
        return list(aceptados), list(resto)


    @classmethod
    def proporcionalPorTopico(cls, n):
        # n es cuantos articulos en total se van a aceptar
        total = sum(len(x) for x in Articulo.porPais.values())
        aceptados = set()
        # print 'Aceptare %d articulos' % propPaises
        # print 'Hay en total participando %d articulos' % total
        for (k,x) in Articulo.porTopico.items():
            # print k
            num = len(x)/float(total)
            # print 'Proporcion: %f' % num
            # queremos aceptar 80% *(num/count) articulo de este pais
            aceptables = min(len(x), int(round(n * num)))
            # print 'Aceptare de este topico %d articulos' % aceptables
            aceptados |= set([y for y in x[:aceptables]])
        no_aceptados = [x for x in Articulo.objects.values()
                        if x not in aceptados]
        while len(aceptados) < n:
            poss = [(x.nota, x)
                    for x in no_aceptados]
            try:
                agg = max(poss)
            except ValueError:
                break
            else:
                if agg not in aceptados:
                    aceptados.add(agg[-1])
                    no_aceptados.remove(agg[-1])

        return list(aceptados)



class Clei(Model):
    '''CLEI'''
    objects = {}
    def __init__(self, fechaInscripcionDescuento, fechaInscripcion, 
                 fechaTopeArticulo, fechaNotificacion, tarifaReducida, 
                 tarifaNormal, fechaInicio):
        self.fechaInscripcionDescuento = fechaInscripcionDescuento
        self.fechaInscripcion = fechaInscripcion
        self.fechaTopeArticulo = fechaTopeArticulo
        self.fechaNotificacion = fechaNotificacion
        self.tarifaReducida = tarifaReducida
        self.tarifaNormal = tarifaNormal
        self.cp = None
        self.topicos = set()
        self.articulos = set()
        self.fechaInicio = fechaInicio
        self.dias = 5

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
            ('fechaInscripcion',('Fecha tope de Inscripcion [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('fechaInscripcionDescuento',('Fecha tope de Inscripcion con descuento [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('fechaTopeArticulo',('Fecha de Tope Articulos [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('fechaNotificacion',('Fecha de Notificacion [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
            ('tarifaReducida',('Tarifa reducida: ', float, [greaterThanZero]),),
            ('tarifaNormal',('Tarifa normal: ', float, [greaterThanZero]),),
            ('topicos',('Lista de topicos CLEI (lista separado por coma [,]): ', toTopico, [notEmpty])),
            ('fechaInicio',('Fecha de inicio del congreso [dd/mm/yyyy]: ', toDatetime, [afterToday]),),
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
    # Dicccionario con key topico, value lista de articulos
    porTopico = {}
    #Diccionario key pais,value numero de articulos asociados a pais
    count_paises= {}
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
        tr = 'Titulo: %s\nAutores: %s\nTopicos: %s'
        return tr % (self.titulo,
                     ', '.join('%s %s (%s) [Nota=%f]' % (x.nombre, x.apellido, x.pais, self.nota) for x in self.autores),
                     ', '.join('%s' % x.nombre for x in self.topicos)
        )

    def __repr__(self):
        return "Articulo[%s]" % (self.titulo)

    @classmethod
    def agruparPorTopico(cls):
        cls.porTopico ={}
        for articulo in cls.objects.values():
            for topico in articulo.topicos:
                if topico.nombre in cls.porTopico:
                    cls.porTopico[topico.nombre].append(articulo)
                else:
                    cls.porTopico[topico.nombre] =[articulo]
        for topico in cls.porTopico:
            cls.porTopico[topico] = list(reversed(sorted(set(cls.porTopico[topico]),key= lambda x: x.nota)))


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
            cls.porPais[pais] = list(reversed(sorted(set(cls.porPais[pais]),key= lambda x: x.nota)))


class Evento(Model):

    '''
    En Eventos aceptaremos aquellos que cumplan las condiciones del enunciado.
    Si no es asi estaran en la clase respectica pero no aqui
    '''
    objects = {}

    def __init__(self,nombre=None,fecha=None,horaInicio=None,horaFin=None,lugar=None,tipo=None):
        self.nombre = nombre
        self.fecha = fecha
        self.horaInicio = horaInicio
        self.horaFin = horaFin
        self.lugar = lugar
        self.tipo = tipo

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return other.nombre == self.nombre

    def __str__(self):
        tr = 'Nombre: %s\n'
        return tr % (self.nombre)

    def save(self,clei):        
        aceptar = True
        if self.tipo == 'taller':
            aceptar = aceptar and (self.fecha < (clei.fechaInicio + timedelta(days=2)))
        if self.tipo == 'ponencia':
            aceptar = aceptar and ((clei.fechaInicio + timedelta(days=2)) <= self.fecha < (clei.fechaInicio + timedelta(days=5)))    
        if aceptar and self.noCoincideHora():
            self.pk = self.nombre
            Evento.objects[self.pk] = self
            return True
        else:
            print 'El evento ingresado coincide con uno ya existente en la fecha-hora y lugar indicada'
            return False

    def esActividad(self):
        return self.tipo == 'taller' or self.tipo == 'ponencia' or self.tipo == 'charla'

    def noCoincideHora(self):
        aceptar = self.noCoincideSocial()
        if aceptar: aceptar = aceptar and self.noCoincideApertura()
        if aceptar: aceptar = aceptar and self.noCoincideClausura()
        if aceptar and self.esActividad():        
            values = Evento.objects.values()
            for value in values:
                if value.esActividad() and (value.fecha == self.fecha) and (value.lugar == self.lugar):
                    aceptar = aceptar and not(horasCoinciden(self.horaInicio,self.horaFin,value.horaInicio,value.horaFin))
        return aceptar

    def noCoincideSocial(self):
        aceptar = True
        values = Social.objects.values()    
        for value in values:
            if value.fecha == self.fecha:
                aceptar = aceptar and not horasCoinciden(self.horaInicio,self.horaFin,value.horaInicio,value.horaFin)
        return aceptar

    def noCoincideApertura(self):
        aceptar = True
        values = Apertura.objects.values()    
        for value in values:
            if value.fecha == self.fecha:
                aceptar = aceptar and not horasCoinciden(self.horaInicio,self.horaFin,value.horaInicio,value.horaFin)
        return aceptar

    def noCoincideClausura(self):
        aceptar = True
        values = Clausura.objects.values()    
        for value in values:
            if value.fecha == self.fecha:
                aceptar = aceptar and not horasCoinciden(self.horaInicio,self.horaFin,value.horaInicio,value.horaFin)
        return aceptar

    @staticmethod
    def readRaw():
        return readRawValues(
            ('nombre', ('Nombre: ', str, [notEmpty])),
            ('fecha', ('Fecha del Evento [dd/mm/yyyy]: ', toDatetime, [afterToday])),
            ('horaInicio', ('Hora de Inicio [hh:mm]:', toHora, [])),
            ('horaFin', ('Hora de Fin:', toHora, [])),
            ('lugar', ('Lugar donde se desarrollara el evento:', toLugar, []))
        )

    @classmethod
    def read(cls):
        while True:
            values = Evento.readRaw()
            dif = values['horaFin']-values['horaInicio']
            if dif.days == 0:
                return cls(**values)
            else:
                print 'La hora de finalizacion del evento debe ser mayor a la de inicio'


class Taller(Evento):

    objects = {}

    def __init__(self, *args, **kwargs):
        super(Taller, self).__init__(*args, **kwargs)

    def save(self,clei):
        if super(Taller, self).save(clei):
            Taller.objects[self.pk] = self

    @classmethod
    def read(cls):
        values = Evento.readRaw()
        values.update({'tipo':'taller'})
        return cls(**values)

class Ponencia(Evento):

    objects = {}

    def __init__(self, *args, **kwargs):
        self.articulos = kwargs.pop('articulos')
        self.moderador = kwargs.pop('moderador')
        self.ponentes = kwargs.pop('ponentes')
        super(Ponencia, self).__init__(*args, **kwargs)

    def save(self,clei):
        if super(Ponencia, self).save(clei):
            if 2 <= len(self.articulos) <= 4: 
                Ponencia.objects[self.pk] = self
            else:
                print 'La ponencia no cumple con el min o el max de articulos permitidos'

    @staticmethod
    def readRaw():
        return readRawValues(
            ('articulos',('Lista de articulos presentados (separados por coma [,]) Minimo 2:Maximo 4: ', toArticulo, [notEmpty])),
            ('ponentes',('Lista de ponentes (separados los ID por coma [,]): ', toAutor, [])),
            ('moderador',('Moderador de la ponencia (ID del miembro del CP): ', toModerador, [])),
        )

    @classmethod
    def read(cls):
        values = Evento.readRaw()
        values.update(Ponencia.readRaw())
        values.update({'tipo':'ponencia'})
        return cls(**values)

class Charla(Evento):

    objects = {}

    def __init__(self, *args, **kwargs):
        self.moderador = kwargs.pop('moderador')
        self.charlista = kwargs.pop('charlista')
        super(Charla, self).__init__(*args, **kwargs)

    def save(self,clei):
        if super(Charla, self).save(clei):
            Charla.objects[self.pk] = self

    @staticmethod
    def readRaw():
        return readRawValues(
            ('charlista',('Charlista(ID): ', toCharlista, [])),
            ('moderador',('Moderador de la ponencia (ID del miembro del CP): ', toModerador, [])),
        )

    @classmethod
    def read(cls):
        values = Evento.readRaw()
        values.update(Charla.readRaw())
        values.update({'tipo':'charla'})
        return cls(**values)

class Social(Evento):

    objects = {}

    def __init__(self, *args, **kwargs):
        super(Social, self).__init__(*args, **kwargs)

    def save(self,clei):
        if super(Social, self).save(clei):
            Social.objects[self.pk] = self

    @classmethod
    def read(cls):
        values = Evento.readRaw()
        values.update({'tipo':'social'})
        return cls(**values)

class Apertura(Evento):

    objects = {}

    def __init__(self, *args, **kwargs):
        super(Apertura, self).__init__(*args, **kwargs)

    def save(self,clei):
        if super(Apertura, self).save(clei):
            Apertura.objects[self.pk] = self

    @classmethod
    def read(cls):
        values = Evento.readRaw()
        values.update({'tipo':'apertura'})
        return cls(**values)

class Clausura(Evento):

    objects = {}

    def __init__(self, *args, **kwargs):
        super(Clausura, self).__init__(*args, **kwargs)

    def save(self,clei):
        if super(Clausura, self).save(clei):
            Clausura.objects[self.pk] = self

    @classmethod
    def read(cls):
        values = Evento.readRaw()
        values.update({'tipo':'clausura'})
        return cls(**values)

class Lugar(Model):

    objects = {}
    
    def __init__(self,nombre,ubicacion,capacidad):
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.capacidad = capacidad
        self.eventos = set()

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return other.nombre == self.nombre

    def __str__(self):
        tr = 'Nombre: %s\n Ubicacion: %s\n Capacidad: %s'
        return tr % (self.nombre, self.ubicacion, self.capacidad)

    def save(self):
        self.pk = self.nombre
        Lugar.objects[self.pk] = self

    @staticmethod
    def readRaw():
        return readRawValues(
            ('nombre', ('Nombre del lugar: ', str, [notEmpty])),
            ('ubicacion', ('Ubicacion: ', str, [notEmpty])),
            ('capacidad', ('Capacidad:', int, [greaterThanZero])),
        )

    @classmethod
    def read(cls):
        values = Lugar.readRaw()
        lugar = Lugar(values['nombre'],values['ubicacion'],values['capacidad'])
        lugar.save()
        return lugar


##################
#    Interface   #
##################

if __name__ == '__main__':

    
    ######################## CLEI & LOCACIONES ####################
    print '='*50
    print "Bienvenido al CLEI"
    print "Iniciando proceso de creacion de un nuevo CLEI"
    print '='*50
    clei = Clei.read()
    clei.save()

    n = int(raw_input("Indique el numero de locaciones: "))
    for i in range(n):
        print "\nLocacion #%d" %(i+1)
        print '='*50
        lugar = Lugar.read()
        lugar.save()
        
    print "\nLista de locaciones"
    for x in sorted(Lugar.objects.values(), key=lambda x: x.pk):
        print x

    print '='*50

    ######################## ARTICULOS ############################

    print "\nProceso de carga de articulos"
    print '='*50
    n = int(raw_input("\nIndique el numero de autores: "))
    for i in range(n):
        print "\nAutor #%d" % (i+1)
        print '='*50
        autor = Autor.read()
        autor.save()
    print '\nLista de autores registrados'
    for x in sorted(Autor.objects.values(), key=lambda x: x.pk):
        print x
    print '='*50
    n = int(raw_input("Indique el numero de articulos "))
    print '='*50
    for i in range(n):
        art = Articulo.read(clei)
        art.save()
        print '='*50

    print '\nLista de articulos registrados con sus autores'
    for art in Articulo.objects.values():
        print art

    print "\nHaciendo una asignacion aleatoria de articulos..."
    clei.asignarArticulos()

    ######################### EVALUACION ###########################
    print '='*50
    print 'Proceso de evaluacion'
    print '='*50
    print 'A continuacion para cada miembro del CP se presentaran los articulos que debe evaluar y se preguntara para cada uno la nota'
    for miembrocp in clei.cp.miembros:
        print '='*50
        print 'Articulos asignados a %s %s' % (miembrocp.nombre, miembrocp.apellido)
        for art in miembrocp.correcciones.keys():
            nota = random.randint(1, 5)
            print art, nota

            values = readRawValues(
                ('nota', ('Nota asignada [1-5]: ', int, [valueBetween(1, 5)]))
            )
            miembrocp.evaluarArticulo(art, values['nota'])
            miembrocp.evaluarArticulo(art, nota)

    print '='*50
    n_articulos = int(raw_input("Indique el numero de articulo que se aceptaran: "))
    print '='*50

    print '='*50
    print 'Hay diversas maneras de aceptar los articulos en el CLEI:'
    print '1 - Por promedio y desempate del Presidente del CP'
    print '2 - Por un minimo de articulos por pais y desempate entre los menos representados'
    print '3 - Por corte de nota:'
    print '\tNota 1: Emplea el esquema 1 a partir de la nota indicada '
    print '\tNota 2: Prioridad por paises menos representados a partir de esa nota '
    print '4 - Proporcional por Pais'
    print '5 - Proporcional por Topico'
    opcion = 0
    while not (0 < opcion < 6):
        opcion = int(raw_input("Indique como quiere aceptar los articulos: "))
    
    print '='*50    
    
    Articulo.agruparPorPais()
    Articulo.agruparPorTopico()

    if opcion == 1:

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


    if opcion == 2:
        paises_diferentes = len(Articulo.porPais)
        print 'Hay %d paises diferentes: ' % paises_diferentes
        print '\n'.join(Articulo.porPais.keys())
        while True:
            p = int(raw_input("Ingrese minimo de articulos a aceptar por pais: "))
            if paises_diferentes*p > n_articulos:
                print 'Previamente dijiste que querias aceptar %d articulos. Obligar al menos %d por pais *potencialmente* excede ese numero, vuelve a intentarlo.' % (n_articulos, p)
            else: break
        aceptados, resto = CP.aceptarPorPais(p,n_articulos)
        print "ACEPTADOS POR PAIS"
        for x in aceptados:
            print x
        print "ACEPTADOS POR NOTA/PAIS MENOS REPRESENTADO"
        for x in resto:
            print x


    if opcion == 3:
        n1=0
        n2=1
        while n1<n2:
            print "Primer punto de corte debe ser mayor que el segundo. \n"
            n1 = float(raw_input("Ingrese el punto de corte: "))
            n2 = float(raw_input("Ingrese el segundo punto de corte: "))


        primer, segundo = CP.cortePorNota(n1,n2)
        print 'ACEPTADOS PRIMER CORTE'
        print '\n'.join([str(x) for x in primer])
        print 'ACEPTADOS SEGUNDO CORTE'
        print '\n'.join([str(x) for x in segundo])

    if opcion == 4:
        primer, segundo = CP.proporcionalPorPaises(n_articulos)
        print 'ACEPTADOS PRIMER CORTE'
        print '\n'.join([str(x) for x in primer])
        print 'ACEPTADOS SEGUNDO CORTE'
        print '\n'.join([str(x) for x in segundo])

    if opcion == 5:
        primer = CP.proporcionalPorTopico(n_articulos)
        print 'ACEPTADOS PRIMER CORTE'
        print '\n'.join([str(x) for x in primer])

    '''
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

    Dibujamofo(dicc_plot_autor.keys(), dicc_plot_autor.values())
    #Por topico
    Dibujamofo(dicc_plot_topico.keys(), dicc_plot_topico.values())

    #Por institucion
    Dibujamofo(dicc_plot_inst.keys(), dicc_plot_inst.values())

    #Por pais
    Dibujamofo(dicc_plot_pais.keys(), dicc_plot_pais.values())
    print '='*50
    '''

    ##################### INSCRIPCION ###############################
    print '='*50
    print "Proceso de Inscripcion"
    print '='*50
    n = int(raw_input("Indique el numero de inscripciones: "))
    for i in range(n):
        print "Inscripcion #%d" %(i+1)
        inscripcion = Inscripcion.read()
        inscripcion.save()

    print "Lista de personas inscritas para solo charlas"
    for x in sorted(Inscripcion.charlas.values(), key=lambda x: x.pk):
        print x

    print "Lista de personas inscritas solo para talleres"
    for x in sorted(Inscripcion.talleres.values(), key=lambda x: x.pk):
        print x

    print "Lista de persoans inscritas para charlas y talleres"
    for x in sorted(Inscripcion.charlasTalleres.values(), key=lambda x: x.pk):
        print x

    print "Lista de personas inscritas con descuento"
    for x in sorted(Inscripcion.descuento.values(), key=lambda x: x.pk):
        print x


    ########################## EVENTOS ###############################
    print '='*50
    print "Proceso de Planificacion de Eventos"
    print '='*50
    print 'Apertura del CLEI'
    apertura = Apertura.read()
    apertura.save(clei)
    print '='*50
    print 'Clausura del CLEI'
    clausura = Clausura.read()
    clausura.save(clei)
    print '='*50
    print 'Eventos Sociales del CLEI'
    n = int(raw_input("Indique el numero de eventos sociales: "))
    for i in range(n):
        social = Social.read()
        social.save(clei)
    print '='*50
    print 'Talleres del CLEI (Primeros dos dias del CLEI)'
    n = int(raw_input("Indique el numero de talleres: "))
    for i in range(n):
        taller = Taller.read()
        taller.save(clei)
    print '='*50
    print 'Ponencias del CLEI (Ultimos tres dias del CLEI)'
    n = int(raw_input("Indique el numero de ponencias: "))
    for i in range(n):
        ponencia = Ponencia.read()
        ponencia.save(clei)
    print '='*50
    print 'Charla del CLEI'
    n = int(raw_input("Indique el numero de charlas: "))
    for i in range(n):
        charla = Charla.read()
        charla.save(clei)
    print '='*50
    print "Programa de eventos del CLEI"
    print '='*50
    for x in sorted(Evento.objects.values(), key=lambda x: x.pk):
        print x    
    print '='*50


    

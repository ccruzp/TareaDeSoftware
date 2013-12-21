#Implementa los casos de prueba genericos con los que se prueba los modulos
from main import *
from datetime import datetime
class Fixture(object):
    data = None
    def __init__(self, cls):
        self.classTest = cls
    def up(self):
        self.instances = [self.classTest(**fixture)
                          for fixture in self.fixtures]
        for instance in self.instances:
            instance.save()

    def down(self):
        self.classTest.objects = {}


class TopicoFixture(Fixture):
    fixtures = [
        {
            'nombre': 'Base de Datos'
        },
        {
            'nombre': 'Ingenieria de Software',
        },
        {
            'nombre': 'Sistemas de Informacion'
        }
    ]

class ArticuloFixture(Fixture):
    fixtures = [
        {
            "titulo": 'Reliable Composite Web Services Execution: Towards a Dynamic Recovery Decision',
            "pclaves": 'reliable,composite,web,services',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'A library for parallel thread-level speculation',
            "pclaves": 'library,parallel,thread,speculation',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'Virtual Machine Placement. A Multi-Objective Approach',
            "pclaves": 'virtual,machine,placement',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'GRiNGA: A Service-oriented Middleware for Interactive TV Grids',
            "pclaves": 'service,middleware,interactive,tv',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'Distributed Chronicles for Recognition of Failures in Web Services Composition',
            "pclaves": 'distributed,chronicles,recognition,failure',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'Goal Oriented Techniques and Methods: Goal Refinement and Levels of Abstraction',
            "pclaves": 'goal,oriented,techniques,methods',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },

        {
            "titulo": 'MeRinde process model adaptation with Requirements Engineering techniques supported by Free Software tools',
            "pclaves": 'process,model,adaptation',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'A Strategy for Supporting the Allocation of the Requirements Specification Phase in Distributed Software Development',
            "pclaves": 'strategy,supporting,allocation,requirements',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'About Fuzzy Query Procesing',
            "pclaves": 'fuzzy,query,processing',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
        {
            "titulo": 'Experiences on Fuzzy DBMS: Implementation and use',
            "pclaves": 'fuzzy,dbms',
            "clei": ('7/10/2014', '14/04/2014', '01/06/2014'),
        },
    ]
    def up(self):
        for fixture in self.fixtures:
            if isinstance(fixture['pclaves'], list):
                continue
            fixture['pclaves'] = fixture['pclaves'].split(',')
        super(ArticuloFixture, self).up()

class PersonaFixture(Fixture):
    fixtures = [
        {
            'nombre': 'Enrique',
            'apellido': 'Ferreira',
            'institucion': 'USB',
            'correo': 'eferreira@usb.ve'
        },
        {
            'nombre': 'Juan',
            'apellido': 'Hernandez',
            'institucion': 'USB',
            'correo': 'jhernandez@usb.ve'
        },
        {
            'nombre': 'Ana',
            'apellido': 'Martinez',
            'institucion': 'UCV',
            'correo': 'amartinez@ucv.ve',
        },
        {
            'nombre': 'Alberto',
            'apellido': 'Mendez',
            'institucion': 'UNEFA',
            'correo': 'amendez@unefa.gob.ve',
        },
        {
            'nombre': 'Cecilia',
            'apellido': 'Arteagas',
            'institucion': 'UC',
            'correo': 'carteagas@uc.edu.ve',
        },
        {
            'nombre': 'Roque',
            'apellido': 'Vera',
            'institucion': 'UDO',
            'correo': 'rvera@udo.ve',
        },
    ]

class MiembroCPFixture(Fixture):
    fixtures = [
        {
            'nombre': 'Enrique',
            'apellido': 'Ferreira',
            'institucion': 'USB',
            'correo': 'eferreira@usb.ve',
            'esPresidente': True,
            'experticies': ['Otro']

        },
        {
            'nombre': 'Juan',
            'apellido': 'Hernandez',
            'institucion': 'USB',
            'correo': 'jhernandez@usb.ve',
            'esPresidente': True,
            'experticies': ['Redes']
        },
        {
            'nombre': 'Ana',
            'apellido': 'Martinez',
            'institucion': 'UCV',
            'correo': 'amartinez@ucv.ve',
            'esPresidente': True,
            'experticies': ['Ing Software']
        },
        {
            'nombre': 'Alberto',
            'apellido': 'Mendez',
            'institucion': 'UNEFA',
            'correo': 'amendez@unefa.gob.ve',
            'esPresidente': False,
            'experticies': ['Ing Software']
        },
        {
            'nombre': 'Cecilia',
            'apellido': 'Arteagas',
            'institucion': 'UC',
            'correo': 'carteagas@uc.edu.ve',
            'esPresidente': False,
            'experticies': ['AI']
        },
        {
            'nombre': 'Roque',
            'apellido': 'Vera',
            'institucion': 'UDO',
            'correo': 'rvera@udo.ve',
            'esPresidente': False,
            'experticies': ['Base de Datos']
        },
    ]

    def up(self):
        self.articulosFixture = ArticuloFixture(Articulo)
        self.articulosFixture.up()
        for x in self.fixtures:
            x['experticies'] = [Topico.getOrCreate(y) for y in x['experticies']]
        super(MiembroCPFixture, self).up()

    def down(self):
        super(MiembroCPFixture, self).down()
        self.articulosFixture.down()
        Persona.objects = {}
        MiembroCP.objects = {}
        Topico.objects = {}

class AutorFixture(Fixture):
    fixtures = [
        {
            'nombre': 'Enrique',
            'apellido': 'Ferreira',
            'institucion': 'USB',
            'correo': 'eferreira@usb.ve',
            'pais' : 'Venezuela'
        },
        {
            'nombre': 'Juan',
            'apellido': 'Hernandez',
            'institucion': 'USB',
            'correo': 'jhernandez@usb.ve',
            'pais' : 'Venezuela'
        },
        {
            'nombre': 'Ana',
            'apellido': 'Martinez',
            'institucion': 'UCV',
            'correo': 'amartinez@ucv.ve',
            'pais' : 'Venezuela'
        },
        {
            'nombre': 'Alberto',
            'apellido': 'Mendez',
            'institucion': 'UNEFA',
            'correo': 'amendez@unefa.gob.ve',
            'pais' : 'Venezuela'
        },
        {
            'nombre': 'Cecilia',
            'apellido': 'Arteagas',
            'institucion': 'UC',
            'correo': 'carteagas@uc.edu.ve',
            'pais' : 'Venezuela'
        },
        {
            'nombre': 'Roque',
            'apellido': 'Vera',
            'institucion': 'UDO',
            'correo': 'rvera@udo.ve',
            'pais' : 'Venezuela'
        },
    ]

    def up(self):
        self.articulosFixture = ArticuloFixture(Articulo)
        self.articulosFixture.up()
        super(AutorFixture, self).up()

    def down(self):
        super(AutorFixture, self).down()
        self.articulosFixture.down()

class CleiFixture(Fixture):
    fixtures = [
        {
            'fechaInscripcionDescuento': '5/10/2014',
            'fechaInscripcion': '7/10/2014',
            'fechaTopeArticulo': '14/04/2014',
            'fechaNotificacion': '01/06/2014',
            'tarifaReducida': '2500',
            'tarifaNormal': '3500',
            'fechaInicio': '02/02/2015'
        },

    ]
    def up(self):
        self.articuloFixture = ArticuloFixture(Articulo)
        self.articuloFixture.up()
        self.miembrocpFixture = MiembroCPFixture(MiembroCP)
        self.miembrocpFixture.up()

        super(CleiFixture, self).up()
    def down(self):
        super(CleiFixture, self).down()
        self.articuloFixture.down()
        self.miembrocpFixture.down()

class CPFixture(Fixture):
    fixtures = [
        {
            'clei': ('7/10/2014', '14/04/2014', '01/06/2014')
        },
    ]
    def up(self, save=False):
        self.cleiFixture = CleiFixture(Clei)
        self.cleiFixture.up()
        if save:
            self.cleiFixture.instances[0].save()
        super(CPFixture, self).up()
    def down(self):
        super(CPFixture, self).down()
        self.cleiFixture.down()

class EventoFixture(Fixture):
    fixtures = [
        {
            'nombre': 'EventoA',
            'fecha': '7/10/2014',
            'horaInicio': '8:00',
            'horaFin': '10:00',
            'lugar': 'USB',
            'tipo': 'charla'
        },
    ]

class LugarFixture(Fixture):
    fixtures = [
        {
            'nombre': 'LugarA',
            'ubicacion': 'USB',
            'capacidad': '200',
        },
    ]



class IncripcionFixture(Fixture):
    fixtures = [
        {   
            'nombre': 'Andreina',
            'apellido': 'Soza',
            'institucion': 'USB',
            'correo': 'asoza@usb.ve',
            'dirPostal': '1080',
            'pagWeb': 'www.pagina1.com',
            'telf': '04120000000',
            'tipo': 1,
        },
        {
            'nombre': 'Alejandro',
            'apellido': 'Perez',
            'institucion': 'USB',
            'correo': 'aperez@usb.ve',
            'dirPostal': '1081',
            'pagWeb': 'www.pagina2.com',
            'telf': '04120000001',
            'tipo': 2,
        },
        {
            'nombre': 'Alejandra',
            'apellido': 'Riera',
            'institucion': 'USB',
            'correo': 'ariera@usb.ve',
            'dirPostal': '1082',
            'pagWeb': 'www.pagina3.com',
            'telf': '04120000003',
            'tipo': 3,
        },
        {
            'nombre': 'Pedro',
            'apellido': 'Marmol',
            'institucion': 'USB',
            'correo': 'pmarmol@usb.ve',
            'dirPostal': '1083',
            'pagWeb': 'www.pagina4.com',
            'telf': '04120000004',
            'tipo': 4,
        },
    ]
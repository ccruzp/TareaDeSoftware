import unittest
import random
from main import *
from fixtures import *

class GeneralClassTest(unittest.TestCase):
    def setUp(self):
        self.fixtures.up()
        self.instances = self.fixtures.instances

    def tearDown(self):
        self.fixtures.down()

    def testConstructorAssignment(self):
        fixtureInstances = zip(self.fixtures.fixtures, self.instances)
        for (fixture, instance) in fixtureInstances:
            self.assertTrue(all(fixture[key] == getattr(instance, key)
                                for key in fixture.keys()))

    def testEquality(self):
        if len(self.instances) > 2:
            x, y = self.instances[0:2]
            self.assertFalse(x == y)
            self.assertTrue(x == x)

    def testSave(self):
        for instance in self.instances:
            self.assertTrue(instance.pk in self.classTest.objects)

    def testFind(self):
        for x in self.instances:
            fobj = self.classTest.find(x.pk)
            self.assertTrue(fobj == x)


class TestPersona(GeneralClassTest):
    classTest = Persona
    fixtures = PersonaFixture(Persona)

class TestTopico(GeneralClassTest):
    classTest = Topico
    fixtures = TopicoFixture(Topico)

    def testGetOrCreate(self):
        existing = Topico.find("Base de Datos")
        self.assertTrue(existing == Topico.getOrCreate("Base de Datos"))
        self.assertFalse(existing == Topico.getOrCreate("Traductores"))
        traductores = Topico.getOrCreate("Traductores")
        self.assertTrue(traductores == Topico.getOrCreate("Traductores"))
        self.assertFalse(traductores == existing)



class TestMiembroCP(GeneralClassTest):
    classTest = MiembroCP
    fixtures = MiembroCPFixture(MiembroCP)

    def testAsignarArticulo(self):
        for miembrocp in self.instances:
            articulo = random.choice(Articulo.objects.values())
            miembrocp.asignarArticulo(articulo)
            self.assertTrue(articulo in miembrocp.correcciones)
            self.assertTrue(miembrocp in articulo.evaluadores)
            self.assertTrue(articulo.status == Articulo.REVISANDO)


    def testEvaluarArticulo(self):
        # asignar articulos
        for miembrocp in self.instances:
            articulo = random.choice(Articulo.objects.values())
            miembrocp.asignarArticulo(articulo)
            self.assertTrue(articulo in miembrocp.correcciones)
            self.assertTrue(miembrocp in articulo.evaluadores)
            # evaluar
            notaPrevia = articulo.nota
            evaluacionesPrevias = articulo.correcciones
            sumatoria = notaPrevia*evaluacionesPrevias
            notaAgregada = random.randint(1, 5)
            miembrocp.evaluarArticulo(articulo, notaAgregada)
            self.assertTrue(articulo.nota == (sumatoria+notaAgregada)/float(evaluacionesPrevias+1))


class TestLugar(GeneralClassTest):
    classTest = Lugar
    fixtures = LugarFixture(Lugar)

class TestAutor(GeneralClassTest):
    classTest = Autor
    fixtures = AutorFixture(Autor)
    def testAgregarArticulo(self):
        for autor in self.instances:
            # seleccionar articulo aleatorio
            articulo = random.choice(Articulo.objects.values())
            autor.agregarArticulo(articulo)
            self.assertTrue(articulo in autor.articulos)
            self.assertTrue(autor in articulo.autores)

class TestCP(GeneralClassTest):
    classTest = CP
    fixtures = CPFixture(CP)
    def setUp(self):
        super(TestCP, self).setUp()
        self.normales = [miembrocp
                    for miembrocp in MiembroCP.objects.values() if not miembrocp.esPresidente]
        self.presidentes = [miembrocp
                       for miembrocp in MiembroCP.objects.values() if miembrocp.esPresidente]

    def testAgregarMiembro(self):
        for cp in self.instances:
            miembros = random.sample(self.normales, 2)
            presidente = random.choice(self.presidentes)
            miembros.append(presidente)
            for miembro in miembros:
                cp.agregarMiembro(miembro)
                self.assertTrue(miembro in cp.miembros)
                self.assertTrue(cp in miembro.cp)

    def testProbarSoloUnPresidente(self):
        # seleccionar un cp
        cp = random.choice(self.instances)
        # seleccionar dos presidentes
        p1, p2 = random.sample(self.presidentes, 2)
        cp.agregarMiembro(p1)
        with self.assertRaises(ValueError):
            cp.agregarMiembro(p2)

class TestClei(GeneralClassTest):
    classTest = Clei
    fixtures = CleiFixture(Clei)

    def testAgregarTopico(self):
        topico = Topico.getOrCreate("Topico Prueba")
        clei =         self.instances[0]
        clei.agregarTopico(topico)
        self.assertTrue(topico in clei.topicos)


class TestInscripcion(GeneralClassTest):
    classTest = Persona
    fixtures = IncripcionFixture(Inscripcion)


class TestAsignacionEvaluacion(unittest.TestCase):
    def setUp(self):
        self.cpFixture = CPFixture(CP)
        self.cpFixture.up(save=True)
        self.cp = self.cpFixture.instances[0]
        self.cp.clei = Clei.find(self.cp.clei)
        for articulo in Articulo.objects.values():
            articulo.clei = Clei.find(articulo.clei)
        normales = [x for x in MiembroCP.objects.values() if not x.esPresidente]
        presidente = random.choice([x for x in MiembroCP.objects.values() if x.esPresidente])
        normales.append(presidente)
        for miembroCP in normales:
            self.cp.agregarMiembro(miembroCP)

    def tearDown(self):
        self.cpFixture.down()

    def testAsignacion(self):
        self.cp.clei.asignarArticulos()
        for articulo in Articulo.objects.values():
            self.assertTrue(articulo.evaluadores)
            for evaluador in articulo.evaluadores:
                self.assertTrue(articulo in evaluador.correcciones)

    def testParticionCasosBase(self):
        self.cp.clei.asignarArticulos()
        for articulo in Articulo.objects.values():
            for evaluador in articulo.evaluadores:
                evaluador.evaluarArticulo(articulo, 3)
        aceptados, empatados = self.cp.clei.particionarArticulos(5)
        self.assertTrue(len(aceptados) == 0)
        self.assertTrue(len(empatados) == 10)
        aceptados, empatados = self.cp.clei.particionarArticulos(10)
        self.assertTrue(len(aceptados) == 10)
        self.assertTrue(len(empatados) == 0)

    def testParticionAleatoria(self):
        self.cp.clei.asignarArticulos()
        for articulo in Articulo.objects.values():
            for evaluador in articulo.evaluadores:
                evaluador.evaluarArticulo(articulo, random.randint(1, 5))
        aceptados, empatados = self.cp.clei.particionarArticulos(5)
        self.assertTrue(len(aceptados) <= 5)
        self.assertTrue(all(x.nota >= 3.0 and x.correcciones >= 2.0
                            for x in aceptados))
        # los que estan en empatados o son mas de lo que se puede aceptar
        # o se lleno la lista
        considerable = len([x for x in Articulo.objects.values()
                            if x.nota >= 3.0 and x.correcciones >= 2.0])

        # los aceptados son LOS mejores
        articulos = Articulo.objects.values()[:]
        articulos.sort(key=lambda x: x.nota)
        articulos.reverse()
        self.assertTrue(articulos[:len(aceptados)] == aceptados)
        # los empatados es son los mejores posibles despues de los aceptados
        self.assertTrue(articulos[len(aceptados):len(aceptados)+len(empatados)] == empatados)


class TestEvento(GeneralClassTest):
    classTest = Evento
    fixtures = EventoFixture(Evento)

class TestArticulo(GeneralClassTest):
    classTest = Articulo
    fixtures = ArticuloFixture(Articulo)
    def testAgregarTopico(self):
        topico = Topico.getOrCreate('adsgadjslkgj')
        for x in self.instances:
            x.agregarTopico(topico)
            self.assertTrue(topico in x.topicos)
            self.assertTrue(x in topico.articulos)
    def testAgruparPorPais(self):
        paises = {}
        for x in self.instances:
            for y in x.autores:
                if y.pais not in paises:
                    paises.append(y.pais)
        self.assertTrue(len(Articulo.count_paises) == len(paises))

    def testAgruparPorTopico(self):
        topicos = {}
        for x in self.instances:
            for y in x.topicos:
                topicos.append(y)
        self.assertTrue(len(Articulo.porTopico) == len(topicos))

def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPersona))
    suite.addTests(loader.loadTestsFromTestCase(TestTopico))
    suite.addTests(loader.loadTestsFromTestCase(TestMiembroCP))
    suite.addTests(loader.loadTestsFromTestCase(TestAutor))
    suite.addTests(loader.loadTestsFromTestCase(TestCP))
    suite.addTests(loader.loadTestsFromTestCase(TestClei))
    suite.addTests(loader.loadTestsFromTestCase(TestArticulo))
    suite.addTests(loader.loadTestsFromTestCase(TestAsignacionEvaluacion))
    suite.addTests(loader.loadTestsFromTestCase(TestEvento))
    suite.addTests(loader.loadTestsFromTestCase(TestLugar))
    suite.addTests(loader.loadTestsFromTestCase(TestInscripcion))
    return suite

if __name__ == '__main__':
    unittest.main(verbosity=2)

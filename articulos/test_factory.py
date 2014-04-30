from . import models
from factory import django
import factory
import random
from decimal import Decimal


class FactoryFamilia(django.DjangoModelFactory):
    FACTORY_FOR = models.Familia
    nombre = factory.Sequence(lambda n: u'Familia%d' % n)
    markup = 50


class FactoryRubro(django.DjangoModelFactory):
    FACTORY_FOR = models.Rubro
    nombre = factory.Sequence(lambda n: u'Rubro%d' % n)
    markup = 40
    familia = factory.SubFactory(FactoryFamilia)


class FactoryMarca(django.DjangoModelFactory):
    FACTORY_FOR = models.Marca
    nombre = factory.Sequence(lambda n: u'Marca%d' % n)
    markup = 30


class FactoryAlicuota(django.DjangoModelFactory):
    FACTORY_FOR = models.AlicuotaIVA
    porcentaje = 21


class FactoryCotizacion(django.DjangoModelFactory):
    FACTORY_FOR = models.Cotizacion
    nombre = factory.Sequence(lambda n: u'Moneda%d' % n)
    cotiza_a_ref = 1
    simbolo = "$"


class FactoryProveedor(django.DjangoModelFactory):
    FACTORY_FOR = models.Proveedor
    nombre = factory.Sequence(lambda n: u'Proveedor%d' % n)


class FactoryArticulo(django.DjangoModelFactory):
    FACTORY_FOR = models.Articulo
    rubro = factory.SubFactory(FactoryRubro)
    marca = factory.SubFactory(FactoryMarca)
    nombre = factory.Sequence(lambda n: u'Articulo%d' % n)
    iva = factory.SubFactory(FactoryAlicuota)
    #moneda = factory.SubFactory(FactoryCotizacion)


class FactoryPrecioPorProveedor(django.DjangoModelFactory):

    FACTORY_FOR = models.PrecioPorProveedor
    articulo = factory.SubFactory(FactoryArticulo)
    proveedor = factory.SubFactory(FactoryProveedor)
    moneda  = factory.SubFactory(FactoryCotizacion)
    codigo_interno = str(factory.LazyAttribute(lambda a: random.uniform(1, 5000)))
    precio = 10
    referencia = False
    ultimacompra = False
    razon_ultimacompra = "Razón por la que compró a este proveedor"


class FactoryPrecioPorProveedorConPrecioAzar(django.DjangoModelFactory):

    FACTORY_FOR = models.PrecioPorProveedor
    articulo = factory.SubFactory(FactoryArticulo)
    proveedor = factory.SubFactory(FactoryProveedor)
    moneda  = factory.SubFactory(FactoryCotizacion)
    codigo_interno = str(random.randint(1,50000))
    precio = factory.LazyAttribute(lambda a: Decimal(random.uniform(1, 1000)))
    referencia = False
    ultimacompra = False
    razon_ultimacompra = "Razón por la que compró a este proveedor"



def obtenerArticuloCompleto(**kwargs):
    art = FactoryArticulo(**kwargs)
    for a in range(3):
        costo = FactoryPrecioPorProveedor(articulo=art, referencia=(a==2))
    return art

def listaArticulosCompletos(cantidad=5):
    lista=[]
    for c in range(cantidad):
        lista.append(obtenerArticuloCompleto())
    return lista

def listaArticulos(cantidad=5):
    lista=[]
    for c in range(cantidad):
        lista.append(FactoryArticulo())
    return lista

#---------------------------------------------------------
#  GRUPOS
#---------------------------------------------------------

class FactoryGrupo(django.DjangoModelFactory):
    FACTORY_FOR = models.Grupo
    nombre = factory.Sequence(lambda n: u'Grupo%d' % n)
    codigo = "COD"


class FactoryItemGrupo(django.DjangoModelFactory):
    FACTORY_FOR = models.ItemGrupo
    grupo =  factory.SubFactory(FactoryGrupo)
    articulo = factory.SubFactory(FactoryArticulo, markup=100)
    cant_predeterminada = 1


def ungrupo(hijos=5, cantidad_por_item=1):
    gp = FactoryGrupo()
    for x in range(hijos):
        artc = obtenerArticuloCompleto(markup=100)
        ig = FactoryItemGrupo(grupo=gp, articulo=artc, cant_predeterminada=cantidad_por_item)
    return gp
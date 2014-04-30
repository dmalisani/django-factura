from django.test import TestCase
from articulos.models import Articulo, Familia, Rubro, Marca, AlicuotaIVA, Cotizacion
from articulos.test_factory import *
import decimal


class TestArticulo(TestCase):
    def setUp(self):
        self.articulo  = obtenerArticuloCompleto()
        #self.articulo = FactoryArticulo()

    def test_tiene_marca(self):
        self.assertIsNotNone(self.articulo.marca)

    def test_tiene_rubro(self):
        self.assertIsNotNone(self.articulo.rubro)

    def test_tiene_descripcion(self):
        self.assertIsNotNone(self.articulo.nombre)

    def test_existe_costo(self):
        costos = self.articulo.costo()
        self.assertIsNotNone(costos)

    def test_precio_markup_flia(self):
        art = self.articulo
        costo = art.costo().precio
        self.assertGreater(costo,0,"costo en 0")
        art.rubro.familia.markup = 50 #---Debe tomar este
        art.rubro.markup = 0
        art.marca.markup = 0
        art.markup = 0
        self.assertEqual(art.aplicar_markup(), costo * Decimal("1.5"), "Markup en FAMILIA calculado incorrectamente")

    def test_precio_markup_rubro(self):
        art = self.articulo
        costo = art.costo().precio
        self.assertGreater(costo,0,"costo en 0")
        art.rubro.familia.markup = 10
        art.rubro.markup = 50       #---Debe tomar este
        art.marca.markup = 0
        art.markup = 0
        self.assertEqual(art.aplicar_markup(), costo * Decimal("1.5"), "Markup en RUBRO calculado incorrectamente")

    def test_precio_markup_marca(self):
        art = self.articulo
        costo = art.costo().precio
        self.assertGreater(costo,0,"costo en 0")

        art.rubro.familia.markup = 10
        art.rubro.markup = 20
        art.marca.markup = 50       #---Debe tomar este
        art.markup = 0
        self.assertEqual(art.aplicar_markup(), costo * Decimal("1.5"), "Markup en MARCA calculado incorrectamente")

    def test_precio_markup_articulo(self):
        art = self.articulo
        costo = art.costo().precio
        self.assertGreater(costo,0,"costo en 0")
        art.rubro.familia.markup = 10
        art.rubro.markup = 20
        art.marca.markup = 30
        art.markup = 50      #---Debe tomar este
        self.assertEqual(art.aplicar_markup(), costo * Decimal("1.5"), "Markup en ARTICULO calculado incorrectamente")

    def test_neto(self):
        art = self.articulo
        art.markup = 100
        self.assertEqual(art.precio_neto(), Decimal("20"), "Error en IVA")

    def test_iva(self):
        art = self.articulo
        art.markup = 100
        self.assertEqual(art.monto_iva(), Decimal("4.2"), "Error en IVA")

    def test_precio_venta(self):
        art = self.articulo
        art.markup = 100
        self.assertEqual(art.precio_venta(), Decimal("24.20"), "Error en IVA")

    def test_precio_moneda(self):
        art = FactoryArticulo(cvmoneda=False, markup=100)
        #self.assertFalse(art.cvmoneda,"Error en atributo convertir moneda")
        cot1 = FactoryCotizacion(cotiza_a_ref = 2, simbolo="U$S")
        c1 = FactoryPrecioPorProveedor(articulo=art, moneda=cot1, referencia=True)
        self.assertEqual(art.precio_neto(), 20, "Error en costo")

    def test_precio_moneda_extranjera(self):
        cot1 = FactoryCotizacion(cotiza_a_ref=1, simbolo="U$S")
        art = FactoryArticulo(cvmoneda=True, markup=100)
        #self.assertFalse(art.cvmoneda,"Error en atributo convertir moneda")
        cot1 = FactoryCotizacion(cotiza_a_ref = 5, simbolo="U$S")
        c1 = FactoryPrecioPorProveedor(articulo=art, moneda=cot1, referencia=True)
        self.assertEqual(art.precio_neto(), 100, "Error en costo de al convertir moneda")

    def test_art_sincosto(self):
        art=FactoryArticulo()
        self.assertEqual(art.precio_venta(), 0, "Error en el cálculo de precio de venta al no tener costo")

class TestCotizacion(TestCase):

    def setUp(self):
        self.cot1 = FactoryCotizacion()
        self.cot2 = FactoryCotizacion(cotiza_a_ref=2)
        self.cot3 = FactoryCotizacion(cotiza_a_ref=Decimal(1.5))

    def test_cot1(self):
        self.assertEqual(self.cot1.cotiza_a_ref, 1, "Error en COTIZACION de referencia")

    def test_cot2(self):
        self.assertEqual(self.cot2.cotiza_a_ref, 2, "Error en COTIZACION de referencia")

    def test_cot3(self):
        self.assertEqual(self.cot3.cotiza_a_ref, Decimal(1.5), "Error en COTIZACION de referencia")

    def test_conversion_1a2(self):
        convertido = self.cot1.convertir_a(1, self.cot2)
        self.assertEqual(convertido, Decimal(2), "Error conviritiendo A MONEDA")

    def test_conversion_1a1_5(self):
        convertido = self.cot1.convertir_a(2, self.cot3)
        self.assertEqual(convertido, Decimal(3), "Error conviritiendo A MONEDA")

    def test_convertir_desde_2_a_1(self):
        convertido = self.cot1.convertir_desde(5, self.cot2)
        self.assertEqual(convertido, 2.5, "Error conviritiendo DESDE MONEDA")

    def test_convertir_desde_2_a_2(self):
        convertido = self.cot2.convertir_desde(5, self.cot2)
        self.assertEqual(convertido, 5, "Error conviritiendo DESDE MONEDA")

    def test_convertir_desde_2_a_1_5(self):
        convertido = self.cot2.convertir_desde(Decimal(1.5), self.cot3)
        self.assertEqual(convertido, 2, "Error conviritiendo DESDE MONEDA")

    def test_convertir_desde_1_5_a_2(self):
        convertido = self.cot3.convertir_desde(2, self.cot2)
        self.assertEqual(convertido, Decimal(1.5), "Error conviritiendo DESDE MONEDA")


class TestGrupos(TestCase):
    def setUp(self):
        self.grupo  = ungrupo(hijos=10, cantidad_por_item=1)

    def test_calculo_total_grupo(self):
        self.assertEqual(self.grupo.total_neto(), 200, "Error en el calculo del neto del grupo")

    def test_addalgrupo(self):
        cant = self.grupo.miembros_del_grupo.count()
        item = FactoryItemGrupo()
        self.grupo.agregar_articulo(item)
        self.assertEqual(self.grupo.miembros_del_grupo.count(), cant+1, "No se agregó item al grupo")

    def test_quitardelgrupo(self):
        cant = self.grupo.miembros_del_grupo.count()
        item = self.grupo.miembros_del_grupo.all()[0]
        self.grupo.quitar_articulo(item)
        self.assertEqual(self.grupo.miembros_del_grupo.count(), cant-1, "No se quito item del grupo")









#!/usr/bin/python
# -*- coding: utf8 -*-
from decimal import Decimal
from django.db import models


DOS_DECIMALES = Decimal(10) ** -2

#--Errores generales
ERR_COTIZACION = "01"
ERR_FAMILIA = "02"
ERR_ARTICULO = "03"
ERR_RUBRO = "04"
ERR_MARCA = "05"
ERR_PROVEEDOR = "06"
ERR_ALICUOTA = "07"
ERR_COSTO = "08"
ERR_GRUPO = "09"

#--Error tipo

ERR_FALTA_DATO = "01"
ERR_INCONSISTENCIA = "02"
ERR_DUPLICADO = "03"
ERR_DESBORDE = "04"




class Cotizacion(models.Model):
    """El valor de cada moneda, el que tenga valor 1 se tomará como referencia
        los demás se usara la cotiza_a_ref como multiplicador.
        Ej. Si la moneda actual es el PESO la cotización de ese será 1 y la moneda
        DOLAR tendrá como cotización 4.3 (con referencia al peso) si se quiere emplear
        DOLAR cómo moneda se pondrá 1 en su cotización y el peso 0.23
        NOTA: Puede haber ilimitadas monedas.
    """
    nombre=models.CharField(max_length=15, verbose_name=u"Nombre de moneda")
    cotiza_a_ref=models.FloatField(verbose_name=u"Cotización a moneda de referencia",  blank=False,  null=False,  default=1)
    simbolo=models.CharField(max_length=4, verbose_name=u"Símbolo de moneda")

    class Meta:
        verbose_name_plural="Cotizaciones"

    def __str__(self):
        return self.simbolo

    def obtener_moneda_actual(self):
        return main_obtener_moneda_actual()

    def convertir_a(self,valor, moneda_destino):
        return valor * moneda_destino.cotiza_a_ref

    def convertir_desde(self, valor, moneda_origen):
        return valor * self.cotiza_a_ref/moneda_origen.cotiza_a_ref

def main_obtener_moneda_actual():
    """Obtiene la moneda con cotización 1"""
    cots =  Cotizacion.objects.filter(cotiza_a_ref=1)
    cot = None
    if cots == None:
        informar_error("no hay moneda de referencia", ERR_COTIZACION+ERR_FALTA_DATO, True)
        cot = Cotizacion(simbolo="Test$", cotiza_a_ref=1)
    if len(cots)>1:
        informar_error("hay más de una moneda de referencia", ERR_COTIZACION+ERR_FALTA_DATO, True)
        cot = Cotizacion(simbolo="Test$", cotiza_a_ref=1)
    else:
        cot = cots[0]
    return cot

class Familia(models.Model):
    """Normalización primaria de productos. Markup obligatoiro"""
    nombre=models.CharField(max_length=25, verbose_name="Nombre de Familia",  unique="True")
    markup=models.DecimalField(verbose_name="Márgen", max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]


class Rubro(models.Model):
    nombre=models.CharField(max_length=30, verbose_name="Nombre de Rubro",  unique="True")
    markup=models.DecimalField(verbose_name="Márgen", max_digits=5, decimal_places=2,  blank=True,  null=True)
    familia=models.ForeignKey(Familia)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]

class Marca(models.Model):
    nombre=models.CharField(max_length=30, verbose_name="Marca",  unique="True")
    markup=models.DecimalField(verbose_name="Márgen", max_digits=5, decimal_places=2,  blank=True,  null=True)

    class Meta:
        ordering = ["nombre", ]

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre=models.CharField(max_length=40, verbose_name=u"Razón Social", unique=True)
    telefono=models.CharField(max_length=30, verbose_name="Tel/Fax",  blank=True, null=True)
    email=models.EmailField(blank=True, null=True)
    cuentas=models.TextField(blank=True,  null=True)
    viajante =  models.TextField(blank=True,  null=True, verbose_name="Datos del viajante/Contacto")
    descuento_a_lista = models.DecimalField(verbose_name = "Descuento aplicado al precio de lista (%)",  max_digits=5, decimal_places=2,  blank=True,  null=True)

    class Meta:
        ordering=["nombre", ]
        verbose_name="Proveedor"
        verbose_name_plural="Proveedores"

    def __str__(self):
        return self.nombre

class AlicuotaIVA(models.Model):
    porcentaje=models.DecimalField(verbose_name="Porcentaje", max_digits=5, decimal_places=3)

    def coeficiente(self):
        return 1.0+float(self.porcentaje)/100.0

    def __str__(self):
        return "IVA %5.2f%s " % (self.porcentaje, '%')

    class Meta:
        verbose_name=u"Alícuota de IVA"
        verbose_name_plural=u"Alícuotas de IVA"

class Articulo(models.Model):
    rubro = models.ForeignKey(Rubro )
    nombre = models.CharField(max_length=200, verbose_name="Descripción")
    medida = models.CharField(max_length=60, verbose_name=u"Medida/Caracteristica",  blank=True,  null=True)
    nro_orden = models.CharField(max_length=3, verbose_name="Ordenación",  blank=True,  null=True)
    marca = models.ForeignKey(Marca )
    markup = models.DecimalField(verbose_name="Márgen", max_digits=5, decimal_places=2,  blank=True,  null=True)
    iva = models.ForeignKey(AlicuotaIVA )
    usar_pv = models.BooleanField(verbose_name="Emplear Precio de venta manual", default=False)
    venta = models.DecimalField(verbose_name="Precio de venta", max_digits=6, decimal_places=3,  blank=True,  null=True)
    ubicacion = models.CharField(max_length=25, verbose_name="Ubicación",  blank=True,  null=True)
    CHOICE_UNIDAD_VENTA = (('UN', 'Unidad'), ('KG', 'Kilogramo'), ('CJ', 'Caja'), ('LT', 'Litro'), ('BL', 'Blister'), ('MT', 'Metro'), ('BS', 'Bolsa'), )
    unidad_venta = models.CharField(max_length=2, choices=CHOICE_UNIDAD_VENTA,  verbose_name="Modo de venta",  default="UN", null=True)
    cantidad_por_bulto = models.DecimalField(verbose_name="Cantidad por bulto/caja", max_digits=5, decimal_places=0, blank=True,  null=True)
    codigo_barras = models.CharField(verbose_name=u"Código de Barras",  max_length=160, blank=True , null=True)
    codigo_propio = models.CharField(verbose_name=u"Código Propio",  max_length=160, blank=True, null=True)
    cvmoneda = models.BooleanField(verbose_name="Convertir moneda", help_text=('Adapta el precio a la moneda local según la cotización'), default=True)
    #redondear = models.BooleanField(verbose_name="Redondear Precio", help_text=('Adapta redondea el precio para evitar problemas de cambio'), default=True)
    #partes_redondeo = models.SmallIntegerField(default = 4, blank=True, null=True)
    #TODO: Pasar las propiedades de redondeo a facturación.
    informacion = models.TextField(blank=True,  null=True)
    #moneda  = models.ForeignKey(Cotizacion,  verbose_name="Moneda")
    en_oferta = models.BooleanField(verbose_name=u"Artículo en oferta", default=False)
    texto_oferta = models.TextField(blank=True,  null=True)

    def __str__(self):
        return self.completo()

    def completo(self):
        if self.medida:
                respuesta=('%s %s %s %s' % (self.rubro,  self.nombre,  self.marca, self.medida))
        else:
                respuesta=('%s %s %s' % (self.rubro,  self.nombre,  self.marca))
        return respuesta

    def costo(self):
        tmpcosto=self.ppp_articulo.all().filter(referencia=True)
        if tmpcosto:
            if len(tmpcosto)>1:
                informar_error("MAS DE UNA REFERENCIA:" + self.completo(), ERR_ARTICULO+ERR_INCONSISTENCIA, True)
            tmpcosto=tmpcosto[0] #devuelve el primer elemento si hay varios como referencia (que sería un error)
        else:
            #--Debug--comentada la sgte linea-
            informar_error("NO HAY COSTO: " + self.completo(), ERR_ARTICULO+ERR_FALTA_DATO, True)
            tmpcosto=None
        return tmpcosto

    def monedaActual(self):
        moneda_devuelta = None
        if self.costo():
            moneda_actual = main_obtener_moneda_actual()
            if (self.costo().moneda == moneda_actual or self.cvmoneda):
                moneda_devuelta = moneda_actual
            else:
                moneda_devuelta = self.costo().moneda
        return moneda_devuelta

    def aplicar_markup(self):
        """Calcula el precio de venta que debe tener el artículo en base
        a los markups establecidos con esta presendecia)
        Markup Local(del articulo)
        Markup Marca
        Markup Rubro
        Markup Familia
        """
        # --------calculo del markup-------------------
        markup_actual = self.rubro.familia.markup
        if markup_actual is None or markup_actual == 0:
            informar_error("SIN MARKUP:"+ self.rubro.familia.nombre, ERR_FAMILIA + ERR_FALTA_DATO, True)
            markup_actual = 0
        if not (self.rubro.markup is None) and (self.rubro.markup > 0):
            markup_actual = self.rubro.markup
        if not (self.marca.markup is None) and (self.marca.markup > 0):
            markup_actual = self.marca.markup
        if not (self.markup is None) and (self.markup > 0):
            markup_actual = self.markup
        # -------------------
        costo = self.costo()

        if costo is None:
            informar_error("SIN COSTO:" + self.completo(), ERR_ARTICULO + ERR_FALTA_DATO)
            venta = 0
        else:
            precio_costo = costo.precio
            venta = precio_costo * Decimal(1 + (markup_actual/100))

        return venta

    def aplicar_iva(self, importe):
        iva = importe * Decimal(self.iva.porcentaje)/100
        return iva

    def precio_neto(self):
        temp_neto = self.aplicar_markup()

        if self.cvmoneda and temp_neto>0:
            if main_obtener_moneda_actual():
                informar_error("NO HAY MONEDA ACTUAL", ERR_COTIZACION+ERR_INCONSISTENCIA, True)
                temp_neto = temp_neto * Decimal(self.costo().moneda.cotiza_a_ref)

        return temp_neto

    def monto_iva(self):
        return self.aplicar_iva(self.precio_neto())

    def precio_venta(self):
        return self.precio_neto()+self.monto_iva()


class PrecioPorProveedor(models.Model):
    articulo = models.ForeignKey(Articulo,related_name="ppp_articulo")
    proveedor = models.ForeignKey(Proveedor)
    precio = models.DecimalField(verbose_name="Precio de costo", max_digits=9, decimal_places=3, help_text=('Introduzca el precio sin iva'))
    moneda  = models.ForeignKey(Cotizacion,   verbose_name="Moneda")
    codigo_interno = models.CharField(max_length=40, verbose_name=u"Código en lista", blank=True,  null=True,   help_text=(u'El código en la lista del proveedor'))
    referencia = models.BooleanField(verbose_name="Tomar como referencia",default=False)
    ultimacompra = models.BooleanField(verbose_name=u"última compra",   help_text=(u'Indique si le compró la última vez a este proveedor'),default=False)
    razon_ultimacompra = models.CharField(max_length=40, verbose_name=u"Razón por la que compró a este proveedor", blank=True,  null=True,   help_text=(u'Si desea aclarar por qué decidió comprar la ultima vez a este proveedor'))
    ultima_actualizacion = models.DateField(verbose_name=u"Última actualización de este registro",auto_now=True)
    observaciones = models.CharField(max_length=200,  blank=True,  null=True)

    def __str__(self):
        if not self.precio:
            self.precio=0
        return "%s %s %6.2f" % (self.proveedor.nombre,  self.moneda.simbolo,  self.precio)

    class Meta:
        verbose_name=u"Precio por Proveedor"
        verbose_name_plural=u"Precios por Proveedores"
        ordering = ("-precio", )
        unique_together = ("articulo", "proveedor", 'referencia')


class Grupo(models.Model):
    nombre = models.CharField(max_length=100, verbose_name=u"Nombre del grupo")
    codigo = models.CharField(max_length=100, verbose_name=u"Código del grupo")
    observaciones = models.TextField(blank=True,  null=True)

    def total_neto(self):
        acum = 0
        for item in self.miembros_del_grupo.all():
             acum = acum + item.articulo.precio_neto() * item.cant_predeterminada
        #    print(item.articulo)
        return Decimal(acum).quantize(DOS_DECIMALES)

    def __str__(self):
        return self.nombre

    def agregar_articulo(self, item):
        self.miembros_del_grupo.add(item)

    def quitar_articulo(self, item):
        item.delete()


class ItemGrupo(models.Model):
    articulo = models.ForeignKey(Articulo)
    grupo = models.ForeignKey(Grupo, related_name="miembros_del_grupo")
    cant_predeterminada = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.articulo.completo()


def informar_error(titulo, codigo, grave=False):
    pass
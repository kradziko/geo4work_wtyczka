# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickLayoutDialog
                                 A QGIS plugin
 This plugin enables to make a quick layout.
                             -------------------
        begin                : 2016-09-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by GeoINFO
        email                : anotherfable@gmial.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, sys

from PyQt4 import QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'quick_layout_dialog_base.ui'))


class QuickLayoutDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(QuickLayoutDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.filepath = "" # przechowuje sciezke do pliku wyjsciowego
        self.btnDruk.clicked.connect(self.mapa) # przypisuje metode mapa do  klikniecia przycisku Drukuj
        self.btnAnul.clicked.connect(self.anuluj) # przypisuje metode anuluj do  klikniecia przycisku Anuluj

    def openBrowse(self, rozszerzenie):
        # otwieranie okienka z opcją zapisu pliku
        qfd = QFileDialog()
        qfd.setDefaultSuffix(rozszerzenie)
        self.filepath = qfd.getSaveFileName()
        # self.filepath += rozszerzenie
        

    def drukujDoPDF(self, c):
	# c - kompozycja qgisa
	printer = QPrinter() # instancja do QPrinter
        printer.setOutputFormat(QPrinter.PdfFormat) # podanie ze plik bedzie pdfem
        printer.setOutputFileName(self.filepath) # dodanie nazwy pliku
        printer.setPaperSize(QSizeF(c.paperWidth(), c.paperHeight()), QPrinter.Millimeter) # wymiary
        printer.setFullPage(True) 
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(c.printResolution())
        
        pdfPainter = QPainter(printer)
        paperRectMM = printer.pageRect(QPrinter.Millimeter)
        paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
        c.render(pdfPainter, paperRectPixel, paperRectMM)
        pdfPainter.end()
        print("done")


    def drukujDoPNG(self, c):	
        dpi = c.printResolution()
        dpmm = dpi / 25.4
        width = int(dpmm * c.paperWidth())
        height = int(dpmm * c.paperHeight())
        
        # tworzenie obrazu wyjściowego i jego inicjalizacja
        image = QImage(QSize(width, height), QImage.Format_ARGB32)
        image.setDotsPerMeterX(dpmm * 1000)
        image.setDotsPerMeterY(dpmm * 1000)
        image.fill(0)

        # renderowanie
        imagePainter = QPainter(image)
        sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight())
        targetArea = QRectF(0, 0, width, height)
        c.render(imagePainter, targetArea, sourceArea)
        imagePainter.end()

        image.save(self.filepath, "png")
        print("Utworzono png")

    def mapa(self):
        mapRender = self.iface.mapCanvas().mapRenderer()
        c = QgsComposition(mapRender)
        c.setPlotStyle(QgsComposition.Print)

        # dodanie mapy do wydruku
        x, y = 0, 0
        w, h = c.paperWidth(), c.paperHeight()
        composerMap = QgsComposerMap(c, x, y, w, h)
        c.addItem(composerMap)

        
        if self.chLeg.isChecked():
            # dodaj legende do mapy
            legend = QgsComposerLegend(c)               # inicjalizacja legendy
            legend.model().setLayerSet(mapRender.layerSet())
            legend.setFrameEnabled(True)                # ramka legendy
            hLeg = legend.ItemHeight                    # wysokosc legendy
            print hLeg
            legend.move(5, h-hLeg*2-5)                  # ustawienie pozycji legendy na mapie
            c.addItem(legend)                           # dodanie legendy do mapy
        
        if self.chStrz.isChecked():
            # dodaj strzalke polnocy
            arrow = QgsComposerArrow(c)                 # inicjalizacja strzalki
            wArr = arrow.ItemWidth                      # szerokosc strzalki
            arrow.move(w-wArr-5, 5)                     # ustawienie pozycji strzalki na mapie
            c.addItem(arrow)                            # dodanie strzalki do mapy

        #### wybieranie formatu zapisu
        if self.btnPDF.isChecked():
            self.openBrowse(".pdf")
	    self.drukujDoPDF(c)
            QMessageBox.information(self, u'Sukces!', u'Zapisano dokument pdf')

        elif self.btnPNG.isChecked():
            self.openBrowse(".png")
	    self.drukujDoPNG(c)
            QMessageBox.information(self, u'Sukces!', u'Zapisano obraz w formacie png')
        
        else:
            QMessageBox.warning(self,u'Błąd',u'Musisz wybrać format zapisu')


    def anuluj(self):
        #zamkniecie wtyczki
        QWidget.close(self)


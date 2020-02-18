# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickLayoutDialog
                                 A QGIS plugin
 This plugin enables to make a quick layout.
                             -------------------
        begin                : 2016-09-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by kr
        email                : kra@giap.pl
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

import os, sys, time

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
        self.setWindowTitle("Wydruk mapy z widoku projektu") # zmiana tytułu okienka wtyczki
        self.iface = iface
        self.filepath = "" # przechowuje sciezke do pliku wyjsciowego
        self.btnDruk.clicked.connect(self.mapa) # przypisuje metode mapa do  klikniecia przycisku Drukuj
        self.btnAnul.clicked.connect(self.anuluj) # przypisuje metode anuluj do  klikniecia przycisku Anuluj
        self.chSkal.clicked.connect(self.wylacz)

    def openBrowse(self, rozszerzenie):
        # otwieranie okienka z opcją zapisu pliku
        qfd = QFileDialog()
        qfd.setDefaultSuffix(rozszerzenie)
        qfd.setAcceptMode(QFileDialog.AcceptSave)
        qfd.setNameFilters(['Dokument ' + rozszerzenie + '(*.'+rozszerzenie+')'])
        if qfd.exec_() == QtGui.QDialog.Accepted:
            self.filepath = qfd.selectedFiles()[0]
        else:
            print('Cancelled')
       
    def openBrowse2(self, rozszerzenie):
        # otwieranie okienka z opcją zapisu pliku
        qfd = QFileDialog()
        qfd.setDefaultSuffix(rozszerzenie)
        self.filepath = qfd.getSaveFileName()
 
    def progress(self):
        file = range(30)
        number = len(file)
        progressWasCancelled = False
        prog = QProgressDialog("Zapisuje","Przerwij",0, number)
        prog.setWindowModality(QtCore.Qt.WindowModal)
        prog.setMinimumDuration(0)
        for lNumber, line in enumerate(file):
            prog.setValue(lNumber)
            if prog.wasCanceled():
                progressWasCancelled = True
                break
            time.sleep(0.05)
        prog.setValue(number)
        prog.deleteLater()

    def drukujDoPDF(self, c):
	# c - kompozycja qgisa
	printer = QPrinter() # instancja do QPrinter
        printer.setOutputFormat(QPrinter.PdfFormat) # podanie ze plik bedzie pdfem
        printer.setOutputFileName(self.filepath) # dodanie nazwy pliku
        printer.setPaperSize(QSizeF(c.paperWidth(), c.paperHeight()), QPrinter.Millimeter) # wymiary
        printer.setFullPage(True) 
        printer.setPrintRange(c.numPages()) # this is for printing all pages
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(c.printResolution())
       
        pdfPainter = QPainter(printer)
        c.renderPage(pdfPainter, 0)
        if c.numPages() is 2:
            printer.newPage()
            c.renderPage(pdfPainter, 1)
        pdfPainter.end()


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

        image.save(self.filepath, "png")

        if c.numPages() is 2: #dodanie 2 strony z legenda
            c.renderPage(imagePainter, 1)
            image.save(self.filepath[:-4]+"_2"+self.filepath[-4:], "png")
        imagePainter.end()

    def wylacz(self):
        if self.chSkal.isChecked():
            self.btnSNum.setEnabled(True)
            self.btnSLin.setEnabled(True)
        else:
            self.btnSNum.setDisabled(True)
            self.btnSLin.setDisabled(True)
    
    def mapa(self):
        mapRender = self.iface.mapCanvas().mapRenderer()
        c = QgsComposition(mapRender)
        c.setPlotStyle(QgsComposition.Print)
        # dodanie mapy do wydruku
        x, y = 30, 30
        w, h = c.paperWidth(), c.paperHeight()
        composerMap = QgsComposerMap(c, x, y, w-60, h-60)
        composerMap.setFrameEnabled(True)
        c.addItem(composerMap)
        
        if self.chLeg.isChecked():
            # dodaj legende do mapy z warstwami widocznymi w oknie widoku
            c.setNumPages(2)                            # utworzenie dodatkowej strony dla legendy
            c.setPagesVisible(True)
            legend = QgsComposerLegend(c)               # inicjalizacja legendy
            layerGroup = QgsLayerTreeGroup()            # utworzenie grupy warstw
            n = 0                                       # licznik id
            # petla iteruje po liscie aktywnych warstw
            visibleLayers = self.iface.mapCanvas().layers()
            visibleLayersCount = len(visibleLayers)     # pobranie dlugosci listy
            for the_layer in visibleLayers:
                layerGroup.insertLayer(n, the_layer)    # dodanie widocznej warstwy do grupy warstw layerGroup
                n += 1                                  # zwiekszanie id o 1
            legend.modelV2().setRootGroup(layerGroup)
            legend.setSymbolHeight(3.0)                 # zmiana wysokosci symbolu w legendzie
            legend.setSymbolWidth(5.0)                  # zmiana szerokosci symbolu w legendzie
            # zmiana odstepow pomiedzy kolejnymi warstwami w legendzie dzieki czemu miesci sie duzo warstw
            legend.rstyle(QgsComposerLegendStyle.Symbol).setMargin(QgsComposerLegendStyle.Top, 0.7)
            legend.setColumnCount(3)                    # 3 kolumny warstw w legendzie
            legend.setSplitLayer(True)                  # warstwy nie są pogrupowane względem topologii
            legendSize = legend.paintAndDetermineSize(None)
            legend.setResizeToContents(True)
            c.addItem(legend)                           # dodanie legendy do mapy
            # ustawienie pozycji legendy na mapie na 2 kartce
            legend.setItemPosition(5, h+8, legendSize.width(), legendSize.height(), QgsComposerItem.UpperLeft, 2)


        if self.chStrz.isChecked():
            # dodaj strzalke polnocy
            arrow = QgsComposerArrow(QPointF(w-15, 30), QPointF(w-15, 10), c) 
            c.addItem(arrow)                            # dodanie strzalki do mapy

        if self.chSkal.isChecked():
            # dodaje skalę        
#            if not (self.btnSNum.isChecked() or self.btnSLin.isChecked()):
#               QMessageBox.critical(self,u'Błąd',u'Musisz wybrać rodzaj skali')
            skala = QgsComposerScaleBar(c)
            skala.setComposerMap(composerMap)
            if self.btnSNum.isChecked():
                skala.setStyle('Numeric')                       #numeryczna
                czcionka2 = QFont()
                czcionka2.setPixelSize(100)
                skala.setFont(czcionka2)
            else:
                skala.applyDefaultSize()
                skala.setNumSegmentsLeft(0)
            skala.move(5, h-18)
            c.addItem(skala)                                #dodanie skali do mapy
            
        if self.linTyt.text():
            tytul = QgsComposerLabel(c)
            tytul.setText(self.linTyt.text())
            czcionka = QFont()
            czcionka.setPointSize(36)   #rozmiar czcionki
            czcionka.setWeight(75)      #pogrubiona czcionka
            tytul.setFont(czcionka)
            tytul.adjustSizeToText()
            #tytul.setVAlign(Qt.AlignVCenter) #z jakiegoś powodu nie chce to działać, może wy coś poradzicie (wyrównanie do środka)
            #tytul.vAlign()
            c.addItem(tytul)
            tytul.setItemPosition(w/2, 10, QgsComposerItem.UpperMiddle)
            #tytul.move(w/2-len(tytul.text())*7.5/2, 15)
        else:
            QMessageBox.warning(self,u'Błąd',u'Nie wpisano tytułu')
        
        
            
        #### wybieranie formatu zapisu
        if self.btnPDF.isChecked():
            self.openBrowse("pdf")
            if self.filepath is not "":
	        self.drukujDoPDF(c)
                QMessageBox.information(self, u'Sukces!', u'Zapisano dokument pdf')

        elif self.btnPNG.isChecked():
            self.openBrowse("png")
            if self.filepath is not "":
	        self.drukujDoPNG(c)
                QMessageBox.information(self, u'Sukces!', u'Zapisano obraz w formacie png')
        
        else:
            QMessageBox.warning(self,u'Błąd',u'Musisz wybrać format zapisu')


    def anuluj(self):
        #zamkniecie wtyczki
        QWidget.close(self)


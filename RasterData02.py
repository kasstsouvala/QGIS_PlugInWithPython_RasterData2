# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RasterData02
                                 A QGIS plugin
 Store in a csv all cell values, coordinates and coordinates as string
                              -------------------
        begin                : 2014-10-02
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Kassiani
        email                : 
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from Raster_Data02_dialog import RasterData02Dialog
import os.path

import numpy as np
import decimal
import csv
import array
import sys
import os, sys, time, gdal
from gdalconst import *

from qgis.core import QgsMapLayer
from qgis.core import QgsMapLayerRegistry

from qgis.gui import QgsVertexMarker
from PyQt4.QtCore import *
import sys
import numpy as np
import decimal
import csv
import array

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import decimal
import csv
import array
import sys
import os, sys, time, gdal
from gdalconst import *

class RasterData02:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RasterData02_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = RasterData02Dialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Raster Data02')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RasterData02')
        self.toolbar.setObjectName(u'RasterData02')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RasterData02', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RasterData02/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'RasterData02_all info'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Raster Data02'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        #layers = QgsMapLayerRegistry.instance().mapLayers().values()
        #for layer in layers:
            #if layer.type() == QgsMapLayer.RasterLayer:
                #self.dlg.comboBoxRaster.addItem(layer.name(), layer )
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        
        # See if OK was pressed
        if result == 1:
            #Get the values from the dialog:
            Lonmax = self.dlg.doubleSpinBoxLonmax.value()
            Lonmin = self.dlg.doubleSpinBoxLonmin.value()
            Latmax = self.dlg.doubleSpinBoxLatmax.value()
            Latmin = self.dlg.doubleSpinBoxLatmin.value()
            path = self.dlg.lineEditPath.text()
            nameSave = self.dlg.lineEditName_2.text()
            name = self.dlg.lineEditName.text()
            fileForm = self.dlg.lineEditExcel.text()

            #Novalue = self.dlg.doubleSpinBoxNovalue.value()
            save = self.dlg.lineEditSave.text()
            
            name1 = nameSave+"1"
            name2 = nameSave+"2"
            name3 = nameSave+"3"
            name4 = nameSave+"4"
            name5 = nameSave+"5"
            name6 = nameSave+"6"
            name7 = nameSave+"7"
            name8 = nameSave+"8"
            name9 = nameSave+"9"
            name10 = nameSave+"10"
            name11 = nameSave+"11"
            
            #call the selected layer:
            #index = self.dlg.comboBoxRaster.currentIndex()
            #ds = self.dlg.comboBoxRaster.itemData(index)

            #start timing
            startTime = time.time()

            os.chdir(path)
            gdal.AllRegister()
            ds = gdal.Open(name, GA_ReadOnly)

            #c= csv.writer(open(save, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c1= csv.writer(open(save+name1+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c2= csv.writer(open(save+name2+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c3= csv.writer(open(save+name3+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c4= csv.writer(open(save+name4+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c5= csv.writer(open(save+name5+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c6= csv.writer(open(save+name6+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c7= csv.writer(open(save+name7+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c8= csv.writer(open(save+name8+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c9= csv.writer(open(save+name9+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c10= csv.writer(open(save+name10+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            c11= csv.writer(open(save+name11+fileForm, "wb"),  delimiter=',' , lineterminator="\n")#, sys.stdout, lineterminator='\n') #lineterminator='\n' OR , delimiter=','
            

            #c.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c1.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c2.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c3.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c4.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c5.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c6.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c7.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c8.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c9.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c10.writerow(['Value','Longitude', 'Latitude', 'CoordString'])
            c11.writerow(['Value','Longitude', 'Latitude', 'CoordString'])


            # get georeference info
            transform = ds.GetGeoTransform()
            xOrigin = transform[0]+(transform[1]/2)#we do /2 to get the center of the cell
            yOrigin = transform[3]+(transform[5]/2)
            pixelWidth = transform[1]
            pixelHeight = transform[5]

            xValues =[]
            yValues =[]
            valueCell =[]
            xxValues = []
            yyValues = []
	    string = []

            #coordinates to get pixel values for
            for x in np.arange ((xOrigin),(Lonmin), pixelWidth):#CHANGE TO xOrigin
                for y in np.arange ((yOrigin) ,(Latmin), pixelHeight) : #CHANGE TO yOrigin
                    xValues.extend([x])
                    yValues.extend([y])

            # get image size
            rows = ds.RasterYSize
            cols = ds.RasterXSize
            bands = ds.RasterCount

            # loop through the coordinates
            for i in range(len(xValues)): #len(xValues)
                # get x,y
                x = xValues[i]
                y = yValues[i]
		xy = str(str(round(x,4))+(",")+str(round(y,4)))
                # compute pixel offset
                xOffset = int((x - xOrigin) / pixelWidth)
                yOffset = int((y - yOrigin) / pixelHeight)
                #create a string to print out
                s = str(x) + ' ' + str(y) + ' ' + str(xOffset) + ' ' + str(yOffset) + ' '
                for j in range(bands):
                    band = ds.GetRasterBand(1) # 1-based index
                    #read data and add the value to the string
                    data = ds.ReadAsArray(xOffset, yOffset, 1, 1)
                    if (data is not None ):
                        value = data[0,0]
                        #if (value != [0.0]) :
                        valueCell.extend([value])
                        xxValues.extend([x])
                        yyValues.extend([y])
			string.extend([xy])
                        #value = data[0,0]
                        #s = str(value)

            #for t in range(len(valueCell)):
                #c.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                #print (valueCell[t], xxValues[t], yyValues[t])
            for t in range(len(valueCell)):
                if (t>=1)&(t<=1000000):
                    c1.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>1000000)&(t<=2000000):
                    c2.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>2000000)&(t<=3000000):
                    c3.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>3000000)&(t<=4000000):
                    c4.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>4000000)&(t<=5000000):
                    c5.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>5000000)&(t<=6000000):
                    c6.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>6000000)&(t<=7000000):
                    c7.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>7000000)&(t<=8000000):
                    c8.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>8000000)&(t<=9000000):
                    c9.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                elif (t>9000000)&(t<=10000000):
                    c10.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                else:
                    c11.writerow([valueCell[t], xxValues[t], yyValues[t], string[t]])
                    
            #figure out how long the script took to run
            endTime = time.time()
            endTimeSec = (endTime - startTime)
            endTimeMin = (endTime - startTime) / 60
            print 'The script took ' + str(endTime - startTime) + ' seconds'

            QMessageBox.information(self.iface.mainWindow(),"Raster data","%s in (%d min) or (%d sec)" %('Done', endTimeMin, endTimeSec))



            
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

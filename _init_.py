# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RasterData02
                                 A QGIS plugin
 Store in a csv all cell values, coordinates and coordinates as string
                             -------------------
        begin                : 2014-10-02
        copyright            : (C) 2014 by Kassiani
        email                : 
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RasterData02 class from file RasterData02.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Raster_Data02 import RasterData02
    return RasterData02(iface)

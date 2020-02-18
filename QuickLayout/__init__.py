# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickLayout
                                 A QGIS plugin
 This plugin enables to make a quick layout.
                             -------------------
        begin                : 2016-09-08
        copyright            : (C) 2016 by kr
        email                : kra@giap.pl
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
    """Load QuickLayout class from file QuickLayout.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .quick_layout import QuickLayout
    return QuickLayout(iface)

#-------------------------------------------------------------------------------
# Copyright (c) 2013 Gael Honorez.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that i will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui
import util

class PlanetaryReinforcementDelegate(QtGui.QStyledItemDelegate):
    
    def __init__(self, *args, **kwargs):
        QtGui.QStyledItemDelegate.__init__(self, *args, **kwargs)
        
    def paint(self, painter, option, index, *args, **kwargs):
        self.initStyleOption(option, index)       
        painter.save()
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        
        icon = QtGui.QIcon(option.icon)
        iconsize = icon.actualSize(option.rect.size())
        #clear icon and text before letting the control draw itself because we're rendering these parts ourselves
        option.icon = QtGui.QIcon()        
        option.text = ""  
        option.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)
        
        if index.model().flags(index) == QtCore.Qt.NoItemFlags:
            icon.paint(painter, option.rect.adjusted(5-2, -2, 0, 0), QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, mode=1)
        else :
            icon.paint(painter, option.rect.adjusted(5-2, -2, 0, 0), QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        #Description
        painter.translate(option.rect.left() + iconsize.width() + 10, option.rect.top())
        clip = QtCore.QRectF(0, 0, option.rect.width()-iconsize.width() - 10 - 5, option.rect.height())
        html.drawContents(painter, clip)
        painter.restore()
        

    def sizeHint(self, option, index, *args, **kwargs):
        self.initStyleOption(option, index)        
        html = QtGui.QTextDocument()
        html.setHtml(option.text)
        html.setTextWidth(PlanetaryItem.TEXTWIDTH)
        return QtCore.QSize(PlanetaryItem.ICONSIZE + PlanetaryItem.TEXTWIDTH + PlanetaryItem.PADDING, PlanetaryItem.ICONSIZE)  

class PlanetaryItem(QtGui.QListWidgetItem):
    TEXTWIDTH = 370
    ICONSIZE = 64
    PADDING = 10
    WIDTH = ICONSIZE + TEXTWIDTH

    FORMATTER_REINFORCEMENT       = unicode(util.readfile("galacticwar/formatters/planetarydefenses.qthtml"))   
    
    def __init__(self, uid, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)
        self.uid            = uid
        self.structure      = None
        self.price          = None
        self.activation     = None
        self.description    = None

        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled)

        self.setHidden(True)
    

    def data(self, role):
        if role == QtCore.Qt.UserRole :
            return self.uid
        return super(PlanetaryItem, self).data(role) 
    
    def setEnabled(self):
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled)
        self.setText(self.FORMATTER_REINFORCEMENT.format(color="black", description = self.description, activation=self.activation, price=self.price))

    def setDisabled(self):
        self.setFlags(QtCore.Qt.NoItemFlags)
        self.setText(self.FORMATTER_REINFORCEMENT.format(color="grey", description = self.description, activation=self.activation, price=self.price))
        
    def update(self, message, client):
        '''update this item'''
        self.client = client

        self.structure      = message['structure']
        self.price          = message['price']
        self.activation     = "%0.1f" % (message['activation']/60.0)
        self.description    = message["description"]

        iconName = "%s_icon.png" % self.structure
        icon = util.iconUnit(iconName)
        self.setIcon(icon)
        self.setHidden(False)
        
        self.setText(self.FORMATTER_REINFORCEMENT.format(color="black", description = self.description, activation=self.activation, price=self.price))
        
    def __ge__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return not self.__lt__(other)
    
    
    def __lt__(self, other):
        ''' Comparison operator used for item list sorting '''        
        return self.price < other.price
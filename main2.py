global cajasApiladas
cajasApiladas=0

# Model design
import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.batchrunner import BatchRunner
from mesa.datacollection \
    import DataCollector
from mesa.space import Grid
import numpy as np
import math

# Visualization
import matplotlib.pyplot as plt 
import IPython
from random import choice
from IPython.display import HTML

def funcionVacia():
    return True

def llenarTupla(cCajas):
    estantes= math.ceil(cCajas/5)
    contador=0
    tupla=[]
    while(contador!=estantes):
        tupla.append((0,contador))
        contador=contador+1
    return tupla

class agenteCaja(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def setupParameters(self, coordenada):
        self.coordenadaX = coordenada[0]
        self.coordenadaY = coordenada[1]
        self.estado=True

class agentePila(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    def setupParameters(self, coordenada):
        self.coordenadaX = coordenada[0]
        self.coordenadaY = coordenada[1]
        self.limite = 5
        self.contador = 0

    def appendCaja(self):
        if (self.contador!=self.limite):
            self.contador = self.contador+1
            #print(self, self.contador)
            return True
        else:
            return False

class agenteRobot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def setupParameters(self, coordenada):
        self.coordenadaX = coordenada[0]
        self.coordenadaY = coordenada[1]
        self.carga = False
        self.origen = False
        self.caja= None
        self.movimientos=0
    
    def moveOrigen(self):
        if(self.coordenadaX!=0):
            self.moveBy(-1,0)
        elif(self.coordenadaY!=1):
            self.moveBy(0,-1)
    
    def buscarCerca(self):
        agentes= self.model.grid.get_neighbors((self.coordenadaX, self.coordenadaY), True)
        for i in agentes:
            if(str(type(i))=="<class '_main_.agenteCaja'>" and i.estado):
                #SOLO FALTA HACER QUE SE MUEVA A DONDE QUEDE LA CAJA
                #i.estado=False
                #self.carga=True
                #print(self," ",self.coordenadaX, self.coordenadaY)
                #print(i, " ",i.coordenadaX, self.coordenadaY)
                return True
        return False
    
    def agarraCaja(self):
        agentes= self.model.grid.iter_neighbors()
        for i in agentes:
            if(str(type(i))=="<class '_main_.agenteCaja'>"):
                if(i.estado):
                    i.estado=False
                    self.carga=True
                    self.caja=i
                    break
                
    def moverRandom(self):
        global ANCHO
        global LARGO
        movimiento=[0,1,-1]
        primerMovimiento=random.choice(movimiento)
        segundoMovimiento=random.choice(movimiento)
        #print(primerMovimiento, segundoMovimiento)
        if (primerMovimiento==0 and segundoMovimiento==0):
            primerMovimeinto=1
        if (self.coordenadaX<=0):
            primerMovimiento=1
        if (self.coordenadaX>=LARGO):
            primerMovimiento=-1
        if (self.coordenadaY>=ANCHO):
            segundoMovimiento=-1
        if (self.coordenadaY<=0):
            segundoMovimiento=1
        self.moveBy(primerMovimiento, segundoMovimiento)
        
    def moveBy(self, nuevaCoordenadaX, nuevaCoordenadaY):
        self.coordenadaX = self.coordenadaX + nuevaCoordenadaX
        self.coordenadaY = self.coordenadaY + nuevaCoordenadaY
        #print(self, self.coordenadaX, self.coordenadaY)
        self.model.grid.move_agent(self, (nuevaCoordenadaX,nuevaCoordenadaY))
        self.movimientos=self.movimientos+1
        
    def preguntarEstante(self):
        agentes=self.model.grid.neighbors(self, distance=1)
        for i in agentes:
            if(str(type(i))=="<class '_main_.agentePila'>"):
                if(i.contador!=5):
                    print(" ")
                    print("Apildada en pila:",self.caja, "con posicion inicial: (", self.caja.coordenadaX, self.caja.coordenadaY,")")
                    i.appendCaja()
                    caja=self.caja
                    
                    caja.model.grid.move_agent(caja, (i.coordenadaX, i.coordenadaY))
                    return True
        return False

class modeloAlmacen(Model):

    def __init__(self, width, height, agentsCaja, agentsRobot):
        # Called at the start of the simulation
        global ANCHO
        global LARGO
        ANCHO = width
        LARGO = height
        self.grid = Grid(ANCHO, LARGO , True)
        
        cantidadEstantes=math.ceil(agentsCaja/5)

        self.running = True
        self.num_Estantes = cantidadEstantes
        self.schedule = RandomActivation(self)
        
        posicionesEstantes=llenarTupla(agentsCaja)

        global arrayPila
        global arrayCaja
        global arrayRobot
        global arrayRobotPos
        arrayPila = []
        arrayCaja = []
        arrayRobot = []
        arrayRobotPos = []
        for i in range(self.num_Estantes):
            a = agentePila(i, self)
            self.schedule.add(a)
            self.grid.place_agent(a, posicionesEstantes[i])
            a.setupParameters(posicionesEstantes[i])
            arrayPila.append(a)
        
        self.num_Cajas = agentsCaja
        
        for j in range(self.num_Estantes, self.num_Cajas+self.num_Estantes):
            a = agenteCaja(j, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            posicion2 = (x,y)
            self.grid.place_agent(a, posicion2)
            arrayCaja.append(a)
            a.setupParameters(posicion2)
            
        self.num_Robots = agentsRobot

        for k in range(self.num_Estantes+self.num_Cajas, self.num_Robots+self.num_Estantes+self.num_Cajas):
            a = agenteRobot(k, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            posicion3 = (x,y)
            self.grid.place_agent(a,posicion3)
            arrayRobot.append(a)
            a.setupParameters(posicion3)


    def step(self):
        global cajasApiladas

        for i in arrayRobot:
            if(i.carga):
                if(((arrayRobotPos[i][0]==0 or arrayRobotPos[i][0]==1) and (arrayRobotPos[i][1]==0 or arrayRobotPos[i][1]==1)) or i.origen==True):
                    i.origen=True
                    if(i.preguntarEstante()):
                        #print("La dejo")
                        i.caja=None
                        i.carga=False
                        i.origen=False
                        cajasApiladas=cajasApiladas+1
                        print(" ")
                        print("CAJAS APILADAS HASTA EL MOMENTO", cajasApiladas)
                        if(cajasApiladas == self.num_Cajas):
                            self.stop()
                    else:
                        i.moveBy(0,1)
                else:
                    i.moveOrigen()
            else:
                if(i.buscarCerca()):
                    i.agarraCaja()
                    #print("La agarro")
                else:
                    i.moverRandom()
        
        self.schedule.step()
        

model = modeloAlmacen(9,10,20,5)
for i in range(50):
    model.step()

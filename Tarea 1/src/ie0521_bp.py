import numpy as np
import math

class ie0521_bp:
    def __init__(self, bits_PC=11, bits_LH=8):
        self.bits_PC = bits_PC
        self.bits_LH = bits_LH
        
        # Historia Local como un registro desplazante de strings
        self.LH_reg = ""
        for _ in range(bits_LH):
            self.LH_reg += "0"
        
        # Tabla de PC
        self.table_PC = [self.LH_reg for _ in range(2**bits_PC)]
        
        # Matriz de perceptrones
        self.perceptron_table = np.zeros((2**bits_LH, bits_LH+1))
        
        # Información necesaria para los perceptrones
        self.umbral = math.floor(1.93*bits_LH + 14)
        self.pred = 0
        self.x0 = 1
        
        # Cálculo de presupuesto:
        self.presupuesto = (self.bits_LH * 2**self.bits_PC) + (7 * 2**self.bits_LH * (self.bits_LH +1))
        
        self.total_predictions = 0
        self.total_taken_pred_taken = 0
        self.total_taken_pred_not_taken = 0
        self.total_not_taken_pred_taken = 0
        self.total_not_taken_pred_not_taken = 0
        

    def print_info(self):
        print("Parámetros del predictor:")
        print("\tTipo de predictor:\t\t\t Perceptron-Shared")
        print("\tEntradas en la Tabla PC:\t\t\t"+str(2**self.bits_PC))
        print("\tTamaño de los registros de historia global:\t"+str(self.bits_LH))
        print("\tPresupuesto total:\t\t\t\t" + str(self.presupuesto))

    def print_stats(self):
        print("Resultados de la simulación")
        print("\t# branches:\t\t\t\t\t\t"+str(self.total_predictions))
        print("\t# branches tomados predichos correctamente:\t\t"+str(self.total_taken_pred_taken))
        print("\t# branches tomados predichos incorrectamente:\t\t"+str(self.total_taken_pred_not_taken))
        print("\t# branches no tomados predichos correctamente:\t\t"+str(self.total_not_taken_pred_not_taken))
        print("\t# branches no tomados predichos incorrectamente:\t"+str(self.total_not_taken_pred_taken))
        perc_correct = 100*(self.total_taken_pred_taken+self.total_not_taken_pred_not_taken)/self.total_predictions
        formatted_perc = "{:.3f}".format(perc_correct)
        print("\t% predicciones correctas:\t\t\t\t"+str(formatted_perc)+"%")

    def predict(self, PC):
        pc_index = int(PC) % 2**self.bits_PC
        perceptron_index = int(self.table_PC[pc_index], 2)
        self.pred = self.perceptron_table[perceptron_index][0] # w0
        
        for i in range(1, self.bits_LH+1):
            self.pred += self.perceptron_table[perceptron_index][i] * self.reg(self.table_PC[pc_index][-i])

        if self.pred >= 0:
            return "T"
        else:
            return "N"
        
    def update(self, PC, result, prediction):
        pc_index = int(PC) % 2**self.bits_PC
        perceptron_index = int(self.table_PC[pc_index], 2)
        
        # Creo la variable t
        if result == "T":
            t = 1
        else:
            t = -1
        
        # Actualizo los pesos con 7 bits CON signo
        if np.sign(self.pred) != t or abs(self.pred) <= self.umbral:
            # Actualizo w_0
            self.perceptron_table[perceptron_index][0] += t*self.x0
            if self.perceptron_table[perceptron_index][0] >= 63:
                self.perceptron_table[perceptron_index][0] = 63
            elif self.perceptron_table[perceptron_index][0] <= -64:
                self.perceptron_table[perceptron_index][0] = -64
            
            # Actualizo w_i
            for i in range(1, self.bits_LH+1):
                self.perceptron_table[perceptron_index][i] += t*self.reg(self.table_PC[pc_index][-i])
                if self.perceptron_table[perceptron_index][i] >= 63:
                    self.perceptron_table[perceptron_index][i] = 63
                elif self.perceptron_table[perceptron_index][i] <= -64:
                    self.perceptron_table[perceptron_index][i] = -64

        # Actualizo los registros desplazantes de la tabla PC
        if result == "T":
            entry_reg = self.table_PC[pc_index]
            entry_reg = entry_reg[-self.bits_LH+1:] + "1"
            self.table_PC[pc_index] = entry_reg
        else:
            entry_reg = self.table_PC[pc_index]
            entry_reg = entry_reg[-self.bits_LH+1:] + "0"
            self.table_PC[pc_index] = entry_reg
        
        # Actualizo los stats
        if result == "T" and result == prediction:
            self.total_taken_pred_taken += 1
        elif result == "T" and result != prediction:
            self.total_taken_pred_not_taken += 1
        elif result == "N" and result == prediction:
            self.total_not_taken_pred_not_taken += 1
        else:
            self.total_not_taken_pred_taken += 1
            
        self.total_predictions += 1
    
    '''Esta función recibe como parámetros un string que toma desde el registro desplazante
    de historia local (que contiene únicamente 1s y 0s y los devuelve como enteros: 1 si se
    toma un "1" y -1 si se toma un "0")'''
    def reg(self, bit):
        if bit == "1":
            return 1
        elif bit == "0":
            return -1

import pysofaconventions as sofa
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.fft import fft, ifft, fftfreq, irfft
from netCDF4 import Dataset
import time
import os

class min_phase_converter:


    def __init__(self, SOFA_filepath):
        self.SOFA_filepath = SOFA_filepath
        self.HRIR_SOFA_file = sofa.SOFAFile(self.SOFA_filepath, 'r')

        self.HRIR_positions = self.HRIR_SOFA_file.getVariableValue('SourcePosition')
        self.HRIR_data = self.HRIR_SOFA_file.getDataIR()


        self.min_phase_HRIR_data = np.zeros(self.HRIR_data.shape)
        #print('temp shape: ', self.min_phase_HRIR_data.shape)




    def convert_HRIR(self):
        number_of_measurements = self.min_phase_HRIR_data.shape[0]
        HRIR_length = self.min_phase_HRIR_data.shape[2]
        print('number of measurements: ', number_of_measurements)
        print('len of HRIR: ', HRIR_length)


        for index in range(0, number_of_measurements):
            self.min_phase_HRIR_data[index][0] = self.min_phase_conversion(self.HRIR_data[index][0], HRIR_length, index)
            self.min_phase_HRIR_data[index][1] = self.min_phase_conversion(self.HRIR_data[index][1], HRIR_length, index)

        '''
        print('position: ', self.HRIR_positions[155])
        plt.figure()
        plt.plot(self.min_phase_HRIR_data[155][0], label="left", linewidth=0.5, marker='o', markersize=1)
        plt.plot(self.min_phase_HRIR_data[155][1], label="right", linewidth=0.5, marker='o', markersize=1)
        plt.grid()
        plt.legend()
        plt.show()
        '''

        '''
        print('printing positions: ', self.HRIR_positions.shape)
        print('printing data: ', self.HRIR_data.shape)

        print('printing positions: ', self.HRIR_positions)
        print('printing data: ', self.HRIR_data.shape)
        '''
        self.write_SOFA_file()






    def min_phase_conversion(self,HRIR, HRIR_length, index):
        '''

        :param HRIR: the desired HRIR impulse response to convert into minimum phase
        :return: the minimum phase version of the original HRIR
        '''

        HRIR_fft = fft(HRIR, 44100)

        #Check here the damned exception
        try:
            minimum_phase = np.imag(-hilbert(np.log(np.abs(HRIR_fft))))
        except:
            print('error log zero \n')
            print('Printing HRIR spectrum: \n')
            print(HRIR_fft)

        min_phase_HRIR = irfft(np.abs(HRIR_fft) * np.exp(1j * minimum_phase), 44100)  # |H(w)|*e^(jPhi(w))
        min_phase_HRIR = min_phase_HRIR[0:HRIR_length]

        return min_phase_HRIR


    def write_SOFA_file(self):
        '''
        This methods uses the computed minimum phase HRIRs and saves them into a SOFA format file.

        :return: nothing
        '''

        filename_min_phase = self.HRIR_SOFA_file.getGlobalAttributeValue('DatabaseName') + '_min_phase.sofa'
        print('printing filename: ', filename_min_phase)
        filePath  = '../../HRTF_data/' + filename_min_phase

        rootgrp = Dataset(filePath, 'w', format='NETCDF4')

        attributes = self.HRIR_SOFA_file.getGlobalAttributesAsDict()
        print('printing attributes: ', attributes)

        # ----------Required Attributes----------#

        rootgrp.Conventions = attributes["Conventions"]
        rootgrp.Version = attributes["Version"]
        rootgrp.SOFAConventions = attributes["SOFAConventions"]
        rootgrp.SOFAConventionsVersion = attributes["SOFAConventionsVersion"]
        rootgrp.APIName = attributes["APIName"]
        rootgrp.APIVersion = attributes["APIVersion"]
        rootgrp.AuthorContact = attributes["AuthorContact"]
        rootgrp.Organization = attributes["Organization"]
        rootgrp.License = attributes["License"]
        rootgrp.DataType = attributes["DataType"]
        rootgrp.RoomType = attributes["RoomType"]
        rootgrp.DateCreated = attributes["DateCreated"]
        rootgrp.DateModified = attributes["DateModified"]
        rootgrp.Title = attributes["Title"]
        rootgrp.DatabaseName = attributes["DatabaseName"]
        rootgrp.ListenerShortName = attributes["ListenerShortName"]

        # ----------Required Dimensions----------#

        dimensions = self.HRIR_SOFA_file.getDimensionsAsDict()
        print('dimensions: ', dimensions)


        m = dimensions['M'].size
        n = dimensions['N'].size
        r = dimensions['R'].size
        e = dimensions['E'].size
        i = dimensions['I'].size  # I and C are default ones. Their value is constant and fixed
        c = dimensions['C'].size  # same as above https://www.sofaconventions.org/mediawiki/index.php/SOFA_conventions#AnchorDimensions
        rootgrp.createDimension('M', m)
        rootgrp.createDimension('N', n)
        rootgrp.createDimension('E', e)
        rootgrp.createDimension('R', r)
        rootgrp.createDimension('I', i)
        rootgrp.createDimension('C', c)

        # ----------Required Variables----------#


        #--------- Listener Variables ---------#
        listenerPositionVar = rootgrp.createVariable('ListenerPosition', 'f8', ('I', 'C'))
        listenerPosUnits, listenerPosType = self.HRIR_SOFA_file.getListenerPositionInfo()
        listenerPos = self.HRIR_SOFA_file.getListenerPositionValues()

        listenerPositionVar.Units = listenerPosUnits
        listenerPositionVar.Type = listenerPosType
        listenerPositionVar[:] = listenerPos

        if self.HRIR_SOFA_file.hasListenerUp():
            listenerUpVar = rootgrp.createVariable('ListenerUp', 'f8', ('I', 'C'))
            listenerUpUnits, listenerUpType = self.HRIR_SOFA_file.getListenerUpInfo()
            listenerUp = self.HRIR_SOFA_file.getListenerUpValues()

            if listenerUpType is not None:
                listenerUpVar.Type = listenerUpType
            if listenerUpUnits is not None:
                listenerUpVar.Units = listenerUpUnits

            listenerUpVar[:] = listenerUp

        if self.HRIR_SOFA_file.hasListenerView():
            listenerViewVar = rootgrp.createVariable('ListenerView', 'f8', ('I', 'C'))
            listenerViewUnits, listenerViewType = self.HRIR_SOFA_file.getListenerViewInfo()
            listenerView = self.HRIR_SOFA_file.getListenerViewValues()
            if listenerViewType is not None:
                listenerViewVar.Type = listenerViewType
            if listenerViewUnits is not None:
                listenerViewVar.Units = listenerViewUnits
            listenerViewVar[:] = listenerView


        #------ Emitter ------#
        emitterPositionVar = rootgrp.createVariable('EmitterPosition', 'f8', ('E', 'C', 'I'))
        emitterPosUnits, emitterPosType = self.HRIR_SOFA_file.getEmitterPositionInfo()
        emitterPos = self.HRIR_SOFA_file.getEmitterPositionValues()

        emitterPositionVar.Units = emitterPosUnits
        emitterPositionVar.Type = emitterPosType
        emitterPositionVar[:] = emitterPos


        #-------- Source ------#
        sourcePositionVar = rootgrp.createVariable('SourcePosition', 'f8', ('M', 'C'))
        sourcePosUnits, sourcePosType = self.HRIR_SOFA_file.getSourcePositionInfo()
        sourcePos = self.HRIR_SOFA_file.getSourcePositionValues()
        print('printing source positions: ', sourcePos)
        sourcePositionVar.Units = sourcePosUnits
        sourcePositionVar.Type = sourcePosType
        sourcePositionVar[:] = sourcePos


        if self.HRIR_SOFA_file.hasSourceUp():
            sourceUpVar = rootgrp.createVariable('SourceUp', 'f8', ('I', 'C'))
            sourceUpUnits, sourceUpType = self.HRIR_SOFA_file.getSourceUpInfo()
            sourceUp = self.HRIR_SOFA_file.getSourceUpValues()

            sourceUpVar.Units = sourceUpUnits
            sourceUpVar.Type = sourceUpType
            sourceUpVar[:] = sourceUp


        if self.HRIR_SOFA_file.hasSourceView():
            sourceViewVar = rootgrp.createVariable('SourceView', 'f8', ('I', 'C'))
            sourceViewUnits, sourceViewType= self.HRIR_SOFA_file.getSourceViewInfo()
            sourceView = self.HRIR_SOFA_file.getSourceViewValues()

            sourceViewVar.Units = sourceViewUnits
            sourceViewVar.Type = sourceViewType
            sourceViewVar[:] = sourceView


        #------- Receiver -------#

        receiverPositionVar = rootgrp.createVariable('ReceiverPosition', 'f8', ('R', 'C', 'I'))
        receiverPosUnits, receiverPosType = self.HRIR_SOFA_file.getReceiverPositionInfo()
        receiverPos = self.HRIR_SOFA_file.getReceiverPositionValues()

        receiverPositionVar.Units = receiverPosUnits
        receiverPositionVar.Type = receiverPosType
        receiverPositionVar[:] = receiverPos



        samplingRateVar = rootgrp.createVariable('Data.SamplingRate', 'f8', ('I'))
        samplingRateVar.Units = self.HRIR_SOFA_file.getSamplingRateUnits()
        samplingRateVar[:] = self.HRIR_SOFA_file.getSamplingRate()

        delayVar = rootgrp.createVariable('Data.Delay', 'f8', ('I', 'R'))
        delay = self.HRIR_SOFA_file.getDataDelay()
        delayVar[:, :] = delay

        dataIRVar = rootgrp.createVariable('Data.IR', 'f8', ('M', 'R', 'N'))
        channelOrdering = self.HRIR_SOFA_file.getDataIRChannelOrdering()
        dataNormalization = self.HRIR_SOFA_file.getDataIRNormalization()

        if channelOrdering is not None:
            dataIRVar.ChannelOrdering = channelOrdering
        if dataNormalization is not None:
            dataIRVar.Normalization = dataNormalization

        dataIRVar[:] = self.min_phase_HRIR_data

        # ----------Close it----------#

        rootgrp.close()




























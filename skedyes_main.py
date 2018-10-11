import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL
from skqtui import Ui_SkedYes
from stbcom import TestCommnad, SkedTelnet, buildCommandList, command_list
# telnet program example
import socket, select, string, threading, time
from threading import Thread, Lock
import xml.etree.ElementTree as ET
#from sklearn import tree
import re
import signal
from Queue import Queue


hddmutex = Lock()


exitFlag = 0
hddtestCnt =0
hddtestFlag = 0

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

def getHDDTestFlag():
    hddmutex.acquire()
    value =  hddtestFlag
    hddmutex.release()
    return value

def setHDDTestFlag(value):
    global hddtestFlag
    hddmutex.acquire()
    hddtestFlag = value
    hddmutex.release()

def ptc_num_to_ui_options(uioption):
    return {
        0: "updateClock",
        1: "updateTemp",
        2: "updateHDDSerialNumber",
        3: "updateSoftwareVersion",
        4: "updateEthMacAddr",
        5: "updateWifiMacAddr",
        6: "updateTelnetEditor"
    }. get(uioption,"default")

def ptc_ui_to_num_options(uioption):
    return {
        "updateClock" : 0,
        "updateTemp" : 1,
        "updateHDDSerialNumber" : 2,
        "updateSoftwareVersion" : 3,
        "updateEthMacAddr" : 4,
        "updateWifiMacAddr" : 5,
        "updateTelnetEditor" : 6
    }. get("default", 99)

class getPTCThread(QThread):
    def __init__(self,msgQ ,telnetcli, option,value, msg ):
        QThread.__init__(self)
        self.msgQ = msgQ
        self.option = option
        self.value  = value
        self.msg = msg
        self.telnetcli = telnetcli

    def __del__(self):
        self.wait()

    def ptc_update_msg(self,option,value, msg):
        self.emit(SIGNAL("uiUpdateProcess(QString,QString,QString)"),option,value, msg)

    def run(self):
        while self.runThread:
            msg = self.msgQ.get()
            print " %s " % msg
            if(msg == "startTunerTest"):
                ret = stbPerformTunerTest(self,self.telnetcli)
                if(ret > 0):
                    print "Tuner Test Passed"
                    self.ptc_update_msg("updateTunerTestResult","PASS",'')
                else:
                    print "Tuner Test Failed"
                    self.ptc_update_msg("updateTunerTestResult","FAIL",'')
            elif (msg == "stopTunerTest"):
                    stbStopTunerTest(self,self.telnetcli)
            elif(msg == "startHddTest"):
                ret = stbPerformHddTest(self,self.telnetcli)
                if(ret > 0):
                    print "HDD Test Passed"
                    self.ptc_update_msg("updateHddTestResult","PASS",'')
                else:
                    print "HDD Test Failed"
                    self.ptc_update_msg("updateHddTestResult","FAIL",'')
            elif (msg == "startUsbTest"):
                ret = stbPerformUsbTest(self,self.telnetcli)
                if(ret > 0):
                    print "USB Test Passed"
                    self.ptc_update_msg("updateUsbTestResult","PASS",'')
                else:
                    print "USB Test Failed"
                    self.ptc_update_msg("updateUsbTestResult","FAIL",'')
            elif (msg == "stopUsbTest"):
                print "stopUsbTest"
                stbStopUsbTest(self,self.telnetcli)
            elif (msg == "startSmartcardTest"):
                ret = stbPerformSmartcardTest(self,self.telnetcli)
                if(ret > 0):
                    print "Smartcard Test Passed"
                    self.ptc_update_msg("updateSmartcardTestResult","PASS",'')
                else:
                    print "Smartcard Test Failed"
                    self.ptc_update_msg("updateSmartcardTestResult","FAIL",'')
            elif  (msg == "stopSmartcardTest"):
                 print "stopSmartcardTest"
                 stbStopSmartcardTest(self,self.telnetcli)
            elif (msg == "startFanTest"):
                ret = stbPerformFanTest(self,self.telnetcli)
                if(ret > 0):
                    print "Fan Test Passed"
                    self.ptc_update_msg("updateFanTestResult","PASS",'')
                else:
                    print "Fan Test Failed"
                    self.ptc_update_msg("updateFanTestResult","FAIL",'')
            elif  (msg == "stopFanTest"):
                 print "stopFanTest"
                 stbStopFanTest(self,self.telnetcli)
            elif (msg == "startLedTest"):
                ret = stbPerformLedTest(self,self.telnetcli)
                if(ret > 0):
                    print "Led Test Passed"
                    self.ptc_update_msg("updateLedTestResult","PASS",'')
                else:
                    print "Led Test Failed"
                    self.ptc_update_msg("updateLedTestResult","FAIL",'')
            elif  (msg == "stopLedTest"):
                 print "stopLedTest"
                 stbStopLedTest(self,self.telnetcli)
            elif (msg == "startFpTest"):
                ret = stbPerformFpTest(self,self.telnetcli)
                if(ret > 0):
                    print "Fp Test Passed"
                    self.ptc_update_msg("updateFpTestResult","PASS",'')
                else:
                    print "Fp Test Failed"
                    self.ptc_update_msg("updateFpTestResult","FAIL",'')
            elif  (msg == "stopFpTest"):
                print "stopFpTest"
                stbStopFpTest(self,self.telnetcli)
            elif (msg == "startButtonTest"):
                ret = stbPerformButtonTest(self,self.telnetcli)
                if(ret > 0):
                    print "Button Test Passed"
                    self.ptc_update_msg("updateButtonTestResult","PASS",'')
                else:
                    print "Button Test Failed"
                    self.ptc_update_msg("updateButtonTestResult","FAIL",'')
            elif  (msg == "stopButtonTest"):
                print "stopButtonTest"
                stbStopButtonTest(self,self.telnetcli)

            elif (msg == "startIrTest"):
                ret = stbPerformIrTest(self,self.telnetcli)
                if(ret > 0):
                    print "IR Test Passed"
                    self.ptc_update_msg("updateIrTestResult","PASS",'')
                else:
                    print "IR Test Failed"
                    self.ptc_update_msg("updateIrTestResult","FAIL",'')
            elif  (msg == "stopIrTest"):
                print "stopIrTest"
                stbStopIrTest(self,self.telnetcli)

            elif (msg == "startHdcpKeyProgram"):

                ret = stbPerformHdcpKeyProgramming(self,self.telnetcli)
                if(ret > 0):
                    print "HDCP Key Program Passed"
                    self.ptc_update_msg("updateHdcpKeyResult","PASS",'')
                else:
                    print "HDCP Key Program Failed"
                    self.ptc_update_msg("updateHdcpKeyResult","FAIL",'')
            elif  (msg == "startUiUpgrade"):
                print "startUiUpgrade"
                ret = stbPerformUiUpgrade(self,self.telnetcli)
                if(ret > 0):
                    print "UI Upgrade passed"
                    self.ptc_update_msg("updateUiUpgradeResult","PASS",'')
                else:
                    print "IR Test Failed"
                    self.ptc_update_msg("updateUiUpgradeResult","FAIL",'')
            elif  (msg == "startLnbTest"):
                print "startLnbTest"
                ret = stbPerformLnbTest(self,self.telnetcli)
                if(ret > 0):
                    print "LNB Test passed"
                    self.ptc_update_msg("updateLnbTestResult","PASS",'')
                else:
                    print "LNB Test Failed"
                    self.ptc_update_msg("updateLnbTestResult","FAIL",'')

            #print " %s" % ( time.ctime(time.time()))
            #timenow = '%s' % (time.ctime(time.time()))
            #self.ptc_update_msg("updateClock",timenow,"")
            self.sleep(1)
            self.msgQ.task_done()

    def startThread(self):
        self.runThread = 1
    def stopThread(self):
        self.runThread = 0
    def ptc_update_systemInfo(self):
        stbSoftwareVer = stbGetSoftwareVersion(self, self.telnetcli)
        self.ptc_update_msg("updateSoftwareVersion",stbSoftwareVer,"")
        macadd = stbGetMacAddress(self, self.telnetcli)
        ethMac = "%s" % macadd[0]
        wifiMac = "%s" % macadd[1]
        print ethMac
        print wifiMac
        self.ptc_update_msg("updateEthMacAddr",ethMac,"")
        self.ptc_update_msg("updateWifiMacAddr",wifiMac,"")
        self.ptc_update_msg("updateModelName","OEMS-1802","")
        temp = stbGetTemperature(self,self.telnetcli)
        self.ptc_update_msg("updateTemp",temp,"")


class SkedYesUI(QtGui.QMainWindow):
    def __init__(self, parent= None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_SkedYes()
        self.ui.setupUi(self)
        self.ui.connectToStbButton.clicked.connect(self.connectTheSTB)
        self.ui.disconnectButton.clicked.connect(self.disconectTheSTB)
        self.msgQ = Queue()
        self.ui.disconnectButton.setEnabled(False)
        self.ui.tunerStopButton.setEnabled(False)
        self.ui.hddStopButton.setEnabled(False)
        self.ui.usbStopButton.setEnabled(False)
        self.ui.smartcardStopButton.setEnabled(False)
        self.ui.fanStopButton.setEnabled(False)
        self.ui.ledStopButton.setEnabled(False)
        self.ui.fpStopButton.setEnabled(False)
        self.ui.irStopButton.setEnabled(False)
        self.ui.buttonStopButton.setEnabled(False)
        self.ui.lnbStopButton.setEnabled(False)
        self.ui.tunerResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.hddResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.usbResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.smartcardResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.fanResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.ledResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.fpResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.irResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.buttonResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.hdcpKeyResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.uiUpgradeResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.lnbResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");


    def disconectTheSTB(self):
        self.telnetcli.telWrite('\x03') #ctrl + c
        time.sleep(1)
        #self.telnetcli.telWrite("exit") #Exit
        self.telnetcli.telExit() # close the telenet connection
        self.ptcHandlingThread.stopThread()
        self.ui.connectToStbButton.setEnabled(True)
        self.ui.disconnectButton.setEnabled(False)
        self.tunerTestOptionUpdate()
        self.updateConnectionStatus("Not Connected ")
        self.resetValues()


    def resetValues(self):
        self.ui.disconnectButton.setEnabled(False)
        self.ui.tunerStopButton.setEnabled(False)
        self.ui.lnbStopButton.setEnabled(False)
        self.ui.hddStopButton.setEnabled(False)
        self.ui.usbStopButton.setEnabled(False)
        self.ui.smartcardStopButton.setEnabled(False)
        self.ui.fanStopButton.setEnabled(False)
        self.ui.ledStopButton.setEnabled(False)
        self.ui.fpStopButton.setEnabled(False)
        self.ui.irStopButton.setEnabled(False)
        self.ui.buttonStopButton.setEnabled(False)
        self.ui.tunerTestProgressBar.setProperty("value", 5)
        self.ui.lnbTestProgressbar.setProperty("value", 5)
        self.ui.hddTestProgressBar.setProperty("value", 5)
        self.ui.usbTestProgressBar.setProperty("value", 5)
        self.ui.smartcardTestProgressbar.setProperty("value", 5)
        self.ui.fanTestProgressbar.setProperty("value", 5)
        self.ui.ledTestProgressbar.setProperty("value", 5)
        self.ui.fpTestProgressbar.setProperty("value", 5)
        self.ui.irTestProgressbar.setProperty("value", 5)
        self.ui.buttonTestProgressbar.setProperty("value", 5)
        self.ui.tunerResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.hddResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.usbResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.smartcardResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.fanResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.ledResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.fpResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.irResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.buttonResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.hdcpKeyResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.uiUpgradeResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.lnbResult.setStyleSheet("QLabel { background-color : silver; color : gray; }");
        self.ui.textStbSwVersion.clear()
        self.ui.textStbEth0Mac.clear()
        self.ui.textStbWifiMac.clear()
        self.ui.textStbModel.clear()
        self.ui.textStbHddSn.clear()
        self.ui.statusMsgLabel.clear()


    def connectTheSTB(self):
        print "Connecting to telnet ... "
        self.telnetcli = SkedTelnet()
        print "Connected "
        self.updateConnectionStatus("Connected ")
        buildCommandList()
        option = ""
        value = ""
        msg = ""
        self.ptcHandlingThread = getPTCThread(self.msgQ, self.telnetcli,option,value,msg )
        self.connect(self.ptcHandlingThread, SIGNAL("uiUpdateProcess(QString,QString,QString)"),self.uiUpdateProcess)
        self.ui.disconnectButton.clicked.connect(self.disconectTheSTB)
        self.ptcHandlingThread.start()
        self.ptcHandlingThread.startThread()
        self.ptcHandlingThread.ptc_update_systemInfo()
        self.ui.connectToStbButton.setEnabled(False)
        self.ui.disconnectButton.setEnabled(True)

        self.ui.tunerStartButton.clicked.connect(self.startTunerTest)
        self.ui.tunerStopButton.clicked.connect(self.stopTunerTest)

        self.ui.lnbStartButton.clicked.connect(self.startLnbTest)
        self.ui.lnbStopButton.clicked.connect(self.stopLnbTest)

        self.ui.hddStartButton.clicked.connect(self.startHddTest)
        self.ui.hddStopButton.clicked.connect(self.stopHddTest)
        self.ui.usbStartButton.clicked.connect(self.startUsbTest)
        self.ui.usbStopButton.clicked.connect(self.stopUsbTest)
        self.ui.smartcardStartButton.clicked.connect(self.startSmartcardTest)
        self.ui.smartcardStopButton.clicked.connect(self.stopSmartcardTest)
        self.ui.fanStartButton.clicked.connect(self.startFanTest)
        self.ui.fanStopButton.clicked.connect(self.stopFanTest)
        self.ui.ledStartButton.clicked.connect(self.startLedTest)
        self.ui.ledStopButton.clicked.connect(self.stopLedTest)
        self.ui.fpStartButton.clicked.connect(self.startFpTest)
        self.ui.fpStopButton.clicked.connect(self.stopFpTest)
        self.ui.buttonStartButton.clicked.connect(self.startButtonTest)
        self.ui.buttonStopButton.clicked.connect(self.stopButtonTest)
        self.ui.irStartButton.clicked.connect(self.startIrTest)
        self.ui.irStopButton.clicked.connect(self.stopIrTest)
        self.ui.hdcpStartButton.clicked.connect(self.startHdcpKeyProgram)
        self.ui.uiUpdateStartButton.clicked.connect(self.startUiUpgrade)
        self.ui.statusMsgLabel.setStyleSheet("QLabel { background-color : black; color : white; }")
        if(self.ui.autoTestButton.isChecked()):
            self.startHddTest()

    def tunerTestOptionUpdate(self):
        self.ui.tunerStartButton.setEnabled(True)
        self.ui.tunerStopButton.setEnabled(False)

    def startTunerTest(self):
        self.msgQ.put("startTunerTest")
        self.ui.tunerStartButton.setEnabled(False)
        self.ui.tunerResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.tunerStopButton.setEnabled(True)

    def stopTunerTest(self):
        self.ui.tunerStartButton.setEnabled(True)
        self.ui.tunerStopButton.setEnabled(False)
        self.msgQ.put("stopTunerTest")

    def startLnbTest(self):
        self.msgQ.put("startLnbTest")
        self.ui.lnbStartButton.setEnabled(False)
        self.ui.lnbResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.lnbStopButton.setEnabled(True)

    def stopLnbTest(self):
        self.ui.lnbStartButton.setEnabled(True)
        self.ui.lnbStopButton.setEnabled(False)
        self.msgQ.put("stopLnbTest")

    def startButtonTest(self):
        self.msgQ.put("startButtonTest")
        self.tunerTestOptionUpdate()
        self.ui.buttonStartButton.setEnabled(False)
        self.ui.buttonResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.buttonStopButton.setEnabled(True)

    def stopButtonTest(self):
        self.ui.buttonStartButton.setEnabled(True)
        self.ui.buttonStopButton.setEnabled(False)
        self.msgQ.put("stopButtonTest")


    def startIrTest(self):
        self.msgQ.put("startIrTest")
        self.tunerTestOptionUpdate()
        self.ui.irStartButton.setEnabled(False)
        self.ui.irResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.irStopButton.setEnabled(True)

    def stopIrTest(self):
        self.ui.irStartButton.setEnabled(True)
        self.ui.irStopButton.setEnabled(False)
        self.msgQ.put("stopIrTest")


    def startHddTest(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startHddTest")
        self.ui.hddStartButton.setEnabled(False)
        self.ui.hddResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.hddStopButton.setEnabled(True)

    def stopHddTest(self):
        self.ui.hddStartButton.setEnabled(True)
        self.ui.hddStopButton.setEnabled(False)
        self.msgQ.put("stopHddTest")

    def startUsbTest(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startUsbTest")
        self.ui.usbStartButton.setEnabled(False)
        self.ui.usbStopButton.setEnabled(True)
        self.ui.usbResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
    def stopUsbTest(self):
        self.ui.usbStartButton.setEnabled(True)
        self.ui.usbStopButton.setEnabled(False)
        self.msgQ.put("stopUsbTest")

    def startSmartcardTest(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startSmartcardTest")
        self.ui.smartcardStartButton.setEnabled(False)
        self.ui.smartcardResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
    def stopSmartcardTest(self):
        self.ui.smartcardStartButton.setEnabled(True)
        self.msgQ.put("stopSmartcardTest")
        self.ui.smartcardSopButton.setEnabled(False)

    def startFanTest(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startFanTest")
        self.ui.fanStartButton.setEnabled(False)
        self.ui.fanResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.fanStopButton.setEnabled(True)

    def stopFanTest(self):
        self.ui.fanStartButton.setEnabled(True)
        self.msgQ.put("stopUsbTest")
        self.ui.fanStopButton.setEnabled(False)

    def startLedTest(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startLedTest")
        self.ui.ledStartButton.setEnabled(False)
        self.ui.ledResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.ledStopButton.setEnabled(True)

    def stopLedTest(self):
        self.ui.ledStartButton.setEnabled(True)
        self.msgQ.put("stopLedTest")
        self.ui.ledStopButton.setEnabled(False)

    def startFpTest(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startFpTest")
        self.ui.fpStartButton.setEnabled(False)
        self.ui.fpResult.setStyleSheet("QLabel { background-color : gray; color : black; }");
        self.ui.fpStopButton.setEnabled(True)

    def stopFpTest(self):
        self.ui.fpStartButton.setEnabled(True)
        self.msgQ.put("stopFpTest")
        self.ui.fpStopButton.setEnabled(False)

    def startHdcpKeyProgram(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startHdcpKeyProgram")
        self.ui.hdcpStartButton.setEnabled(False)
        self.ui.hdcpKeyResult.setStyleSheet("QLabel { background-color : gray; color : black; }");

    def startUiUpgrade(self):
        self.tunerTestOptionUpdate()
        self.msgQ.put("startUiUpgrade")
        self.ui.uiUpdateStartButton.setEnabled(False)
        self.ui.uiUpgradeResult.setStyleSheet("QLabel { background-color : gray; color : black; }");


    def uiUpdateProcess( self, option, value, msg ):
        if(option == "updateClock"):
            self.updateClock(value)
        elif(option == "updateTemp"):
            self.updateTemperature(value)
        elif(option == "updateTelnetEditor"):
            self.updateTelEditor(value)
        elif(option == "updateSoftwareVersion"):
            self.updateSwVersion(value)
        elif(option == "updateEthMacAddr"):
            self.updateEthMac(value)
        elif(option == "updateWifiMacAddr"):
            self.updateWifiMac(value)
        elif(option == "updateModelName"):
            self.updateModelName(value)
        elif(option == "updateHddSerial"):
            self.updateHddSerailNumber(value)
        elif(option == "updateHddTestProgress"):
            self.updateHddTestProgress(value,int(msg))
        elif(option == "updateHddTestResult"):
            self.updateHddTestResult(value)
        elif (option == "updateUsbTestResult"):
            self.updateUsbTestResult(value)
        elif (option == "updateUsbTestProgress"):
            self.updateUsbTestProgress(value, int (msg))
        elif (option == "updateSmartcardTestResult"):
            self.updateSmartcardTestResult(value)
        elif (option == "updateSmartcardTestProgress"):
            self.updateSmartcardTestProgress(value, int (msg))
        elif (option == "updateFanTestResult"):
            self.updateFanTestResult(value)
        elif (option == "updateFanTestProgress"):
            self.updateFanTestProgress(value, int (msg))
        elif (option == "updateLedTestResult"):
            self.updateLedTestResult(value)
        elif (option == "updateLedTestProgress"):
            self.updateLedTestProgress(value, int (msg))
        elif (option == "updateFpTestResult"):
            self.updateFpTestResult(value)
        elif (option == "updateFpTestProgress"):
            self.updateFpTestProgress(value, int (msg))
        elif (option == "updateButtonTestProgress"):
            self.updateButtonTestProgress(value, int (msg))
        elif (option == "updateButtonTestResult"):
            self.updateButtonTestResult(value)
        elif (option == "updateIrTestProgress"):
            self.updateIrTestProgress(value, int (msg))
        elif (option == "updateIrTestResult"):
            self.updateIrTestResult(value)
        elif (option == "updateFanTestSpeed"):
            self.updateFanTestSpeed(value)
        elif (option == "updateTunerTestResult"):
            self.updateTunerTestResult(value)
        elif (option == "updateTunerTestProgress"):
            self.updateTunerTestProgress(value, int (msg))
        elif (option == "updateLnbTestResult"):
            self.updateLnbTestResult(value)
        elif (option == "updateLnbTestProgress"):
            self.updateLnbTestProgress(value, int (msg))
        elif (option == "updateHdcpKeyResult"):
            self.updateHdcpKeyResult(value)
        elif (option == "updateUiUpgradeResult"):
            self.updateUiUpgradeResult(value)


    def updateConnectionStatus(self,text):
        connectionstr = "Telnet Connection Status : "
        connectionstr = connectionstr + text
        self.ui.telnetConnection.setText(connectionstr)

    def updateSwVersion(self,text):
        self.ui.textStbSwVersion.setOverwriteMode(True)
        self.ui.textStbSwVersion.setPlainText(text)
        self.ui.textStbSwVersion.setReadOnly(True)

    def updateTelEditor(self,text):
        self.ui.telnetEditorOuput.insertPlainText(text)
        self.ui.telnetEditorOuput.verticalScrollBar().setValue(self.ui.telnetEditorOuput.verticalScrollBar().maximum())
        #following for allow max chars need to implement
        '''
        max_length = 524288 #(512 KB)
        if (self.ui.telnetEditorOuput.toPlainText().length()> max_length):
            diff = self.ui.telnetEditorOuput.toPlainText - max_length
            nexText = self.ui.telnetEditorOuput.toPlainText;
            nexText.chop(diff)
            self.ui.telnetEditorOuput.insertPlainText(nexText)
            self.ui.telnetEditorOuput.verticalScrollBar().setValue(self.ui.telnetEditorOuput.verticalScrollBar().maximum())
        else:
        '''
    def updateEthMac(self,text) :
        self.ui.textStbEth0Mac.setText(text)
        self.ui.textStbEth0Mac.setReadOnly(True)

    def updateWifiMac(self,text) :
        self.ui.textStbWifiMac.setText(text)
        self.ui.textStbWifiMac.setReadOnly(True)

    def updateClock(self,text):
        self.ui.dateAndTime.setText(text)
    def updateTemperature(self,text):
        print text
        #self.ui.labelTemperatureValue.setStyleSheet("QLabel { background-color : blue; color : white; }")
        self.ui.labelTemperatureValue.setText(text)
    def updateHddSerailNumber(self, text):
        self.ui.textStbHddSn.setText(text)
    def updateHddTestResult(self, text):
        if(text == "PASS"):
            self.ui.hddResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.hddResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.hddResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.hddResult.setText("FAIL")
        self.ui.hddStartButton.setEnabled(True)
        self.ui.hddStopButton.setEnabled(False)
        if(self.ui.autoTestButton.isChecked()):
            self.startUsbTest()
        #    self.startHddTest()

    def updateHddTestProgress(self,text, value):
        self.ui.hddTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("HDD Test :")
        cntstr = " Test Count %d " % hddtestCnt
        textStr = text + cntstr
        self.ui.statusMsgLabel.setText(textStr)

    def updateUsbTestProgress(self,text, value):
        self.ui.usbTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("USB Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateUsbTestResult(self, text):
        if(text == "PASS"):
            self.ui.usbResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.usbResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.usbResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.usbResult.setText("FAIL")
        self.ui.usbStartButton.setEnabled(True)
        self.ui.usbStopButton.setEnabled(False)
        if(self.ui.autoTestButton.isChecked()):
            self.startSmartcardTest()

    def updateHdcpKeyResult(self,text):
        if(text == "PASS"):
            self.ui.hdcpKeyResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.hdcpKeyResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.hdcpKeyResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.hdcpKeyResult.setText("FAIL")
        self.ui.hdcpStartButton.setEnabled(True)


    def updateUiUpgradeResult(self,text):
        if(text == "PASS"):
            self.ui.uiUpgradeResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.uiUpgradeResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.uiUpgradeResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.uiUpgradeResult.setText("FAIL")
        self.ui.uiUpdateStartButton.setEnabled(True)

    def updateSmartcardTestProgress(self,text, value):
        self.ui.smartcardTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Smartcard Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateSmartcardTestResult(self, text):
        if(text == "PASS"):
            self.ui.smartcardResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.smartcardResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.smartcardResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.smartcardResult.setText("FAIL")

        self.ui.smartcardStartButton.setEnabled(True)
        self.ui.smartcardStopButton.setEnabled(False)
        if(self.ui.autoTestButton.isChecked()):
            self.startFanTest()


    def updateIrTestProgress(self,text, value):
        self.ui.irTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("IR Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateIrTestResult(self, text):
        if(text == "PASS"):
            self.ui.irResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.irResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.irResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.irResult.setText("FAIL")
        self.ui.irStartButton.setEnabled(True)
        self.ui.irStopButton.setEnabled(False)

    def updateFanTestProgress(self,text, value):
        self.ui.fanTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Fan Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateFanTestResult(self, text):
        if(text == "PASS"):
            self.ui.fanResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.fanResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.fanResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.fanResult.setText("FAIL")
        self.ui.fanStartButton.setEnabled(True)
        self.ui.fanStopButton.setEnabled(False)
        if(self.ui.autoTestButton.isChecked()):
            self.startLnbTest()

    def updateFanTestSpeed(self,text):
            self.ui.fanSpeed.setText(text)

    def updateLedTestResult(self, text):
        if(text == "PASS"):
            self.ui.ledResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.ledResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.ledResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.ledResult.setText("FAIL")
        self.ui.ledStartButton.setEnabled(True)
        self.ui.ledStopButton.setEnabled(False)

    def updateLedTestProgress(self,text, value):
        self.ui.ledTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("LED Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateTunerTestResult(self, text):
        if(text == "PASS"):
            self.ui.tunerResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.tunerResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.tunerResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.tunerResult.setText("FAIL")


    def updateTunerTestProgress(self,text, value):
        self.ui.tunerTestProgressBar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Tuner Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateLnbTestResult(self, text):
        if(text == "PASS"):
            self.ui.lnbResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.lnbResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.lnbResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.lnbResult.setText("FAIL")

        self.ui.lnbStartButton.setEnabled(True)
        self.ui.lnbStopButton.setEnabled(False)
        #if(self.ui.autoTestButton.isChecked()):
        #    self.startTunerTest()

    def updateLnbTestProgress(self,text, value):
        self.ui.lnbTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("LNB Test :")
        self.ui.statusMsgLabel.setText(text)

    def updateFpTestResult(self, text):
        if(text == "PASS"):
            self.ui.fpResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.fpResult.setText("PASS")
        elif(text == "FAIL"):
            self.ui.fpResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.fpResult.setText("FAIL")
        self.ui.fpStartButton.setEnabled(True)
        self.ui.fpStopButton.setEnabled(False)

    def updateFpTestProgress(self,text, value):
        self.ui.fpTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("FP Test :")
        self.ui.statusMsgLabel.setText(text)


    def updateButtonTestResult(self, text):
        if(text == "PASS"):
            self.ui.buttonResult.setStyleSheet("QLabel { background-color : green; color : white; }");
            self.ui.buttonResult.setText("PASS")
            Keystr = "Key : "
            Keystr = Keystr + "Pressed"
            self.ui.buttonKeysRecivce.setText(Keystr)
        elif(text == "FAIL"):
            self.ui.buttonResult.setStyleSheet("QLabel { background-color : red; color : white; }");
            self.ui.buttonResult.setText("FAIL")
        self.ui.buttonStartButton.setEnabled(True)
        self.ui.buttonStopButton.setEnabled(False)

    def updateButtonTestProgress(self,text, value):
        self.ui.buttonTestProgressbar.setProperty("value",value)
        self.ui.statusMsgLabel.setText("Button Test :")
        self.ui.statusMsgLabel.setText(text)


    def updateModelName(self, text):
        self.ui.textStbModel.setText(text)

def stbGetTemperature(appThread,tel):
    tempFindString = "temp_monitor"
    tel.telWrite(command_list[TestCommnad.GET_TEMPERATURE])
    time.sleep(2)
    data = tel.telReadSocket(appThread)
    match = re.search(tempFindString,data)
    #print list(data)
    if match:
        temperature = data[(data.find("temp_monitor")):(data.find("temp_monitor"))+15]
        temperature = temperature.translate(None,"temp_monitor")
        temperature = temperature + " " + "C"
        #print temperature
        return temperature
    else:
        return "0 C"


def stbGetSoftwareVersion( app, tel) :
    tel.telWrite(command_list[TestCommnad.GET_VER])
    data = tel.telReadSocket(app)
    print data
    swver = data[(data.find("stb")):]
    swver =  swver.translate(None,'#')
    return swver

def stbGetMacAddress( app, tel) :
    macaddrFindString = ":"
    tel.telWrite(command_list[TestCommnad.GET_MACADR])
    time.sleep(1)
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        if data:
            match = re.search(macaddrFindString,data)
            if match :
                waitforfind = 0
                data = data.translate(None, "read_mac.sh") # descard read_mac.sh
                ethmac = (data [2:19]) # Taken only the Eth Macaddr
                wifimac = (data [21:38]) # Taken only the Wifi Macaddr
                print list(ethmac)
                macadd= [ethmac, wifimac ]
                return macadd
            else :
                continue
        else :
            continue




def stbDiseqcSettings(app,tel):
    print "Diseqc Settings is called "
    print "LNB 18V ON and 22Khz ON"
    tel.telWrite(command_list[TestCommnad.LNB_HIGH_22K_ON])
    time.sleep(1)
    data = tel.telReadSocket(app)

def stbPerformLnbTest(app, tel):
    currentProgressbarValue = 20
    matchStr18V = "18V"
    matchStr22k ="22k:on"
    print "LNB 18V ON and 22Khz ON"
    app.ptc_update_msg("updateLnbTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.LNB_HIGH_22K_ON])
    time.sleep(1)
    data = tel.telReadSocket(app)
    currentProgressbarValue = 50
    app.ptc_update_msg("updateLnbTestProgress","Test Progress",str(currentProgressbarValue))
    match = re.search(matchStr18V,data)
    match1 = re.search(matchStr22k,data)
    if match and match1:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateLnbTestProgress","Test Done",str(currentProgressbarValue))
        return 1
    else:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateLnbTestProgress","Test Done",str(currentProgressbarValue))
        return 0

def stbPerformTunerTest(app,tel):

    currentProgressbarValue = 20
    TunerTestProgress = 1
    tunerPassString = "Decoding sat"
    tunerFailString = "No channels found"
    app.ptc_update_msg("updateTunerTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.TUNE_TEST])
    time.sleep(1)
    currentProgressbarValue = currentProgressbarValue + 20
    app.ptc_update_msg("updateTunerTestProgress","Test Progress",str(currentProgressbarValue))
    time.sleep(3)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(tunerPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
        return 1
    else:
        match1 = re.search(tunerFailString,data)
        if match1:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
            return 0
        else:
            while TunerTestProgress:
                data = tel.telReadSocket(app)
                print list(data)
                print data
                match = re.search(tunerPassString,data)
                if match:
                    TunerTestProgress = 0
                    currentProgressbarValue = 100
                    app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
                    return 1
                else:
                    match1 = re.search(tunerFailString,data)
                    if match1:
                        currentProgressbarValue = 100
                        TunerTestProgress = 0
                        app.ptc_update_msg("updateTunerTestProgress","Test Done",str(currentProgressbarValue))
                        return 0
                    else:
                        currentProgressbarValue = currentProgressbarValue + 20
                        app.ptc_update_msg("updateTunerTestProgress","Test Progress ",str(currentProgressbarValue))
                        continue




def stbStopTunerTest(app,tel):
    tel.telWrite('\x03') #ctrl + c
    print ("Tuner_Test_Stopped")


def stbPerformFanTest(app,tel):
    currentProgressbarValue = 20
    fanPassString = "speed:"

    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c

    app.ptc_update_msg("updateFanTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD1])
    time.sleep(1)
    currentProgressbarValue = currentProgressbarValue + 10
    app.ptc_update_msg("updateFanTestProgress","Test Progress",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD2])
    time.sleep(1)
    currentProgressbarValue = currentProgressbarValue + 10
    app.ptc_update_msg("updateFanTestProgress","Test Progress",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD3])
    time.sleep(1)
    currentProgressbarValue = currentProgressbarValue + 10
    app.ptc_update_msg("updateFanTestProgress","Test Progress",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD4])
    time.sleep(1)
    currentProgressbarValue = currentProgressbarValue + 10
    app.ptc_update_msg("updateFanTestProgress","Test Progress",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.FAN_TEST_CMD5])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(fanPassString,data)
    if match:
        currentProgressbarValue = 80

        speed = data[(data.find(fanPassString)): (data.find(fanPassString)) + 15]
        print speed
        msgStr = "FAN : " + "%s"  % speed
        print msgStr
        app.ptc_update_msg("updateFanTestSpeed", msgStr, "")
        app.ptc_update_msg("updateFanTestProgress",msgStr,str(currentProgressbarValue))
        stbStopFanTest(app,tel)
        currentProgressbarValue = 100
        app.ptc_update_msg("updateFanTestProgress",msgStr,str(currentProgressbarValue))
        return 1
    else:
        currentProgressbarValue = 80
        app.ptc_update_msg("updateFanTestProgress","Fan Test Failed ",str(currentProgressbarValue))
        stbStopFanTest(app,tel)
        currentProgressbarValue = 100
        app.ptc_update_msg("updateFanTestProgress","Fan Test Failed ",str(currentProgressbarValue))
        return 0


def stbStopFanTest(app,tel):
    print("Fan Test Stopped")
    rmfanmodstr = "mstcgio"
    tel.telWrite('\x03') #ctrl + c
    tel.telWrite(command_list[TestCommnad.REMOVER_FAN_TEST_MODULE_CMD1])
    time.sleep(2)
    data = tel.telReadSocket(app)
    tel.telWrite(command_list[TestCommnad.REMOVER_FAN_TEST_MODULE_CMD2])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(rmfanmodstr,data)
    if match:
        print " Fan Module Not Removed "
    else :
        print " Fan Module Removed "


def stbPerformSmartcardTest(app,tel):
    currentProgressbarValue = 20

    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    smcPassString = "ATR Bytes received"
    smcFailString = "Test all Failed"
    smcNotInsertString = "Smartcard isn't inserted"
    app.ptc_update_msg("updateSmartcardTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.SMC_TEST])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(smcNotInsertString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateSmartcardTestProgress","Smartcard isn't inserted",str(currentProgressbarValue))
        return 0
    else:
        match1 = re.search(smcPassString,data)
        if match1:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateSmartcardTestProgress","Smartcard Test Passed ",str(currentProgressbarValue))
            return 1
        else:
            match2 = re.search(smcFailString,data)
            if match2:
                currentProgressbarValue = 100
                app.ptc_update_msg("updateSmartcardTestProgress","Smartcard Test Failed ",str(currentProgressbarValue))
                return 0


def stbStopSmartcardTest(app,tel):
    print("Smartcard Test Stopped")
    tel.telWrite('\x03') #ctrl + c

def stbPerformUsbTest(app,tel):
    currentProgressbarValue = 20
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    usbPassString = "Test all PASS"
    usbPassString1 = "USB type: usb3.0"
    usbFailString = "Test all Failed"
    usbNotInsertString = "Cannot find USB storage Device"
    app.ptc_update_msg("updateUsbTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.USB_TEST])
    time.sleep(2)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(usbNotInsertString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateUsbTestProgress","Cannot find USB storage Device",str(currentProgressbarValue))
        return 0
    else:
        match1 = re.search(usbPassString,data)
        match2 =  re.search(usbPassString1,data)
        if match1 or match2:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateUsbTestProgress","USB Test Passed ",str(currentProgressbarValue))
            return 1
        else:
            match3 = re.search(usbFailString,data)
            if match3:
                currentProgressbarValue = 100
                app.ptc_update_msg("updateUsbTestProgress","USB Test Failed ",str(currentProgressbarValue))
                return 0

def stbStopUsbTest(app,tel):
    print("USB Test Stopped")
    tel.telWrite('\x03') #ctrl + c

# ['\r', '\n', '#', ' ', 'h', 'd', 'd', 'S', 'e', 'r', 'i', 'a', 'l', 'N', 'u', 'm', 'b', 'e', 'r', '\r', '\n', 'Z', '9', 'C', '5', 'P', 'J', '9', '3', '\r', '\n', '#', ' ']
def stbPerformHddTest(app,tel):
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    formatstartString = "Format Started"
    formatCompleteString = "Format Completed"
    hddTestCompleteString = "aft"
    hddTestFailString = "Sata'test is failed"
    #update the HDD serial number
    # do the format
    # do the read/write test
    tel.telWrite(command_list[TestCommnad.GET_HDD_SERIAL])
    time.sleep(1)
    data = tel.telReadSocket(app)
    print list(data)
    hddserial = (data[21:29])
    print hddserial
    app.ptc_update_msg("updateHddSerial",hddserial,"")
    app.ptc_update_msg("updateHddTestProgress","Test Initiated",str(currentProgressbarValue))

    tel.telWrite(command_list[TestCommnad.HDD_FORMAT_CMD1])
    data = tel.telReadSocket(app)
    tel.telWrite(command_list[TestCommnad.HDD_FORMAT_CMD2])
    data = tel.telReadSocket(app)
    currentProgressbarValue = currentProgressbarValue + 10
    app.ptc_update_msg("updateHddTestProgress","Format begins",str(currentProgressbarValue))
    #app.updateHDDTestProgress("Format begins",currentProgressbarValue)
    match = re.search(formatstartString,data)

    if match:
        FormatStartedFlag = 1
        print "Format is Progress"
        currentProgressbarValue = currentProgressbarValue + 4
        app.ptc_update_msg("updateHddTestProgress","Format Progress",str(currentProgressbarValue))
        count = 1;
        while FormatStartedFlag: # keep read the socket untill get pass result
            QtCore.QCoreApplication.processEvents()
            count = count + 1
            data = tel.telReadSocket(app)
            match1 = re.search(formatCompleteString,data)
            if match1:
                currentProgressbarValue = currentProgressbarValue + (count * 2)
                app.ptc_update_msg("updateHddTestProgress","Format Completed",str(currentProgressbarValue))
                FormatStartedFlag = 0
            else :
                currentProgressbarValue = currentProgressbarValue + (count * 2)
                app.ptc_update_msg("updateHddTestProgress","Format Progress",str(currentProgressbarValue))
                time.sleep(1)
                continue
    #Format Completed and do the HDD test
    tel.telWrite(command_list[TestCommnad.HDD_TEST])
    HddTestStartedFlag = 1
    app.ptc_update_msg("updateHddTestProgress","HDD R/W Test Progress",str(currentProgressbarValue))
    print "Test is Progress"
    while HddTestStartedFlag: # keep read the socket untill get pass result
            QtCore.QCoreApplication.processEvents()
            data = tel.telReadSocket(app)
            match1 = re.search(hddTestCompleteString,data)
            match2 = re.search(hddTestFailString,data)
            if match1 or match2:
                print "HDD test Completed"
                HddTestStartedFlag = 0
                if match2:
                    print "HDD Test Failed"
                    app.ptc_update_msg("updateHddTestProgress","HDD Test Failed",str(currentProgressbarValue))
                    return 0
            else :
                time.sleep(1)
                continue
    if not match2:
        global hddtestCnt
        currentProgressbarValue = 100
        app.ptc_update_msg("updateHddTestProgress","HDD Test Done",str(currentProgressbarValue))
        hddtestCnt = hddtestCnt + 1
        print " Test Count %d " % hddtestCnt
        return hddtestCnt

def stbStopHddTest(app,tel):
    print("HDD test Stopped")
    tel.telWrite('\x03') #ctrl + c


def stbPerformLedTest(app,tel):
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    retry = 1
    retrycnt = 0
    currentProgressbarValue = 20
    ledPassString = "LED all on"
    app.ptc_update_msg("updateLedTestProgress","Test Initiated",str(currentProgressbarValue))
    command_list[TestCommnad.LED_TEST] = "led 0"
    tel.telWrite(command_list[TestCommnad.LED_TEST])
    time.sleep(2)
    command_list[TestCommnad.LED_TEST] = "led 1"
    tel.telWrite(command_list[TestCommnad.LED_TEST])
    data = tel.telReadSocket(app)
    time.sleep(2)
    #print list(data)
    match = re.search(ledPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateLedTestProgress","Led Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        while retry :
            data = tel.telReadSocket(app)
            time.sleep(2)
            #print list(data)
            match = re.search(ledPassString,data)
            if match:
                retry = 0
                currentProgressbarValue = 100
                app.ptc_update_msg("updateLedTestProgress","Led Test Passed ",str(currentProgressbarValue))
                return 1
            else:
                if(retrycnt > 5):
                    currentProgressbarValue =  currentProgressbarValue + 6
                    app.ptc_update_msg("updateLedTestProgress","Led Test Failed ",str(currentProgressbarValue))
                    return 0
                retrycnt = retrycnt + 1
                continue




def stbStopLedTest(app,tel):
    print("Led Test Stopped")
    command_list[TestCommnad.LED_TEST] = "led 0"
    tel.telWrite(command_list[TestCommnad.LED_TEST])
    time.sleep(2)


def stbPerformFpTest(app,tel):
    retry = 1
    retrycnt = 0
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    fpPassString = "act_gridon"
    app.ptc_update_msg("updateFpTestProgress","Test Initiated",str(currentProgressbarValue))
    command_list[TestCommnad.VFD_TEST] = "/root/htp/vfd -r -i -x 0"
    tel.telWrite(command_list[TestCommnad.VFD_TEST])
    time.sleep(2)
    command_list[TestCommnad.VFD_TEST] = "/root/htp/vfd -r -i -x 1"
    tel.telWrite(command_list[TestCommnad.VFD_TEST])
    data = tel.telReadSocket(app)
    time.sleep(2)
    #print list(data)
    match = re.search(fpPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateFpTestProgress","FP Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        return 0


def stbStopFpTest(app,tel):
    print("Fp Test Stopped")
    command_list[TestCommnad.VFD_TEST] = "/root/htp/vfd -r -i -x 0"
    tel.telWrite(command_list[TestCommnad.VFD_TEST])
    time.sleep(2)


def stbPerformIrTest(app,tel):
    retry = 1
    retrycnt = 0
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    irPassString = "IR test: pass"
    irFailString = "IR test: failed"
    app.ptc_update_msg("updateIrTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.IR_TEST])
    time.sleep(5)
    data = tel.telReadSocket(app)
    #print list(data)
    match = re.search(irPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateIrTestProgress","IR Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        match = re.search(irFailString,data)
        if match:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateIrTestProgress","IR Test Failed ",str(currentProgressbarValue))
            return 0
        else:
            while retry :
                data = tel.telReadSocket(app)
                time.sleep(2)
                #print list(data)
                match = re.search(irPassString,data)
                if match:
                    retry = 0
                    currentProgressbarValue = 100
                    app.ptc_update_msg("updateIrTestProgress","IR Test Passed ",str(currentProgressbarValue))
                    return 1
                else:
                    match = re.search(irFailString,data)
                    if match:
                        currentProgressbarValue = 100
                        app.ptc_update_msg("updateIrTestProgress","IR Test Failed ",str(currentProgressbarValue))
                        return 0
                    elif(retrycnt > 5):
                        currentProgressbarValue =  currentProgressbarValue + 6
                        app.ptc_update_msg("updateIrTestProgress","Waiting for IR-Key Press ",str(currentProgressbarValue))
                        return 0
                retrycnt = retrycnt + 1
                continue




def stbStopIrTest(app,tel):
    print("IR Test Stopped")
    tel.telWrite(command_list[TestCommnad.STOP_TUNE_TEST]) # ctrl +c to stop
    time.sleep(2)

def stbPerformHdcpKeyProgramming(app,tel):
    hdcpKeyResponseMatchString1 = "Get key from key server"
    hdcpKeyResponseMatchString2 = "Key Server IP"
    hdcpKeyResponseMatchString3 = "MAC"
    hdcpKeyResponseMatchString4 = "Handling HDCP key is successful"
    hdcpKeyResponseMatchString5 = "Handling HDCP key is failed"
    hdcpKeyResponseMatchString6 = "HDCP1.4 key isn't exist"
    hdcpKeyResponseMatchString7 = "HDCP2.2 key isn't exist"

    print "start hdcp key programming"
    macadd = myapp.ui.macAddressInputValue.text()
    print macadd
       # Write MAC Address
    statusStr = "Write MAC successfully"
    tel.telWrite('\x03') #ctrl + c
    time.sleep(1)
    write_cmd = command_list[TestCommnad.WRITE_MAC] +" "+macadd
    tel.telWrite(write_cmd)
    time.sleep(1)
    print time.time()
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        match = re.search(statusStr,data)
        if match :
            waitforfind = 0
            print data

    macaddList = stbGetMacAddress(app, tel)
    ethMac = "%s" % macaddList[0]
    wifiMac = "%s" % macaddList[1]
    print ethMac
    print wifiMac
    app.ptc_update_msg("updateEthMacAddr",ethMac,"")
    app.ptc_update_msg("updateWifiMacAddr",wifiMac,"")

    tel.telWrite('\x03') #ctrl + c
    tel.telWrite(command_list[TestCommnad.PROGRAM_HDCP])
    data = tel.telReadSocket(app)
    time.sleep(.5)
    match = re.search(hdcpKeyResponseMatchString1,data)
    if match:
        tel.telWrite("Y")
        time.sleep(.2)
        data = tel.telReadSocket(app)
        match = re.search(hdcpKeyResponseMatchString2,data)
        if match:
            tel.telWrite("192.192.192.3")
            time.sleep(.2)
            data = tel.telReadSocket(app)
            match = re.search(hdcpKeyResponseMatchString3,data)
            if match:
                macadd =str( myapp.ui.macAddressInputValue.text())
                print [macadd]
                tel.telWrite(macadd)
                time.sleep(.2)
                matchcase = 1
                count = 0
                while matchcase or count < 30:
                    data = tel.telReadSocket(app)
                    match = re.search(hdcpKeyResponseMatchString4,data)
                    match1 = re.search(hdcpKeyResponseMatchString5,data)
                    if  match1:
                        app.ptc_update_msg("updateHdcpKeyResult","FAIL","")
                        return 0
                    elif match:
                        #verify the Keys 1.x
                        tel.telWrite(command_list[TestCommnad.VERIFY_HDCP_1X])
                        time.sleep(1)
                        data = tel.telReadSocket(app)
                        match = re.search(hdcpKeyResponseMatchString6,data)
                        if match:
                            print "HDCP 1.x Validation Fail Please check the mac address"
                            app.ptc_update_msg("updateHdcpKeyResult","FAIL","")
                            return 0
                        #verify the Keys 2.x
                        tel.telWrite(command_list[TestCommnad.VERIFY_HDCP_2X])
                        time.sleep(1)
                        data = tel.telReadSocket(app)
                        match = re.search(hdcpKeyResponseMatchString7,data)
                        if match:
                            print "HDCP 2.x Validation Fail Please check the mac address"
                            app.ptc_update_msg("updateHdcpKeyResult","FAIL","")
                            return 0

                        app.ptc_update_msg("updateHdcpKeyResult","PASS","")
                        return 1

                    else:
                        count +=1
                        continue


def stbDumpUecCode(app,tel) :
    dumpResponseString = "seconds"
    dumpMd5SumString = "UECN1_nopad_dump"
    tel.telWrite(command_list[TestCommnad.DUMP_UECCODE])
    data = tel.telReadSocket(app)
    print data
    waitforfind = 1
    while waitforfind:
        data = tel.telReadSocket(app)
        match = re.search(dumpResponseString,data)
        if match :
            waitforfind = 0
            print data
        else:
            continue

    #check and compare UEC code md5sum
    tel.telWrite(command_list[TestCommnad.CHECK_UECCODE])
    waitforfind = 1
    data1 = ""
    while waitforfind:
        data1 = tel.telReadSocket(app)
        match = re.search(dumpMd5SumString,data1)
        if match :
            waitforfind = 0
            print data1
            return 1
        else:
            continue

def stbPerformUiUpgrade(app,tel):
    print "start UI Upgrade and OTP"
    changeFwConfirmationMsg = "Are you sure want to change FW to"
    changeToUECFWMatchStr = "Change firmware to UEC is successful"
    otpStatusMatchStr = "006 Production OTP lock "
    ret = stbDumpUecCode(app,tel)
    if ret:
        print "Code dump OK - going to do the code swap"

        tel.telWrite(command_list[TestCommnad.UEC_FW_CODE_SWAP])
        time.sleep(3)
        data = tel.telReadSocket(app)
        match = re.search(changeFwConfirmationMsg,data)
        if match :
            tel.telWrite("Y")
            time.sleep(.2)
            waitforfind = 1
            while waitforfind:
                data = tel.telReadSocket(app)
                match = re.search(changeToUECFWMatchStr,data)
                if match :
                    waitforfind = 0
                    print "Change firmware to UEC is successful"
                    print data
                else:
                    continue

        #upgradeFirmwareSuccesfull Do the OTP
        tel.telWrite(command_list[TestCommnad.SET_OTP_CMD1])
        time.sleep(1)
        data = tel.telReadSocket(app)
        tel.telWrite(command_list[TestCommnad.SET_OTP_CMD2])
        time.sleep(1)
        waitforfind = 1
        data = ""
        while waitforfind:
            data = tel.telReadSocket(app)
            match = re.search(otpStatusMatchStr,data)
            if match :
                waitforfind = 0
                print "Change OTP to UEC is successful"
                print data
            else:
                continue

        app.ptc_update_msg("updateUiUpgradeResult","PASS","")
        return 1


def stbPerformButtonTest(app,tel):
    retry = 1
    retrycnt = 0
    #Send Ctrl C to stop previous running tests
    tel.telWrite('\x03') #ctrl + c
    currentProgressbarValue = 20
    buttonPassString = "Button1 pass 1"
    buttonFailString = "Button1 Failed 0"
    app.ptc_update_msg("updateButtonTestProgress","Test Initiated",str(currentProgressbarValue))
    tel.telWrite(command_list[TestCommnad.BUTTON_TEST])
    time.sleep(2)
    data = tel.telReadSocket(app)
    time.sleep(2)
    #print list(data)
    match = re.search(buttonPassString,data)
    if match:
        currentProgressbarValue = 100
        app.ptc_update_msg("updateButtonTestProgress","Button Test Passed ",str(currentProgressbarValue))
        return 1
    else:
        match = re.search(buttonFailString,data)
        if match:
            currentProgressbarValue = 100
            app.ptc_update_msg("updateButtonTestProgress","Button Test Failed ",str(currentProgressbarValue))
            return 0
        else:
            while retry :
                data = tel.telReadSocket(app)
                time.sleep(2)
                #print list(data)
                match = re.search(buttonPassString,data)
                if match:
                    retry = 0
                    currentProgressbarValue = 100
                    app.ptc_update_msg("updateButtonTestProgress","Button Test Passed ",str(currentProgressbarValue))
                    return 1
                else:
                    match = re.search(buttonFailString,data)
                    if match:
                        currentProgressbarValue = 100
                        app.ptc_update_msg("updateButtonTestProgress","Button Test Failed ",str(currentProgressbarValue))
                        return 0
                    elif(retrycnt > 5):
                        currentProgressbarValue =  currentProgressbarValue + 6
                        app.ptc_update_msg("updateButtonTestProgress","Waiting for button Press ",str(currentProgressbarValue))
                        return 0
                retrycnt = retrycnt + 1
                continue




def stbStopButtonTest(app,tel):
    print("Button Test Stopped")
    tel.telWrite(command_list[TestCommnad.STOP_TUNE_TEST]) # ctrl +c to stop
    time.sleep(2)


def forceCloseApp():
    print "App Closed force"
    exitFlag = 1

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = SkedYesUI()
    myapp.setWindowTitle(_translate("SkedYes", "SKED YES V1.07", None))

    timenow = '%s' % (time.ctime(time.time()))
    myapp.ui.dateAndTime.setText(timenow)
    myapp.show()
    myapp.updateConnectionStatus("Not Connected ")
    QtCore.QObject.connect(app, QtCore.SIGNAL(_fromUtf8("lastWindowClosed()")),forceCloseApp)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())

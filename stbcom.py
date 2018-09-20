import sys
import telnetlib
import time
import select
import serial
from PyQt4 import QtCore, QtGui


HOST = "192.192.192.2"
#HOST = "192.168.0.240"
#HOST = "192.168.77.240"
command_list = []

class TestCommnad:
    GET_VER = 0
    DUMP_UECCODE = 1
    CHECK_UECCODE = 2
    GET_STBSN = 3
    HDD_TEST = 4
    GET_HDD_SERIAL = 5
    HDD_FORMAT_CMD1 = 6
    HDD_FORMAT_CMD2 = 7
    LNB_LOW_22K_ON = 8
    LNB_LOW_22K_OFF = 9
    LNB_HIGH_22K_ON = 10
    LNB_HIGH_22K_OFF = 11
    USB_TEST = 12
    SMC_TEST = 13
    GET_TEMPERATURE = 14
    FAN_TEST_CMD1 = 15
    FAN_TEST_CMD2 = 16
    FAN_TEST_CMD3 = 17
    FAN_TEST_CMD4 = 18
    FAN_TEST_CMD5 = 19
    REMOVER_FAN_TEST_MODULE_CMD1 = 20
    REMOVER_FAN_TEST_MODULE_CMD2 = 21
    TUNE_TEST = 22
    STOP_TUNE_TEST = 23
    IR_TEST = 24
    BUTTON_TEST = 25
    LED_TEST = 26
    VFD_TEST = 27
    GET_MACADR = 28
    PROGRAM_HDCP = 29
    VERIFY_HDCP_1X = 30
    VERIFY_HDCP_2X = 31
    UEC_FW_CODE_SWAP = 32
    SET_OTP_CMD1 = 33
    SET_OTP_CMD2 = 34
    HDMI_OUTPUT_TEST = 35
    WRITE_MAC = 36
    MOCA_TEST_CMD1 = 37
    MOCA_TEST_CMD2 = 38
    MOCA_TEST_CMD3 = 39
    RF_TEST_INIT_COMMAND = 40
    RF_CH_SEL_CMD = 41
    RF_ANT_SEL_CMD = 42
    DUT_ZIGBEE_PING_TEST_CMD1 = 43
    DUT_ZIGBEE_PING_TEST_CMD2 = 44
    GS_ZIGBEE_PING_TEST_CMD1 = 45
    GS_ZIGBEE_PING_TEST_CMD2 = 46
    DUT_ZIGBEE_PING_TEST_STAT_CMD = 47
    DUT_ZIGBEE_PING_TEST_STOP_CMD = 48
    DUT_CH_PWR_TEST_STAT_CMD1 = 49
    DUT_CH_PWR_TEST_STOP_CMD = 50

def buildCommandList():
    command_list.append("/root/htp/atcfg -g FW_GIT_VER") # GET_VER = 0
    command_list.append("dd if=/dev/mtd0 of=/tmp/UECN1_nopad_dump bs=40110848 count=1") # DUMP_UECCODE = 1
    command_list.append("md5sum /tmp/UECN1*") # CHECK_UECCODE = 2
    command_list.append("/root/htp/generateSTBSN -r") # GET_STBSN = 3
    command_list.append("sata -d -t") # HDD_TEST = 4
    command_list.append("hddSerialNumber") # GET_HDD_SERIAL = 5
    command_list.append("cd /root/htp/" ) # HDD_FORMAT_CMD1 = 6
    command_list.append("/root/htp/xtv_format_utility /dev/sda p 1 EXT2 200") # HDD_FORMAT_CMD2 = 7
    command_list.append("diseqc 13 1") # LNB_LOW_22K_ON = 8
    command_list.append("diseqc 13 0") # LNB_LOW_22K_OFF = 9
    command_list.append("diseqc 18 1") # LNB_HIGH_22K_ON = 10
    command_list.append("diseqc 18 0") # LNB_HIGH_22K_OFF = 11
    command_list.append("usb") # USB_TEST = 12
    command_list.append("smartcard") # SMC_TEST = 13
    command_list.append("temperature 0") # GET_TEMPERATURE = 14
    command_list.append("/root/htp/gpio 2 0 75 1 2 ") # FAN_TEST_CMD1 = 15
    command_list.append("/root/htp/pwm -c 3 -w 1E92 -f 1 -o 81 -p 80 -s ") # FAN_TEST_CMD2 = 16
    command_list.append("cd /root/htp " ) # FAN_TEST_CMD3 = 17
    command_list.append("insmod ./mstcgio.ko FAN_PINNUM=72 FAN_MINPULSES=20 ") # FAN_TEST_CMD4 = 18
    command_list.append("/root/htp/fan_speed " ) # FAN_TEST_CMD5 = 19
    command_list.append("rmmod mstcgio" ) # REMOVER_FAN_TEST_MODULE_CMD1 = 20
    command_list.append("lsmod" ) # REMOVER_FAN_TEST_MODULE_CMD2 = 21
    command_list.append("/root/htp/live -sat 8pskldpc -sym 7200000 -freq 1899") # TUNE_TEST = 22
    command_list.append("ctrl+c ") # STOP_TUNE_TEST = 23
    command_list.append("irctl 30" ) # IR_TEST = 24
    command_list.append("/root/htp/gpio_interrupt 4 10 2 1 10" ) # BUTTON_TEST = 25
    command_list.append("led" ) # LED_TEST = 26
    command_list.append("/root/htp/vfd -r -i -x") # VFD_TEST = 27
    command_list.append("read_mac.sh") # GET_MACADR = 28
    command_list.append("handleHDCP") # PROGRAM_HDCP = 29
    command_list.append("HDCP14_L20byte") # VERIFY_HDCP_1X = 30
    command_list.append("HDCP22_L20byte") # VERIFY_HDCP_2X = 31
    command_list.append("changeToUECFW") # UEC_FW_CODE_SWAP = 32
    command_list.append("cd /root/htp" ) # SET_OTP_CMD1 = 33
    command_list.append("otp_bl -w -s all") # SET_OTP_CMD2 = 34
    command_list.append("/root/htp/graphics_as_video") # HDMI_OUTPUT_TEST =35
    command_list.append("write_mac.sh") # WRITE_MAC = 36
    command_list.append("ifconfig eth1 192.192.168.10") # MOCA_TEST_CMD1 = 37
    command_list.append("init_moca") # MOCA_TEST_CMD2 = 38
    command_list.append("moca_throughput 192.192.168.1 5 350 350") # MOCA_TEST_CMD3 = 39
    command_list.append("GP510_transceiver 2") # RF_TEST_INIT_COMMAND = 40
    command_list.append("ch ") # RF_CH_SEL_CMD = 41
    command_list.append("an 0") # RF_ANT_SEL_CMD = 42
    command_list.append("R") # DUT_ZIGBEE_PING_TEST_CMD1 = 43
    command_list.append("rx 1") # DUT_ZIGBEE_PING_TEST_CMD2 = 44
    command_list.append("w 3") # GS_ZIGBEE_PING_TEST_CMD1 = 45
    command_list.append("tx 1000 10") # GS_ZIGBEE_PING_TEST_CMD2 = 46
    command_list.append("P") # DUT_ZIGBEE_PING_TEST_STAT_CMD = 47
    command_list.append("rx 0") # DUT_ZIGBEE_PING_TEST_STOP_CMD = 48
    command_list.append("cw u") # DUT_CH_PWR_TEST_STAT_CMD1 = 49
    command_list.append("cw o") # DUT_CH_PWR_TEST_STOP_CMD = 50


#user = raw_input("Enter user name:")
#password = getpass.getpass()
class SkedTelnet():
    def __init__(self):
        print "init"
        tn = telnetlib.Telnet(HOST)
        tn.read_until("login: ")
        tn.write("root" + "\r\n")
        print "login enter"
        #tn.read_until("Password: ")
        #tn.write("606202123" + "\n")
        #tn.write("whoami" +"\n")
        self.tn = tn
        #print tn.read_until("gps")

    def telWrite(self,string):
        try:
            self.tn.write(string + "\r\n")
        except:
            time.sleep(1)

    def telReadSocket(self,app):
        try:
            s= self.tn.get_socket()
            while 1:
                QtCore.QCoreApplication.processEvents()
                time.sleep(.5)
                data = s.recv(4096)
                if not data :
                    print 'No data from Telnet Server'
                else :
                    #print data
                    sys.stdout.write(data)
                    #user entered a message
                    if data:
                        app.ptc_update_msg("updateTelnetEditor",data,"")
                        return data
                    else:
                        return ''
        except:
            print "There is not connection "

    def telread(self,string):
        return self.tn.read_until(string)
    def telexit(self):
        self.tn.write("exit" "\r\n")
        return self.tn.read_all()


#user = raw_input("Enter user name:")
#password = getpass.getpass()
class SkedSerial():
    def __init__(self):
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff = False,
            rtscts = True
        )

        ser.isOpen()
        self.serial = ser
        #print tn.read_until("gps")

    def telWrite(self,string):
        try:
            print("Going To write " + string)
            self.serial.write(string + "\r\n")
        except:
            time.sleep(1)

    def telReadSocket(self,app):
        print "telReadSocket"
        try:
            data = ''
            while self.serial.inWaiting() > 0:
                data += self.serial.read(1)

            if data != '':
                #print list(data)
                app.ptc_update_msg("updateTelnetEditor",data,"")
                return data
            else:
                return ''
        except:
            print "There is no connection "

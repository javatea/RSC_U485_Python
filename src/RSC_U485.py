#!/usr/bin/env python2.6
# coding: utf-8
"""FutabaのRS405,RS406CB制御用ライブラリ
"""
import serial,struct

class RSC_U485:
    def __init__(self,port,baudrate):
        self.ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)

#        print self.ser.portstr

    def move(self,sId,sPos,sTime):
        """
       サーボを指定角度へ動かす
       可動範囲は中央が0度で，サーボ上面から見て時計回りが+，反時計回りが-
       指定角度の単位は0.1度単位
       指定時間の単位は10ms単位(最大0.5%の誤差)
        """
        sendbuf = []
        #パケット作成
        sendbuf.append(0xFA) # ヘッダー1
        sendbuf.append(0xAF) # ヘッダー2
        sendbuf.append(sId) # サーボID
        sendbuf.append(0x00) # フラグ
        sendbuf.append(0x1E) # アドレス(0x1E=30)
        sendbuf.append(0x04) # 長さ(4byte)
        sendbuf.append(0x01) # 個数
        sendbuf.append((sPos & 0x00FF)) # 位置
        sendbuf.append(((sPos & 0xFF00) >> 8)) # 位置
        sendbuf.append((sTime & 0x00FF)) # 時間
        sendbuf.append(((sTime & 0xFF00) >> 8)) # 時間
        # チェックサムの計算
        sum = sendbuf[2]
        
        for x in range(3,11):
            sum = sum ^ sendbuf[x]

        sendbuf.append(sum) # チェックサム

        # 送信
        for x in range(12):
            self.ser.write(struct.pack('B',sendbuf.pop(0)));
        return
        
    def torque(self,sId,sMode):
        """
        サーボのトルクをON/OFFできる
        """
        # パケット作成
        sendbuf = []

        sendbuf.append(0xFA) #ヘッダー1
        sendbuf.append(0xAF) # ヘッダー2
        sendbuf.append(sId)  # サーボID
        sendbuf.append(0x00) # フラグ
        sendbuf.append(0x24) # アドレス(0x24=36)
        sendbuf.append(0x01) # 長さ(4byte)
        sendbuf.append(0x01) # 個数 
        sendbuf.append((sMode&0x00FF))
        
        #チェックサムの計算
        sum = sendbuf[2]

        for x in range(3,8):
            sum = sum ^ sendbuf[x]

        sendbuf.append(sum)

        #送信
        for x in range(9):
            self.ser.write(struct.pack('B',sendbuf.pop(0)))
        
        return
            
    def getAngle(self,sId):
        """
        サーボの現在角度を0.1度単位で得る
        可動範囲の中央を0として反時計方向に-150度，時計方向に150度の範囲
       
        """
        readbuf = self._getParam(sId);
        param1 =  struct.unpack('H',(readbuf[8]+ '\00'))[0]
        param2 =  struct.unpack('H',(readbuf[7]+ '\00'))[0]
        return ((param1 << 8) & 0x0000FF00) | (param2 & 0x000000FF) 
    
    def getTime(self,sId):
        """
         サーボが指令を受信し，移動を開始してからの経過時間を10msの単位で得る
         移動が完了すると最後の時間を保持する
        """
        readbuf = self._getParam(sId);
        param1 =  struct.unpack('H',(readbuf[10]+ '\00'))[0]
        param2 =  struct.unpack('H',(readbuf[9]+ '\00'))[0]
        return ((param1 << 8) & 0x0000FF00) | (param2 & 0x000000FF) 
    
    def getSpeed(self,sId):
        """
         サーボの現在回転スピードをdeg/sec単位で得る
         瞬間のスピードをあらわしている
        """
        readbuf = self._getParam(sId);
        param1 =  struct.unpack('H',(readbuf[12]+ '\00'))[0]
        param2 =  struct.unpack('H',(readbuf[11]+ '\00'))[0]
        return ((param1 << 8) & 0x0000FF00) | (param2 & 0x000000FF) 
        
    def getLoad(self,sId):
        """
        サーボの負荷をmA単位で得る
        """
        readbuf = self._getParam(sId);
        param1 =  struct.unpack('H',(readbuf[14]+ '\00'))[0]
        param2 =  struct.unpack('H',(readbuf[13]+ '\00'))[0]
        return ((param1 << 8) & 0x0000FF00) | (param2 & 0x000000FF) 
        
    def getTemperature(self,sId):
        """
        サーボの基板上の温度を得る
        温度センサには個体差により +-3度程度の誤差がある
        一度温度による保護機能が働くと，サーボをリセットする必要がある
        """
        readbuf = self._getParam(sId);
        param1 =  struct.unpack('H',(readbuf[16]+ '\00'))[0]
        param2 =  struct.unpack('H',(readbuf[15]+ '\00'))[0]
        return ((param1 << 8) & 0x0000FF00) | (param2 & 0x000000FF) 
    
    def getSpeed(self,sId):
        """
        サーボに供給されている電源の電圧を10mV単位で得る
        およそ+-0.3V程度の誤差がある
        """
        readbuf = self._getParam(sId);
        param1 =  struct.unpack('H',(readbuf[18]+ '\00'))[0]
        param2 =  struct.unpack('H',(readbuf[17]+ '\00'))[0]
        return ((param1 << 8) & 0x0000FF00) | (param2 & 0x000000FF) 
    
    
    def _getParam(self,sId):
        # パケット作成
        sendbuf = []
        
        sendbuf.append(0xFA) # ヘッダー1
        sendbuf.append(0xAF) # ヘッダー2
        sendbuf.append(sId) # サーボID
        sendbuf.append(0x09) # フラグ(0x01 | 0x04<<1)
        sendbuf.append(0x00) # アドレス(0x00)
        sendbuf.append(0x00) # 長さ(0byte)
        sendbuf.append(0x01) # 個数
        # チェックサムの計算
        sum = sendbuf[2];
        for x in range(3,7):
            sum = sum ^ sendbuf[x]
        
        sendbuf.append(sum) # チェックサム

        # 送信
        for x in range(8):
            self.ser.write(struct.pack('B',sendbuf.pop(0)))

        # 読み込み
        readbuf = []
        for x in range(26):
            readbuf.append(self.ser.read())

        return readbuf


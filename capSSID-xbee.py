import sys, csv, os, time
import subprocess
import urllib
import serial
import string, operator

def isPrintable(s):
    return all(c in string.printable for c in s)

def run_command(command):
    p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, shell=True)
    return iter(p.stdout.readline, b'')

if len(sys.argv) != 2:
    print 'Usage:', sys.argv[0], 'interface'

PORT = '/dev/ttyUSB0'
RATE = '115200'
ser = serial.Serial(PORT, RATE)
if ser.isOpen():
    print 'Serial opened:', PORT, RATE
else:
    print 'Cannot open serial.'
    sys.exit(1)

tsharkPara = ['-e wlan_mgt.ssid',
              '-e wlan.fc.subtype']

tsharkCmd = '/usr/bin/tshark ' + ' '.join(tsharkPara)
tsharkCmd += ' -T fields -E separator=,'
tsharkCmd += ' -i ' + sys.argv[1]
# set capture filter to capture probe response frames.
# tsharkCmd += ' -f "type mgt subtype proberesp"'
# set capture filter to capture beacon frames.
tsharkCmd += ' -f "type mgt"'

print 'Running:', tsharkCmd
print '=========='
content = []
ssidCnt = {}
startT = time.time()
lastReportT = time.time()
for aline in run_command(tsharkCmd):
    alist = aline.strip().split(',')
    if len(alist) != len(tsharkPara):
        print "error! # of fields =", len(alist), 'should be', len(tsharkPara), aline
        continue

    ssid = alist[0]
    subtype = int(alist[1])
    if ssid != '' and isPrintable(ssid):
            if ssid in ssidCnt:
                tmp = ssidCnt[ssid]
            else:
                tmp = [0,0,0,0,0] # total, beacon, req, resp, ?

            tmp[0] += 1
            if subtype == 8:
                tmp[1] += 1
            elif subtype == 4:
                tmp[2] += 1
            elif subtype == 5:
                tmp[3] += 1
            else:
                tmp[4] += 1
            ssidCnt[ssid] = tmp
            #print ssid, ssidCnt[ssid]
    else:
        print 'not printable SSID:', ssid
    if (time.time() - lastReportT) > 10:
        sortedCnt = sorted(ssidCnt.items(), key=operator.itemgetter(1,0), reverse=True)
        for i in range(min(len(sortedCnt), 5)):
            (s,cnt) = sortedCnt[i]
            ser.write('RPI: ' + s + '\t(' + str(cnt[0]) +',B:'+str(cnt[1]) +',Q:'+str(cnt[2]) +',R:'+str(cnt[3]) +',?:'+str(cnt[4]) +  ')\n\r')
            print 'RPI: ' + s + '\t(' + str(cnt) + ')'
            time.sleep(0.01)
        ssidCnt = {}
        lastReportT = time.time()
        print '======================================='
        ser.write('RPI: ===================\n\r')
print '=========='

print 'All done!'

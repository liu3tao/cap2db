import sys, csv, os
import subprocess

def run_command(command):
    p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, shell=True)
    return iter(p.stdout.readline, b'')

if len(sys.argv) != 2:
    print 'Usage:', sys.argv[0], 'cap file'

capFile = os.path.abspath(sys.argv[1])
csvFile = capFile[0 : capFile.rfind('.')] + '.csv'

tsharkPara = ['-e frame.time_epoch',
            '-e wlan.channel',
            '-e wlan.signal_strength',
            '-e wlan.data_rate',
            '-e wlan.ra',
            '-e wlan.da',
            '-e wlan.ta',
            '-e wlan.sa',
            '-e wlan.fc.type',
            '-e wlan.fc.subtype',
            '-e wlan.fc.retry',
            '-e frame.len',
            '-e wlan.seq',
            '-e wlan_mgt.fixed.beacon']

tsharkCmd = '/usr/bin/tshark ' + ' '.join(tsharkPara)
tsharkCmd += ' -T fields -E separator=,'
tsharkCmd += ' -r ' + capFile

print 'Running:', tsharkCmd
print '=========='
sys.exit()
content = []
for aline in run_command(tsharkCmd):
    alist = aline.strip().split(',')
    if len(alist) != len(tsharkPara):
        print "error! # of fields =", len(alist), 'should be', len(tsharkPara)
        continue
    content.append(alist)
print '=========='
print 'Writing to csv:', csvFile
with open(csvFile, 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(content)
print 'All done!'

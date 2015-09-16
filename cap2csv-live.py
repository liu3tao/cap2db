import sys, csv, os
import subprocess

def run_command(command):
    p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, shell=True)
    return iter(p.stdout.readline, b'')


def post2Influx(statement):
    prefix = "curl -i -XPOST 'http://localhost:8086/write?db=defcon1' --data-binary '"
    os.system(prefix + statement + "'")

def write2Influx(row):
    #print '==>', row
    try:
        if float(row[0]) <= 0.0:
            return
    except:
        return
    epoch_time  = row[0]
    channel     = row[1]
    signal      = row[2]
    drate       = row[3]
    rt_freq     = row[4]
    rt_signalDBM= row[5]
    rt_datarate = row[6]
    ra          = row[7]
    da          = row[8]
    ta          = row[9]
    sa          = row[10]
    fctype      = row[11]
    fcsubtype   = row[12]
    fcretry     = row[13]
    frame_len   = row[14]
    frame_seq   = row[15]
    beacon_interval = row[16]
        

    tstamp = epoch_time[:10] + epoch_time[11:]
    series = 'metainfo'
    st = series
    
    # tags
    if ra:
        st += ',receiver_addr=' + ra
    if da:
        st += ',dest_addr=' + da
    if ta:
        st += ',sender_addr=' + ta
    if sa:
        st += ',source_addr=' + sa
    if fctype:
        st += ',fc_type=' + fctype
    if fcsubtype:
        st += ',fc_subtype=' + fcsubtype
    if fcretry:
        st += ',fc_retry=' + fcretry
    # value
    st += ' '
    if not frame_len:
        return
    st += 'length=' + frame_len
    if channel:
        st += ',ieee_channel=' + channel
    if signal:
        st += ',signal_percent=' + signal
    if drate:
        st += ',data_rate=' + drate
    if rt_freq:
        st += ',frequency=' + rt_freq
    if rt_signalDBM:
        st += ',signal_dbm=' + rt_signalDBM
    if rt_datarate:
        st += ',datarate_Mbps=' + rt_datarate
    if frame_seq:
        st += ',frame_seq=' + frame_seq
    if beacon_interval:
        st += ',beacon_interval=' + beacon_interval
    #time stamp
    st += ' '
    st += tstamp
    st += '\n'
    
    write2Influx.count += 1
    write2Influx.buffer += st
    if write2Influx.count > 99:
        print '---'
        #print write2Influx.buffer
        #sys.exit(0)
        post2Influx(write2Influx.buffer)
        write2Influx.buffer = ''
        write2Influx.count = 0
    else:
        print '\r\r'+ str(write2Influx.count),
    
# init the counter
write2Influx.count = 0
write2Influx.buffer = ''

def post2Influx(statement):
    prefix = "curl -i -XPOST 'http://localhost:8086/write?db=live' --data-binary '"
    os.system(prefix + statement + "'")

if len(sys.argv) != 2:
    print 'Usage:', sys.argv[0], 'interface'

tsharkPara = ['-e frame.time_epoch',
            '-e wlan.channel',
            '-e wlan.signal_strength',
            '-e wlan.data_rate',
            '-e radiotap.channel.freq',
            '-e radiotap.dbm_antsignal',
            '-e radiotap.datarate',
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
tsharkCmd += ' -i ' + sys.argv[1]

print 'Running:', tsharkCmd
print '=========='
content = []
for aline in run_command(tsharkCmd):
    alist = aline.strip().split(',')
    if len(alist) != len(tsharkPara):
        print "error! # of fields =", len(alist), 'should be', len(tsharkPara)
        continue
    
    # print alist
    # Write to database
    write2Influx(alist)
print '=========='

print 'All done!'

import sys, csv, os, time
import subprocess
import urllib

def run_command(command):
    p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, shell=True)
    return iter(p.stdout.readline, b'')


def post2Influx(statement, hostname, db):
    prefix = "curl -i -XPOST 'http://" + hostname + "/write?db=" + db + "' --data-binary '"
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
    ssid        = row[17]
        

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
    if ssid:
        st += ',ssid='+urllib.quote(ssid)
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
    if len(write2Influx.buffer) > 50000:
        print '---- WRITE', write2Influx.count, 'PACKETS ----'
        t0 = time.time()
        #print write2Influx.buffer, sys.argv[1], sys.argv[2]
        #sys.exit(0)
        post2Influx(write2Influx.buffer, sys.argv[2], sys.argv[3])
        print '---- DONE IN', time.time() - t0, 'SECONDS ----'
        write2Influx.buffer = ''
        write2Influx.count = 0
    elif write2Influx.count % 100 == 0:
        print str(write2Influx.count)
    
# init the counter
write2Influx.count = 0
write2Influx.buffer = ''

if len(sys.argv) != 4:
    print 'Usage:', sys.argv[0], 'interface', 'db_host', 'db_name'

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
            '-e wlan_mgt.fixed.beacon',
            '-e wlan_mgt.ssid']

tsharkCmd = '/usr/bin/tshark ' + ' '.join(tsharkPara)
tsharkCmd += ' -T fields -E separator=,'
tsharkCmd += ' -i ' + sys.argv[1]

print 'Running:', tsharkCmd
print '=========='
content = []
startT = time.time()
for aline in run_command(tsharkCmd):
    alist = aline.strip().split(',')
    if len(alist) != len(tsharkPara):
        print "error! # of fields =", len(alist), 'should be', len(tsharkPara), aline
        continue
    
    # print alist
    # Write to database
    write2Influx(alist)
    if time.time() - startT > 3600: # exit after 1 hour to prevent pipe overflow.
        break
print '=========='

print 'All done!'

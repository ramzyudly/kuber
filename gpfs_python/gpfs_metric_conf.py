import os
import time

host = os.popen("hostname").read().split(".")[0].rstrip()
# Check labels
def get_labels(metric):
    lbl = []
    for key in metric.keys():
        for name in metric[key].keys():
            if name not in lbl:
                lbl.append(name)
    return lbl

# 1. Check mmfsd daemon status:
def gpfs_daemon_status(name):
    info = {}
    ds = [name]
    status = os.system("ps -ef | grep " + name + " | grep -v grep > /dev/null ")
    if status == 0:
        mmfsd_status = 1
    else:
        mmfsd_status = 0
    info[name] = {
        "daemon_status": mmfsd_status,
        "server": host,
    }
    return info, info[name]['daemon_status']

# 2. Get GPFS mount status:
def get_mount_status(name):
    info = {}
    ms = [name]
    status = os.system("df -hP " + name + " > /dev/null")
    if status != 0:
        mount = 0
    else:
        mount = 1
    info[name] = {
        "mount_status": mount,
        "server": host,
    }
    return info,info[name]['mount_status']

# 3. GPFS nsd status:
class nsd_details:
    def __init__(self, device):
        self.device = device
        server = []
        try:
            #data = os.popen("/usr/lpp/mmfs/bin/mmlsdisk " + self.device + " -m | grep localhost").read()
            data = os.popen("/usr/lpp/mmfs/bin/mmlsnsd | grep " + host).read()
            for item in data.splitlines()[0:]:
                info = item.rsplit()
                server.append(info[1])
        except:
            pass
        self.server_list = server

    def get_gpfs_device_nsds(self):
        info = {}
        data = os.popen("/usr/lpp/mmfs/bin/mmlsdisk" + " " + self.device).read()
        for item in data.splitlines()[1:]:
            disk_info = item.rsplit()
            if disk_info[6] == 'ready':
                stat = 1
            else:
                stat = 0
            if disk_info[0] in self.server_list:
                info[disk_info[0]] = {
                    # "holds_metadata": disk_info[4],
                    # "holds_data": disk_info[5],
                    "nsd_status": stat,
                    # "availability": disk_info[7],
                    "storage_pool": disk_info[-1],
                    "server": host,
                }
        return info

# 4. GPFS should be writable
def check_writable(dir):
    info = {}
    testfile = dir + '/testfile_' + time.strftime("%Y%m%d_%H%M%S") + '.txt'
    try:
        fh = open(testfile, 'w')
        fh.write('checking gpfs is writable or not \n')
        fh.close()
        if os.path.exists(testfile):
            info[dir] = {
                "gpfs_write_status": 1,
                "server": host,
            }
            os.remove(testfile)
            if os.path.exists(testfile):
                print('unable to delete testfile.txt')
            return info
    except:
        info[dir] = {
            "gpfs_write_status": 0,
            "server": host,
        }
        return info

# 5. GPFS disk space utilization:
def get_gpfs_mount_info(device):
    info1 = {}
    info2 = {}
    info3 = {}
    data = os.popen("df -P | grep " + device).read()
    for item in data.splitlines()[0:]:
        mount_info = item.rsplit()
        info1[mount_info[-1]] = {
            "total_size": mount_info[1],
        }
        info2[mount_info[-1]] = {
            "disk_used": mount_info[2],
        }
        info3[mount_info[-1]] = {
            "disk_available": mount_info[2],
        }
    return info1, info2, info3


# 6. GPFS pool status:
def get_gpfs_device_pools(device):
    info = {}
    data = os.popen("/usr/lpp/mmfs/bin/mmlspool" + " " + device).read()

    for item in data.splitlines()[2:]:
        pool_info = item.rsplit()
        info[pool_info[0]] = {
            "id": pool_info[1],
            "block_size": pool_info[2],
            "data": pool_info[4],
            "meta": pool_info[5],
            "total": pool_info[6],
            "free": pool_info[7],
        }
    return info


# 7. GPFS Filesets:
# Fileset can be sent as an argument. --all will scheck status for all filesets.
def get_gpfs_filesets(device, fs_name):
    info = {}
    if fs_name == 'all':
        data = os.popen("/usr/lpp/mmfs/bin/mmlsfileset" + " " + device).read()
    else:
        data = os.popen("/usr/lpp/mmfs/bin/mmlsfileset" + " " + device + " " + fs_name).read()
    for item in data.splitlines()[2:]:
        fs_info = item.rsplit()
        if fs_info[1] == 'Linked':
            fs_stat = 1
        else:
            fs_stat = 0
        info[fs_info[0]] = {
            "fileset_status": fs_stat,
            "server": host,
            "path": fs_info[2]
        }
    return info

# 8. GPFS status:
def get_gpfs_status(stat_metric, key_value):
    info = {}
    if key_value[1] == 1 and 0 not in stat_metric:
        stat = 1
    else:
        stat = 0
    info['gpfs'] = {
        "status": stat,
        "server": host,
        "write_dir": key_value[0],
    }
    return info

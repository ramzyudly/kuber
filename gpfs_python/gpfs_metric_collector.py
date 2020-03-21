import gpfs_metric_conf as f
import ConfigParser
#import configparser
from gpfs_metric_conf import nsd_details
from custom_collector import CollectMetric
import os

if __name__ == '__main__':
    host = os.popen("hostname").read().split(".")[0]
    ## Read configuration from the conf file
    config = ConfigParser.ConfigParser()
    #config = configparser.ConfigParser()
    config.read("config.conf")

    device=config.get("input_checks","gpfs_device")
    daemon_name=config.get("input_checks","gpfs_daemon")
    mount=config.get("input_checks","mount_name")
    dir_name=config.get("input_checks","dir_list")
    fs_name=config.get("fileset_inputs","fileset_name")

    metric_filename=config.get("metric_file","output_file")
    gpfs_stat = []
    gpfs_write = {}
    try:
        with open(metric_filename,'w') as file:
            print('mmfsd daemon status')
            x, aa = f.gpfs_daemon_status(daemon_name)
            gpfs_stat.append(aa)
            my_new_out = CollectMetric(x, labels=f.get_labels(x), key_name="daemon").collect()
            for line in my_new_out:
                file.write(line + '\n')

            print('gpfs mount status')
            m, bb = f.get_mount_status(mount)
            gpfs_stat.append(bb)
            my_new_out = CollectMetric(m, labels=f.get_labels(m), key_name="mount").collect()
            for line in my_new_out:
                file.write(line + '\n')

            print('gpfs writable')
            dirs = [i for i in dir_name.split(',')]
            for dy in range(0, len(dirs)):
                w = f.check_writable(dirs[dy])
                cc = w[dirs[dy]]['gpfs_write_status']
                gpfs_write[dirs[dy]] = cc
                my_new_out = CollectMetric(w, labels=f.get_labels(w), key_name="directory").collect()
                for line in my_new_out:
                    file.write(line + '\n')

            print('gpfs status')
            for values in gpfs_write.items():
                g = f.get_gpfs_status(gpfs_stat, values)
                my_new_out = CollectMetric(g, labels=f.get_labels(g), key_name="metric").collect()
                for line in my_new_out:
                    file.write(line + '\n')

            print('gpfs disk usage')
            p, q, r = f.get_gpfs_mount_info(device)
            my_new_out = CollectMetric(p, labels=f.get_labels(p), key_name="mount").collect()
            for line in my_new_out:
                file.write(line + '\n')

            my_new_out = CollectMetric(q, labels=f.get_labels(q), key_name="mount").collect()
            for line in my_new_out:
                file.write(line + '\n')

            my_new_out = CollectMetric(r, labels=f.get_labels(r), key_name="mount").collect()
            for line in my_new_out:
                file.write(line + '\n')

            print('nsd status')
            nd = nsd_details(device)
            b = nd.get_gpfs_device_nsds()
            try:
                my_new_out = CollectMetric(b, labels=f.get_labels(b), key_name="nsd").collect()
                for line in my_new_out:
                    file.write(line + '\n')
            except:
                pass

            print('filesets')
            e = f.get_gpfs_filesets(device, fs_name)
            my_new_out = CollectMetric(e, labels=f.get_labels(e), key_name="fileset").collect()
            for line in my_new_out:
                file.write(line + '\n')

            """
            print('device pool')
            d = f.get_gpfs_device_pools(device)
            my_new_out = CollectMetric(d, labels=f.get_labels(d), key_name="pool").collect()
            for line in my_new_out:
                file.write(line + '\n')
            """
    except:
        pass

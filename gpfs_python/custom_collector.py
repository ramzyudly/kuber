import time

class CollectMetric():
    def __init__(self, metric, labels, key_name):
        self.metric = metric
        self.labels = labels
        self.key_name = key_name
        labels[0] = self.key_name
        # print(self.labels)

    def collect(self):
        # print('# HELP ' + name + 'Help text')
        # print('# HELP' + name + 'Help text')
        final_out = []
        global m
        for key in self.metric.keys():
            part = self.key_name + '=' + '"' + key + '"'
            for i in self.metric[key].keys():
                if i not in self.labels:
                    m = i
                else:
                    part = part + ',' + i + '=' + '"' + self.metric[key][i] + '"'
            out = m + '{' + part + '} ' + str(self.metric[key][m])
            final_out.append(out)
        return final_out

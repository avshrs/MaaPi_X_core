class CheckDevCond:

   def conditions(self,devices_db, dev_id, value):
        condition_min   = False
        condition_max   = False
        condition       = False
        condition_min_max = False
        force           = False
        # if collect values is enabled
        condition = devices_db[dev_id]['dev_collect_values_if_cond_e']
        if condition:

            #if cond. from dev is enabled and id is not empty
            if devices_db[dev_id]['dev_collect_values_if_cond_from_dev_e'] and devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']:

                #if cond. min ebaled and value is not none
                if devices_db[dev_id]['dev_collect_values_if_cond_min_e'] and devices_db[dev_id]['dev_collect_values_if_cond_min']:

                    #if value from releted dev is less then min value
                    if devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_value'] < devices_db[dev_id]['dev_collect_values_if_cond_min']:
                        condition_min = True
                    else:
                        condition_min = False
                else:
                    condition_min = False

                if devices_db[dev_id]['dev_collect_values_if_cond_max_e'] and devices_db[dev_id]['dev_collect_values_if_cond_max']:

                    if devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_value'] > devices_db[dev_id]['dev_collect_values_if_cond_max']:
                        condition_max = True
                    else:
                        condition_max = False
                else:
                    condition_max = False
            else:

                if devices_db[dev_id]['dev_collect_values_if_cond_min_e'] and devices_db[dev_id]['dev_collect_values_if_cond_min']:
                    if value <= devices_db[dev_id]['dev_collect_values_if_cond_min']:
                        condition_min = True
                    else:
                        condition_min = False
                else:
                    condition_min = False
                if devices_db[dev_id]['dev_collect_values_if_cond_max_e'] and devices_db[dev_id]['dev_collect_values_if_cond_max']:
                    if value >= devices_db[dev_id]['dev_collect_values_if_cond_max']:
                        condition_max = True
                    else:
                        condition_max = False
                else:
                    condition_max = False

            if condition_max == False or condition_min == True:
                condition_min_max = False
            else:
                condition_min_max = True

            if condition_min_max == False:
                if devices_db[dev_id]['dev_collect_values_if_cond_force_value_e']:
                    force = devices_db[dev_id]['dev_collect_values_if_cond_force_value']

        return condition,condition_min_max, force

    def checkDevCond(self, devices_db, dev_id, value):
        condition, condition_min_max, force_value  = self.conditions(devices_db, dev_id)
        if condition:
            if condition_min_max:
                return value
            else:
                return value
        else:
            return value

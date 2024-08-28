from prometheus_client import Counter, Summary

pm_counter_consume_sucess_counter = Counter('rApp_consume_sucessful_pm_counter_messages', 'Number of consumed message from pm counter topic')
pm_counter_consume_failure_counter = Counter('rApp_consume_fail_pm_counter_message', 'Number of consumed message from pm counter topic')
pm_event_4g_consume_sucess_counter = Counter('rApp_consume_sucessful_4G_pm_event_messages', 'Number of consumed message from 4g pm event topic')
pm_event_4g_consume_failure_counter = Counter('rApp_consume_fail_4G_pm_event_message', 'Number of consumed message from 4g pm event topic')
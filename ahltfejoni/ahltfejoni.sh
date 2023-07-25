#!/bin/bash

# $oc_login
OC_LOGIN_COMMAND=$oc_login

login using oc command
if [ -n "$OC_LOGIN_COMMAND" ];then
    $OC_LOGIN_COMMAND
fi

if [ $? != 0 ];then
    echo "Error logging in to OpenShift, please check your credentials"
    exit 1
fi

#### check cluster nodes ####
ready_nodes=0
total_nodes=$(oc get nodes --no-headers | wc -l)
start_time=$(date +%s)
timeout=60

while [ $ready_nodes -ne $total_nodes ]
do
    oc get nodes | awk 'BEGIN{print "+--------------------------+"}{printf "| %-15s | %s |\n", $1, $2}END{print "+--------------------------+"}'
    node_status=$(oc get nodes --no-headers | awk '{print $2}')
    ready_nodes=$(echo "$node_status" | grep -c "^Ready$")
    total_nodes=$(echo "$node_status" | wc -l)
    echo "Ready Node(s): $ready_nodes/$total_nodes"

    if [ $ready_nodes -ne $total_nodes ]; then
        sleep 5s
    fi
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [[ $elapsed_time -gt $timeout ]]; then
        echo "Timeout reached. Some node(s) is/are not in Ready state."
        break
    fi
done

#####For testing, get the unready state of a node by manually stopping the Kubernetes services on that node.#####
#i.e. run below comand in the node terminal
#systemctl stop kubelet
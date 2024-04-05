#!/bin/bash

RED='\033[0;31m'       #  ${RED}
GREEN='\033[0;32m'     #  ${GREEN}
CYAN='\033[0;36m'       #  ${CYAN}
YELLOW='\033[0;33m'     #  ${YELLOW}
NOCOL=$(tput sgr0)
STATUS_POSITION="\033[60G"

status_busy() {
  echo -ne "    $@ $STATUS_POSITION${CYAN} busy $NOCOL"
  SUCCESS=0
}

status_done() {
  echo -e "$STATUS_POSITION${GREEN} done $NOCOL"
}

status_failed() {
  echo -e "$STATUS_POSITION${RED}failed$NOCOL"
  echo -ne "${YELLOW}exit code $@${NOCOL}"
  echo
  exit 1
}

status_unknown() {
  echo -e "$STATUS_POSITION${YELLOW}unknown$NOCOL"
}


if [[ $1 == "" ]]
    then
      echo available commands are:
      >&2 echo -e "    ${YELLOW}node_create_full$@${NOCOL}               recreate node from scratch and run"
      >&2 echo -e "    ${YELLOW}create_container_from_scratch$@${NOCOL}  only create node from scratch"
      >&2 echo -e "    ${YELLOW}reconfigure_node_vpn$@${NOCOL}           reconfigure node vpn"
      >&2 echo -e "    ${YELLOW}reconfigure_vpn_decl$@${NOCOL}           reconfigure vpn declaratively (provide full vpn name)"      
      >&2 echo -e "    ${YELLOW}node_stop$@${NOCOL}                      stop node docker container"
      >&2 echo -e "    ${YELLOW}node_start$@${NOCOL}                     start node docker container"
      >&2 echo -e "    ${YELLOW}node_stop_remove$@${NOCOL}               stop and remove node docker container"
      >&2 echo -e "    ${YELLOW}node_set_storage$@${NOCOL}               setup storage and restart node docker container"
      >&2 echo -e "    ${YELLOW}debug$@${NOCOL}                          debug node config"
      >&2 echo
      exit
fi

# if ! [[ $2 =~ ^[0-9]+$ ]]
#     then
#         >&2 echo "Only integers allowed"
#         exit
# fi

create_container_from_scratch() {
  status_busy "create node docker container from scratch"
  NODE_ID=$@
  if (ansible-playbook playbooks/create_node_docker_container_from_scratch.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

start_node_docker_contaier() {
  status_busy "start node docker container"
  NODE_ID=$@
  if (ansible-playbook playbooks/start_node_docker_container.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

stop_node_docker_contaier() {
  status_busy "stop node docker container"
  NODE_ID=$@
  if (ansible-playbook playbooks/stop_node_docker_container.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

remove_node_docker_contaier() {
  status_busy "remove node docker container"
  NODE_ID=$@
  if (ansible-playbook playbooks/remove_node_docker_container.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

generate_session_config() {
  status_busy "generate session config"
  NODE_ID=$@
  SESSION_CONFIG="/tmp/${UUID}.json"
  if (ansible-playbook playbooks/generate_session_config.yml -i ${INVENTORY} --extra-vars "SESSION_CONFIG=${SESSION_CONFIG} NODE_ID=$NODE_ID CONFIG_PATH=${CONFIG_PATH}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

node_create_full() {
  status_busy "recreate node from scratch and run"
  NODE_ID=$@
  if (ansible-playbook playbooks/node_create_full.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

reconfigure_node_vpn() {
  status_busy "reconfigure node vpn"
  NODE_ID=$@
  if (ansible-playbook playbooks/reconfigure_node_vpn.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

reconfigure_vpn_decl() {
  status_busy "reconfigure vpn declaratively"
  VPN=$@
  if (ansible-playbook playbooks/vpn_reconfigure_declaratively.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" --extra-vars ahost=${VPN} >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

reconfigure_node_mikrotik() {
  status_busy "reconfigure node mikrotik"
  NODE_ID=$@
  if (ansible-playbook playbooks/reconfigure_node_mikrotik.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}" >> log.log 2>> log.log)
  then
    status_done
  else
    status_failed $?
  fi
}

building_static_inventory() {
  status_busy "building static inventory"
  if (python3 scripts/_build_inventory.py ${CONFIG_PATH} >> log.log 2>> log.log)
  then 
    status_done
  else
    status_failed
  fi
}

debug() {
  status_busy "debug node config"
  NODE_ID=$@
  if (ansible-playbook playbooks/debug.yml -i ${INVENTORY} --extra-vars "@${SESSION_CONFIG}")
  then
    status_done
  else
    status_failed $?
  fi
}



. .env
UUID=$(cat /proc/sys/kernel/random/uuid)
SESSION_CONFIG="/tmp/${UUID}.json"
NODE_CONFIG="/tmp/$2.json"
INVENTORY=${CONFIG_PATH}/inventory
echo inventory is ${INVENTORY}
echo session config is ${SESSION_CONFIG}
echo -e "node config is ${CYAN}${NODE_CONFIG}${NOCOL}"

source venv/bin/activate

building_static_inventory
#python3 ./playbooks/_build_hosts.py

if [[ $1 == 'node_create_full' ]]
then
  NODE_ID=$2
  generate_session_config ${NODE_ID}
  create_container_from_scratch ${NODE_ID}
  # reconfigure_node_mikrotik ${NODE_ID}
  reconfigure_node_vpn ${NODE_ID}
  start_node_docker_contaier ${NODE_ID}
fi

if [[ $1 == 'create_container_from_scratch' ]]
then
  NODE_ID=$2
  generate_session_config ${NODE_ID}
  create_container_from_scratch ${NODE_ID}
fi

if [[ $1 == 'debug' ]]
then
  NODE_ID=$2
  generate_session_config ${NODE_ID}
  jq --sort-keys . ${NODE_CONFIG}
  jq --sort-keys . ${SESSION_CONFIG}
  # debug ${NODE_ID}
fi

if [[ $1 == 'node_stop' ]]
then
  NODE_ID=$2
  generate_session_config ${NODE_ID}
  stop_node_docker_contaier ${NODE_ID}
fi

if [[ $1 == 'node_start' ]]
then
  NODE_ID=$2
  generate_session_config ${NODE_ID}
  start_node_docker_contaier ${NODE_ID}
fi

if [[ $1 == 'node_set_storage' ]]
then
  NODE_ID=$2
  STORAGE=$3
  cat <<< $(jq --arg storage "$STORAGE" '.NODE_STORAGE |= $storage' ${CONFIG_PATH}/configuration_items/node/${NODE_ID}/config) > ${CONFIG_PATH}/configuration_items/node/${NODE_ID}/config
  cat <<< $(jq '.NODE_STORAGE |= tonumber' ${CONFIG_PATH}/configuration_items/node/${NODE_ID}/config) > ${CONFIG_PATH}/configuration_items/node/${NODE_ID}/config
  generate_session_config ${NODE_ID}
  create_container_from_scratch ${NODE_ID}
  start_node_docker_contaier ${NODE_ID}
fi

if [[ $1 == 'node_stop_remove' ]]
then
  NODE_ID=$2
  generate_session_config ${NODE_ID}
  remove_node_docker_contaier ${NODE_ID}
fi


if [[ $1 == 'reconfigure_vpn_decl' ]]
then
  VPN=$2
  generate_session_config 101
  reconfigure_vpn_decl ${VPN}
fi
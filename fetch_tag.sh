#!/bin/bash

##
## fetch_tag.sh
## retrieve latest tag from repo
##

## functions
function die { echo "$*" 1>&2 && exit 1; }

## checkout master branch of repo
function clone_repo {
  local repo_name=$1
  local git_url=$2
  ## cleanup any existing directories
  [[ -d /tmp/${repo_name} ]] && rm -rf /tmp/${repo_name}  
  cd /tmp && git clone --quiet ${git_url}
  echo "/tmp/${repo_name}"
}

function checkout_branch {
  local branch=$1
  local repo_path=$2
  ## cleanup any existing directories
  cd ${repo_path} && git checkout --quiet ${branch}
}

## fetch release tag from production branch
function fetch_tag {
  local repo_path=$1
  [[ -d ${repo_path} ]] && cd ${repo_path}
  local git_tag=$(git describe --abbrev=0 --tags)
  printf "%s\n" ${git_tag}
}

function cleanup {
  local repo_path=$1
  rm -rf ${repo_path}
}

function usage() {
  echo "Usage: $0 -g [GIT_TOKEN] -r [repo_name]" && exit 1
}
## end functions

## main
PATH=bin:/usr/local/bin:/usr/local/sbin:/bin:/sbin:/usr/bin:/usr/sbin

while getopts ":r:g:" opt; do
  case $opt in
    r) REPO_NAME=${OPTARG}
      ;;
    g) GIT_TOKEN=${OPTARG}
      ;;
  esac
done

## require file (packer json)
[[ -z $REPO_NAME ]] && usage

## specify git url
[[ ! -z $GIT_TOKEN ]] && git_url=https://${GIT_TOKEN}@github.com/brukshut/${REPO_NAME}.git ||
  GIT_URL=https://github.com/brukshut/${REPO_NAME}.git

LOCAL_REPO=$(clone_repo $REPO_NAME $GIT_URL)
checkout_branch master ${LOCAL_REPO}
fetch_tag ${LOCAL_REPO} && cleanup ${LOCAL_REPO}

## end main

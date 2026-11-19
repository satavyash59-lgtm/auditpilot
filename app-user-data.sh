#!/bin/bash
set -eux

dnf update -y
dnf install -y docker awscli

systemctl enable --now docker

mkdir -p /opt/auditpilot

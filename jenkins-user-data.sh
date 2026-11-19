#!/bin/bash
set -eux

apt-get update -y
apt-get install -y fontconfig openjdk-21-jre docker.io curl unzip

systemctl enable --now docker

mkdir -p /usr/share/keyrings
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  -o /usr/share/keyrings/jenkins-keyring.asc

echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  > /etc/apt/sources.list.d/jenkins.list

apt-get update -y
apt-get install -y jenkins

usermod -aG docker jenkins
systemctl enable jenkins
systemctl restart jenkins

curl -fsSL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip \
  -o /tmp/awscliv2.zip

unzip -q /tmp/awscliv2.zip -d /tmp
/tmp/aws/install

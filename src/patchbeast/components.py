"""Static registry of server components PatchBeast can detect.

Each entry maps a human-readable component name to the binary used for
detection, the arguments used to query its version, and the Debian/Ubuntu
``apt`` package used for updates (``None`` means detect-only).
"""

from __future__ import annotations

from typing import TypedDict


class Component(TypedDict):
    """A single detectable server component."""

    name: str
    command: str
    args: str
    package: str | None


COMPONENTS: list[Component] = [
    {"name": "PHP", "command": "php", "args": "-v", "package": "php"},
    {"name": "Python", "command": "python3", "args": "--version", "package": "python3"},
    {"name": "Node.js", "command": "node", "args": "--version", "package": "nodejs"},
    {"name": "npm", "command": "npm", "args": "--version", "package": None},
    {"name": "Apache", "command": "apache2", "args": "-v", "package": "apache2"},
    {"name": "Nginx", "command": "nginx", "args": "-v", "package": "nginx"},
    {"name": "Lighttpd", "command": "lighttpd", "args": "-v", "package": "lighttpd"},
    {"name": "Caddy", "command": "caddy", "args": "version", "package": None},
    {"name": "Git", "command": "git", "args": "--version", "package": "git"},
    {"name": "curl", "command": "curl", "args": "--version", "package": "curl"},
    {"name": "OpenSSL", "command": "openssl", "args": "version", "package": "openssl"},
    {"name": "MySQL Client", "command": "mysql", "args": "--version", "package": "mysql-client"},
    {"name": "MariaDB", "command": "mariadb", "args": "--version", "package": "mariadb-server"},
    {"name": "PostgreSQL", "command": "postgres", "args": "--version", "package": "postgresql"},
    {"name": "Redis", "command": "redis-server", "args": "--version", "package": "redis-server"},
    {"name": "MongoDB", "command": "mongod", "args": "--version", "package": "mongodb-org"},
    {"name": "SQLite", "command": "sqlite3", "args": "--version", "package": "sqlite3"},
    {"name": "Composer", "command": "composer", "args": "--version", "package": None},
    {"name": "Java", "command": "java", "args": "-version", "package": "default-jre"},
    {"name": "Go", "command": "go", "args": "version", "package": "golang"},
    {"name": "Ruby", "command": "ruby", "args": "--version", "package": "ruby"},
    {"name": "Perl", "command": "perl", "args": "--version", "package": "perl"},
    {"name": "Docker", "command": "docker", "args": "--version", "package": "docker.io"},
    {"name": "Podman", "command": "podman", "args": "--version", "package": "podman"},
    {"name": "Plesk", "command": "plesk", "args": "version", "package": None},
    {"name": "cPanel", "command": "cat", "args": "/usr/local/cpanel/version", "package": None},
    {"name": "DirectAdmin", "command": "/usr/local/directadmin/directadmin", "args": "v", "package": None},
    {"name": "Webmin", "command": "webmin", "args": "--version", "package": "webmin"},
    {"name": "Postfix", "command": "postfix", "args": "mail_version", "package": "postfix"},
    {"name": "Dovecot", "command": "dovecot", "args": "--version", "package": "dovecot-core"},
    {"name": "Fail2ban", "command": "fail2ban-client", "args": "version", "package": "fail2ban"},
    {"name": "UFW", "command": "ufw", "args": "version", "package": "ufw"},
    {"name": "ClamAV", "command": "clamscan", "args": "--version", "package": "clamav"},
    {"name": "Memcached", "command": "memcached", "args": "-V", "package": "memcached"},
    {"name": "Varnish", "command": "varnishd", "args": "-V", "package": "varnish"},
    {"name": "HAProxy", "command": "haproxy", "args": "-vv", "package": "haproxy"},
    {"name": "Supervisor", "command": "supervisord", "args": "--version", "package": "supervisor"},
    {"name": "Elasticsearch", "command": "elasticsearch", "args": "--version", "package": "elasticsearch"},
    {"name": "RabbitMQ", "command": "rabbitmqctl", "args": "version", "package": "rabbitmq-server"},
    {"name": "Kafka", "command": "kafka-topics.sh", "args": "--version", "package": None},
    {"name": "Grafana", "command": "grafana-server", "args": "-v", "package": "grafana"},
    {"name": "Prometheus", "command": "prometheus", "args": "--version", "package": "prometheus"},
    {"name": "Zabbix Agent", "command": "zabbix_agentd", "args": "--version", "package": "zabbix-agent"},
    {"name": "Jenkins", "command": "jenkins", "args": "--version", "package": "jenkins"},
    {"name": "GitLab Runner", "command": "gitlab-runner", "args": "--version", "package": "gitlab-runner"},
    {"name": "aaPanel", "command": "bt", "args": "version", "package": None},
    {"name": "CyberPanel", "command": "cyberpanel", "args": "--version", "package": None},
    {"name": "Virtualmin", "command": "virtualmin", "args": "version", "package": None},
    {"name": "Traefik", "command": "traefik", "args": "version", "package": None},
    {"name": "Keepalived", "command": "keepalived", "args": "--version", "package": "keepalived"},
    {"name": "etcd", "command": "etcd", "args": "--version", "package": "etcd-server"},
    {"name": "Consul", "command": "consul", "args": "version", "package": None},
    {"name": "Vault", "command": "vault", "args": "version", "package": None},
    {"name": "MinIO", "command": "minio", "args": "--version", "package": None},
    {"name": "HestiaCP", "command": "hestia", "args": "version", "package": None},
    {"name": "Froxlor", "command": "froxlor", "args": "--version", "package": None},
    {"name": "ISPConfig", "command": "ispconfig", "args": "--version", "package": None},
    {"name": "CWP", "command": "cwp", "args": "--version", "package": None},
    {"name": "Exim", "command": "exim", "args": "--version", "package": "exim4"},
    {"name": "SpamAssassin", "command": "spamassassin", "args": "--version", "package": "spamassassin"},
    {"name": "Amavis", "command": "amavisd-new", "args": "--version", "package": "amavisd-new"},
    {"name": "ClickHouse", "command": "clickhouse-server", "args": "--version", "package": "clickhouse-server"},
    {"name": "TimescaleDB", "command": "timescaledb", "args": "--version", "package": "timescaledb-2-postgresql-16"},
    {"name": "InfluxDB", "command": "influxd", "args": "version", "package": "influxdb"},
    {"name": "CouchDB", "command": "couchdb", "args": "-V", "package": "couchdb"},
    {"name": "Cassandra", "command": "cassandra", "args": "--version", "package": "cassandra"},
    {"name": "Neo4j", "command": "neo4j", "args": "version", "package": "neo4j"},
    {"name": "KeyDB", "command": "keydb-server", "args": "--version", "package": "keydb"},
    {"name": "Dragonfly", "command": "dragonfly", "args": "--version", "package": None},
    {"name": "Uptime Kuma", "command": "uptime-kuma", "args": "--version", "package": None},
    {"name": "Nagios", "command": "nagios", "args": "--version", "package": "nagios4"},
    {"name": "Portainer", "command": "portainer", "args": "--version", "package": None},
    {"name": "containerd", "command": "containerd", "args": "--version", "package": "containerd"},
    {"name": "k3s", "command": "k3s", "args": "--version", "package": None},
    {"name": "kubectl", "command": "kubectl", "args": "version --client", "package": "kubectl"},
    {"name": "Helm", "command": "helm", "args": "version", "package": None},
    {"name": "Ansible", "command": "ansible", "args": "--version", "package": "ansible"},
    {"name": "Terraform", "command": "terraform", "args": "version", "package": None},
    {"name": "Packer", "command": "packer", "args": "version", "package": None},
    {"name": "Vagrant", "command": "vagrant", "args": "--version", "package": None},
    {"name": "Puppet", "command": "puppet", "args": "--version", "package": "puppet"},
    {"name": "Chef", "command": "chef-client", "args": "--version", "package": "chef"},
    {"name": "Salt", "command": "salt-minion", "args": "--version", "package": "salt-minion"},
    {"name": "Rust", "command": "rustc", "args": "--version", "package": "rustc"},
    {"name": "Deno", "command": "deno", "args": "--version", "package": None},
    {"name": "Bun", "command": "bun", "args": "--version", "package": None},
    {"name": "Elixir", "command": "elixir", "args": "--version", "package": "elixir"},
    {"name": "Erlang", "command": "erl", "args": "-version", "package": "erlang"},
    {"name": "Gitea", "command": "gitea", "args": "--version", "package": None},
    {"name": "Drone", "command": "drone", "args": "--version", "package": None},
    {"name": "Netdata", "command": "netdata", "args": "-v", "package": "netdata"},
]

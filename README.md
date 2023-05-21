# OPNSense Control Center

Solution to centrally manage [OPNSense firewalls](https://github.com/opnsense).

The idea is to create a hub that communicates to multiple firewalls and let you manage them using their Rest-HTTP-APIs.

The API interaction will mainly be done using [Ansible](https://www.ansible.com).

Status updates may be fetched using plain Python3.

----

## Development

Feel free to..

* [start a discussion](https://github.com/ansibleguy/opnsense-control-center/discussions)
* [file issues](https://github.com/ansibleguy/opnsense-control-center/issues)
* [contribute by creating pull-requests](https://github.com/ansibleguy/opnsense-control-center/pulls)

### Web Development

**PLEASE**: The project currently is lacking Web-Frontend experience.

If you are interested to contribute some of your time => reach out to [guy@ansibleguy.net](mailto:guy@ansibleguy.net)


### DEVELOPMENT IN PROGRESS!

Not yet in a usable state!

----

## Main parts

* [OPNSense Ansible Collection](https://github.com/ansibleguy/collection_opnsense)

* [Semaphore Ansible WebUI](https://github.com/ansible-semaphore/semaphore)

* [Graylog for centralized logging incl. analysis and alerting](https://github.com/Graylog2/graylog2-server)

* [Config and information versioning using git (with WebUI)](https://github.com/gogs/gogs)

* [Config management using Web IDE/Editor](https://github.com/coder/code-server)

* [OAuth Proxy if you want to use you IDP](https://github.com/oauth2-proxy/oauth2-proxy)

* custom WebUI to
  * manage configuration

* management service
  * checking firewalls for config changes => history using VCS
    * pulling xml-config
    * relevant filesystem config-directories
    * ansible-playbooks in 'check-mode'
  * alerting rules if changes are found

----

## Services

Services use docker-compose to manage docker containers.

```bash
.
├── nginx.service  # web proxy, handles authentication
└── docker.service
    ├── opn-cc-ansible.service
    │   └── semaphoreui/semaphore
    ├── opn-cc-ide.service  # Web-IDE/Editor
    │   └── codercom/code-server
    ├── opn-cc-log.service  # log server
    │   ├── graylog/graylog
    │   ├── mongo
    │   └── opensearchproject/opensearch
    └── opn-cc-vcs.service  # version control system
        └── gogs/gogs
```

----

## Thoughts

* CC WebUI routing should allow easy switching between components
  * maybe use iframe for sub-components with small component-navigation on-top

* Connection to CC
  * active - target has static IP that can be reached by CC
  * passive - target needs to start a vpn-tunnel (wireguard) for the management connection; CC needs to have a static IP
    * vpn would also be good to have to enable us to use 'unencrypted' data-transfers like out-of-the-box syslog log-forwarding
  * optional: CC should have a client-network that allows proxied access to firewall webUI, ssh and so on (useful if passive connection is used)

* Switches for..
  * Centralized logging
    * insert syslog forwarding

* Dashboard/Box overview
  * have history settings for those stats/infos
  * switches for different types
  * like opnsense widgets
    * firmware version
    * response time/latency
    * hardware
    * online status (ping, tcp check on webUI and optional any custom port)
    * service status
    * resources (cpu, ram, disk, ...)
    * diagnostics api results
    * gateway status

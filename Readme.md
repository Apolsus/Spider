# Ensp Confige Generator

## Introduction

A simple tool to generate the configuration file for the ENSP simulator, support configure version v7

## Usage

1. modify the `config.json` file to fit your needs
2. run the `parser.py` script
3. check res for the generated configuration file

## Warning

1. The bgp group function is buggy, help wanted!

## TODO List

Features I will implement when I have time (and interest or money)

-[ ] A drag-and-drop front-end UI (Reference to https://github.com/Tidlo/netweaver)
-[ ] A simulator for complex static config check
-[ ] Support difference version of ENSP

## Develop

If you want to participate in the development you need to know the necessary knowledge

```
├── check.py    # Config checker, complex check relies on the simulator
├── config.json  # Networking configuration of the user.
├── model.py    # Logical modeling of networks
├── parser.py   # Used to read user configuration to establish intermediate logical representation
├── res         # The generated configuration file
│   ├── RT1.vrf
│   └── SW1.vrf
├── simulate.py # Used to simulate the network, not implemented yet
└── utils.py    # Functions that are not directly related to the main function
```

At present, it seems that there is still a lot of things to write, and it would be much better to have a UI
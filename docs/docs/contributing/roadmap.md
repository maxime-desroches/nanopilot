# Roadmap

This is the roadmap for the next major openpilot releases. Also check out
* [Milestones](https://github.com/commaai/openpilot/milestones) for minor releases
* [Projects](https://github.com/commaai/openpilot/projects?query=is%3Aopen) for shorter-term projects not tied to releases
* [Bounties](https://comma.ai/bounties) for paid individual issues

## openpilot 0.10

openpilot 0.10 will be the first release with a driving policy trained in
a [learned simulator](https://youtu.be/EqQNZXqzFSI).

### Driving

- [ ] Always-on driver monitoring (behind a toggle)
      
As of openpilot 0.9, driver monitoring only works while openpilot is engaged.
In 0.10, we will introduce an opt-in toggle that enables driver monitoring even while
disengaged, albeit with a slightly more relaxed policy.

- [ ] Driving model trained in a learned simlator

The bar for this model will be equivalent performance to the model in latest openpilot
release, which was trained in a reprojective simulator.

### System

- [ ] 100KB qlogs

`qlogs` are the smallest logs and only ones that we upload indiscriminately (all other logs are uploaded on request).
The `qlog`. 100KB should be enough to do that, and it's small enough to always upload those even as more users come online.

- [ ] `master-ci` pushed after 1000 hours in the testing closet

[`master-ci`](https://github.com/commaai/openpilot/tree/master-ci) is the latest master commit stripped, tested, and pushed out by CI.
This project introduces a second modality to our CI that will run for 1000 hours across a few dozen comma 3X's every day.


### Project

- [ ] Support for Linux x86, Linux arm64, Mac arm64

Historically, openpilot has only targeted Ubuntu 20.04. It's what runs on the comma 3/3X and what we ran on our workstations.
We'll test the latest Ubuntu LTS in x86 and arm64, and Apple Silicon macOS in CI.

- [ ] Car interface code moved into [opendbc](https://github.com/commaai/opendbc)

This pulls out most of the code in `selfdrive/car/` into a self-contained submodule that will also be its own pip-installable package.

- [ ] `./launch_openpilot.sh` on PC launches into a full openpilot experience in a simulator
      
You'll be able to go onroad/offroad, drive around, enage openpilot, and everything else you can do with a comma 3X in a car.

## openpilot 1.0

openpilot 1.0 will feature a fully end-to-end driving policy.

### Driving

- [ ] End-to-end longitudinal control in Chill mode
- [ ] Automatic Emergency Braking (AEB)
- [ ] Driver monitoring with sleep detection

### System

- [ ] Rolling updates/releases pushed out by CI
- [ ] 
  - [ ] Reports per-car
- [ ] [panda safety 1.0](https://github.com/orgs/commaai/projects/27)

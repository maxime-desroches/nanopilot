# Roadmap

This is the roadmap for the next major openpilot releases. Also check out
* [Milestones](https://github.com/commaai/openpilot/milestones) for minor releases
* [Projects](https://github.com/commaai/openpilot/projects?query=is%3Aopen) for short-lived projects
* [Bounties](https://comma.ai/bounties) for paid individual issues

## openpilot 0.10

Driving:
- [ ] Always-on driver monitoring (behind a toggle)
      
As of openpilot 0.9, driver monitoring only works while openpilot is engaged.
In 0.10, we will introduce an opt-in toggle that enables driver monitoring even while
disengaged, albeit with a slightly more relaxed policy.

- [ ] Driving model trained in a [learned simlator](https://youtu.be/EqQNZXqzFSI)

The bar for this model will be equivalent performance to the model in latest openpilot release, which was trained in a reprojective simulator.

System:
- [ ] 100KB qlogs
      `qlogs` are the smallest logs and only ones that we upload indiscriminately (all other logs are uploaded on request).
      The `qlog`. 100KB should be enough to do that, and it's small enough to always upload those even as more users come online. 
- [ ] 1000 hours MTBF in the testing closet

Project:
- [ ] Support for Linux x86, Linux arm64, Mac arm64

Historically, openpilot has only targeted Ubuntu 20.04. It's what runs on the comma 3/3X and what we ran on our workstations.
It's time to . 

- [ ] Car interface code moved into [opendbc](https://github.com/commaai/opendbc)

This pulls out most of the code in `selfdrive/car/` into a self-contained submodule that will also be its own pip-installable package.

- [ ] `./launch_openpilot.sh` on PC launches into a full openpilot experience in a simulator

You'll be able to go onroad/offroad, drive around, enage openpilot, and everything else you can do with a comma 3X in a car.

## openpilot 1.0

Driving:
- [ ] End-to-end longitudinal control in Chill mode
- [ ] Automatic Emergency Braking (AEB)
- [ ] Driver monitoring with sleep detection

System:
- [ ] Rolling updates/releases pushed out by CI
- [ ] 
  - [ ] Reports per-car
- [ ] panda safety 1.0

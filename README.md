# drone-deploy-gate
Drone plugin which can be used to gate future steps in a pipeline based on branch and/or promotion info.

[![Build Status](https://cloud.drone.io/api/badges/tangibleintelligence/drone-deploy-gate/status.svg)](https://cloud.drone.io/tangibleintelligence/drone-deploy-gate)

## Usage

Example usage in `.drone.yml` file:

```yaml
---
kind: pipeline
name: deploy
type: docker

depends_on:
  - "build"
  - "run tests"

steps:
  - name: check deploy valid
    image: austin1howard/drone-deploy-gate
    settings:
        autodeploy_branches:
            - uat
            - prod
        check_mainline: true
        mainline_branch: master
  - name: deploy
    ...
```

When the `check deploy valid` step runs, it will determine the deployment environment to use. If currently running as part of a promotion, then the promote environment will
be used as the environment name. Otherwise, if the current branch is one of the `autodeploy_branches`, the branch name will be used as the environment name. Otherwise, the
plugin will exit, gracefully stopping any future steps from running in the pipeline. (The build will not be marked as failed in this case.)

If `check_mainline` is true (the default) then the branch being deployed will be confirmed to be up to date relative to a 'mainline' branch, associated with the production environment. (This name defauls to master, but can be changed with `mainline_branch`.) If this is configured, a build that _should_ deploy but isn't up to date will fail instead.

## Environment name
If a downstream step needs the environment name being used, then `${DRONE_DEPLOY_TO:=${DRONE_BRANCH}}` will expand into the appropriate environment name, based on promotion target or branch name, as needed.
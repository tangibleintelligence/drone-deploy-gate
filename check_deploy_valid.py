"""
Checks if we should deploy or not. Return 0 if we should, code 87 if we shouldn't. (87 is a special exit code in Drone that skips
remaining steps.)
"""
import os
import subprocess
import sys
from typing import Optional

CONTINUE_EXIT_CODE = 0
SKIP_EXIT_CODE = 78
ERROR_EXIT_CODE = 1


def _should_deploy(branch: str, deploy_to: str, autodeploy_branches):
    # Check for deployment target first
    if deploy_to is not None:
        print(f"Deployment target is valid, will deploy to {deploy_to}")
        return True

    # Otherwise, branch?
    if branch is not None and branch in autodeploy_branches:
        print(f"Branch {branch} is an autodeploy branch, will deploy there.")
        return True


def main():
    # get autodeploy branches from environment
    autodeploy_branches_str = os.environ.get("PLUGIN_AUTODEPLOY_BRANCHES", None)
    if autodeploy_branches_str is None:
        autodeploy_branches = []
    else:
        autodeploy_branches = autodeploy_branches_str.split(",")

    check_mainline_str = os.environ.get("PLUGIN_CHECK_MAINLINE", "true")
    check_mainline = True if check_mainline_str.lower() == "true" else False
    mainline_branch_name = os.environ.get("PLUGIN_MAINLINE_BRANCH", "master")

    # Get build info from drone (environment)
    branch: Optional[str] = os.getenv("DRONE_BRANCH", None)
    deploy_to: Optional[str] = os.getenv("DRONE_DEPLOY_TO", None)

    print("Checking for valid deployment")
    print(f"Branch is {branch}, deployment target is {deploy_to}")

    # Should we deploy?
    if _should_deploy(branch, deploy_to, autodeploy_branches):
        # Make sure everything's valid for deployment. In particular, git branch business.
        if check_mainline and branch != mainline_branch_name:
            print("Validating state of git branches")

            # There's probably a way to do this with a python library directly, but I know the git commands needed so
            # we'll just use that for now

            # fetch the commit pointed to by mainline branch
            p = subprocess.run(["git", "fetch", "origin", f"+refs/heads/{mainline_branch_name}"], capture_output=True, text=True)

            if p.returncode != 0:
                print("Failure in fetching git origin.")
                print(p.stdout)
                print(p.stderr)

            # See if that branch has been fully merged into the current one

            p = subprocess.run(["git", "branch", "-r", "--merged"], capture_output=True, text=True)
            if p.returncode != 0:
                print("Failure comparing git branches.")
                print(p.stdout)
                print(p.stderr)

            cmd_output = p.stdout
            if cmd_output is None or f"origin/{mainline_branch_name}" not in [b.strip() for b in cmd_output.split("\n")]:
                print(
                    "Current branch is not up to date with mainline branch {mainline_branch_name}. Please merge it in before attempting to deploy."
                )
                sys.exit(ERROR_EXIT_CODE)
            else:
                print("Current branch is up to date with mainline. Proceeding with deployment.")

        # All clear
        sys.exit(CONTINUE_EXIT_CODE)
    else:
        # Otherwise nope.
        print("Deployment should not proceed. Skipping remainder of steps in Drone pipeline")
        sys.exit(SKIP_EXIT_CODE)


if __name__ == "__main__":
    main()

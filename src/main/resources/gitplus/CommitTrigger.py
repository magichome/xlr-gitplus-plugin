#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

###################################################################################
#  Name: GitPlus Commit Trigger
#
#  Description: Trigger new release when new commit is made to a git repository
#
#  Known Issues:
#    - when a branch is first added, it will always trigger a release regardless
#      of triggerOnInitialPublish state
#    - only handles a maximum of 1000 branches per repository
###################################################################################

import sys, string, urllib
import json
import pprint
import re

if server is None:
    print "No Git server provided."
    sys.exit(1)

if commitId == triggerState:
    return

request = HttpRequest(server, username, password)
context = "/api/v3/repos/%s/%s" % (owner, repo)
commit_path = "%s/commits/%s" % (context, commitId)
response = request.get(commit_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

if not response.isSuccessful():
    if response.status == 404 and triggerOnInitialPublish:
        print "Repository '%s:%s' not found in Git. Ignoring." % (owner, repo)
        # the following initialisation is to enable a scenario where we wish
        # to trigger a release on a first publish of an artifact to Git
        if not triggerState:
            branch = commitId = triggerState = committerEmail = 'unknown'
    else:
        print "Failed to fetch branch information from Git server %s" % server['url']
        response.errorDump()
        sys.exit(1)
else:
    info = json.loads(response.response)

    committerEmail = info["commit"]["committer"]["email"]

    match = false

    # check files
    if fileRegex:
        pfile = re.compile(fileRegex)
        for f in info["files"]:
            if pfile.match(f["filename"]):
                match = true
                break
    else:
        match = true

    # check branch
    if match and branchRegex:
        match = false

        branches_path = "%s/branches" % context
        response = request.get(branches_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

        if not response.isSuccessful():
            print "Failed to fetch branch information from Git server %s" % server['url']
            response.errorDump()
            sys.exit(1)


....
    # build a map of the commit ids for each branch
    newCommit = {}
    for branch in info["values"]:
        branchname = branch["displayId"]
        lastcommit = branch["latestCommit"]
        newCommit[branchname] = lastcommit

    # trigger state is perisisted as json
    newTriggerState = json.dumps(newCommit)

    if triggerState != newTriggerState:
        if len(triggerState) == 0:
            oldCommit = {}
        else:
            oldCommit = json.loads(triggerState)

        branch, commitId = findNewCommit(oldCommit, newCommit)

        triggerState = newTriggerState

        print("Git triggered for %s-%s" % (branch, commitId))

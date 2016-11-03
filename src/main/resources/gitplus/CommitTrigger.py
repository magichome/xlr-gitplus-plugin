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

repoPath = '%s/%s' % (owner, repo) # helper var for downstream tasks, not used here.

request = HttpRequest(server, username, password)
context = "/api/v3/repos/%s/%s" % (owner, repo)

# get summary info about most recent commit
commit_path = "%s/commits?per_page=1" % (context)
response = request.get(commit_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

if not response.isSuccessful():
    if response.status == 404 and triggerOnInitialPublish:
        # repo doesn't exist but that's ok.
        print "Repo not found.  Will trigger on initial publish."
    else:
        print "Failed to fetch commit information from Git server %s" % server['url']
        response.errorDump()
        sys.exit(1)

else:
    # list of commits
    info = json.loads(response.response)

    if len(info) > 0:
        # most recent commit is first (I believe)
        commitId = info[0]["sha"]

        # only do the follow checks if this is a new commit
        if triggerState != commitId:
            commitMessage = info[0]["commit"]["message"]
            committerEmail = info[0]["commit"]["committer"]["email"]
            committerName = info[0]["commit"]["committer"]["name"]
            # assume match
            match = True

            # optionally filter by file or branch
            if fileRegex or branchRegex:
                # get detail info about commit
                commit_path = "%s/commits/%s" % (context, commitId)
                response = request.get(commit_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

                if not response.isSuccessful():
                    print "Failed to fetch commit information for %s" % commitId
                    response.errorDump()
                    sys.exit(1)

                info = json.loads(response.response)
                match = False

                # check files first because we already have them
                if fileRegex:
                    pfile = re.compile(fileRegex)
                    for f in info["files"]:
                        if pfile.match(f["filename"]):
                            match = True
                            break
                else:
                    match = True

                # check branch
                if match and branchRegex:
                    match = False

                    branches_path = "%s/branches" % context
                    response = request.get(branches_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

                    if not response.isSuccessful():
                        print "Failed to fetch branch information from Git server %s" % server['url']
                        response.errorDump()
                        sys.exit(1)

                    info = json.loads(response.response)

                    # loop over branches to find the one that has our commit id
                    pfile = re.compile(branchRegex)
                    for b in info:
                        if b["commit"]["sha"] == commitId:
                            if pfile.match(b["name"]):
                                match = True
                                break

            if match:
                triggerState = commitId

                print("Git triggered for %s" % (commitId))

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
if debug:
    print 'Checking commits.  Request: %s' % commit_path

response = request.get(commit_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')
if debug:
    print 'Checking commits.  Response status: %s' % response.status

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
        if debug:
            print 'Trigger State: %s, CommitId %s' % (triggerState, commitId)

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
                if debug:
                    print 'Checking file or branch regex. Request: %s' % commit_path
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
                        if debug:
                            print '..checking file %s' % f["filename"]
                        if pfile.match(f["filename"]):
                            if debug:
                                print '....matched'
                            match = True
                            break
                    if debug:
                        print 'File regex %s match: %s' % (fileRegex, match)
                else:
                    match = True

                # check branch
                if match and branchRegex:
                    match = False

                    branches_path = "%s/branches" % context
                    if debug:
                        print 'Checking branch regex. Request: %s' % branches_path
                    response = request.get(branches_path, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

                    if not response.isSuccessful():
                        print "Failed to fetch branch information from Git server %s" % server['url']
                        response.errorDump()
                        sys.exit(1)

                    info = json.loads(response.response)

                    # loop over branches to find the one that has our commit id
                    pfile = re.compile(branchRegex)
                    for b in info:
                        if debug:
                            print '..checking branch %s with sha %s' % (b["name"], b["commit"]["sha"])
                        if b["commit"]["sha"] == commitId:
                            if pfile.match(b["name"]):
                                if debug:
                                    print '....matched'
                                match = True
                                break
                    if debug:
                        print 'Branch regex %s match: %s' % (branchRegex, match)

            if match:
                triggerState = commitId

                print("Git triggered for %s" % (commitId))

            if debug:
                print 'Final result. Match: %s' % match

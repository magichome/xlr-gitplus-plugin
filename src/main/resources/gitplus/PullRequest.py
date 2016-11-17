# tag release-candidate branch
import json

# connection to GIT server
connection = HttpRequest(server, username, password)

context = "/api/v3/repos/%s/%s" % (owner, repo)

# create the release
uri = "%s/pulls" % context
body = """{
  "title": "%s",
  "head": "%s",
  "base": "%s",
  "body": "%s"
}""" % (title, branch, base, body)

response = connection.post(uri, body, contentType = 'application/json', accept = 'application/vnd.github.v3+json')

if not response.isSuccessful():
	print response.errorDump()
	sys.exit(1)

info = json.loads(response.response)
print info

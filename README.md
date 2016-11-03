# Preface #

This document describes the functionality provided by the XL Release GIT Plus plugin.

See the **[XL Release Documentation](https://docs.xebialabs.com/xl-release/)**] for background information on XL Release concepts.

# Overview #

The XL Release GIT Plus plugin provides a couple new features.
* gitplus.CommitTrigger
	* Monitor a GIT repository for commits to any branch.  Only triggers a release when the branch and/or changed files match user define regex.
* gitplus.TagCommit
	* Tag a commit in GIT
* gitplus.PullRequest
	* Create a pull request from one branch to another.  This is useful after successful deployment of a release candidate.

# Requirements #

* **Requirements**
	* **XL Release** 5.x

# Installation #

* Place the plugin JAR file into your `SERVER_HOME/plugins` directory.
* Restart the server  

# Usage #

CommitTrigger can be found when you create a new trigger on a template.  TagCommit is a task you can add to a template.

#!/usr/bin/python3

import argparse
import concurrent.futures
import json
import os
import re
import requests
import subprocess
import tempfile

from contextlib import contextmanager

def find_all_image_commits_in_repo():
    """Find all of the commits in a repo where an image was Added, Modified.

    Copied, Deleted, Renamed, Type Changed, Unmerged, Unknown, Broken likely
    have no impact here, as they imply the file was already committed once.

    :returns: a list of [hash, filename] lists

    Refs:
    https://www.git-scm.com/docs/git-log
    """
    output = subprocess.check_output('git log --all --date-order --diff-filter=AM --name-only --pretty=format:%h --reverse'.split(' '))
    output = output.decode(errors='replace')

    table = {}

    groups = output.split('\n\n')
    for group in groups:
        g = group.strip().split('\n')
        table[g[0]] = g[1:]

    image_commits = []
    image_pattern = re.compile('|'.join(['jpg', 'jpeg']), re.IGNORECASE)

    for hash in table:
        for file in table[hash]:
            if any(image_pattern.findall(file)):
                image_commits.append([hash, file])

    # Now we have all the image_commits we want to check with the hashes where they
    # were added or modified.

    # Check the files out to /tmp and check them.
    # This is inherently parallelizable (but you have to watch out for identical filenames)
    return image_commits


def check_one_image_commit(tempdir, commit_hash, commit_filename):
    assert isinstance(tempdir, str)
    assert isinstance(commit_hash, str)
    assert isinstance(commit_filename, str)

    # pipe_filename = commit_hash + '-' + commit_filename
    # pipe_filename = pipe_filename.replace(os.path.sep, '-')
    # pipe_filename = os.path.join(tempdir, pipe_filename)
    pipe_filename = os.path.join(tempdir, commit_hash, commit_filename)
    os.makedirs(os.path.dirname(pipe_filename), exist_ok=True)
    command = f'git show {commit_hash}:{commit_filename} > {pipe_filename}'
    # print(command)
    # print(subprocess.run(command, shell=True))
    # print(subprocess.run('ls -lR /tmp', shell=True))
    output_git = subprocess.check_call(command, shell=True)
    output_exiftool = subprocess.run(f'exiftool -sort {pipe_filename} | grep -E "^GPS"', shell=True, capture_output=True)
    # print(output_git)
    # print(output_exiftool)
    # output = subprocess.run(command, shell=True)
    if output_exiftool.stdout:
        # print(f"{commit_hash} {commit_filename} contains GPS metadata and was checked in")
        return output_exiftool.stdout


def check_one_work_package(work_package):
    assert isinstance(work_package, dict)
    assert work_package.keys() & {'tempdir', 'commit_hash', 'commit_filename'}

    work_package['output'] = check_one_image_commit(work_package['tempdir'], work_package['commit_hash'], work_package['commit_filename'])
    return work_package


def check_all_image_commits_in_repo(image_commits):
    assert isinstance(image_commits, list)

    with tempfile.TemporaryDirectory(prefix='eigendoxx-') as tempdir:
        work_package = [{ 'tempdir': tempdir, 'commit_hash': item[0], 'commit_filename': item[1]} for item in image_commits]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            outputs = executor.map(check_one_work_package, work_package)
            return [o for o in outputs if o['output']]


def print_dangerous_commits(gps_commits, verbose=False):
    assert isinstance(gps_commits, list)

    if gps_commits:
        print()
        print('The following commits have pushed GPS metadata into the repo:')
        print()

    for g in gps_commits:
        print(f"{g['commit_hash']}: {g['commit_filename']}")

        if verbose:
            data = g['output'].decode(errors='replace')
            print(data)


# Ref: https://gist.github.com/howardhamilton/537e13179489d6896dd3
@contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


def check_local_folder(folder, verbose=False):
    assert isinstance(folder, str)

    with pushd(folder):
        image_commits = find_all_image_commits_in_repo()
        gps_commits = check_all_image_commits_in_repo(image_commits)

        print_dangerous_commits(gps_commits, verbose)


def check_git_repo(repo):
    pass


def clone_git_repo(url, folder):
    assert isinstance(url, str)
    assert isinstance(folder, str)


def check_public_repo_urls(urls):
    assert isinstance(urls, list)




# Ref: https://stackoverflow.com/questions/29314287/python-requests-download-only-if-newer
def check_github_user(user, verbose=False):
    assert isinstance(user, str)

    rest_filename = f'{user}-rest.json'
    status_filename = f'{user}-status.json'

    rest = {}
    status = {}

    if not os.path.isfile(rest_filename):
        r = requests.get(f'https://api.github.com/users/{user}/repos', {"type": "public", "per_page": 100, "page": 1})
        if r.status_code == 200:
            with open(rest_filename, 'wb') as file:
                file.write(r.content)
                rest = r.json()
    else:
        with open(rest_filename, 'r') as file:
            rest = json.load(file)

    if not os.path.isfile(status_filename):
        if rest:
            for item in rest:
                status[item['html_url']] = { "checked": False, "output": "" }
            with open(status_filename, 'w') as file:
                json.dump(status, file)

    print(status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Checks for GPS data in all committed files through the entire repo history.")
    parser.add_argument('-f', '--folder')  # 1st positional argument, if empty then current working directory is used
    parser.add_argument('-u', '--user')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.folder:
        if not os.path.isdir(args.folder):
            print(f'Error: "{args.folder}" does not exist, please specify a folder that can be used')
            parser.print_usage()
            exit(1)

        if not os.path.isdir(os.path.join(args.folder, '.git')):
            print(f'Error: "{args.folder}" is not a local git repository, please specify a folder that contains one')
            parser.print_usage()
            exit(1)

    elif args.user:
        check_github_user(args.user)

    # check_local_folder(args.folder)

#!/usr/bin/python3

import argparse
import concurrent.futures
import os
import re
import subprocess
import tempfile

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
    output_exiftool = subprocess.run(f'exiftool {pipe_filename} | grep -E "^GPS"', shell=True, capture_output=True)
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
            for o in outputs:
                print(o)


if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Checks for GPS data in all committed files through the entire repo history.")
    image_commits = find_all_image_commits_in_repo()
    check_all_image_commits_in_repo(image_commits)